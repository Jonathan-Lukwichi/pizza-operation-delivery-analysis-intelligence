"""
Threshold-based alerting logic for PizzaOps Intelligence.
Generates alerts based on KPI thresholds.
"""

import pandas as pd
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

from core.constants import (
    DELIVERY_TARGET_MINUTES, DELIVERY_WARNING_MINUTES, DELIVERY_CRITICAL_MINUTES,
    KPI_TARGETS, OVEN_TEMP_MIN_C, OVEN_TEMP_MAX_C, STAGE_BENCHMARKS
)


@dataclass
class Alert:
    """Represents a system alert."""
    level: str  # 'critical', 'warning', 'info'
    category: str  # 'delivery', 'complaint', 'oven', 'staff', 'process'
    title: str
    message: str
    metric_name: str
    current_value: float
    threshold: float
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


def generate_alerts(df: pd.DataFrame, kpis: Dict) -> List[Alert]:
    """
    Generate alerts based on current data and KPIs.

    Args:
        df: Transformed DataFrame
        kpis: Calculated KPI values

    Returns:
        List of Alert objects
    """
    alerts = []

    # Delivery time alerts
    alerts.extend(check_delivery_alerts(df, kpis))

    # Complaint alerts
    alerts.extend(check_complaint_alerts(df, kpis))

    # Oven temperature alerts
    alerts.extend(check_oven_alerts(df))

    # Process bottleneck alerts
    alerts.extend(check_process_alerts(df))

    # Sort by level
    level_order = {"critical": 0, "warning": 1, "info": 2}
    alerts.sort(key=lambda x: level_order.get(x.level, 3))

    return alerts


def check_delivery_alerts(df: pd.DataFrame, kpis: Dict) -> List[Alert]:
    """Check delivery-related thresholds."""
    alerts = []

    # On-time percentage
    on_time_pct = kpis.get("on_time_pct", 100)
    target = KPI_TARGETS["on_time_pct"]

    if on_time_pct < target * 0.7:
        alerts.append(Alert(
            level="critical",
            category="delivery",
            title="Critical: On-Time Delivery Below Target",
            message=f"Only {on_time_pct:.1f}% of orders delivered on time (target: {target}%)",
            metric_name="On-Time %",
            current_value=on_time_pct,
            threshold=target
        ))
    elif on_time_pct < target:
        alerts.append(Alert(
            level="warning",
            category="delivery",
            title="Warning: On-Time Delivery Declining",
            message=f"{on_time_pct:.1f}% on-time delivery rate is below target of {target}%",
            metric_name="On-Time %",
            current_value=on_time_pct,
            threshold=target
        ))

    # Average delivery time
    avg_time = kpis.get("avg_delivery_time", 0)
    if avg_time > DELIVERY_CRITICAL_MINUTES:
        alerts.append(Alert(
            level="critical",
            category="delivery",
            title="Critical: Average Delivery Time Exceeded",
            message=f"Average delivery time is {avg_time:.1f} min (critical threshold: {DELIVERY_CRITICAL_MINUTES} min)",
            metric_name="Avg Delivery Time",
            current_value=avg_time,
            threshold=DELIVERY_CRITICAL_MINUTES
        ))
    elif avg_time > DELIVERY_TARGET_MINUTES:
        alerts.append(Alert(
            level="warning",
            category="delivery",
            title="Warning: Delivery Times Above Target",
            message=f"Average delivery time is {avg_time:.1f} min (target: {DELIVERY_TARGET_MINUTES} min)",
            metric_name="Avg Delivery Time",
            current_value=avg_time,
            threshold=DELIVERY_TARGET_MINUTES
        ))

    # Area-specific alerts
    if "delivery_area" in df.columns and "delivery_duration" in df.columns:
        area_avg = df.groupby("delivery_area")["delivery_duration"].mean()
        for area, avg in area_avg.items():
            if avg > DELIVERY_TARGET_MINUTES * 1.3:
                alerts.append(Alert(
                    level="warning",
                    category="delivery",
                    title=f"Area {area} Delivery Delays",
                    message=f"Area {area} averaging {avg:.1f} min delivery time",
                    metric_name=f"Area {area} Avg Time",
                    current_value=avg,
                    threshold=DELIVERY_TARGET_MINUTES
                ))

    return alerts


