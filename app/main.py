"""
Marketing Automation Engine - Main Application
Automated marketing campaign system for the Autonomous Company OS
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import os

from app.config import settings
from app.database import init_db
from app.routers import campaigns, email, social, leads, segments, analytics


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
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
app.include_router(email.router, prefix="/email", tags=["email"])
app.include_router(social.router, prefix="/social", tags=["social"])
app.include_router(leads.router, prefix="/leads", tags=["leads"])
app.include_router(segments.router, prefix="/segments", tags=["segments"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])


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
    return {
        "status": "healthy",
        "service": "marketing-automation-engine",
        "timestamp": logger.info("Health check performed")
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8039,
        reload=True
    )
