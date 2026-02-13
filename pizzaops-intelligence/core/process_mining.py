"""
Process mining and pipeline analysis for PizzaOps Intelligence.
Analyzes the in-store preparation pipeline.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

from core.constants import STAGE_BENCHMARKS, PIPELINE_STAGES


def get_stage_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate mean, median, P95, std for each stage.

    Args:
        df: Transformed DataFrame

    Returns:
        DataFrame with stage statistics
    """
    stage_cols = {
        "dough_prep": "dough_prep_time",
        "styling": "styling_time",
        "oven": "oven_time",
        "boxing": "boxing_time",
    }

    results = []
    for stage, col in stage_cols.items():
        if col not in df.columns:
            continue

        data = df[col].dropna()
        benchmark = STAGE_BENCHMARKS.get(stage, {})

        results.append({
            "stage": stage,
            "mean": round(data.mean(), 2),
            "median": round(data.median(), 2),
            "std": round(data.std(), 2),
            "min": round(data.min(), 2),
            "max": round(data.max(), 2),
            "p25": round(data.quantile(0.25), 2),
            "p75": round(data.quantile(0.75), 2),
            "p95": round(data.quantile(0.95), 2),
            "target": benchmark.get("target"),
            "benchmark_p95": benchmark.get("p95_max"),
        })

    return pd.DataFrame(results)


def detect_bottlenecks(df: pd.DataFrame, threshold_pct: float = 95) -> List[Dict]:
    """
    Identify pipeline stages that exceed performance benchmarks.

    Args:
        df: Transformed DataFrame
        threshold_pct: Percentile to check against benchmarks

    Returns:
        List of dicts with bottleneck details
    """
    stage_cols = {
        "dough_prep": "dough_prep_time",
        "styling": "styling_time",
        "oven": "oven_time",
        "boxing": "boxing_time",
    }

    bottlenecks = []

    for stage, col in stage_cols.items():
        if col not in df.columns:
            continue

        benchmark = STAGE_BENCHMARKS.get(stage, {})
        benchmark_p95 = benchmark.get("p95_max")

        if benchmark_p95 is None:
            continue

        data = df[col].dropna()
        actual_p95 = data.quantile(threshold_pct / 100)

        if actual_p95 > benchmark_p95:
            # Find peak hours for this bottleneck
            peak_hours = []
            if "hour_of_day" in df.columns:
                hourly_p95 = df.groupby("hour_of_day")[col].quantile(0.95)
                peak_hours = hourly_p95[hourly_p95 > benchmark_p95].index.tolist()

            severity = "high" if actual_p95 > benchmark_p95 * 1.2 else "medium"

            bottlenecks.append({
                "stage": stage,
                "actual_p95": round(actual_p95, 2),
                "benchmark_p95": benchmark_p95,
                "excess_time": round(actual_p95 - benchmark_p95, 2),
                "severity": severity,
                "peak_hours": peak_hours,
                "affected_orders_pct": round(
                    (data > benchmark_p95).sum() / len(data) * 100, 1
                ) if len(data) > 0 else 0
            })

    # Sort by severity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    bottlenecks.sort(key=lambda x: (severity_order.get(x["severity"], 3), -x["excess_time"]))

    return bottlenecks


