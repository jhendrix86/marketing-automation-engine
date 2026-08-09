"""
Email campaign router

/create and /{id}/send do real work: /create persists a real EmailCampaign
row (validating the parent Campaign exists); /send fetches it and actually
calls SendGrid per recipient via app/services/esp/sendgrid_client.py,
recording a real EmailStats row from the outcomes - or an honest failure
when SendGrid isn't configured, rather than faking success.

Optionally, /create can take 2+ subject-line variants. When it does, /send
uses the shared ab_testing package (../ab-testing) to deterministically split
recipients across variants (ab_testing.assign_variant) instead of sending
everyone the same subject/content, and /{id}/ab-results reports a real
winner via ab_testing.two_proportion_z_test - using "delivered" as the
outcome metric since open/click tracking isn't wired yet.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from loguru import logger

from ab_testing.models import Experiment, Variant
from ab_testing.assignment import assign_variant
from ab_testing.stats import two_proportion_z_test

from app.database import get_db
from app.models.campaign import Campaign
from app.models.email_campaign import EmailCampaign, EmailCampaignVariant, EmailStats
from app.models.lead import Lead
from app.services.esp.sendgrid_client import SendGridClient
from app.utils.serializers import model_to_dict

router = APIRouter()


class EmailVariantIn(BaseModel):
    """One subject-line/content variant to A/B test."""
    name: str
    subject: str
    html_content: Optional[str] = None


class CreateEmailCampaignRequest(BaseModel):
    """Request to create an email campaign"""
    campaign_id: str
    subject: str
    from_name: Optional[str] = None
    from_email: str
    template_id: Optional[str] = None
    html_content: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    is_drip: Optional[bool] = False
    drip_interval_days: Optional[int] = None
    variants: Optional[List[EmailVariantIn]] = None


class SendEmailCampaignRequest(BaseModel):
    """Request to send an email campaign. Omit recipient_emails to send to every lead on file."""
    recipient_emails: Optional[List[str]] = None


async def _get_campaign_with_variants(db: AsyncSession, email_campaign_id: str) -> Optional[EmailCampaign]:
    result = await db.execute(
        select(EmailCampaign)
        .options(selectinload(EmailCampaign.variants))
        .where(EmailCampaign.id == uuid.UUID(email_campaign_id))
    )
    return result.scalar_one_or_none()


@router.post("/create")
async def create_email_campaign(
    request: CreateEmailCampaignRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create an email campaign"""
    try:
        logger.info(f"Creating email campaign: {request.subject}")

        campaign = await db.get(Campaign, uuid.UUID(request.campaign_id))
        if campaign is None:
            raise HTTPException(status_code=404, detail=f"Campaign not found: {request.campaign_id}")

        email_campaign = EmailCampaign(
            campaign_id=campaign.id,
            subject=request.subject,
            from_name=request.from_name,
            from_email=request.from_email,
            template_id=request.template_id,
            html_content=request.html_content,
            scheduled_at=request.scheduled_at,
            is_drip=request.is_drip,
            drip_interval_days=request.drip_interval_days,
        )
        db.add(email_campaign)

        variants: List[EmailCampaignVariant] = []
        if request.variants:
            if len(request.variants) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="Provide at least 2 variants for an A/B test, or omit variants entirely",
                )
            await db.flush()  # populate email_campaign.id for the FK below
            for v in request.variants:
                variant = EmailCampaignVariant(
                    email_campaign_id=email_campaign.id,
                    name=v.name,
                    subject=v.subject,
                    html_content=v.html_content,
                )
                db.add(variant)
                variants.append(variant)

        await db.commit()
        await db.refresh(email_campaign)
        for v in variants:
            await db.refresh(v)

        logger.info(f"Email campaign created: {email_campaign.id}")
        result = model_to_dict(email_campaign)
        result["variants"] = [model_to_dict(v) for v in variants]
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create email campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{email_campaign_id}/send")
async def send_email_campaign(
    email_campaign_id: str,
    request: SendEmailCampaignRequest = SendEmailCampaignRequest(),
    db: AsyncSession = Depends(get_db),
):
    """Send an email campaign via SendGrid"""
    try:
        logger.info(f"Sending email campaign {email_campaign_id}")

        email_campaign = await _get_campaign_with_variants(db, email_campaign_id)
        if email_campaign is None:
            raise HTTPException(status_code=404, detail=f"Email campaign not found: {email_campaign_id}")

        if request.recipient_emails:
            recipients = request.recipient_emails
        else:
            result = await db.execute(select(Lead.email))
            recipients = [row[0] for row in result.all()]

        experiment: Optional[Experiment] = None
        variants_by_name: dict = {}
        if email_campaign.variants and len(email_campaign.variants) >= 2:
            experiment = Experiment(
                id=str(email_campaign.id),
                name=email_campaign.subject,
                variants=[Variant(name=v.name) for v in email_campaign.variants],
            )
            variants_by_name = {v.name: v for v in email_campaign.variants}

        client = SendGridClient()
        sent = delivered = bounced = 0
        first_error: Optional[str] = None
        for recipient in recipients:
            subject = email_campaign.subject
            html_content = email_campaign.html_content or ""
            variant = None
            if experiment is not None:
                variant_name = assign_variant(experiment, recipient)
                variant = variants_by_name[variant_name]
                subject = variant.subject
                html_content = variant.html_content or ""

            send_result = await client.send_email(
                to_email=recipient,
                from_email=email_campaign.from_email,
                subject=subject,
                html_content=html_content,
            )
            sent += 1
            if variant is not None:
                variant.sent += 1
            if send_result.success:
                delivered += 1
                if variant is not None:
                    variant.delivered += 1
            else:
                bounced += 1
                first_error = first_error or send_result.error

        email_campaign.sent_at = datetime.utcnow()
        stats = EmailStats(
            email_campaign_id=email_campaign.id,
            sent=sent,
            delivered=delivered,
            bounced=bounced,
            open_rate=0,
            click_rate=0,
            bounce_rate=int(bounced / sent * 100) if sent else 0,
        )
        db.add(stats)
        await db.commit()

        result = {
            "id": str(email_campaign.id),
            "status": "sent" if delivered else "failed",
            "recipients": sent,
            "delivered": delivered,
            "bounced": bounced,
            "sent_at": email_campaign.sent_at.isoformat(),
            "ab_test": experiment is not None,
        }
        if first_error:
            result["error"] = first_error
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send email campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{email_campaign_id}/ab-results")
async def get_email_ab_results(email_campaign_id: str, db: AsyncSession = Depends(get_db)):
    """
    Real statistical-significance results for a 2-variant email subject-line
    test, computed from actual send/delivery counts recorded by /send - not
    a mock. Uses "delivered" as the outcome metric since open/click tracking
    isn't wired up yet.
    """
    try:
        email_campaign = await _get_campaign_with_variants(db, email_campaign_id)
        if email_campaign is None:
            raise HTTPException(status_code=404, detail=f"Email campaign not found: {email_campaign_id}")

        if not email_campaign.variants or len(email_campaign.variants) != 2:
            raise HTTPException(
                status_code=400,
                detail="A/B results require exactly 2 variants on this campaign",
            )

        variant_a, variant_b = sorted(email_campaign.variants, key=lambda v: v.name)[:2]
        z_result = two_proportion_z_test(
            conversions_a=variant_a.delivered, visitors_a=variant_a.sent,
            conversions_b=variant_b.delivered, visitors_b=variant_b.sent,
        )

        winner_name = None
        if z_result.winner == "a":
            winner_name = variant_a.name
        elif z_result.winner == "b":
            winner_name = variant_b.name

        return {
            "email_campaign_id": str(email_campaign.id),
            "metric": "delivered / sent",
            "variants": {
                variant_a.name: {"sent": variant_a.sent, "delivered": variant_a.delivered, "rate": z_result.rate_a},
                variant_b.name: {"sent": variant_b.sent, "delivered": variant_b.delivered, "rate": z_result.rate_b},
            },
            "z_score": z_result.z_score,
            "p_value": z_result.p_value,
            "significant_at_95": z_result.significant_at_95,
            "winner": winner_name,
            "error": z_result.error,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to compute A/B results for {email_campaign_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{email_campaign_id}/stats")
async def get_email_stats(email_campaign_id: str, db: AsyncSession = Depends(get_db)):
    """Get stats for an email campaign"""
    try:
        logger.info(f"Getting email stats for {email_campaign_id}")

        # In production, this would query from database
        # For now, return a mock response
        stats = {
            "email_campaign_id": email_campaign_id,
            "sent": 1000,
            "delivered": 980,
            "opened": 410,
            "clicked": 96,
            "bounced": 20,
            "unsubscribed": 3,
            "open_rate": 42,
            "click_rate": 10,
            "bounce_rate": 2
        }

        return stats

    except Exception as e:
        logger.error(f"Failed to get email stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_email_campaigns(
    campaign_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List email campaigns"""
    try:
        logger.info("Listing email campaigns")

        # In production, this would query from database with filters
        # For now, return a mock response
        email_campaigns = [
            {"id": "email_camp_001", "subject": "Welcome to the family!", "is_drip": True},
            {"id": "email_camp_002", "subject": "Your product launch is live", "is_drip": False},
        ]

        return {
            "total": len(email_campaigns),
            "email_campaigns": email_campaigns,
            "filters": {"campaign_id": campaign_id},
            "pagination": {"limit": limit, "offset": offset}
        }

    except Exception as e:
        logger.error(f"Failed to list email campaigns: {e}")
        raise HTTPException(status_code=500, detail=str(e))
