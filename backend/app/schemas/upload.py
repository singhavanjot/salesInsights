"""Pydantic models for upload and health endpoints."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Response model for file upload endpoint."""

    status: Literal["success", "error"]
    message: str
    preview: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = "healthy"
    version: str
    provider: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
