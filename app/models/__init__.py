"""
Database models for Marketing Automation Engine
"""

from .tenant import Tenant
from .tenant_base import TenantBase, apply_tenant_context
from .campaign import Campaign, CampaignStatus, CampaignType
from .email_campaign import EmailCampaign, EmailStats
from .social_post import SocialPost, SocialPlatform
from .lead import Lead, LeadScore
from .segment import Segment

__all__ = [
    'Tenant',
    'TenantBase',
    'apply_tenant_context',
    'Campaign',
    'CampaignStatus',
    'CampaignType',
    'EmailCampaign',
    'EmailStats',
    'SocialPost',
    'SocialPlatform',
    'Lead',
    'LeadScore',
    'Segment'
]
