"""
Social post models
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum, ForeignKey, Text, JSON
from sqlalchemy import Uuid
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base
from app.models.tenant_base import TenantBase


class SocialPlatform(str, enum.Enum):
    """Social platform enumeration"""
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"


class SocialPost(TenantBase, Base):
    """Social post model"""
    __tablename__ = "social_posts"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(Uuid(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    
    # Post details
    platform = Column(Enum(SocialPlatform), nullable=False)
    content = Column(Text, nullable=False)
    media_urls = Column(JSON, nullable=True)  # List of media URLs
    
    # Schedule
    scheduled_at = Column(DateTime, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(20), default="scheduled")  # scheduled, posted, failed
    
    # External IDs
    external_post_id = Column(String(255), nullable=True)
    
    # Metrics
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    
    # Metadata
    extra_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign")
    
    def __repr__(self):
        return f"<SocialPost {self.id} - {self.platform}>"
