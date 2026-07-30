"""
Segment models
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Segment(Base):
    """Segment model"""
    __tablename__ = "segments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Segment details
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Segment rules
    rules = Column(JSON, nullable=False)  # Segment definition rules
    rule_type = Column(String(50), default="dynamic")  # dynamic, static
    
    # Size
    lead_count = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    extra_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaigns = relationship("Campaign")
    
    def __repr__(self):
        return f"<Segment {self.name} - {self.lead_count} leads>"
