"""CSV/XLSX file parser for sales data."""

import logging
from io import BytesIO
from typing import Any

import pandas as pd
from fastapi import HTTPException, UploadFile

logger = logging.getLogger(__name__)


async def parse_file(file: UploadFile) -> dict[str, Any]:
    """
    Parse a CSV or XLSX file and extract sales data summary.
    
    Args:
        file: The uploaded file (CSV or XLSX)
        
    Returns:
        Dictionary containing parsed data summary:
        - columns: list of column names
        - shape: (rows, cols) tuple
        - dtypes: column data types
        - numeric_summary: descriptive statistics
        - top_rows: first 5 rows as records
        - null_counts: null values per column
        - date_range: min/max dates if date column exists
        - total_revenue: sum of Revenue column if exists
        - category_breakdown: revenue by category if columns exist
        - region_breakdown: revenue by region if columns exist
        
    Raises:
        HTTPException: 422 if file cannot be parsed
    """
    try:
        # Read file content into BytesIO buffer
        content = await file.read()
        buffer = BytesIO(content)
        
        # Get filename and detect file type
        filename = file.filename or ""
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        
        # Parse based on file type
        if ext == "csv":
            df = pd.read_csv(
                buffer,
                encoding="utf-8-sig",
                on_bad_lines="skip",  # Skip malformed rows
            )
        elif ext == "xlsx":
            df = pd.read_excel(buffer, sheet_name=0)
        else:
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported file format: {ext}",
            )
        
        # Build result dictionary
        result: dict[str, Any] = {
            "columns": df.columns.tolist(),
            "shape": df.shape,
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "numeric_summary": {},
            "top_rows": df.head(5).to_dict(orient="records"),
            "null_counts": df.isnull().sum().to_dict(),
            "date_range": None,
            "total_revenue": None,
            "category_breakdown": None,
            "region_breakdown": None,
        }
        
        # Get numeric summary if there are numeric columns
        numeric_df = df.select_dtypes(include=["number"])
        if not numeric_df.empty:
            result["numeric_summary"] = numeric_df.describe().to_dict()
        
        # Try to find date range
        date_columns = ["Date", "date", "DATE", "Order_Date", "order_date"]
        for col in date_columns:
            if col in df.columns:
                try:
                    date_series = pd.to_datetime(df[col], errors="coerce")
                    valid_dates = date_series.dropna()
                    if not valid_dates.empty:
                        result["date_range"] = {
                            "min": str(valid_dates.min()),
                            "max": str(valid_dates.max()),
                        }
                        break
                except Exception:
                    continue
        
        # Calculate total revenue if Revenue column exists
        revenue_columns = ["Revenue", "revenue", "REVENUE", "Total", "Sales", "Amount"]
        for col in revenue_columns:
            if col in df.columns:
                try:
                    result["total_revenue"] = float(df[col].sum())
                    break
                except Exception:
                    continue
        
        # Category breakdown if relevant columns exist
        category_columns = ["Product_Category", "Category", "product_category", "category"]
        revenue_col = next(
            (c for c in ["Revenue", "revenue", "REVENUE", "Amount", "Sales"] if c in df.columns),
            None,
        )
        
        if revenue_col:
            for cat_col in category_columns:
                if cat_col in df.columns:
                    try:
                        result["category_breakdown"] = (
                            df.groupby(cat_col)[revenue_col].sum().to_dict()
                        )
                        break
                    except Exception:
                        continue
            
            # Region breakdown
            region_columns = ["Region", "region", "REGION", "Territory"]
            for reg_col in region_columns:
                if reg_col in df.columns:
                    try:
                        result["region_breakdown"] = (
                            df.groupby(reg_col)[revenue_col].sum().to_dict()
                        )
                        break
                    except Exception:
                        continue
        
        logger.info(f"Successfully parsed file with shape {df.shape}")
        return result
        
    except HTTPException:
        raise
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=422,
            detail="The uploaded file is empty.",
        )
    except pd.errors.ParserError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to parse file: {str(e)}",
        )
    except Exception as e:
        logger.exception("File parsing failed")
        raise HTTPException(
            status_code=422,
            detail=f"Failed to parse file: {str(e)}",
        )
