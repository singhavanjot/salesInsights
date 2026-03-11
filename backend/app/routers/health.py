"""Health check endpoint."""

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.schemas.upload import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns the API health status, version, and configured providers.
    No authentication required.
    """
    settings = get_settings()
    
    # Check critical configurations
    llm_configured = bool(
        (settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY)
        or (settings.LLM_PROVIDER == "groq" and settings.GROQ_API_KEY)
    )
    
    email_configured = bool(
        (settings.EMAIL_PROVIDER == "sendgrid" and settings.SENDGRID_API_KEY)
        or (settings.EMAIL_PROVIDER == "resend" and settings.RESEND_API_KEY)
    )
    
    if not llm_configured or not email_configured:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "llm_configured": llm_configured,
                "email_configured": email_configured,
                "message": "Critical configuration missing",
            },
        )
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        provider=f"LLM: {settings.LLM_PROVIDER}, Email: {settings.EMAIL_PROVIDER}",
    )
