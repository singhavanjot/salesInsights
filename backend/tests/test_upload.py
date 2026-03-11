"""Tests for the upload endpoint."""

import pytest
from unittest.mock import AsyncMock, patch
from io import BytesIO

from fastapi import UploadFile
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.config import get_settings, Settings


# Override settings for testing
def get_test_settings():
    return Settings(
        API_KEY="test-key",
        LLM_PROVIDER="gemini",
        GEMINI_API_KEY="fake-gemini-key",
        EMAIL_PROVIDER="sendgrid",
        SENDGRID_API_KEY="fake-sendgrid-key",
        ALLOWED_ORIGINS=["http://localhost:5173"],
    )


@pytest.fixture
def test_csv_content():
    """Sample CSV content for testing."""
    return b"""Date,Product_Category,Region,Units_Sold,Unit_Price,Revenue,Status
2026-01-05,Electronics,North,150,1200,180000,Shipped
2026-01-12,Home Appliances,South,45,450,20250,Shipped
"""


@pytest.fixture
async def test_client():
    """Create async test client."""
    # Override settings
    app.dependency_overrides[get_settings] = get_test_settings
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_requires_api_key(test_client, test_csv_content):
    """Test that upload endpoint requires API key."""
    # Create form data
    files = {"file": ("test.csv", BytesIO(test_csv_content), "text/csv")}
    data = {"recipient_email": "test@example.com"}
    
    response = await test_client.post(
        "/api/upload",
        files=files,
        data=data,
        # No X-API-Key header
    )
    
    assert response.status_code == 401
    assert "Missing API key" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_wrong_api_key(test_client, test_csv_content):
    """Test that wrong API key is rejected."""
    files = {"file": ("test.csv", BytesIO(test_csv_content), "text/csv")}
    data = {"recipient_email": "test@example.com"}
    
    response = await test_client.post(
        "/api/upload",
        files=files,
        data=data,
        headers={"X-API-Key": "wrong-key"},
    )
    
    assert response.status_code == 403
    assert "Invalid API key" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_invalid_file_type(test_client):
    """Test that invalid file types are rejected."""
    files = {"file": ("test.txt", BytesIO(b"plain text"), "text/plain")}
    data = {"recipient_email": "test@example.com"}
    
    response = await test_client.post(
        "/api/upload",
        files=files,
        data=data,
        headers={"X-API-Key": "test-key"},
    )
    
    assert response.status_code == 422
    assert "Invalid file type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_invalid_email(test_client, test_csv_content):
    """Test that invalid email format is rejected."""
    files = {"file": ("test.csv", BytesIO(test_csv_content), "text/csv")}
    data = {"recipient_email": "invalid-email"}
    
    response = await test_client.post(
        "/api/upload",
        files=files,
        data=data,
        headers={"X-API-Key": "test-key"},
    )
    
    assert response.status_code == 422
    assert "Invalid email format" in response.json()["detail"]


@pytest.mark.asyncio
async def test_health_endpoint(test_client):
    """Test health check endpoint returns 200."""
    response = await test_client.get("/api/health")
    
    # May return 503 if providers not configured, but should not error
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data or "detail" in data


@pytest.mark.asyncio
async def test_successful_upload(test_client, test_csv_content):
    """Test successful file upload with mocked services."""
    # Mock the services
    with patch("app.routers.upload.parse_file") as mock_parse, \
         patch("app.routers.upload.generate_summary") as mock_generate, \
         patch("app.routers.upload.send_summary") as mock_send:
        
        mock_parse.return_value = {
            "columns": ["Date", "Revenue"],
            "shape": (2, 7),
            "total_revenue": 200250,
        }
        mock_generate.return_value = "# Test Summary\nThis is a test."
        mock_send.return_value = True
        
        files = {"file": ("test.csv", BytesIO(test_csv_content), "text/csv")}
        data = {"recipient_email": "test@example.com"}
        
        response = await test_client.post(
            "/api/upload",
            files=files,
            data=data,
            headers={"X-API-Key": "test-key"},
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert "test@example.com" in result["message"]
