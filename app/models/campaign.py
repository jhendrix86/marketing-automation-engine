"""
Campaign models
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum, ForeignKey, Text, JSON
from sqlalchemy import Uuid
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base
from app.models.tenant_base import TenantBase


class CampaignStatus(str, enum.Enum):
    """Campaign status enumeration"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CampaignType(str, enum.Enum):
    """Campaign type enumeration"""
    EMAIL = "email"
    SOCIAL = "social"
    MULTI_CHANNEL = "multi_channel"
    RETARGETING = "retargeting"
    NURTURE = "nurture"


class Campaign(TenantBase, Base):
    """Campaign model"""
    __tablename__ = "campaigns"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Campaign details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    campaign_type = Column(Enum(CampaignType), nullable=False)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    
    # Schedule
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # Targeting
    segment_id = Column(Uuid(as_uuid=True), ForeignKey("segments.id"), nullable=True)
    
    # Budget
    budget = Column(Integer, nullable=True)
    spent = Column(Integer, default=0)
    
    # Goals
    target_leads = Column(Integer, nullable=True)
    target_conversions = Column(Integer, nullable=True)
    
    # Results
    actual_leads = Column(Integer, default=0)
    actual_conversions = Column(Integer, default=0)
    
    # Metadata
    extra_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    segment = relationship("Segment", back_populates="campaigns")
    
    def __repr__(self):
        return f"<Campaign {self.name} - {self.status}>"
