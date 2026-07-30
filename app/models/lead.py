"""
Lead models
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Lead(Base):
    """Lead model"""
    __tablename__ = "leads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Contact information
    email = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    
    # Source
    source = Column(String(100), nullable=True)  # funnel, social, email, etc.
    source_details = Column(JSON, nullable=True)
    
    # Status
    status = Column(String(20), default="new")  # new, contacted, qualified, converted, lost
    
    # Metadata
    metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scores = relationship("LeadScore", back_populates="lead")
    
    def __repr__(self):
        return f"<Lead {self.id} - {self.email} - {self.status}>"


class LeadScore(Base):
    """Lead score model"""
    __tablename__ = "lead_scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    
    # Score components
    demographic_score = Column(Integer, default=0)
    behavior_score = Column(Integer, default=0)
    engagement_score = Column(Integer, default=0)
    custom_score = Column(Integer, default=0)
    
    # Total score
    total_score = Column(Integer, default=0)
    
    # Score details
    scoring_model = Column(String(50), default="default")
    score_details = Column(JSON, nullable=True)
    
    # Timestamps
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lead = relationship("Lead", back_populates="scores")
    
    def __repr__(self):
        return f"<LeadScore {self.lead_id} - {self.total_score}>"
