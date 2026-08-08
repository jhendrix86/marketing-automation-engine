"""
Email campaign router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from loguru import logger

from app.database import get_db

router = APIRouter()


class CreateEmailCampaignRequest(BaseModel):
    """Request to create an email campaign"""
    campaign_id: str
    subject: str
    from_name: Optional[str] = None
    from_email: str
    template_id: Optional[str] = None
    html_content: Optional[str] = None
    scheduled_at: Optional[str] = None
    is_drip: Optional[bool] = False
    drip_interval_days: Optional[int] = None


@router.post("/create")
async def create_email_campaign(
    request: CreateEmailCampaignRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create an email campaign"""
    try:
        logger.info(f"Creating email campaign: {request.subject}")

        # In production, this would save to database
        # For now, return a mock response
        email_campaign = {
            "id": "email_camp_123",
            "campaign_id": request.campaign_id,
            "subject": request.subject,
            "from_name": request.from_name,
            "from_email": request.from_email,
            "template_id": request.template_id,
            "scheduled_at": request.scheduled_at,
            "is_drip": request.is_drip,
            "drip_interval_days": request.drip_interval_days,
            "created_at": datetime.utcnow().isoformat()
        }

        logger.info(f"Email campaign created: {email_campaign['id']}")
        return email_campaign

    except Exception as e:
        logger.error(f"Failed to create email campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{email_campaign_id}/send")
async def send_email_campaign(email_campaign_id: str, db: AsyncSession = Depends(get_db)):
    """Send an email campaign"""
    try:
        logger.info(f"Sending email campaign {email_campaign_id}")

        # In production, this would trigger delivery via an ESP
        # For now, return a mock response
        result = {
            "id": email_campaign_id,
            "status": "sent",
            "sent_at": datetime.utcnow().isoformat()
        }

        return result

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
