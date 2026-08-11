"""
Campaign router
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from loguru import logger

from app.database import get_db
from app.models.campaign import Campaign, CampaignStatus, CampaignType
from app.models.tenant_base import apply_tenant_context
from app.utils.serializers import model_to_dict

router = APIRouter()


class CreateCampaignRequest(BaseModel):
    """Request to create campaign"""
    name: str
    description: Optional[str] = None
    campaign_type: CampaignType
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
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

        campaign = Campaign(
            name=request.name,
            description=request.description,
            campaign_type=request.campaign_type,
            start_date=request.start_date,
            end_date=request.end_date,
            segment_id=uuid.UUID(request.segment_id) if request.segment_id else None,
            budget=request.budget,
            target_leads=request.target_leads,
            target_conversions=request.target_conversions,
        )
        apply_tenant_context(campaign)
        db.add(campaign)
        await db.commit()
        await db.refresh(campaign)

        logger.info(f"Campaign created: {campaign.id}")
        return model_to_dict(campaign)

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

        campaign = await db.get(Campaign, uuid.UUID(campaign_id))
        if campaign is None:
            raise HTTPException(status_code=404, detail=f"Campaign not found: {campaign_id}")

        return model_to_dict(campaign)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_campaigns(
    status: Optional[CampaignStatus] = None,
    campaign_type: Optional[CampaignType] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List campaigns"""
    try:
        logger.info("Listing campaigns")

        query = select(Campaign)
        if status is not None:
            query = query.where(Campaign.status == status)
        if campaign_type is not None:
            query = query.where(Campaign.campaign_type == campaign_type)

        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar_one()

        query = query.order_by(Campaign.created_at.desc()).limit(limit).offset(offset)
        result = await db.execute(query)
        campaigns = [model_to_dict(c) for c in result.scalars().all()]

        return {
            "total": total,
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
