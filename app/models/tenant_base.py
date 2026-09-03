"""
Tenant base mixin for multi-tenancy support
"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy import Uuid
from app.tenant_context import get_tenant_context
from loguru import logger


class TenantBase:
    """Mixin class that adds tenant_id to models for multi-tenancy."""
    tenant_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=True,  # Initially nullable for migration
        index=True,
        comment="Tenant identifier for data isolation"
    )


def apply_tenant_context(model_instance):
    """
    Apply the current tenant context to a model instance if not already set.

    Args:
        model_instance: Model instance to apply tenant context to
    """
    tenant_id = get_tenant_context()

    if tenant_id is None:
        logger.debug("No tenant context available, skipping tenant assignment")
        return

    if hasattr(model_instance, 'tenant_id') and model_instance.tenant_id is None:
        model_instance.tenant_id = tenant_id
        logger.debug(f"Applied tenant context to model: {tenant_id}")
