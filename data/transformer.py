"""
Feature engineering and data transformation for PizzaOps Intelligence.
Adds computed columns required for analysis.
"""

import pandas as pd
import numpy as np
from typing import Optional

from core.constants import (
    PEAK_LUNCH, PEAK_DINNER, OVEN_TEMP_MIN_C, OVEN_TEMP_OPTIMAL_C,
    OVEN_TEMP_MAX_C, DELAY_THRESHOLDS, DELIVERY_TARGET_MINUTES
)


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all feature engineering transformations.

    Args:
        df: Cleaned DataFrame from loader

    Returns:
        DataFrame with all computed columns added
    """
    df = df.copy()

    # Add time-based features
    df = add_time_features(df)

    # Add process time features
    df = add_process_features(df)

    # Add oven temperature features
    df = add_oven_features(df)

    # Add delay classification
    df = add_delay_features(df)

    # Add stage proportions
    df = add_stage_proportions(df)

    return df


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add time-based computed columns."""
    df = df.copy()

    # Extract hour from order_time
    if "order_time" in df.columns:
        # Handle different time formats
        if df["order_time"].dtype == 'object':
            # Try to parse as time string
            try:
                time_series = pd.to_datetime(df["order_time"], format='%H:%M:%S', errors='coerce')
                df["hour_of_day"] = time_series.dt.hour
            except:
                df["hour_of_day"] = None
        else:
            df["hour_of_day"] = pd.to_datetime(df["order_time"]).dt.hour

    # Extract day of week from order_date
    if "order_date" in df.columns:
        df["day_of_week"] = df["order_date"].dt.day_name()
        df["day_of_week_num"] = df["order_date"].dt.dayofweek  # 0=Monday, 6=Sunday
        df["is_weekend"] = df["day_of_week_num"].isin([5, 6])

    # Peak hour indicator
    if "hour_of_day" in df.columns:
        df["is_peak_lunch"] = df["hour_of_day"].between(PEAK_LUNCH[0], PEAK_LUNCH[1])
        df["is_peak_dinner"] = df["hour_of_day"].between(PEAK_DINNER[0], PEAK_DINNER[1])
        df["is_peak_hour"] = df["is_peak_lunch"] | df["is_peak_dinner"]

    return df


def add_process_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add process time computed columns."""
    df = df.copy()

    # Total prep time (in-store)
    prep_cols = ["dough_prep_time", "styling_time", "oven_time", "boxing_time"]
    available_prep_cols = [col for col in prep_cols if col in df.columns]

    if available_prep_cols:
        # Sum available prep columns, treating NaN as 0
        df["total_prep_time"] = df[available_prep_cols].fillna(0).sum(axis=1)

    # Total process time (if not already present or all NaN)
    if "total_process_time" not in df.columns or df["total_process_time"].isna().all():
        if "total_prep_time" in df.columns and "delivery_duration" in df.columns:
            df["total_process_time"] = df["total_prep_time"].fillna(0) + df["delivery_duration"].fillna(0)

    # Delivery target met - explicit boolean conversion with NaN handling
    if "total_process_time" in df.columns:
        # Create boolean column, defaulting to False for NaN values
        df["delivery_target_met"] = (df["total_process_time"] <= DELIVERY_TARGET_MINUTES).fillna(False).astype(bool)

    return df


def add_oven_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add oven temperature computed columns."""
    df = df.copy()

    if "oven_temperature" in df.columns:
        # Temperature zone classification
        def classify_temp(temp):
            if pd.isna(temp):
                return "unknown"
            if temp < OVEN_TEMP_MIN_C:
                return "cold"
            elif temp <= OVEN_TEMP_MAX_C:
                return "optimal"
            else:
                return "hot"

        df["oven_temp_zone"] = df["oven_temperature"].apply(classify_temp)

        # Deviation from optimal
        df["oven_temp_deviation"] = abs(df["oven_temperature"] - OVEN_TEMP_OPTIMAL_C)

    return df


def add_delay_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add delay classification columns."""
    df = df.copy()

    if "total_process_time" in df.columns:
        def classify_delay(time):
            if pd.isna(time):
                return "unknown"
            if time <= DELAY_THRESHOLDS["on_time"]:
                return "on_time"
            elif time <= DELAY_THRESHOLDS["at_risk"]:
                return "at_risk"
            elif time <= DELAY_THRESHOLDS["late"]:
                return "late"
            else:
                return "critical"

        df["delay_category"] = df["total_process_time"].apply(classify_delay)

    return df


def add_stage_proportions(df: pd.DataFrame) -> pd.DataFrame:
    """Add stage proportion columns (% of total prep time)."""
    df = df.copy()

    if "total_prep_time" in df.columns:
        # Avoid division by zero
        prep_time = df["total_prep_time"].replace(0, np.nan)

        stage_cols = {
            "dough_prep_time": "pct_dough_prep",
            "styling_time": "pct_styling",
            "oven_time": "pct_oven",
            "boxing_time": "pct_boxing"
        }

        for source_col, target_col in stage_cols.items():
            if source_col in df.columns:
                df[target_col] = (df[source_col] / prep_time * 100).round(2)

    return df


def aggregate_by_date(df: pd.DataFrame, freq: str = 'D') -> pd.DataFrame:
    """
    Aggregate data by date for time series analysis.

    Args:
        df: Transformed DataFrame
        freq: Frequency for grouping ('D' for daily, 'H' for hourly)

    Returns:
        Aggregated DataFrame
    """
    if "order_date" not in df.columns:
        return pd.DataFrame()

    df = df.copy()

    if freq == 'H' and "hour_of_day" in df.columns:
        # Create datetime index with hour
        df["datetime"] = pd.to_datetime(df["order_date"]) + pd.to_timedelta(df["hour_of_day"], unit='h')
        group_col = "datetime"
    else:
        group_col = "order_date"

    agg_dict = {
        "order_id": "count",
    }

    # Add numeric columns to aggregation
    numeric_cols = [
        "total_process_time", "total_prep_time", "delivery_duration",
        "dough_prep_time", "styling_time", "oven_time", "boxing_time",
        "oven_temperature"
    ]
    for col in numeric_cols:
        if col in df.columns:
            agg_dict[col] = "mean"

    # Add complaint rate
    if "complaint" in df.columns:
        agg_dict["complaint"] = lambda x: x.sum() / len(x) * 100 if len(x) > 0 else 0

    result = df.groupby(group_col).agg(agg_dict).reset_index()
    result = result.rename(columns={"order_id": "order_count", "complaint": "complaint_rate"})

    return result


def filter_by_date_range(
    df: pd.DataFrame,
    start_date: Optional[pd.Timestamp] = None,
    end_date: Optional[pd.Timestamp] = None
) -> pd.DataFrame:
    """Filter DataFrame by date range."""
    if "order_date" not in df.columns:
        return df

    df = df.copy()

    if start_date is not None:
        df = df[df["order_date"] >= start_date]

    if end_date is not None:
        df = df[df["order_date"] <= end_date]

    return df


def filter_by_area(df: pd.DataFrame, areas: list) -> pd.DataFrame:
    """Filter DataFrame by delivery areas."""
    if "delivery_area" not in df.columns or not areas:
        return df

    return df[df["delivery_area"].isin(areas)]


def filter_by_order_mode(df: pd.DataFrame, modes: list) -> pd.DataFrame:
    """Filter DataFrame by order modes."""
    if "order_mode" not in df.columns or not modes:
        return df

    return df[df["order_mode"].isin(modes)]
