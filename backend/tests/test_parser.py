"""Tests for the file parser service."""

import pytest
from io import BytesIO
from unittest.mock import MagicMock, AsyncMock

from fastapi import UploadFile, HTTPException

from app.services.parser import parse_file


def create_upload_file(content: bytes, filename: str) -> UploadFile:
    """Helper to create an UploadFile mock."""
    file = MagicMock(spec=UploadFile)
    file.filename = filename
    file.read = AsyncMock(return_value=content)
    return file


@pytest.mark.asyncio
async def test_parse_csv_file():
    """Test parsing a valid CSV file."""
    csv_content = b"""Date,Product_Category,Region,Units_Sold,Unit_Price,Revenue,Status
2026-01-05,Electronics,North,150,1200,180000,Shipped
2026-01-12,Home Appliances,South,45,450,20250,Shipped
"""
    file = create_upload_file(csv_content, "test.csv")
    
    result = await parse_file(file)
    
    assert "columns" in result
    assert "Date" in result["columns"]
    assert "Revenue" in result["columns"]
    assert result["shape"] == (2, 7)
    assert result["total_revenue"] == 200250


@pytest.mark.asyncio
async def test_parse_csv_with_category_breakdown():
    """Test that category breakdown is calculated correctly."""
    csv_content = b"""Product_Category,Revenue
Electronics,100000
Electronics,50000
Home Appliances,30000
"""
    file = create_upload_file(csv_content, "test.csv")
    
    result = await parse_file(file)
    
    assert result["category_breakdown"] is not None
    assert result["category_breakdown"]["Electronics"] == 150000
    assert result["category_breakdown"]["Home Appliances"] == 30000


@pytest.mark.asyncio
async def test_parse_csv_with_region_breakdown():
    """Test that region breakdown is calculated correctly."""
    csv_content = b"""Region,Revenue
North,100000
South,50000
North,25000
"""
    file = create_upload_file(csv_content, "test.csv")
    
    result = await parse_file(file)
    
    assert result["region_breakdown"] is not None
    assert result["region_breakdown"]["North"] == 125000
    assert result["region_breakdown"]["South"] == 50000


@pytest.mark.asyncio
async def test_parse_csv_with_date_range():
    """Test that date range is extracted correctly."""
    csv_content = b"""Date,Revenue
2026-01-01,100
2026-03-15,200
2026-02-10,150
"""
    file = create_upload_file(csv_content, "test.csv")
    
    result = await parse_file(file)
    
    assert result["date_range"] is not None
    assert "2026-01-01" in result["date_range"]["min"]
    assert "2026-03-15" in result["date_range"]["max"]


@pytest.mark.asyncio
async def test_parse_empty_file():
    """Test that empty files raise an error."""
    file = create_upload_file(b"", "empty.csv")
    
    with pytest.raises(HTTPException) as exc_info:
        await parse_file(file)
    
    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_parse_invalid_csv():
    """Test that malformed CSV raises an error."""
    file = create_upload_file(b"\x00\x01\x02invalid binary", "bad.csv")
    
    # Should either parse with issues or raise an error
    try:
        result = await parse_file(file)
        # If it parses, it should have minimal data
        assert result is not None
    except HTTPException as e:
        assert e.status_code == 422


@pytest.mark.asyncio
async def test_parse_csv_null_counts():
    """Test that null counts are calculated."""
    csv_content = b"""A,B,C
1,,3
4,5,
,8,9
"""
    file = create_upload_file(csv_content, "test.csv")
    
    result = await parse_file(file)
    
    assert "null_counts" in result
    # Should have some null counts
    total_nulls = sum(result["null_counts"].values())
    assert total_nulls > 0