def check_complaint_alerts(df: pd.DataFrame, kpis: Dict) -> List[Alert]:
    """Check complaint-related thresholds."""
    alerts = []

    complaint_rate = kpis.get("complaint_rate", 0)
    target = KPI_TARGETS["complaint_rate_pct"]

    if complaint_rate > target * 2:
        alerts.append(Alert(
            level="critical",
            category="complaint",
            title="Critical: Complaint Rate Very High",
            message=f"Complaint rate at {complaint_rate:.1f}% is more than double the target of {target}%",
            metric_name="Complaint Rate",
            current_value=complaint_rate,
            threshold=target
        ))
    elif complaint_rate > target:
        alerts.append(Alert(
            level="warning",
            category="complaint",
            title="Warning: Complaint Rate Above Target",
            message=f"Complaint rate at {complaint_rate:.1f}% exceeds target of {target}%",
            metric_name="Complaint Rate",
            current_value=complaint_rate,
            threshold=target
        ))

    return alerts


def check_oven_alerts(df: pd.DataFrame) -> List[Alert]:
    """Check oven temperature alerts."""
    alerts = []

    if "oven_temperature" not in df.columns:
        return alerts

    temp_data = df["oven_temperature"].dropna()

    # Check for cold oven issues
    cold_pct = (temp_data < OVEN_TEMP_MIN_C).sum() / len(temp_data) * 100 if len(temp_data) > 0 else 0

    if cold_pct > 10:
        alerts.append(Alert(
            level="warning",
            category="oven",
            title="Warning: Cold Oven Temperatures Detected",
            message=f"{cold_pct:.1f}% of orders made with oven temp below {OVEN_TEMP_MIN_C}°C",
            metric_name="Cold Oven %",
            current_value=cold_pct,
            threshold=10
        ))

    # Check average temperature
    avg_temp = temp_data.mean()
    if avg_temp < OVEN_TEMP_MIN_C:
        alerts.append(Alert(
            level="warning",
            category="oven",
            title="Warning: Average Oven Temperature Low",
            message=f"Average oven temperature {avg_temp:.1f}°C below optimal range",
            metric_name="Avg Oven Temp",
            current_value=avg_temp,
            threshold=OVEN_TEMP_MIN_C
        ))

    return alerts


def check_process_alerts(df: pd.DataFrame) -> List[Alert]:
    """Check process/stage alerts."""
    alerts = []

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
        p95_max = benchmark.get("p95_max")

        if not p95_max:
            continue

        actual_p95 = df[col].quantile(0.95)

        if actual_p95 > p95_max * 1.3:
            alerts.append(Alert(
                level="warning",
                category="process",
                title=f"Process Alert: {stage.replace('_', ' ').title()} Bottleneck",
                message=f"P95 {stage.replace('_', ' ')} time is {actual_p95:.1f} min (benchmark: {p95_max} min)",
                metric_name=f"{stage} P95",
                current_value=actual_p95,
                threshold=p95_max
            ))

    return alerts


def get_alert_summary(alerts: List[Alert]) -> Dict:
    """
    Summarize alerts by category and level.

    Args:
        alerts: List of Alert objects

    Returns:
        Summary dict
    """
    summary = {
        "total": len(alerts),
        "by_level": {"critical": 0, "warning": 0, "info": 0},
        "by_category": {},
        "needs_attention": False
    }

    for alert in alerts:
        summary["by_level"][alert.level] = summary["by_level"].get(alert.level, 0) + 1
        summary["by_category"][alert.category] = summary["by_category"].get(alert.category, 0) + 1

    summary["needs_attention"] = summary["by_level"]["critical"] > 0 or summary["by_level"]["warning"] > 0

    return summary


def format_alert_for_display(alert: Alert) -> Dict:
    """
    Format an alert for UI display.

    Args:
        alert: Alert object

    Returns:
        Dict with display properties
    """
    icons = {
        "critical": "🔴",
        "warning": "🟡",
        "info": "🟢"
    }

    colors = {
        "critical": "#EF4444",
        "warning": "#F59E0B",
        "info": "#10B981"
    }

    return {
        "icon": icons.get(alert.level, "⚪"),
        "color": colors.get(alert.level, "#94A3B8"),
        "title": alert.title,
        "message": alert.message,
        "level": alert.level,
        "category": alert.category,
        "metric": f"{alert.metric_name}: {alert.current_value:.1f} (threshold: {alert.threshold:.1f})"
    }
