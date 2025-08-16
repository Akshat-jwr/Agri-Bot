from fastapi import APIRouter
from app.schemas.response import APIResponse
from app.core.config import settings

router = APIRouter()

@router.get("/", response_model=APIResponse)
async def root():
    """🏠 Welcome endpoint"""
    return APIResponse(
        message=f"Welcome to {settings.APP_NAME}",
        data={
            "version": settings.APP_VERSION,
            "endpoints": {
                "docs": "/docs",
                "register": "/api/v1/auth/register",
                "login": "/api/v1/auth/login"
            }
        }
    )

@router.get("/health", response_model=APIResponse)
async def health_check():
    """❤️ Health check"""
    return APIResponse(
        message="System healthy",
        data={"status": "operational", "database": "connected"}
    )
