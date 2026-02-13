"""
KPI calculation engine for PizzaOps Intelligence.
All KPI calculations and aggregations.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Tuple

from core.constants import (
    DELIVERY_TARGET_MINUTES, KPI_TARGETS, STAGE_BENCHMARKS,
    PIPELINE_STAGES, DELIVERY_AREAS
)


def calculate_overview_kpis(df: pd.DataFrame) -> Dict:
    """
    Calculate overview KPIs for the executive dashboard.

    Args:
        df: Transformed DataFrame

    Returns:
        Dict with KPI values
    """
    kpis = {}

    # Total orders
    kpis["total_orders"] = len(df)

    # On-time delivery percentage
    if "delivery_target_met" in df.columns:
        # Ensure boolean values and count True values
        on_time_series = df["delivery_target_met"].fillna(False).astype(bool)
        on_time = on_time_series.sum()
        kpis["on_time_pct"] = (on_time / len(df) * 100) if len(df) > 0 else 0
        kpis["on_time_count"] = int(on_time)
        kpis["on_time_status"] = get_kpi_status(kpis["on_time_pct"], KPI_TARGETS["on_time_pct"])

    # Complaint rate
    if "complaint" in df.columns:
        # Ensure boolean values and count True values
        complaint_series = df["complaint"].fillna(False).astype(bool)
        complaints = complaint_series.sum()
        kpis["complaint_rate"] = (complaints / len(df) * 100) if len(df) > 0 else 0
        kpis["complaint_count"] = int(complaints)
        # Lower is better for complaint rate
        kpis["complaint_status"] = get_kpi_status(
            KPI_TARGETS["complaint_rate_pct"],
            kpis["complaint_rate"],
            higher_is_better=False
        )

    # Average delivery time
    if "total_process_time" in df.columns:
        kpis["avg_delivery_time"] = df["total_process_time"].mean()
        kpis["avg_delivery_status"] = get_kpi_status(
            KPI_TARGETS["avg_delivery_min"],
            kpis["avg_delivery_time"],
            higher_is_better=False
        )

    # Average prep time
    if "total_prep_time" in df.columns:
        kpis["avg_prep_time"] = df["total_prep_time"].mean()
        kpis["avg_prep_status"] = get_kpi_status(
            KPI_TARGETS["avg_prep_min"],
            kpis["avg_prep_time"],
            higher_is_better=False
        )

    # Peak hour load
    if "is_peak_hour" in df.columns and "hour_of_day" in df.columns:
        peak_df = df[df["is_peak_hour"] == True]
        if len(peak_df) > 0:
            peak_hourly = peak_df.groupby("hour_of_day").size()
            kpis["peak_hour"] = peak_hourly.idxmax()
            kpis["peak_hour_load"] = peak_hourly.max()
        else:
            kpis["peak_hour"] = None
            kpis["peak_hour_load"] = 0

    return kpis


def get_kpi_status(value: float, target: float, higher_is_better: bool = True) -> str:
    """
    Determine KPI status based on value vs target.

    Args:
        value: Current KPI value
        target: Target value
        higher_is_better: True if higher values are better

    Returns:
        Status string: "good", "warning", or "danger"
    """
    if higher_is_better:
        if value >= target:
            return "good"
        elif value >= target * 0.85:
            return "warning"
        else:
            return "danger"
    else:
        if value <= target:
            return "good"
        elif value <= target * 1.15:
            return "warning"
        else:
            return "danger"


def delivery_by_area(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate delivery metrics by area.

    Args:
        df: Transformed DataFrame

    Returns:
        DataFrame with area-level metrics
    """
    if "delivery_area" not in df.columns:
        return pd.DataFrame()

    agg_dict = {
        "order_id": "count",
    }

    if "delivery_duration" in df.columns:
        agg_dict["delivery_duration"] = ["mean", "median", lambda x: x.quantile(0.95)]

    if "total_process_time" in df.columns:
        agg_dict["total_process_time"] = "mean"

    if "delivery_target_met" in df.columns:
        agg_dict["delivery_target_met"] = lambda x: (x.sum() / len(x) * 100) if len(x) > 0 else 0

    if "complaint" in df.columns:
        agg_dict["complaint"] = lambda x: (x.sum() / len(x) * 100) if len(x) > 0 else 0

    result = df.groupby("delivery_area").agg(agg_dict).reset_index()

    # Flatten column names
    result.columns = [
        "delivery_area", "order_count", "avg_delivery_time",
        "median_delivery_time", "p95_delivery_time", "avg_total_time",
        "on_time_pct", "complaint_rate"
    ][:len(result.columns)]

    return result


