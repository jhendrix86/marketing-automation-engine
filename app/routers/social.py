"""
Social post router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from loguru import logger

from app.database import get_db

router = APIRouter()


class CreateSocialPostRequest(BaseModel):
    """Request to create a social post"""
    campaign_id: Optional[str] = None
    platform: str
    content: str
    media_urls: Optional[list] = None
    scheduled_at: Optional[str] = None


@router.post("/create")
async def create_social_post(
    request: CreateSocialPostRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a social post"""
    try:
        logger.info(f"Creating social post for {request.platform}")

        # In production, this would save to database
        # For now, return a mock response
        post = {
            "id": "social_post_123",
            "campaign_id": request.campaign_id,
            "platform": request.platform,
            "content": request.content,
            "media_urls": request.media_urls,
            "scheduled_at": request.scheduled_at,
            "status": "scheduled" if request.scheduled_at else "draft",
            "created_at": datetime.utcnow().isoformat()
        }

        logger.info(f"Social post created: {post['id']}")
        return post

    except Exception as e:
        logger.error(f"Failed to create social post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{post_id}/publish")
async def publish_social_post(post_id: str, db: AsyncSession = Depends(get_db)):
    """Publish a social post"""
    try:
        logger.info(f"Publishing social post {post_id}")

        # In production, this would call the target platform's API
        # For now, return a mock response
        result = {
            "id": post_id,
            "status": "published",
            "published_at": datetime.utcnow().isoformat()
        }

        return result

    except Exception as e:
        logger.error(f"Failed to publish social post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{post_id}")
async def get_social_post(post_id: str, db: AsyncSession = Depends(get_db)):
    """Get a social post"""
    try:
        logger.info(f"Getting social post {post_id}")

        # In production, this would query from database
        # For now, return a mock response
        post = {
            "id": post_id,
            "platform": "twitter",
            "content": "Check out our latest product launch!",
            "status": "published",
            "created_at": datetime.utcnow().isoformat()
        }

        return post

    except Exception as e:
        logger.error(f"Failed to get social post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_social_posts(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List social posts"""
    try:
        logger.info("Listing social posts")

        # In production, this would query from database with filters
        # For now, return a mock response
        posts = [
            {"id": "social_post_001", "platform": "twitter", "status": "published"},
            {"id": "social_post_002", "platform": "linkedin", "status": "scheduled"},
        ]

        return {
            "total": len(posts),
            "posts": posts,
            "filters": {"platform": platform, "status": status},
            "pagination": {"limit": limit, "offset": offset}
        }

    except Exception as e:
        logger.error(f"Failed to list social posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))
