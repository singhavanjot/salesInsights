"""File upload endpoint with full validation and processing pipeline."""

import logging
import re
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Request, UploadFile

from app.config import get_settings
from app.middleware.rate_limiter import limiter
from app.middleware.security import verify_api_key
from app.schemas.upload import UploadResponse
from app.services.ai_engine import generate_summary
from app.services.mailer import send_summary
from app.services.parser import parse_file

router = APIRouter(tags=["Upload"])
logger = logging.getLogger(__name__)

# Email validation regex
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

# Allowed file extensions
ALLOWED_EXTENSIONS = {".csv", ".xlsx"}


def validate_email(email: str) -> str:
    """Validate email format."""
    if not EMAIL_REGEX.match(email):
        raise HTTPException(
            status_code=422,
            detail=f"Invalid email format: {email}",
        )
    return email


def validate_file_extension(filename: str) -> str:
    """Validate file extension is CSV or XLSX."""
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid file type: {ext}. Allowed: .csv, .xlsx",
        )
    return ext


async def validate_file_size(file: UploadFile) -> bytes:
    """Validate file size and return content."""
    settings = get_settings()
    max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    
    content = await file.read()
    await file.seek(0)  # Reset file position
    
    if len(content) > max_size_bytes:
        raise HTTPException(
            status_code=422,
            detail=f"File too large: {len(content) / (1024*1024):.2f}MB. Max: {settings.MAX_FILE_SIZE_MB}MB",
        )
    
    return content


def log_upload_metadata(filename: str, email: str) -> None:
    """Log upload metadata (never log full email or content)."""
    email_domain = email.split("@")[1] if "@" in email else "unknown"
    logger.info(
        "Upload processed",
        extra={
            "filename": filename,
            "email_domain": email_domain,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@router.post("/upload", response_model=UploadResponse)
@limiter.limit("10/minute")
async def upload_file(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="CSV or XLSX sales data file"),
    recipient_email: str = Form(..., description="Email address to send the report"),
    api_key: str = Depends(verify_api_key),
) -> UploadResponse:
    """
    Upload a sales data file and generate an AI-powered insight report.
    
    The report will be sent to the specified email address.
    
    Security:
    - Requires valid X-API-Key header
    - Rate limited to 10 requests per minute per IP
    
    Validation:
    - File must be .csv or .xlsx
    - File size must be <= 10MB
    - Valid email format required
    """
    try:
        # Validate inputs
        validate_email(recipient_email)
        validate_file_extension(file.filename or "")
        await validate_file_size(file)
        
        # Process file through pipeline
        # Step 1: Parse the file
        parsed_data = await parse_file(file)
        
        # Step 2: Generate AI summary
        ai_summary = await generate_summary(parsed_data)
        
        # Step 3: Send email
        email_sent = await send_summary(recipient_email, ai_summary, parsed_data)
        
        if not email_sent:
            raise HTTPException(
                status_code=500,
                detail="Failed to send email. Please try again.",
            )
        
        # Log metadata in background (never log sensitive data)
        background_tasks.add_task(log_upload_metadata, file.filename, recipient_email)
        
        return UploadResponse(
            status="success",
            message=f"Summary sent to {recipient_email}",
            preview=ai_summary[:200] if ai_summary else None,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Upload processing failed")
        return UploadResponse(
            status="error",
            message=str(e),
        )
