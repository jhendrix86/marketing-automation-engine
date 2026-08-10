"""
Email campaign models
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base
from app.models.tenant_base import TenantBase


class EmailCampaign(TenantBase, Base):
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
    extra_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign")
    variants = relationship("EmailCampaignVariant", back_populates="email_campaign", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<EmailCampaign {self.id} - {self.subject}>"


class EmailCampaignVariant(TenantBase, Base):
    """
    A/B test variant for an email campaign. When an EmailCampaign has 2+
    variants, recipients are deterministically split between them
    (ab_testing.assign_variant) rather than everyone getting the campaign's
    top-level subject/html_content.
    """
    __tablename__ = "email_campaign_variants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_campaign_id = Column(UUID(as_uuid=True), ForeignKey("email_campaigns.id"), nullable=False)

    name = Column(String(50), nullable=False)  # e.g. "a", "b"
    subject = Column(String(500), nullable=False)
    html_content = Column(Text, nullable=True)

    # Real, measured outcomes for this variant
    sent = Column(Integer, default=0)
    delivered = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    email_campaign = relationship("EmailCampaign", back_populates="variants")

    def __repr__(self):
        return f"<EmailCampaignVariant {self.name} - {self.email_campaign_id}>"


class EmailStats(TenantBase, Base):
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
