"""
Lead router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from loguru import logger

from app.database import get_db

router = APIRouter()


class CreateLeadRequest(BaseModel):
    """Request to create a marketing lead"""
    email: str
    name: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    source_details: Optional[dict] = None


@router.post("/create")
async def create_lead(
    request: CreateLeadRequest,
    db: AsyncSession = Depends(get_db)
):
    """Capture a new marketing lead"""
    try:
        logger.info(f"Creating lead: {request.email}")

        # In production, this would save to database
        # For now, return a mock response
        lead = {
            "id": "mkt_lead_123",
            "email": request.email,
            "name": request.name,
            "company": request.company,
            "phone": request.phone,
            "source": request.source,
            "status": "new",
            "created_at": datetime.utcnow().isoformat()
        }

        logger.info(f"Lead created: {lead['id']}")
        return lead

    except Exception as e:
        logger.error(f"Failed to create lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{lead_id}/score")
async def get_lead_score(lead_id: str, db: AsyncSession = Depends(get_db)):
    """Get the current lead score"""
    try:
        logger.info(f"Getting lead score for {lead_id}")

        # In production, this would query from database
        # For now, return a mock response
        score = {
            "lead_id": lead_id,
            "demographic_score": 20,
            "behavior_score": 35,
            "engagement_score": 15,
            "total_score": 70,
            "scoring_model": "default"
        }

        return score

    except Exception as e:
        logger.error(f"Failed to get lead score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{lead_id}")
async def get_lead(lead_id: str, db: AsyncSession = Depends(get_db)):
    """Get lead details"""
    try:
        logger.info(f"Getting lead details for {lead_id}")

        # In production, this would query from database
        # For now, return a mock response
        lead = {
            "id": lead_id,
            "email": "lead@example.com",
            "name": "Jordan Lee",
            "status": "contacted",
            "source": "funnel",
            "created_at": datetime.utcnow().isoformat()
        }

        return lead

    except Exception as e:
        logger.error(f"Failed to get lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_leads(
    status: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List marketing leads"""
    try:
        logger.info("Listing leads")

        # In production, this would query from database with filters
        # For now, return a mock response
        leads = [
            {"id": "mkt_lead_001", "email": "lead1@example.com", "status": "new", "source": "funnel"},
            {"id": "mkt_lead_002", "email": "lead2@example.com", "status": "qualified", "source": "social"},
        ]

        return {
            "total": len(leads),
            "leads": leads,
            "filters": {"status": status, "source": source},
            "pagination": {"limit": limit, "offset": offset}
        }

    except Exception as e:
        logger.error(f"Failed to list leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))
