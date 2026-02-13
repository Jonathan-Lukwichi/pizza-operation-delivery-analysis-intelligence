"""
Bottleneck identification algorithms for PizzaOps Intelligence.
Advanced analysis for identifying operational constraints.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from core.constants import STAGE_BENCHMARKS, DELIVERY_TARGET_MINUTES


@dataclass
class Bottleneck:
    """Represents a detected bottleneck."""
    location: str
    type: str  # 'stage', 'area', 'staff', 'time'
    severity: str  # 'critical', 'high', 'medium', 'low'
    metric: str
    current_value: float
    threshold: float
    impact_pct: float
    affected_periods: List[str]
    recommendation: str


def identify_all_bottlenecks(df: pd.DataFrame) -> List[Bottleneck]:
    """
    Comprehensive bottleneck detection across all dimensions.

    Args:
        df: Transformed DataFrame

    Returns:
        List of Bottleneck objects sorted by severity
    """
    bottlenecks = []

    # Stage bottlenecks
    bottlenecks.extend(detect_stage_bottlenecks(df))

    # Area bottlenecks
    bottlenecks.extend(detect_area_bottlenecks(df))

    # Staff bottlenecks
    bottlenecks.extend(detect_staff_bottlenecks(df))

    # Time-based bottlenecks
    bottlenecks.extend(detect_time_bottlenecks(df))

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    bottlenecks.sort(key=lambda x: (severity_order.get(x.severity, 4), -x.impact_pct))

    return bottlenecks


def detect_stage_bottlenecks(df: pd.DataFrame) -> List[Bottleneck]:
    """Detect bottlenecks in pipeline stages."""
    bottlenecks = []

    stage_cols = {
        "dough_prep": "dough_prep_time",
        "styling": "styling_time",
        "oven": "oven_time",
        "boxing": "boxing_time",
    }

    for stage, col in stage_cols.items():
        if col not in df.columns:
            continue

        benchmark = STAGE_BENCHMARKS.get(stage, {})
        target = benchmark.get("target")
        p95_max = benchmark.get("p95_max")

        if not target or not p95_max:
            continue

        data = df[col].dropna()
        actual_p95 = data.quantile(0.95)
        mean_val = data.mean()

        # Check if P95 exceeds benchmark
        if actual_p95 > p95_max:
            excess_ratio = actual_p95 / p95_max
            affected_pct = (data > p95_max).sum() / len(data) * 100

            if excess_ratio > 1.3:
                severity = "critical"
            elif excess_ratio > 1.15:
                severity = "high"
            else:
                severity = "medium"

            # Find affected hours
            affected_hours = []
            if "hour_of_day" in df.columns:
                hourly_p95 = df.groupby("hour_of_day")[col].quantile(0.95)
                affected_hours = [str(h) for h in hourly_p95[hourly_p95 > p95_max].index.tolist()]

            bottlenecks.append(Bottleneck(
                location=stage.replace("_", " ").title(),
                type="stage",
                severity=severity,
                metric="P95 Duration",
                current_value=round(actual_p95, 2),
                threshold=p95_max,
                impact_pct=round(affected_pct, 1),
                affected_periods=affected_hours[:5],
                recommendation=f"Reduce {stage.replace('_', ' ')} time by optimizing workflow or adding resources"
            ))

    return bottlenecks


def detect_area_bottlenecks(df: pd.DataFrame) -> List[Bottleneck]:
    """Detect bottlenecks in delivery areas."""
    bottlenecks = []

    if "delivery_area" not in df.columns or "delivery_duration" not in df.columns:
        return bottlenecks

    # Calculate area metrics
    area_metrics = df.groupby("delivery_area").agg({
        "delivery_duration": ["mean", lambda x: x.quantile(0.95)],
        "order_id": "count"
    }).reset_index()

    area_metrics.columns = ["area", "avg_time", "p95_time", "order_count"]

    # Overall metrics
    overall_avg = df["delivery_duration"].mean()
    overall_p95 = df["delivery_duration"].quantile(0.95)

    for _, row in area_metrics.iterrows():
        # Check if area significantly underperforms
        if row["avg_time"] > overall_avg * 1.2:
            excess_ratio = row["avg_time"] / overall_avg
            impact_pct = row["order_count"] / len(df) * 100

            if excess_ratio > 1.4:
                severity = "high"
            elif excess_ratio > 1.25:
                severity = "medium"
            else:
                severity = "low"

            # Find peak hours for this area
            affected_hours = []
            if "hour_of_day" in df.columns:
                area_df = df[df["delivery_area"] == row["area"]]
                hourly_avg = area_df.groupby("hour_of_day")["delivery_duration"].mean()
                worst_hours = hourly_avg.nlargest(3).index.tolist()
                affected_hours = [str(h) for h in worst_hours]

            bottlenecks.append(Bottleneck(
                location=f"Area {row['area']}",
                type="area",
                severity=severity,
                metric="Avg Delivery Time",
                current_value=round(row["avg_time"], 1),
                threshold=round(overall_avg, 1),
                impact_pct=round(impact_pct, 1),
                affected_periods=affected_hours,
                recommendation=f"Optimize routes for Area {row['area']} or assign faster drivers"
            ))

    return bottlenecks


def detect_staff_bottlenecks(df: pd.DataFrame) -> List[Bottleneck]:
    """Detect bottlenecks related to specific staff members."""
    bottlenecks = []

    # Check drivers
    if "delivery_driver" in df.columns and "delivery_duration" in df.columns:
        driver_metrics = df.groupby("delivery_driver").agg({
            "delivery_duration": "mean",
            "order_id": "count"
        }).reset_index()

        driver_metrics.columns = ["driver", "avg_time", "deliveries"]
        overall_avg = df["delivery_duration"].mean()

        for _, row in driver_metrics.iterrows():
            if row["avg_time"] > overall_avg * 1.25 and row["deliveries"] >= 10:
                severity = "medium" if row["avg_time"] > overall_avg * 1.4 else "low"
                impact_pct = row["deliveries"] / len(df) * 100

                bottlenecks.append(Bottleneck(
                    location=row["driver"],
                    type="staff",
                    severity=severity,
                    metric="Avg Delivery Time",
                    current_value=round(row["avg_time"], 1),
                    threshold=round(overall_avg, 1),
                    impact_pct=round(impact_pct, 1),
                    affected_periods=[],
                    recommendation=f"{row['driver']} may benefit from route training or reassignment"
                ))

    # Check stylists (if complaint correlation exists)
    if "stylist" in df.columns and "complaint" in df.columns:
        stylist_complaints = df.groupby("stylist").agg({
            "complaint": ["sum", "count"]
        }).reset_index()

        stylist_complaints.columns = ["stylist", "complaints", "total"]
        stylist_complaints["rate"] = stylist_complaints["complaints"] / stylist_complaints["total"] * 100

        overall_rate = df["complaint"].mean() * 100

        for _, row in stylist_complaints.iterrows():
            if row["rate"] > overall_rate * 1.5 and row["total"] >= 20:
                severity = "medium"
                impact_pct = row["total"] / len(df) * 100

                bottlenecks.append(Bottleneck(
                    location=row["stylist"],
                    type="staff",
                    severity=severity,
                    metric="Complaint Rate",
                    current_value=round(row["rate"], 1),
                    threshold=round(overall_rate, 1),
                    impact_pct=round(impact_pct, 1),
                    affected_periods=[],
                    recommendation=f"{row['stylist']} shows higher complaint rate - review styling quality"
                ))

    return bottlenecks


def detect_time_bottlenecks(df: pd.DataFrame) -> List[Bottleneck]:
    """Detect time-based bottlenecks (peak hours, days)."""
    bottlenecks = []

    if "hour_of_day" not in df.columns or "total_process_time" not in df.columns:
        return bottlenecks

    # Hourly analysis
    hourly_metrics = df.groupby("hour_of_day").agg({
        "total_process_time": "mean",
        "order_id": "count"
    }).reset_index()

    hourly_metrics.columns = ["hour", "avg_time", "order_count"]
    overall_avg = df["total_process_time"].mean()

    # Find problem hours
    for _, row in hourly_metrics.iterrows():
        if row["avg_time"] > overall_avg * 1.2 and row["order_count"] > len(df) / 24 * 0.5:
            severity = "high" if row["avg_time"] > DELIVERY_TARGET_MINUTES else "medium"
            impact_pct = row["order_count"] / len(df) * 100

            bottlenecks.append(Bottleneck(
                location=f"{int(row['hour']):02d}:00",
                type="time",
                severity=severity,
                metric="Avg Total Time",
                current_value=round(row["avg_time"], 1),
                threshold=round(overall_avg, 1),
                impact_pct=round(impact_pct, 1),
                affected_periods=[],
                recommendation=f"Consider additional staffing at {int(row['hour']):02d}:00"
            ))

    return bottlenecks


def calculate_bottleneck_impact(bottlenecks: List[Bottleneck], df: pd.DataFrame) -> Dict:
    """
    Calculate overall impact of bottlenecks.

    Args:
        bottlenecks: List of detected bottlenecks
        df: Transformed DataFrame

    Returns:
        Dict with impact summary
    """
    impact = {
        "total_bottlenecks": len(bottlenecks),
        "critical_count": sum(1 for b in bottlenecks if b.severity == "critical"),
        "high_count": sum(1 for b in bottlenecks if b.severity == "high"),
        "medium_count": sum(1 for b in bottlenecks if b.severity == "medium"),
        "low_count": sum(1 for b in bottlenecks if b.severity == "low"),
        "by_type": {},
        "top_recommendations": []
    }

    # Count by type
    for bn in bottlenecks:
        if bn.type not in impact["by_type"]:
            impact["by_type"][bn.type] = 0
        impact["by_type"][bn.type] += 1

    # Get top recommendations
    for bn in bottlenecks[:5]:
        impact["top_recommendations"].append({
            "location": bn.location,
            "severity": bn.severity,
            "recommendation": bn.recommendation
        })

    return impact


def get_bottleneck_summary(bottlenecks: List[Bottleneck]) -> str:
    """
    Generate a text summary of bottlenecks.

    Args:
        bottlenecks: List of detected bottlenecks

    Returns:
        Summary string
    """
    if not bottlenecks:
        return "No significant bottlenecks detected. Operations are running smoothly."

    critical = [b for b in bottlenecks if b.severity == "critical"]
    high = [b for b in bottlenecks if b.severity == "high"]

    parts = []

    if critical:
        parts.append(f"Found {len(critical)} critical bottleneck(s) requiring immediate attention")

    if high:
        parts.append(f"{len(high)} high-priority issue(s) identified")

    if not critical and not high:
        parts.append(f"Detected {len(bottlenecks)} minor bottleneck(s)")

    # Add top bottleneck detail
    top = bottlenecks[0]
    parts.append(
        f"Primary concern: {top.location} ({top.metric}: {top.current_value} vs threshold {top.threshold})"
    )

    return ". ".join(parts) + "."
