"""Tests for the AI engine service."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.ai_engine import (
    generate_summary,
    generate_fallback_summary,
    build_user_prompt,
)


@pytest.fixture
def sample_parsed_data():
    """Sample parsed data for testing."""
    return {
        "columns": ["Date", "Product_Category", "Region", "Revenue"],
        "shape": (100, 4),
        "dtypes": {"Date": "object", "Revenue": "float64"},
        "numeric_summary": {
            "Revenue": {"mean": 50000, "min": 10000, "max": 100000}
        },
        "top_rows": [
            {"Date": "2026-01-01", "Revenue": 50000},
            {"Date": "2026-01-02", "Revenue": 60000},
        ],
        "null_counts": {"Date": 0, "Revenue": 2},
        "date_range": {"min": "2026-01-01", "max": "2026-03-31"},
        "total_revenue": 500000,
        "category_breakdown": {"Electronics": 300000, "Home Appliances": 200000},
        "region_breakdown": {"North": 250000, "South": 250000},
    }


def test_build_user_prompt(sample_parsed_data):
    """Test that user prompt is built correctly."""
    prompt = build_user_prompt(sample_parsed_data)
    
    assert "sales data" in prompt.lower()
    assert "100" in prompt  # Row count
    assert "$500,000" in prompt  # Total revenue
    assert "Electronics" in prompt
    assert "North" in prompt
    assert "Q1 2026" in prompt


def test_build_user_prompt_minimal_data():
    """Test prompt building with minimal data."""
    minimal_data = {
        "columns": ["A", "B"],
        "shape": (10, 2),
    }
    
    prompt = build_user_prompt(minimal_data)
    
    assert "A, B" in prompt
    assert "(10, 2)" in prompt


def test_fallback_summary_generation(sample_parsed_data):
    """Test fallback summary is generated correctly."""
    summary = generate_fallback_summary(sample_parsed_data)
    
    assert "Q1 2026" in summary
    assert "Sales Performance" in summary
    assert "$500,000" in summary
    assert "Electronics" in summary
    assert "North" in summary
    assert "Rabbitt AI" in summary


def test_fallback_summary_minimal_data():
    """Test fallback with minimal data."""
    minimal_data = {
        "columns": ["A"],
        "shape": (5, 1),
    }
    
    summary = generate_fallback_summary(minimal_data)
    
    assert "Q1 2026" in summary
    assert "5" in summary  # Row count


@pytest.mark.asyncio
async def test_generate_summary_with_gemini(sample_parsed_data):
    """Test summary generation with mocked Gemini."""
    with patch("app.services.ai_engine.get_settings") as mock_settings, \
         patch("app.services.ai_engine.generate_with_gemini") as mock_gemini:
        
        mock_settings.return_value = MagicMock(LLM_PROVIDER="gemini")
        mock_gemini.return_value = "# Mocked Gemini Summary"
        
        result = await generate_summary(sample_parsed_data)
        
        assert result == "# Mocked Gemini Summary"
        mock_gemini.assert_called_once()


@pytest.mark.asyncio
async def test_generate_summary_with_groq(sample_parsed_data):
    """Test summary generation with mocked Groq."""
    with patch("app.services.ai_engine.get_settings") as mock_settings, \
         patch("app.services.ai_engine.generate_with_groq") as mock_groq:
        
        mock_settings.return_value = MagicMock(LLM_PROVIDER="groq")
        mock_groq.return_value = "# Mocked Groq Summary"
        
        result = await generate_summary(sample_parsed_data)
        
        assert result == "# Mocked Groq Summary"
        mock_groq.assert_called_once()


@pytest.mark.asyncio
async def test_generate_summary_fallback_on_error(sample_parsed_data):
    """Test that fallback is used when LLM fails."""
    with patch("app.services.ai_engine.get_settings") as mock_settings, \
         patch("app.services.ai_engine.generate_with_gemini") as mock_gemini:
        
        mock_settings.return_value = MagicMock(LLM_PROVIDER="gemini")
        mock_gemini.side_effect = Exception("API Error")
        
        result = await generate_summary(sample_parsed_data)
        
        # Should use fallback
        assert "Q1 2026" in result
        assert "Rabbitt AI" in result
        # Gemini should have been called 3 times (initial + 2 retries)
        assert mock_gemini.call_count == 3
