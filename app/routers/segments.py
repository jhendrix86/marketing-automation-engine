"""
Segment router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from loguru import logger

from app.database import get_db

router = APIRouter()


class CreateSegmentRequest(BaseModel):
    """Request to create a segment"""
    name: str
    description: Optional[str] = None
    rules: dict
    rule_type: Optional[str] = "dynamic"


@router.post("/create")
async def create_segment(
    request: CreateSegmentRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a lead segment"""
    try:
        logger.info(f"Creating segment: {request.name}")

        # In production, this would save to database
        # For now, return a mock response
        segment = {
            "id": "segment_123",
            "name": request.name,
            "description": request.description,
            "rules": request.rules,
            "rule_type": request.rule_type,
            "lead_count": 0,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }

        logger.info(f"Segment created: {segment['id']}")
        return segment

    except Exception as e:
        logger.error(f"Failed to create segment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{segment_id}")
async def get_segment(segment_id: str, db: AsyncSession = Depends(get_db)):
    """Get segment details"""
    try:
        logger.info(f"Getting segment details for {segment_id}")

        # In production, this would query from database
        # For now, return a mock response
        segment = {
            "id": segment_id,
            "name": "High-Intent Leads",
            "rule_type": "dynamic",
            "lead_count": 214,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }

        return segment

    except Exception as e:
        logger.error(f"Failed to get segment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_segments(
    is_active: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List segments"""
    try:
        logger.info("Listing segments")

        # In production, this would query from database with filters
        # For now, return a mock response
        segments = [
            {"id": "segment_001", "name": "High-Intent Leads", "lead_count": 214, "is_active": True},
            {"id": "segment_002", "name": "Cold Leads", "lead_count": 890, "is_active": True},
        ]

        return {
            "total": len(segments),
            "segments": segments,
            "filters": {"is_active": is_active},
            "pagination": {"limit": limit, "offset": offset}
        }

    except Exception as e:
        logger.error(f"Failed to list segments: {e}")
        raise HTTPException(status_code=500, detail=str(e))
