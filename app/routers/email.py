"""
Email campaign router

/create and /{id}/send do real work: /create persists a real EmailCampaign
row (validating the parent Campaign exists); /send fetches it and actually
calls SendGrid per recipient via app/services/esp/sendgrid_client.py,
recording a real EmailStats row from the outcomes - or an honest failure
when SendGrid isn't configured, rather than faking success.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from loguru import logger

from app.database import get_db
from app.models.campaign import Campaign
from app.models.email_campaign import EmailCampaign, EmailStats
from app.models.lead import Lead
from app.services.esp.sendgrid_client import SendGridClient
from app.utils.serializers import model_to_dict

router = APIRouter()


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


class SendEmailCampaignRequest(BaseModel):
    """Request to send an email campaign. Omit recipient_emails to send to every lead on file."""
    recipient_emails: Optional[List[str]] = None


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
        await db.commit()
        await db.refresh(email_campaign)

        logger.info(f"Email campaign created: {email_campaign.id}")
        return model_to_dict(email_campaign)

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

        email_campaign = await db.get(EmailCampaign, uuid.UUID(email_campaign_id))
        if email_campaign is None:
            raise HTTPException(status_code=404, detail=f"Email campaign not found: {email_campaign_id}")

        if request.recipient_emails:
            recipients = request.recipient_emails
        else:
            from sqlalchemy import select
            result = await db.execute(select(Lead.email))
            recipients = [row[0] for row in result.all()]

        client = SendGridClient()
        sent = delivered = bounced = 0
        first_error: Optional[str] = None
        for recipient in recipients:
            send_result = await client.send_email(
                to_email=recipient,
                from_email=email_campaign.from_email,
                subject=email_campaign.subject,
                html_content=email_campaign.html_content or "",
            )
            sent += 1
            if send_result.success:
                delivered += 1
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
        }
        if first_error:
            result["error"] = first_error
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send email campaign: {e}")
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
