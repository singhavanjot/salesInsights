"""API routers."""

from .health import router as health_router
from .upload import router as upload_router

__all__ = ["upload_router", "health_router"]
