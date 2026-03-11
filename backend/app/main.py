"""FastAPI application entry point with full configuration."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.middleware.rate_limiter import custom_rate_limit_exceeded_handler, limiter
from app.routers import health_router, upload_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    settings = get_settings()
    logger.info("=" * 50)
    logger.info("Sales Insight Automator API Starting...")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"Email Provider: {settings.EMAIL_PROVIDER}")
    logger.info(f"Rate Limit: {settings.RATE_LIMIT}")
    logger.info(f"Max File Size: {settings.MAX_FILE_SIZE_MB}MB")
    logger.info(f"CORS Origins: {settings.ALLOWED_ORIGINS}")
    logger.info("=" * 50)
    yield
    # Shutdown
    logger.info("Application shutting down...")


# Create FastAPI app with custom configuration
app = FastAPI(
    title="Sales Insight Automator API",
    description="""
    ## Sales Insight Automator API
    
    Upload CSV/Excel sales data files and receive AI-generated professional insight reports via email.
    
    ### Features
    - **File Upload**: Support for CSV and XLSX files up to 10MB
    - **AI Analysis**: Powered by Gemini or Groq LLMs
    - **Email Delivery**: Reports sent via SendGrid or Resend
    - **Security**: API key authentication, rate limiting, input validation
    
    ### Authentication
    All upload endpoints require an `X-API-Key` header.
    """,
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={
        "deepLinking": True,
        "displayRequestDuration": True,
        "docExpansion": "list",
        "operationsSorter": "method",
        "filter": True,
        "syntaxHighlight.theme": "monokai",
    },
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)

# Get settings for middleware configuration
settings = get_settings()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # Configure for production
)


# Global Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors with clear messages."""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({"field": field, "message": error["msg"]})
    
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "detail": "Validation failed",
            "errors": errors,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "detail": exc.detail,
        },
    )


# Include routers
app.include_router(upload_router, prefix="/api")
app.include_router(health_router, prefix="/api")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Sales Insight Automator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }
