"""
Marketing analytics router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta
from loguru import logger

from app.database import get_db

router = APIRouter()


@router.get("/overview")
async def get_marketing_overview(db: AsyncSession = Depends(get_db)):
    """Get a marketing performance overview"""
    try:
        logger.info("Getting marketing overview")

        # In production, this would aggregate from database
        # For now, return a mock response
        overview = {
            "total_leads": 3120,
            "total_campaigns": 18,
            "active_campaigns": 5,
            "total_segments": 6,
            "avg_lead_score": 54
        }

        return {"timestamp": datetime.utcnow().isoformat(), "overview": overview}

    except Exception as e:
        logger.error(f"Failed to get marketing overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaign-performance")
async def get_campaign_performance(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get campaign performance breakdown"""
    try:
        logger.info("Getting campaign performance")

        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
        if not end_date:
            end_date = datetime.utcnow().isoformat()

        # In production, this would aggregate from database
        # For now, return a mock response
        campaigns = [
            {"campaign_id": "camp_001", "name": "Welcome Series", "leads": 450, "conversions": 35},
            {"campaign_id": "camp_002", "name": "Product Launch", "leads": 1200, "conversions": 88},
        ]

        return {
            "period": {"start_date": start_date, "end_date": end_date},
            "campaigns": campaigns
        }

    except Exception as e:
        logger.error(f"Failed to get campaign performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attribution")
async def get_source_attribution(db: AsyncSession = Depends(get_db)):
    """Get lead source attribution breakdown"""
    try:
        logger.info("Getting source attribution")

        # In production, this would aggregate from database
        # For now, return a mock response
        sources = [
            {"source": "funnel", "leads": 1400, "conversions": 120},
            {"source": "social", "leads": 980, "conversions": 60},
            {"source": "email", "leads": 740, "conversions": 45},
        ]

        return {"sources": sources}

    except Exception as e:
        logger.error(f"Failed to get source attribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))
