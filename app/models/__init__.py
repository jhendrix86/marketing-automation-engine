"""
Database models for Marketing Automation Engine
"""

from .campaign import Campaign, CampaignStatus, CampaignType
from .email_campaign import EmailCampaign, EmailStats
from .social_post import SocialPost, SocialPlatform
from .lead import Lead, LeadScore
from .segment import Segment

__all__ = [
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
