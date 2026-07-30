"""
Email campaign models
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class EmailCampaign(Base):
    """Email campaign model"""
    __tablename__ = "email_campaigns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    
    # Email details
    subject = Column(String(500), nullable=False)
    from_name = Column(String(255), nullable=True)
    from_email = Column(String(255), nullable=False)
    
    # Content
    template_id = Column(String(100), nullable=True)
    html_content = Column(Text, nullable=True)
    text_content = Column(Text, nullable=True)
    
    # Schedule
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    
    # Type
    is_drip = Column(Boolean, default=False)
    drip_interval_days = Column(Integer, nullable=True)
    
    # Metadata
    metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign")
    
    def __repr__(self):
        return f"<EmailCampaign {self.id} - {self.subject}>"


class EmailStats(Base):
    """Email statistics model"""
    __tablename__ = "email_stats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_campaign_id = Column(UUID(as_uuid=True), ForeignKey("email_campaigns.id"), nullable=False)
    
    # Metrics
    sent = Column(Integer, default=0)
    delivered = Column(Integer, default=0)
    opened = Column(Integer, default=0)
    clicked = Column(Integer, default=0)
    bounced = Column(Integer, default=0)
    unsubscribed = Column(Integer, default=0)
    
    # Rates
    open_rate = Column(Integer, default=0)  # percentage
    click_rate = Column(Integer, default=0)  # percentage
    bounce_rate = Column(Integer, default=0)  # percentage
    
    # Timestamps
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    email_campaign = relationship("EmailCampaign")
    
    def __repr__(self):
        return f"<EmailStats {self.email_campaign_id} - {self.open_rate}% open rate>"
