"""
Marketing Automation Engine smoke tests
"""
import pytest


@pytest.mark.asyncio
async def test_campaign_models_import():
    """Verify campaign models import without error"""
    from app.models.campaign import Campaign, CampaignStatus, CampaignType
    assert Campaign is not None
    assert CampaignStatus.DRAFT == "draft"
    assert CampaignType.EMAIL == "email"


@pytest.mark.asyncio
async def test_app_instantiation():
    """Verify FastAPI app instantiates without error"""
    from app.main import app
    assert app is not None
    assert app.title == "Marketing Automation Engine"
