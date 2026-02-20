"""
Local Analytics Engine
======================

Offline-capable analytics that work without AI/internet.
Optimized for South African market conditions (load shedding, mobile data).
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
import numpy as np
from datetime import datetime


@dataclass
class KPIs:
    """Key Performance Indicators."""
    total_orders: int
    on_time_rate: float
    complaint_rate: float
    avg_delivery_time: float
    total_revenue: Optional[float] = None


@dataclass
class Bottleneck:
    """A detected bottleneck."""
    area: str
    severity: str  # low, medium, high, critical
    current_value: float
    benchmark: float
    variance_pct: float
    impact_description: str
    suggested_action: str


@dataclass
class Alert:
    """An operational alert."""
    level: str  # info, warning, critical
    title: str
    description: str
    metric_value: float
    threshold: float


class LocalAnalytics:
    """
    All analytics that work offline without AI.

    Designed for:
    - Load shedding conditions (no internet)
    - Mobile data saving (no API calls)
    - Quick response times
    """

    # Industry benchmarks for pizza delivery
    BENCHMARKS = {
        "on_time_rate": 85.0,  # Target: 85%+ on-time
        "complaint_rate": 5.0,  # Target: <5% complaints
        "avg_delivery_time": 30.0,  # Target: 30 min total
        "dough_prep_time": 5.0,
        "styling_time": 3.0,
        "oven_time": 10.0,
        "boxing_time": 2.0,
        "delivery_duration": 10.0,
    }

    def get_kpis(self, df: pd.DataFrame) -> KPIs:
        """
        Calculate key performance indicators locally.

        Args:
            df: Orders dataframe

        Returns:
            KPIs dataclass with all metrics
        """
        total_orders = len(df)

        # On-time rate
        on_time_rate = 0.0
        if "delivery_target_met" in df.columns:
            on_time_rate = df["delivery_target_met"].mean() * 100

        # Complaint rate
        complaint_rate = 0.0
        if "complaint" in df.columns:
            complaint_rate = df["complaint"].mean() * 100

        # Average delivery time
        avg_delivery_time = 0.0
        if "total_process_time" in df.columns:
            avg_delivery_time = df["total_process_time"].mean()

        # Total revenue (if available)
        total_revenue = None
        if "order_value" in df.columns:
            total_revenue = df["order_value"].sum()

        return KPIs(
            total_orders=total_orders,
            on_time_rate=round(on_time_rate, 1),
            complaint_rate=round(complaint_rate, 1),
            avg_delivery_time=round(avg_delivery_time, 1),
            total_revenue=round(total_revenue, 2) if total_revenue else None
        )

    def detect_bottlenecks(self, df: pd.DataFrame) -> List[Bottleneck]:
        """
        Identify operational bottlenecks using rule-based logic.

        No AI required - uses statistical thresholds.

        Args:
            df: Orders dataframe

        Returns:
            List of Bottleneck objects, sorted by severity
        """
        bottlenecks = []

        # Stage-based bottlenecks
        stage_cols = [
            ("dough_prep_time", "Dough Preparation"),
            ("styling_time", "Pizza Styling"),
            ("oven_time", "Oven Stage"),
            ("boxing_time", "Boxing"),
            ("delivery_duration", "Delivery"),
        ]

        for col, name in stage_cols:
            if col not in df.columns:
                continue

            avg = df[col].mean()
            benchmark = self.BENCHMARKS.get(col, avg)
            variance_pct = ((avg - benchmark) / benchmark) * 100 if benchmark > 0 else 0

            # Only flag if >10% above benchmark
            if variance_pct > 10:
                severity = "critical" if variance_pct > 50 else (
                    "high" if variance_pct > 30 else (
                        "medium" if variance_pct > 20 else "low"
                    )
                )

                # Generate suggested action based on stage
                actions = {
                    "dough_prep_time": "Pre-stage dough during slow periods",
                    "styling_time": "Review topping stations efficiency",
                    "oven_time": "Add staff during peak hours or check oven capacity",
                    "boxing_time": "Streamline packaging process",
                    "delivery_duration": "Review delivery routes or driver allocation",
                }

                bottlenecks.append(Bottleneck(
                    area=name,
                    severity=severity,
                    current_value=round(avg, 1),
                    benchmark=benchmark,
                    variance_pct=round(variance_pct, 1),
                    impact_description=f"{name} is {variance_pct:.0f}% slower than benchmark",
                    suggested_action=actions.get(col, "Review process efficiency")
                ))

        # Area-based bottlenecks
        if "delivery_area" in df.columns and "total_process_time" in df.columns:
            overall_avg = df["total_process_time"].mean()
            area_stats = df.groupby("delivery_area")["total_process_time"].agg(["mean", "count"])

            for area, row in area_stats.iterrows():
                area_avg = row["mean"]
                variance_pct = ((area_avg - overall_avg) / overall_avg) * 100

                if variance_pct > 15:  # 15% above average
                    severity = "high" if variance_pct > 30 else "medium"

                    bottlenecks.append(Bottleneck(
                        area=f"Delivery Area {area}",
                        severity=severity,
                        current_value=round(area_avg, 1),
                        benchmark=round(overall_avg, 1),
                        variance_pct=round(variance_pct, 1),
                        impact_description=f"Area {area} is {variance_pct:.0f}% slower than average",
                        suggested_action=f"Assign experienced drivers to Area {area} or review routing"
                    ))

        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        bottlenecks.sort(key=lambda x: severity_order.get(x.severity, 4))

        return bottlenecks

    def generate_alerts(self, df: pd.DataFrame) -> List[Alert]:
        """
        Generate operational alerts based on thresholds.

        Args:
            df: Orders dataframe

        Returns:
            List of Alert objects
        """
        alerts = []
        kpis = self.get_kpis(df)

        # On-time rate alert
        if kpis.on_time_rate < 85:
            level = "critical" if kpis.on_time_rate < 70 else "warning"
            alerts.append(Alert(
                level=level,
                title="On-Time Delivery Below Target",
                description=f"On-time rate is {kpis.on_time_rate}%, target is 85%",
                metric_value=kpis.on_time_rate,
                threshold=85.0
            ))

        # Complaint rate alert
        if kpis.complaint_rate > 5:
            level = "critical" if kpis.complaint_rate > 10 else "warning"
            alerts.append(Alert(
                level=level,
                title="Complaint Rate Above Target",
                description=f"Complaint rate is {kpis.complaint_rate}%, target is <5%",
                metric_value=kpis.complaint_rate,
                threshold=5.0
            ))

        # Average delivery time alert
        if kpis.avg_delivery_time > 30:
            level = "critical" if kpis.avg_delivery_time > 40 else "warning"
            alerts.append(Alert(
                level=level,
                title="Delivery Time Above Target",
                description=f"Avg delivery is {kpis.avg_delivery_time} min, target is 30 min",
                metric_value=kpis.avg_delivery_time,
                threshold=30.0
            ))

        # Check for peak hour issues
        if "order_hour" in df.columns and "total_process_time" in df.columns:
            hour_stats = df.groupby("order_hour")["total_process_time"].mean()
            overall_avg = df["total_process_time"].mean()

            for hour, avg_time in hour_stats.items():
                if avg_time > overall_avg * 1.3:  # 30% above average
                    alerts.append(Alert(
                        level="warning",
                        title=f"Peak Hour Slowdown at {hour}:00",
                        description=f"Avg time is {avg_time:.1f} min at {hour}:00 (vs {overall_avg:.1f} overall)",
                        metric_value=avg_time,
                        threshold=overall_avg * 1.3
                    ))

        # Sort by level
        level_order = {"critical": 0, "warning": 1, "info": 2}
        alerts.sort(key=lambda x: level_order.get(x.level, 3))

        return alerts

    def generate_recommendations(self, df: pd.DataFrame) -> List[Dict[str, str]]:
        """
        Generate rule-based recommendations (no AI).

        Args:
            df: Orders dataframe

        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        bottlenecks = self.detect_bottlenecks(df)
        kpis = self.get_kpis(df)

        # KPI-based recommendations
        if kpis.on_time_rate < 85:
            gap = 85 - kpis.on_time_rate
            recommendations.append({
                "priority": "high",
                "title": "Improve On-Time Delivery",
                "action": f"Reduce total delivery time to improve on-time rate by {gap:.0f}%",
                "expected_impact": f"Could improve customer satisfaction and reduce complaints",
                "evidence": f"Current on-time rate: {kpis.on_time_rate}%"
            })

        if kpis.complaint_rate > 5:
            recommendations.append({
                "priority": "high",
                "title": "Reduce Customer Complaints",
                "action": "Identify top complaint reasons and address root causes",
                "expected_impact": "Improve customer retention and brand reputation",
                "evidence": f"Current complaint rate: {kpis.complaint_rate}%"
            })

        # Bottleneck-based recommendations
        for bottleneck in bottlenecks[:3]:  # Top 3 bottlenecks
            recommendations.append({
                "priority": "medium" if bottleneck.severity in ["high", "critical"] else "quick_win",
                "title": f"Fix {bottleneck.area} Bottleneck",
                "action": bottleneck.suggested_action,
                "expected_impact": f"Could reduce {bottleneck.area.lower()} time by {bottleneck.variance_pct:.0f}%",
                "evidence": f"Currently {bottleneck.current_value} min vs {bottleneck.benchmark} min benchmark"
            })

        # Quick wins
        if "chef_name" in df.columns and "total_process_time" in df.columns:
            chef_stats = df.groupby("chef_name")["total_process_time"].mean()
            best_chef = chef_stats.idxmin()
            worst_chef = chef_stats.idxmax()

            if chef_stats[worst_chef] > chef_stats[best_chef] * 1.2:
                recommendations.append({
                    "priority": "quick_win",
                    "title": "Staff Training Opportunity",
                    "action": f"Have {best_chef} train {worst_chef} on efficiency techniques",
                    "expected_impact": "Reduce performance gap between staff members",
                    "evidence": f"{best_chef}: {chef_stats[best_chef]:.1f} min avg vs {worst_chef}: {chef_stats[worst_chef]:.1f} min avg"
                })

        return recommendations

    def get_trend_data(self, df: pd.DataFrame, days: int = 7) -> Dict[str, List]:
        """
        Get trend data for the last N days.

        Args:
            df: Orders dataframe
            days: Number of days to include

        Returns:
            Dictionary with dates and metrics
        """
        if "order_date" not in df.columns:
            return {"dates": [], "orders": [], "on_time": [], "complaints": []}

        # Ensure datetime
        df = df.copy()
        df["order_date"] = pd.to_datetime(df["order_date"])

        # Get last N days
        max_date = df["order_date"].max()
        min_date = max_date - pd.Timedelta(days=days)
        df_recent = df[df["order_date"] >= min_date]

        # Aggregate by date
        daily_stats = df_recent.groupby(df_recent["order_date"].dt.date).agg({
            "order_id": "count" if "order_id" in df.columns else lambda x: len(x),
            "delivery_target_met": "mean" if "delivery_target_met" in df.columns else lambda x: 0,
            "complaint": "mean" if "complaint" in df.columns else lambda x: 0,
        }).reset_index()

        return {
            "dates": daily_stats["order_date"].astype(str).tolist(),
            "orders": daily_stats["order_id"].tolist() if "order_id" in daily_stats.columns else [],
            "on_time": (daily_stats["delivery_target_met"] * 100).round(1).tolist() if "delivery_target_met" in daily_stats.columns else [],
            "complaints": (daily_stats["complaint"] * 100).round(1).tolist() if "complaint" in daily_stats.columns else [],
        }

    def get_stage_breakdown(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Get average time breakdown by stage.

        Args:
            df: Orders dataframe

        Returns:
            Dictionary mapping stage name to average time
        """
        stages = {
            "Dough Prep": "dough_prep_time",
            "Styling": "styling_time",
            "Oven": "oven_time",
            "Boxing": "boxing_time",
            "Delivery": "delivery_duration",
        }

        breakdown = {}
        for name, col in stages.items():
            if col in df.columns:
                breakdown[name] = round(df[col].mean(), 1)

        return breakdown

    def get_area_performance(self, df: pd.DataFrame) -> List[Dict]:
        """
        Get performance breakdown by delivery area.

        Args:
            df: Orders dataframe

        Returns:
            List of dictionaries with area performance
        """
        if "delivery_area" not in df.columns:
            return []

        results = []
        area_groups = df.groupby("delivery_area")

        for area, group in area_groups:
            result = {
                "area": area,
                "orders": len(group),
            }

            if "total_process_time" in df.columns:
                result["avg_time"] = round(group["total_process_time"].mean(), 1)

            if "delivery_target_met" in df.columns:
                result["on_time_rate"] = round(group["delivery_target_met"].mean() * 100, 1)

            if "complaint" in df.columns:
                result["complaint_rate"] = round(group["complaint"].mean() * 100, 1)

            results.append(result)

        # Sort by orders (descending)
        results.sort(key=lambda x: x.get("orders", 0), reverse=True)

        return results

    # ══════════════════════════════════════════════════════════════════════════════
    # EDA ANALYSIS METHODS
    # ══════════════════════════════════════════════════════════════════════════════

    def get_numerical_stats(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Get distribution statistics for time columns.

        Args:
            df: Orders dataframe

        Returns:
            Dictionary mapping column name to stats dict
        """
        time_cols = ["dough_prep_time", "styling_time", "oven_time",
                     "boxing_time", "delivery_duration", "total_process_time"]
        stats = {}
        for col in time_cols:
            if col in df.columns:
                stats[col] = {
                    "mean": round(df[col].mean(), 2),
                    "median": round(df[col].median(), 2),
                    "std": round(df[col].std(), 2),
                    "min": round(df[col].min(), 2),
                    "max": round(df[col].max(), 2),
                    "q1": round(df[col].quantile(0.25), 2),
                    "q3": round(df[col].quantile(0.75), 2),
                }
        return stats

    def get_categorical_counts(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Get counts and proportions for categorical columns.

        Args:
            df: Orders dataframe

        Returns:
            Dictionary mapping column name to count DataFrame
        """
        cat_cols = ["order_mode", "delivery_area", "delay_category",
                    "oven_temp_zone", "pizza_size"]
        result = {}
        for col in cat_cols:
            if col in df.columns:
                counts = df[col].value_counts().reset_index()
                counts.columns = [col, "count"]
                counts["pct"] = (counts["count"] / len(df) * 100).round(1)
                result[col] = counts
        return result

    def get_temporal_patterns(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Analyze temporal patterns in the data.

        Args:
            df: Orders dataframe

        Returns:
            Dictionary with hourly, daily, and peak patterns
        """
        result = {}

        if "hour_of_day" in df.columns:
            result["hourly"] = df.groupby("hour_of_day").size().to_dict()

        if "day_of_week" in df.columns:
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday", "Saturday", "Sunday"]
            daily = df.groupby("day_of_week").size()
            # Reindex to ensure proper order
            result["daily"] = {day: daily.get(day, 0) for day in day_order}

        if "is_peak_hour" in df.columns and "total_process_time" in df.columns:
            peak_stats = df.groupby("is_peak_hour").agg({
                "total_process_time": ["mean", "count"]
            }).round(1)
            result["peak_comparison"] = {
                "peak": {
                    "avg_time": peak_stats.loc[True, ("total_process_time", "mean")] if True in peak_stats.index else 0,
                    "count": int(peak_stats.loc[True, ("total_process_time", "count")]) if True in peak_stats.index else 0
                },
                "off_peak": {
                    "avg_time": peak_stats.loc[False, ("total_process_time", "mean")] if False in peak_stats.index else 0,
                    "count": int(peak_stats.loc[False, ("total_process_time", "count")]) if False in peak_stats.index else 0
                }
            }

        return result

    def get_correlation_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate correlation matrix for numeric columns.

        Args:
            df: Orders dataframe

        Returns:
            Correlation matrix as DataFrame
        """
        num_cols = ["dough_prep_time", "styling_time", "oven_time",
                    "boxing_time", "delivery_duration", "total_process_time",
                    "oven_temperature"]
        available_cols = [c for c in num_cols if c in df.columns]
        if len(available_cols) < 2:
            return pd.DataFrame()
        return df[available_cols].corr().round(3)

    def detect_outliers_iqr(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Detect outliers using IQR method for time columns.

        Args:
            df: Orders dataframe

        Returns:
            Dictionary mapping column name to outlier count
        """
        time_cols = ["dough_prep_time", "styling_time", "oven_time",
                     "boxing_time", "delivery_duration", "total_process_time"]
        outliers = {}
        for col in time_cols:
            if col in df.columns:
                q1, q3 = df[col].quantile([0.25, 0.75])
                iqr = q3 - q1
                lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                outliers[col] = int(((df[col] < lower) | (df[col] > upper)).sum())
        return outliers

    def get_data_quality_report(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Generate data quality summary.

        Args:
            df: Orders dataframe

        Returns:
            Dictionary with quality metrics
        """
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()

        date_range = {"start": None, "end": None}
        if "order_date" in df.columns:
            date_range["start"] = str(df["order_date"].min())
            date_range["end"] = str(df["order_date"].max())

        return {
            "completeness_score": round((1 - missing_cells / total_cells) * 100, 1) if total_cells > 0 else 100,
            "missing_by_column": df.isnull().sum().to_dict(),
            "missing_pct": (df.isnull().sum() / len(df) * 100).round(1).to_dict(),
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "date_range": date_range,
        }

    # ══════════════════════════════════════════════════════════════════════════════
    # DASHBOARD LEADERBOARD & RADAR METHODS
    # ══════════════════════════════════════════════════════════════════════════════

    def get_driver_leaderboard(self, df: pd.DataFrame, limit: int = 10) -> List[Dict]:
        """
        Get driver leaderboard ranked by on-time delivery rate.

        Args:
            df: Orders dataframe
            limit: Maximum number of drivers to return

        Returns:
            List of driver stats with rank, name, on-time rate, total deliveries
        """
        if "driver_name" not in df.columns:
            return []

        # Filter out rows with no driver
        df_drivers = df[df["driver_name"].notna() & (df["driver_name"] != "")]

        if len(df_drivers) == 0:
            return []

        # Calculate stats per driver
        driver_stats = df_drivers.groupby("driver_name").agg({
            "order_id": "count" if "order_id" in df.columns else lambda x: len(x),
            "delivery_target_met": "mean" if "delivery_target_met" in df.columns else lambda x: 0,
            "delivery_duration": "mean" if "delivery_duration" in df.columns else lambda x: 0,
        }).reset_index()

        driver_stats.columns = ["driver_name", "total_deliveries", "on_time_rate", "avg_delivery_time"]

        # Convert to percentage
        driver_stats["on_time_rate"] = (driver_stats["on_time_rate"] * 100).round(1)
        driver_stats["avg_delivery_time"] = driver_stats["avg_delivery_time"].round(1)

        # Sort by on-time rate (descending), then by total deliveries
        driver_stats = driver_stats.sort_values(
            by=["on_time_rate", "total_deliveries"],
            ascending=[False, False]
        ).head(limit)

        # Convert to list of dicts with rank
        result = []
        for idx, row in enumerate(driver_stats.itertuples(), 1):
            result.append({
                "rank": idx,
                "name": row.driver_name,
                "on_time_rate": row.on_time_rate,
                "total_deliveries": int(row.total_deliveries),
                "avg_delivery_time": row.avg_delivery_time,
                "detail": f"{int(row.total_deliveries)} deliveries",
            })

        return result

    def get_chef_leaderboard(self, df: pd.DataFrame, limit: int = 10) -> List[Dict]:
        """
        Get chef leaderboard ranked by average prep time (lower is better).

        Args:
            df: Orders dataframe
            limit: Maximum number of chefs to return

        Returns:
            List of chef stats with rank, name, avg prep time, total orders
        """
        if "chef_name" not in df.columns:
            return []

        # Filter out rows with no chef
        df_chefs = df[df["chef_name"].notna() & (df["chef_name"] != "")]

        if len(df_chefs) == 0:
            return []

        # Calculate total prep time (sum of kitchen stages)
        prep_cols = ["dough_prep_time", "styling_time", "oven_time", "boxing_time"]
        available_cols = [c for c in prep_cols if c in df.columns]

        if not available_cols:
            return []

        df_chefs = df_chefs.copy()
        df_chefs["total_prep_time"] = df_chefs[available_cols].sum(axis=1)

        # Calculate stats per chef
        chef_stats = df_chefs.groupby("chef_name").agg({
            "order_id": "count" if "order_id" in df.columns else lambda x: len(x),
            "total_prep_time": "mean",
        }).reset_index()

        chef_stats.columns = ["chef_name", "total_orders", "avg_prep_time"]
        chef_stats["avg_prep_time"] = chef_stats["avg_prep_time"].round(1)

        # Sort by avg prep time (ascending - lower is better)
        chef_stats = chef_stats.sort_values(
            by=["avg_prep_time", "total_orders"],
            ascending=[True, False]
        ).head(limit)

        # Convert to list of dicts with rank
        result = []
        for idx, row in enumerate(chef_stats.itertuples(), 1):
            result.append({
                "rank": idx,
                "name": row.chef_name,
                "avg_prep_time": row.avg_prep_time,
                "total_orders": int(row.total_orders),
                "detail": f"{int(row.total_orders)} orders",
            })

        return result

    def get_hourly_heatmap_data(self, df: pd.DataFrame, days: int = 7) -> pd.DataFrame:
        """
        Get order volume by hour and day for heatmap visualization.

        Args:
            df: Orders dataframe
            days: Number of recent days to include

        Returns:
            Pivot table with dates as rows, hours as columns, order counts as values
        """
        if "order_date" not in df.columns or "hour_of_day" not in df.columns:
            return pd.DataFrame()

        df = df.copy()
        df["order_date"] = pd.to_datetime(df["order_date"])

        # Get last N days
        max_date = df["order_date"].max()
        min_date = max_date - pd.Timedelta(days=days)
        df_recent = df[df["order_date"] >= min_date].copy()

        if len(df_recent) == 0:
            return pd.DataFrame()

        # Create date string for grouping
        df_recent["date_str"] = df_recent["order_date"].dt.strftime("%Y-%m-%d")

        # Create pivot table
        pivot = df_recent.groupby(["date_str", "hour_of_day"]).size().unstack(fill_value=0)

        # Ensure all hours 0-23 are present
        for hour in range(24):
            if hour not in pivot.columns:
                pivot[hour] = 0
        pivot = pivot.reindex(columns=sorted(pivot.columns))

        return pivot

    def get_performance_radar_data(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate normalized performance scores for radar chart.

        Dimensions:
        1. On-Time Rate (target: 85%)
        2. Low Complaint Rate (target: <5%)
        3. Fast Delivery (target: 30 min)
        4. Kitchen Efficiency (target: 20 min)
        5. Peak Hour Performance (target: no slowdown vs off-peak)
        6. Area Consistency (target: low variance across areas)

        Args:
            df: Orders dataframe

        Returns:
            Dictionary mapping dimension name to score (0-100)
        """
        scores = {}

        # 1. On-Time Rate Score (higher is better)
        if "delivery_target_met" in df.columns:
            on_time_pct = df["delivery_target_met"].mean() * 100
            scores["On-Time Delivery"] = min(100, round(on_time_pct / 85 * 100, 1))
        else:
            scores["On-Time Delivery"] = 50  # Default

        # 2. Low Complaint Rate Score (lower complaints = higher score)
        if "complaint" in df.columns:
            complaint_pct = df["complaint"].mean() * 100
            # 0% complaints = 100 score, 10%+ = 0 score
            scores["Customer Satisfaction"] = max(0, min(100, round((10 - complaint_pct) / 10 * 100, 1)))
        else:
            scores["Customer Satisfaction"] = 50

        # 3. Fast Delivery Score (30 min target)
        if "total_process_time" in df.columns:
            avg_time = df["total_process_time"].mean()
            # 20 min = 100, 40+ min = 0
            scores["Delivery Speed"] = max(0, min(100, round((40 - avg_time) / 20 * 100, 1)))
        else:
            scores["Delivery Speed"] = 50

        # 4. Kitchen Efficiency Score (20 min target for prep)
        prep_cols = ["dough_prep_time", "styling_time", "oven_time", "boxing_time"]
        available_prep = [c for c in prep_cols if c in df.columns]
        if available_prep:
            avg_prep = df[available_prep].sum(axis=1).mean()
            # 15 min = 100, 30+ min = 0
            scores["Kitchen Efficiency"] = max(0, min(100, round((30 - avg_prep) / 15 * 100, 1)))
        else:
            scores["Kitchen Efficiency"] = 50

        # 5. Peak Hour Performance Score
        if "is_peak_hour" in df.columns and "total_process_time" in df.columns:
            peak_avg = df[df["is_peak_hour"] == True]["total_process_time"].mean() if df["is_peak_hour"].any() else 0
            off_peak_avg = df[df["is_peak_hour"] == False]["total_process_time"].mean() if (~df["is_peak_hour"]).any() else 0

            if off_peak_avg > 0 and peak_avg > 0:
                # If peak is same or faster than off-peak = 100, 30%+ slower = 0
                slowdown_pct = (peak_avg - off_peak_avg) / off_peak_avg * 100
                scores["Peak Hour Handling"] = max(0, min(100, round(100 - slowdown_pct * 3.33, 1)))
            else:
                scores["Peak Hour Handling"] = 50
        else:
            scores["Peak Hour Handling"] = 50

        # 6. Area Consistency Score (low variance across areas = higher score)
        if "delivery_area" in df.columns and "total_process_time" in df.columns:
            area_avgs = df.groupby("delivery_area")["total_process_time"].mean()
            if len(area_avgs) > 1:
                cv = area_avgs.std() / area_avgs.mean() * 100 if area_avgs.mean() > 0 else 0
                # CV of 0% = 100 score, CV of 30%+ = 0 score
                scores["Area Consistency"] = max(0, min(100, round((30 - cv) / 30 * 100, 1)))
            else:
                scores["Area Consistency"] = 100  # Only one area = perfect consistency
        else:
            scores["Area Consistency"] = 50

        return scores

    def get_channel_breakdown(self, df: pd.DataFrame) -> List[Dict]:
        """
        Get order breakdown by channel/order mode.

        Args:
            df: Orders dataframe

        Returns:
            List of channel stats with name, count, percentage
        """
        if "order_mode" not in df.columns:
            return []

        total = len(df)
        if total == 0:
            return []

        channel_counts = df["order_mode"].value_counts()

        result = []
        for channel, count in channel_counts.items():
            result.append({
                "name": str(channel).title(),
                "count": int(count),
                "pct": round(count / total * 100, 1),
            })

        return result

    def get_complaint_breakdown(self, df: pd.DataFrame) -> List[Dict]:
        """
        Get complaint breakdown by reason.

        Args:
            df: Orders dataframe

        Returns:
            List of complaint reasons with name, count, percentage of complaints
        """
        if "complaint" not in df.columns:
            return []

        # Filter to only complaints
        df_complaints = df[df["complaint"] == 1]

        if len(df_complaints) == 0:
            return []

        # Check for reason column
        reason_col = None
        for col in ["complaint_reason", "complaint_type", "reason"]:
            if col in df.columns:
                reason_col = col
                break

        if reason_col is None:
            return [{"name": "Unspecified", "count": len(df_complaints), "pct": 100.0}]

        total_complaints = len(df_complaints)
        reason_counts = df_complaints[reason_col].value_counts()

        result = []
        for reason, count in reason_counts.items():
            result.append({
                "name": str(reason) if pd.notna(reason) else "Unspecified",
                "count": int(count),
                "pct": round(count / total_complaints * 100, 1),
            })

        return result


def get_local_analytics() -> LocalAnalytics:
    """
    Get a LocalAnalytics instance.

    Note: Creates a new instance each call to avoid caching issues
    on Streamlit Cloud where code updates may not reflect in cached singletons.
    """
    return LocalAnalytics()
