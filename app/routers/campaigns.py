"""
Campaign router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from loguru import logger

from app.database import get_db
from app.models.campaign import Campaign, CampaignStatus, CampaignType

router = APIRouter()


class CreateCampaignRequest(BaseModel):
    """Request to create campaign"""
    name: str
    description: Optional[str] = None
    campaign_type: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    segment_id: Optional[str] = None
    budget: Optional[int] = None
    target_leads: Optional[int] = None
    target_conversions: Optional[int] = None


@router.post("/create")
async def create_campaign(
    request: CreateCampaignRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a marketing campaign"""
    try:
        logger.info(f"Creating campaign: {request.name}")
        
        # In production, this would save to database
        # For now, return a mock response
        campaign = {
            "id": "camp_123",
            "name": request.name,
            "description": request.description,
            "campaign_type": request.campaign_type,
            "status": "draft",
            "start_date": request.start_date,
            "end_date": request.end_date,
            "segment_id": request.segment_id,
            "budget": request.budget,
            "target_leads": request.target_leads,
            "target_conversions": request.target_conversions,
            "created_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Campaign created: {campaign['id']}")
        return campaign
        
    except Exception as e:
        logger.error(f"Failed to create campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{campaign_id}/launch")
async def launch_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Launch a campaign"""
    try:
        logger.info(f"Launching campaign {campaign_id}")
        
        # In production, this would update status and start campaign
        # For now, return a mock response
        campaign = {
            "id": campaign_id,
            "status": "running",
            "launched_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Campaign launched: {campaign_id}")
        return campaign
        
    except Exception as e:
        logger.error(f"Failed to launch campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{campaign_id}")
async def get_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get campaign details"""
    try:
        logger.info(f"Getting campaign details for {campaign_id}")
        
        # In production, this would query from database
        # For now, return a mock response
        campaign = {
            "id": campaign_id,
            "name": "Welcome Series",
            "description": "Email welcome campaign for new users",
            "campaign_type": "email",
            "status": "running",
            "start_date": datetime.utcnow().isoformat(),
            "target_leads": 1000,
            "actual_leads": 450,
            "target_conversions": 100,
            "actual_conversions": 35
        }
        
        return campaign
        
    except Exception as e:
        logger.error(f"Failed to get campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_campaigns(
    status: Optional[str] = None,
    campaign_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List campaigns"""
    try:
        logger.info("Listing campaigns")
        
        # In production, this would query from database with filters
        # For now, return a mock response
        campaigns = [
            {
                "id": "camp_001",
                "name": "Welcome Series",
                "campaign_type": "email",
                "status": "running",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "camp_002",
                "name": "Product Launch",
                "campaign_type": "multi_channel",
                "status": "scheduled",
                "created_at": (datetime.utcnow() - timedelta(days=7)).isoformat()
            }
        ]
        
        return {
            "total": len(campaigns),
            "campaigns": campaigns,
            "filters": {
                "status": status,
                "campaign_type": campaign_type
            },
            "pagination": {
                "limit": limit,
                "offset": offset
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to list campaigns: {e}")
        raise HTTPException(status_code=500, detail=str(e))
