"""
Marketing Automation Engine - Main Application
Automated marketing campaign system for the Autonomous Company OS
"""

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
from datetime import datetime
import os

from unkey_auth import require_api_key

from app.config import settings
from app.database import init_db
from app.routers import campaigns, email, social, leads, segments, analytics
from app.middleware.tenant import TenantMiddleware
from empire_operators.middleware import SafetyBoundaryMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Marketing Automation Engine...")
    
    # Initialize database
    await init_db()
    
    logger.info("Marketing Automation Engine started successfully")
    yield
    
    logger.info("Shutting down Marketing Automation Engine...")


# Create FastAPI application
app = FastAPI(
    title="Marketing Automation Engine",
    description="Automated marketing campaign system for the Autonomous Company OS",
    version="1.0.0",
    lifespan=lifespan,
    # SECURITY_REVIEW.md finding: /docs, /redoc, /openapi.json were reachable
    # unauthenticated on every engine (dynamic-pentest-confirmed) - a full
    # interactive API browser plus every unauth write path. Disabled unless
    # DEBUG=true.
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

# Configure CORS — see SECURITY_REVIEW.md finding #1: no wildcard with
# credentials; allowed origins come from the ALLOWED_ORIGINS env var.
def _cors_allowed_origins() -> list:
    # SECURITY_REVIEW.md #1 — no wildcard with credentials. Set
    # ALLOWED_ORIGINS (comma-separated) when a browser client exists.
    import os
    return [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add tenant middleware for multi-tenancy support
app.add_middleware(TenantMiddleware)

# Reject request bodies matching known-unsafe patterns (prompt injection,
# `drop table`, `<script>`) before they reach a router. empire_os
# SafetyBoundaryOperator via the empire-operators sibling — Step 8 Phase B
# rollout, see EMPIRE_OS_INTEGRATION_ANALYSIS.md + SECURITY_REVIEW.md.
app.add_middleware(SafetyBoundaryMiddleware)

# Include routers - gated by Unkey key verification (fails open until
# UNKEY_ROOT_KEY is configured; see unkey-auth/README.md)
_auth = [Depends(require_api_key)]
app.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"], dependencies=_auth)
app.include_router(email.router, prefix="/email", tags=["email"], dependencies=_auth)
app.include_router(social.router, prefix="/social", tags=["social"], dependencies=_auth)
app.include_router(leads.router, prefix="/leads", tags=["leads"], dependencies=_auth)
app.include_router(segments.router, prefix="/segments", tags=["segments"], dependencies=_auth)
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"], dependencies=_auth)


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Marketing Automation Engine",
        "version": "1.0.0",
        "status": "operational",
        "description": "Automated marketing campaign system",
        "features": [
            "Email campaigns",
            "Social media automation",
            "Lead scoring",
            "Lead nurturing",
            "Campaign management",
            "A/B testing",
            "Segmentation",
            "Analytics dashboard"
        ],
        "endpoints": {
            "campaigns": "/campaigns",
            "email": "/email",
            "social": "/social",
            "leads": "/leads",
            "segments": "/segments",
            "analytics": "/analytics"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check performed")
    return {
        "status": "healthy",
        "service": "marketing-automation-engine",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8039,
        reload=True
    )