def driver_scorecards(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate driver performance metrics.

    Args:
        df: Transformed DataFrame

    Returns:
        DataFrame with driver scorecards
    """
    if "delivery_driver" not in df.columns:
        return pd.DataFrame()

    agg_dict = {
        "order_id": "count",
    }

    if "delivery_duration" in df.columns:
        agg_dict["delivery_duration"] = ["mean", lambda x: x.quantile(0.95)]

    if "delivery_target_met" in df.columns:
        agg_dict["delivery_target_met"] = lambda x: (x.sum() / len(x) * 100) if len(x) > 0 else 0

    if "complaint" in df.columns:
        agg_dict["complaint"] = lambda x: (x.sum() / len(x) * 100) if len(x) > 0 else 0

    if "delivery_area" in df.columns:
        agg_dict["delivery_area"] = lambda x: len(x.unique())

    result = df.groupby("delivery_driver").agg(agg_dict).reset_index()

    # Flatten columns
    new_cols = ["driver", "total_deliveries"]
    if "delivery_duration" in df.columns:
        new_cols.extend(["avg_time", "p95_time"])
    if "delivery_target_met" in df.columns:
        new_cols.append("on_time_pct")
    if "complaint" in df.columns:
        new_cols.append("complaint_rate")
    if "delivery_area" in df.columns:
        new_cols.append("areas_served")

    result.columns = new_cols[:len(result.columns)]

    return result


def area_hour_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create area × hour performance matrix.

    Args:
        df: Transformed DataFrame

    Returns:
        Pivot table with avg delivery time
    """
    if "delivery_area" not in df.columns or "hour_of_day" not in df.columns:
        return pd.DataFrame()

    if "delivery_duration" not in df.columns:
        return pd.DataFrame()

    return df.pivot_table(
        values="delivery_duration",
        index="delivery_area",
        columns="hour_of_day",
        aggfunc="mean"
    )


def order_mode_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare performance by order mode.

    Args:
        df: Transformed DataFrame

    Returns:
        DataFrame with order mode metrics
    """
    if "order_mode" not in df.columns:
        return pd.DataFrame()

    agg_dict = {
        "order_id": "count",
    }

    if "total_process_time" in df.columns:
        agg_dict["total_process_time"] = "mean"

    if "delivery_duration" in df.columns:
        agg_dict["delivery_duration"] = "mean"

    if "complaint" in df.columns:
        agg_dict["complaint"] = lambda x: (x.sum() / len(x) * 100) if len(x) > 0 else 0

    result = df.groupby("order_mode").agg(agg_dict).reset_index()

    result.columns = ["order_mode", "order_count", "avg_total_time",
                      "avg_delivery_time", "complaint_rate"][:len(result.columns)]

    return result


def stage_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate metrics for each pipeline stage.

    Args:
        df: Transformed DataFrame

    Returns:
        DataFrame with stage-level metrics
    """
    stage_cols = {
        "dough_prep": "dough_prep_time",
        "styling": "styling_time",
        "oven": "oven_time",
        "boxing": "boxing_time",
    }

    metrics = []
    for stage, col in stage_cols.items():
        if col in df.columns:
            data = df[col].dropna()
            benchmark = STAGE_BENCHMARKS.get(stage, {})

            metrics.append({
                "stage": stage,
                "mean": data.mean(),
                "median": data.median(),
                "std": data.std(),
                "p95": data.quantile(0.95),
                "target": benchmark.get("target", None),
                "benchmark_p95": benchmark.get("p95_max", None),
            })

    return pd.DataFrame(metrics)


def complaint_analysis(df: pd.DataFrame) -> Dict:
    """
    Analyze complaints in detail.

    Args:
        df: Transformed DataFrame

    Returns:
        Dict with complaint analysis results
    """
    analysis = {}

    if "complaint" not in df.columns:
        return analysis

    # Complaints by reason
    if "complaint_reason" in df.columns:
        reason_counts = df[df["complaint"] == True]["complaint_reason"].value_counts()
        analysis["by_reason"] = reason_counts.to_dict()

    # Complaints by area
    if "delivery_area" in df.columns:
        area_complaints = df[df["complaint"] == True].groupby("delivery_area").size()
        area_totals = df.groupby("delivery_area").size()
        analysis["by_area"] = (area_complaints / area_totals * 100).to_dict()

    # Complaints by hour
    if "hour_of_day" in df.columns:
        hour_complaints = df[df["complaint"] == True].groupby("hour_of_day").size()
        hour_totals = df.groupby("hour_of_day").size()
        analysis["by_hour"] = (hour_complaints / hour_totals * 100).fillna(0).to_dict()

    # Complaints vs delivery time
    if "delivery_target_met" in df.columns:
        complaint_df = df[df["complaint"] == True]
        on_time_complaints = complaint_df["delivery_target_met"].sum()
        late_complaints = len(complaint_df) - on_time_complaints
        analysis["on_time_complaints"] = on_time_complaints
        analysis["late_complaints"] = late_complaints
        analysis["on_time_complaint_pct"] = (on_time_complaints / len(complaint_df) * 100) if len(complaint_df) > 0 else 0

    return analysis


def calculate_trends(
    df: pd.DataFrame,
    metric_col: str,
    date_col: str = "order_date",
    periods: int = 7
) -> Dict:
    """
    Calculate trend data for a metric.

    Args:
        df: Transformed DataFrame
        metric_col: Column to calculate trend for
        date_col: Date column
        periods: Number of periods to compare

    Returns:
        Dict with trend information
    """
    if date_col not in df.columns or metric_col not in df.columns:
        return {"current": None, "previous": None, "change": None, "change_pct": None}

    df = df.sort_values(date_col)

    # Get date range
    max_date = df[date_col].max()
    mid_date = max_date - pd.Timedelta(days=periods)

    # Current period
    current_df = df[df[date_col] > mid_date]
    current_val = current_df[metric_col].mean() if len(current_df) > 0 else 0

    # Previous period
    prev_start = mid_date - pd.Timedelta(days=periods)
    prev_df = df[(df[date_col] > prev_start) & (df[date_col] <= mid_date)]
    prev_val = prev_df[metric_col].mean() if len(prev_df) > 0 else 0

    # Calculate change
    change = current_val - prev_val
    change_pct = (change / prev_val * 100) if prev_val != 0 else 0

    return {
        "current": current_val,
        "previous": prev_val,
        "change": change,
        "change_pct": change_pct
    }


def top_performers(
    df: pd.DataFrame,
    group_col: str,
    metric_col: str,
    ascending: bool = True,
    top_n: int = 10
) -> pd.DataFrame:
    """
    Get top performers by a metric.

    Args:
        df: Transformed DataFrame
        group_col: Column to group by
        metric_col: Metric to rank by
        ascending: Sort order
        top_n: Number of results

    Returns:
        DataFrame with top performers
    """
    if group_col not in df.columns or metric_col not in df.columns:
        return pd.DataFrame()

    result = df.groupby(group_col).agg({
        metric_col: "mean",
        "order_id": "count"
    }).reset_index()

    result.columns = [group_col, f"avg_{metric_col}", "order_count"]

    return result.sort_values(f"avg_{metric_col}", ascending=ascending).head(top_n)