def stage_by_hour_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create pivot table: hour_of_day × stage → avg duration.

    Args:
        df: Transformed DataFrame

    Returns:
        Pivot table for heatmap visualization
    """
    stage_cols = ["dough_prep_time", "styling_time", "oven_time", "boxing_time"]
    available_cols = [col for col in stage_cols if col in df.columns]

    if "hour_of_day" not in df.columns or not available_cols:
        return pd.DataFrame()

    result = df.groupby("hour_of_day")[available_cols].mean()

    # Rename columns for display
    result.columns = [col.replace("_time", "").replace("_", " ").title() for col in result.columns]

    return result


def oven_temp_analysis(df: pd.DataFrame) -> Dict:
    """
    Analyze oven temperature correlations.

    Args:
        df: Transformed DataFrame

    Returns:
        Dict with oven temperature analysis results
    """
    analysis = {}

    if "oven_temperature" not in df.columns:
        return analysis

    # Basic stats
    temp_data = df["oven_temperature"].dropna()
    analysis["mean_temp"] = round(temp_data.mean(), 1)
    analysis["min_temp"] = round(temp_data.min(), 1)
    analysis["max_temp"] = round(temp_data.max(), 1)
    analysis["std_temp"] = round(temp_data.std(), 1)

    # Correlation with oven time
    if "oven_time" in df.columns:
        valid_df = df[["oven_temperature", "oven_time"]].dropna()
        if len(valid_df) > 10:
            analysis["temp_time_corr"] = round(
                valid_df["oven_temperature"].corr(valid_df["oven_time"]), 3
            )

    # Complaint rate by temperature zone
    if "complaint" in df.columns and "oven_temp_zone" in df.columns:
        zone_complaints = df.groupby("oven_temp_zone")["complaint"].agg(["sum", "count"])
        zone_complaints["rate"] = (zone_complaints["sum"] / zone_complaints["count"] * 100).round(2)
        analysis["complaint_rate_by_zone"] = zone_complaints["rate"].to_dict()

    # Temperature distribution
    if "oven_temp_zone" in df.columns:
        zone_dist = df["oven_temp_zone"].value_counts(normalize=True) * 100
        analysis["temp_zone_distribution"] = zone_dist.to_dict()

    return analysis


def calculate_stage_contributions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate each stage's contribution to total prep time.

    Args:
        df: Transformed DataFrame

    Returns:
        DataFrame with contribution percentages
    """
    stage_cols = {
        "Dough Prep": "dough_prep_time",
        "Styling": "styling_time",
        "Oven": "oven_time",
        "Boxing": "boxing_time",
    }

    contributions = []
    for stage_name, col in stage_cols.items():
        if col not in df.columns or "total_prep_time" not in df.columns:
            continue

        pct_col = f"pct_{col.replace('_time', '')}"
        if pct_col in df.columns:
            avg_pct = df[pct_col].mean()
        else:
            avg_pct = (df[col] / df["total_prep_time"] * 100).mean()

        contributions.append({
            "stage": stage_name,
            "avg_time": round(df[col].mean(), 2),
            "contribution_pct": round(avg_pct, 1)
        })

    return pd.DataFrame(contributions)


def analyze_process_variability(df: pd.DataFrame) -> Dict:
    """
    Analyze variability in the process.

    Args:
        df: Transformed DataFrame

    Returns:
        Dict with variability metrics
    """
    analysis = {}

    # Total prep time variability
    if "total_prep_time" in df.columns:
        data = df["total_prep_time"].dropna()
        analysis["prep_time_cv"] = round(data.std() / data.mean() * 100, 1)  # Coefficient of variation

    # Identify most variable stage
    stage_cols = ["dough_prep_time", "styling_time", "oven_time", "boxing_time"]
    cvs = {}
    for col in stage_cols:
        if col in df.columns:
            data = df[col].dropna()
            if data.mean() > 0:
                cvs[col.replace("_time", "")] = round(data.std() / data.mean() * 100, 1)

    if cvs:
        analysis["most_variable_stage"] = max(cvs, key=cvs.get)
        analysis["stage_cvs"] = cvs

    # Time of day variability
    if "hour_of_day" in df.columns and "total_prep_time" in df.columns:
        hourly_cv = df.groupby("hour_of_day")["total_prep_time"].agg(
            lambda x: x.std() / x.mean() * 100 if x.mean() > 0 else 0
        )
        analysis["most_variable_hour"] = hourly_cv.idxmax()
        analysis["hourly_cvs"] = hourly_cv.to_dict()

    return analysis


def get_process_recommendations(bottlenecks: List[Dict], oven_analysis: Dict) -> List[str]:
    """
    Generate process improvement recommendations.

    Args:
        bottlenecks: List of detected bottlenecks
        oven_analysis: Oven temperature analysis results

    Returns:
        List of recommendation strings
    """
    recommendations = []

    # Bottleneck recommendations
    for bn in bottlenecks:
        stage = bn["stage"].replace("_", " ").title()
        if bn["severity"] == "high":
            recommendations.append(
                f"Critical: {stage} stage is a severe bottleneck (P95: {bn['actual_p95']} min vs target {bn['benchmark_p95']} min). "
                f"Consider adding staff or equipment during peak hours: {bn['peak_hours']}"
            )
        else:
            recommendations.append(
                f"Warning: {stage} stage exceeds benchmark by {bn['excess_time']} min at P95. "
                f"Monitor performance during hours: {bn['peak_hours']}"
            )

    # Oven temperature recommendations
    if oven_analysis:
        zone_rates = oven_analysis.get("complaint_rate_by_zone", {})
        if zone_rates.get("cold", 0) > zone_rates.get("optimal", 0) * 1.5:
            recommendations.append(
                f"Quality Alert: Cold oven temperatures (<220°C) correlate with {zone_rates.get('cold', 0):.1f}% complaint rate "
                f"vs {zone_rates.get('optimal', 0):.1f}% at optimal temperatures. "
                "Ensure oven preheating protocols are followed."
            )

    if not recommendations:
        recommendations.append("Process is operating within acceptable parameters. Continue monitoring.")

    return recommendations
