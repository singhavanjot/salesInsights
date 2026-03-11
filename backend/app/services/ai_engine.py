"""AI-powered summary generation using Gemini or Groq LLMs."""

import asyncio
import logging
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)

# System prompt for the LLM
SYSTEM_PROMPT = """You are a senior business analyst at Rabbitt AI. You receive structured sales data
and produce executive-ready briefings. Your tone is confident, data-driven, and concise.
Use markdown formatting with clear sections."""


def build_user_prompt(parsed_data: dict[str, Any]) -> str:
    """Build the user prompt with parsed data context."""
    prompt_parts = [
        "Analyze the following sales data and generate a professional Q1 2026 Sales Performance Brief.",
        "",
        f"**Data Overview:**",
        f"- Shape: {parsed_data.get('shape', 'Unknown')} (rows, columns)",
        f"- Columns: {', '.join(parsed_data.get('columns', []))}",
        "",
    ]
    
    # Add date range if available
    if parsed_data.get("date_range"):
        dr = parsed_data["date_range"]
        prompt_parts.append(f"**Date Range:** {dr.get('min')} to {dr.get('max')}")
        prompt_parts.append("")
    
    # Add total revenue if available
    if parsed_data.get("total_revenue"):
        prompt_parts.append(f"**Total Revenue:** ${parsed_data['total_revenue']:,.2f}")
        prompt_parts.append("")
    
    # Add numeric summary
    if parsed_data.get("numeric_summary"):
        prompt_parts.append("**Numeric Summary:**")
        for col, stats in parsed_data["numeric_summary"].items():
            if isinstance(stats, dict) and "mean" in stats:
                prompt_parts.append(
                    f"- {col}: Mean={stats.get('mean', 0):,.2f}, "
                    f"Min={stats.get('min', 0):,.2f}, Max={stats.get('max', 0):,.2f}"
                )
        prompt_parts.append("")
    
    # Add category breakdown
    if parsed_data.get("category_breakdown"):
        prompt_parts.append("**Category Breakdown:**")
        for cat, rev in parsed_data["category_breakdown"].items():
            prompt_parts.append(f"- {cat}: ${rev:,.2f}")
        prompt_parts.append("")
    
    # Add region breakdown
    if parsed_data.get("region_breakdown"):
        prompt_parts.append("**Region Breakdown:**")
        for reg, rev in parsed_data["region_breakdown"].items():
            prompt_parts.append(f"- {reg}: ${rev:,.2f}")
        prompt_parts.append("")
    
    # Add top rows preview
    if parsed_data.get("top_rows"):
        prompt_parts.append("**Sample Data (Top 5 Rows):**")
        for i, row in enumerate(parsed_data["top_rows"][:5], 1):
            row_str = ", ".join(f"{k}={v}" for k, v in list(row.items())[:5])
            prompt_parts.append(f"- Row {i}: {row_str}")
        prompt_parts.append("")
    
    # Instructions for output
    prompt_parts.extend([
        "**Generate a professional Q1 2026 Sales Performance Brief with:**",
        "1. Executive Summary (3-4 sentences)",
        "2. Key Performance Metrics (bullet list with bold labels)",
        "3. Regional Performance Analysis",
        "4. Product Category Insights",
        "5. Notable Trends & Anomalies",
        "6. Strategic Recommendations (2-3 bullet points)",
        "",
        "End with: 'Prepared by Rabbitt AI Insights Engine'",
    ])
    
    return "\n".join(prompt_parts)


def generate_fallback_summary(parsed_data: dict[str, Any]) -> str:
    """Generate a basic template summary when LLM fails."""
    summary_parts = [
        "# Q1 2026 Sales Performance Brief",
        "",
        "## Executive Summary",
        f"This report analyzes sales data containing {parsed_data.get('shape', ['Unknown'])[0]} records "
        f"across {len(parsed_data.get('columns', []))} data dimensions.",
    ]
    
    if parsed_data.get("total_revenue"):
        summary_parts.append(
            f"Total revenue for the period: **${parsed_data['total_revenue']:,.2f}**."
        )
    
    summary_parts.extend([
        "",
        "## Key Performance Metrics",
    ])
    
    if parsed_data.get("total_revenue"):
        summary_parts.append(f"- **Total Revenue:** ${parsed_data['total_revenue']:,.2f}")
    
    if parsed_data.get("shape"):
        summary_parts.append(f"- **Total Transactions:** {parsed_data['shape'][0]}")
    
    if parsed_data.get("date_range"):
        dr = parsed_data["date_range"]
        summary_parts.append(f"- **Reporting Period:** {dr.get('min')} to {dr.get('max')}")
    
    if parsed_data.get("region_breakdown"):
        summary_parts.extend(["", "## Regional Performance"])
        for region, revenue in parsed_data["region_breakdown"].items():
            summary_parts.append(f"- **{region}:** ${revenue:,.2f}")
    
    if parsed_data.get("category_breakdown"):
        summary_parts.extend(["", "## Product Category Insights"])
        for category, revenue in parsed_data["category_breakdown"].items():
            summary_parts.append(f"- **{category}:** ${revenue:,.2f}")
    
    summary_parts.extend([
        "",
        "## Strategic Recommendations",
        "- Continue monitoring top-performing regions and categories",
        "- Investigate underperforming segments for improvement opportunities",
        "- Consider expanding successful product lines",
        "",
        "---",
        "*Prepared by Rabbitt AI Insights Engine*",
    ])
    
    return "\n".join(summary_parts)


async def generate_with_gemini(user_prompt: str) -> str:
    """Generate summary using Google Gemini API."""
    import google.generativeai as genai
    
    settings = get_settings()
    genai.configure(api_key=settings.GEMINI_API_KEY)
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Run in thread pool since genai is synchronous
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: model.generate_content(
            [
                {"role": "user", "parts": [SYSTEM_PROMPT]},
                {"role": "model", "parts": ["Understood. I'll analyze sales data and create executive briefings."]},
                {"role": "user", "parts": [user_prompt]},
            ],
        ),
    )
    
    return response.text


async def generate_with_groq(user_prompt: str) -> str:
    """Generate summary using Groq API."""
    from groq import AsyncGroq
    
    settings = get_settings()
    client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    
    response = await client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=2000,
        temperature=0.7,
    )
    
    return response.choices[0].message.content or ""


async def generate_summary(parsed_data: dict[str, Any]) -> str:
    """
    Generate an AI-powered summary of the sales data.
    
    Args:
        parsed_data: Dictionary containing parsed sales data
        
    Returns:
        Markdown-formatted summary string
        
    Notes:
        - Routes to Gemini or Groq based on settings.LLM_PROVIDER
        - Implements retry logic with 2 retries and 1s backoff
        - Falls back to template summary if all providers fail
    """
    settings = get_settings()
    user_prompt = build_user_prompt(parsed_data)
    
    max_retries = 2
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            if settings.LLM_PROVIDER == "gemini":
                logger.info(f"Generating summary with Gemini (attempt {attempt + 1})")
                return await generate_with_gemini(user_prompt)
            else:  # groq
                logger.info(f"Generating summary with Groq (attempt {attempt + 1})")
                return await generate_with_groq(user_prompt)
                
        except Exception as e:
            last_error = e
            logger.warning(f"LLM generation failed (attempt {attempt + 1}): {e}")
            if attempt < max_retries:
                await asyncio.sleep(1)  # Backoff before retry
    
    # All retries failed, use fallback
    logger.error(f"All LLM attempts failed. Last error: {last_error}. Using fallback template.")
    return generate_fallback_summary(parsed_data)
