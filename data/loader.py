"""
Data loader for PizzaOps Intelligence.
Handles CSV/Excel ingestion, validation, and cleaning.
"""

import pandas as pd
import streamlit as st
from typing import Tuple, Optional, Any
from io import BytesIO

from data.schema import COLUMN_MAPPING, EXPECTED_COLUMNS, get_standardized_name


def load_and_validate(uploaded_file: Any) -> Tuple[pd.DataFrame, dict]:
    """
    Load and validate uploaded data file.

    Args:
        uploaded_file: Streamlit file uploader object

    Returns:
        df: Cleaned DataFrame with standardized column names
        report: Validation report dict with status and warnings
    """
    report = {
        "rows_raw": 0,
        "rows_clean": 0,
        "rows_dropped": 0,
        "missing_columns": [],
        "warnings": [],
        "status": "success"
    }

    try:
        # Determine file type and load
        file_name = uploaded_file.name.lower()

        if file_name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif file_name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            report["status"] = "error"
            report["warnings"].append(f"Unsupported file type: {file_name}")
            return pd.DataFrame(), report

        report["rows_raw"] = len(df)

        # Standardize column names
        df = standardize_columns(df)

        # Validate required columns
        missing = validate_required_columns(df)
        report["missing_columns"] = missing

        if missing:
            report["warnings"].append(f"Missing required columns: {', '.join(missing)}")
            report["status"] = "warning"

        # Clean data types
        df = clean_data_types(df)

        # Drop fully empty rows
        initial_rows = len(df)
        df = df.dropna(how='all')
        report["rows_dropped"] = initial_rows - len(df)

        report["rows_clean"] = len(df)

        if report["rows_dropped"] > 0:
            report["warnings"].append(f"Dropped {report['rows_dropped']} empty rows")

        return df, report

    except Exception as e:
        report["status"] = "error"
        report["warnings"].append(f"Error loading file: {str(e)}")
        return pd.DataFrame(), report


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names using the mapping from schema.

    Args:
        df: Raw DataFrame

    Returns:
        DataFrame with standardized column names
    """
    new_columns = {}

    for col in df.columns:
        # Try to find in mapping
        standardized = get_standardized_name(col)
        new_columns[col] = standardized

    df = df.rename(columns=new_columns)
    return df


def validate_required_columns(df: pd.DataFrame) -> list:
    """
    Check for missing required columns.

    Args:
        df: DataFrame with standardized columns

    Returns:
        List of missing required column names
    """
    missing = []

    for col_name, col_spec in EXPECTED_COLUMNS.items():
        if col_spec.get("required", False):
            if col_name not in df.columns:
                missing.append(col_name)

    return missing


def clean_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and convert data types.

    Args:
        df: DataFrame with standardized columns

    Returns:
        DataFrame with cleaned data types
    """
    df = df.copy()

    # Order date - ensure datetime
    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors='coerce')

    # Order mode - normalize case
    if "order_mode" in df.columns:
        df["order_mode"] = df["order_mode"].astype(str).str.lower().str.strip()

    # Complaint - convert to boolean
    if "complaint" in df.columns:
        df["complaint"] = df["complaint"].astype(str).str.lower().str.strip()
        df["complaint"] = df["complaint"].map({
            "yes": True,
            "no": False,
            "true": True,
            "false": False,
            "1": True,
            "0": False
        })

    # Delivery area - uppercase
    if "delivery_area" in df.columns:
        df["delivery_area"] = df["delivery_area"].astype(str).str.upper().str.strip()

    # Numeric columns - ensure float
    numeric_cols = [
        "dough_prep_time", "styling_time", "oven_time", "boxing_time",
        "delivery_duration", "oven_temperature", "total_process_time",
        "order_receipt_time"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Staff names - strip whitespace
    staff_cols = [
        "order_taker", "dough_prep_staff", "stylist",
        "oven_operator", "boxer", "delivery_driver"
    ]
    for col in staff_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Complaint reason - clean up
    if "complaint_reason" in df.columns:
        df["complaint_reason"] = df["complaint_reason"].astype(str).str.strip()
        df.loc[df["complaint_reason"].isin(["nan", "None", ""]), "complaint_reason"] = None

    return df


@st.cache_data(ttl=300)
def load_cached_data(file_bytes: bytes, file_name: str) -> Tuple[pd.DataFrame, dict]:
    """
    Cached version of data loading for Streamlit.

    Args:
        file_bytes: Raw file bytes
        file_name: Original file name

    Returns:
        Tuple of (DataFrame, validation report)
    """
    # Create a file-like object
    class FileWrapper:
        def __init__(self, data: bytes, name: str):
            self.data = BytesIO(data)
            self.name = name

        def read(self):
            return self.data.read()

        def seek(self, pos):
            return self.data.seek(pos)

    wrapper = FileWrapper(file_bytes, file_name)
    return load_and_validate(wrapper)


def get_date_range(df: pd.DataFrame) -> Tuple[Optional[pd.Timestamp], Optional[pd.Timestamp]]:
    """Get the date range from the dataset."""
    if "order_date" in df.columns and len(df) > 0:
        return df["order_date"].min(), df["order_date"].max()
    return None, None


def get_summary_stats(df: pd.DataFrame) -> dict:
    """Get quick summary statistics for the loaded data."""
    stats = {
        "total_orders": len(df),
        "date_range": get_date_range(df),
        "areas": sorted(df["delivery_area"].unique().tolist()) if "delivery_area" in df.columns else [],
        "order_modes": sorted(df["order_mode"].unique().tolist()) if "order_mode" in df.columns else [],
        "staff_count": {},
    }

    # Count unique staff per role
    staff_cols = ["order_taker", "dough_prep_staff", "stylist", "oven_operator", "boxer", "delivery_driver"]
    for col in staff_cols:
        if col in df.columns:
            stats["staff_count"][col] = df[col].nunique()

    return stats
