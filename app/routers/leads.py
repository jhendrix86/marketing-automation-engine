"""
Lead router
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from loguru import logger

from app.database import get_db
from app.models.lead import Lead
from app.models.tenant_base import apply_tenant_context
from app.utils.serializers import model_to_dict

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

        lead = Lead(
            email=request.email,
            name=request.name,
            company=request.company,
            phone=request.phone,
            source=request.source,
            source_details=request.source_details,
        )
        apply_tenant_context(lead)
        db.add(lead)
        await db.commit()
        await db.refresh(lead)

        logger.info(f"Lead created: {lead.id}")
        return model_to_dict(lead)

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

        lead = await db.get(Lead, uuid.UUID(lead_id))
        if lead is None:
            raise HTTPException(status_code=404, detail=f"Lead not found: {lead_id}")

        return model_to_dict(lead)

    except HTTPException:
        raise
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

        query = select(Lead)
        if status is not None:
            query = query.where(Lead.status == status)
        if source is not None:
            query = query.where(Lead.source == source)

        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar_one()

        query = query.order_by(Lead.created_at.desc()).limit(limit).offset(offset)
        result = await db.execute(query)
        leads = [model_to_dict(l) for l in result.scalars().all()]

        return {
            "total": total,
            "leads": leads,
            "filters": {"status": status, "source": source},
            "pagination": {"limit": limit, "offset": offset}
        }

    except Exception as e:
        logger.error(f"Failed to list leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))
