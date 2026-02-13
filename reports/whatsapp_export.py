"""
WhatsApp Export
===============

Generate simple text summaries for WhatsApp sharing.
Optimized for South African market - mobile-first sharing.
"""

from datetime import datetime
from typing import List, Optional
import pandas as pd
import streamlit as st

# Import local analytics
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.local_analytics import get_local_analytics
except ImportError:
    # Fallback if import fails
    get_local_analytics = None


def generate_whatsapp_summary(
    df: pd.DataFrame,
    include_bottlenecks: bool = True,
    include_recommendations: bool = True,
    custom_header: str = None
) -> str:
    """
    Generate a plain text summary for WhatsApp sharing.

    Args:
        df: Orders dataframe
        include_bottlenecks: Include top issues
        include_recommendations: Include quick actions
        custom_header: Optional custom header text

    Returns:
        Plain text summary formatted for WhatsApp
    """
    # Get analytics
    if get_local_analytics:
        analytics = get_local_analytics()
        kpis = analytics.get_kpis(df)
        bottlenecks = analytics.detect_bottlenecks(df) if include_bottlenecks else []
        recommendations = analytics.generate_recommendations(df) if include_recommendations else []
    else:
        # Fallback calculations
        kpis = _calculate_basic_kpis(df)
        bottlenecks = []
        recommendations = []

    # Build summary
    lines = []

    # Header
    header = custom_header or "DAILY OPERATIONS SUMMARY"
    lines.append(f"*{header}*")
    lines.append(datetime.now().strftime('%d %B %Y'))
    lines.append("")

    # KPI Section
    lines.append("*KEY METRICS*")

    # Total orders
    lines.append(f"Total Orders: {kpis.total_orders:,}")

    # On-time rate with status
    on_time_icon = "OK" if kpis.on_time_rate >= 85 else "LOW"
    lines.append(f"On-Time Rate: {kpis.on_time_rate:.1f}% [{on_time_icon}]")

    # Complaint rate with status
    complaint_icon = "OK" if kpis.complaint_rate < 5 else "HIGH"
    lines.append(f"Complaints: {kpis.complaint_rate:.1f}% [{complaint_icon}]")

    # Average delivery time
    time_icon = "OK" if kpis.avg_delivery_time <= 30 else "SLOW"
    lines.append(f"Avg Time: {kpis.avg_delivery_time:.0f} min [{time_icon}]")

    lines.append("")

    # Bottlenecks section
    if bottlenecks and include_bottlenecks:
        lines.append("*TOP ISSUES*")
        for i, b in enumerate(bottlenecks[:3], 1):
            severity_icon = {
                "critical": "!!",
                "high": "!",
                "medium": "-",
                "low": "."
            }.get(b.severity, "-")
            lines.append(f"{i}. {b.area} {severity_icon}")
            lines.append(f"   {b.current_value} min (target: {b.benchmark})")
        lines.append("")

    # Recommendations section
    if recommendations and include_recommendations:
        lines.append("*QUICK ACTIONS*")
        for i, rec in enumerate(recommendations[:3], 1):
            priority_icon = {
                "high": "[HIGH]",
                "medium": "[MED]",
                "quick_win": "[QUICK]"
            }.get(rec.get("priority", "medium"), "")
            lines.append(f"{i}. {priority_icon} {rec.get('title', '')}")
            lines.append(f"   {rec.get('action', '')[:60]}")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append("_PizzaOps Intelligence_")
    lines.append("_by JLWanalytics_")

    return "\n".join(lines)


def generate_alert_message(
    df: pd.DataFrame,
    alert_type: str = "general"
) -> str:
    """
    Generate an alert message for WhatsApp.

    Args:
        df: Orders dataframe
        alert_type: Type of alert (general, critical, daily_report)

    Returns:
        Alert message text
    """
    if get_local_analytics:
        analytics = get_local_analytics()
        alerts = analytics.generate_alerts(df)
        kpis = analytics.get_kpis(df)
    else:
        return "Unable to generate alert - analytics not available"

    lines = []

    if alert_type == "critical":
        # Only critical alerts
        critical_alerts = [a for a in alerts if a.level == "critical"]
        if not critical_alerts:
            return "No critical alerts at this time."

        lines.append("*!! CRITICAL ALERT !!*")
        lines.append("")
        for alert in critical_alerts:
            lines.append(f"- {alert.title}")
            lines.append(f"  {alert.description}")
        lines.append("")
        lines.append(f"Time: {datetime.now().strftime('%H:%M')}")

    elif alert_type == "daily_report":
        # Full daily report
        lines.append("*DAILY PERFORMANCE REPORT*")
        lines.append(datetime.now().strftime('%A, %d %B %Y'))
        lines.append("")
        lines.append(f"Orders: {kpis.total_orders}")
        lines.append(f"On-Time: {kpis.on_time_rate}%")
        lines.append(f"Complaints: {kpis.complaint_rate}%")
        lines.append(f"Avg Time: {kpis.avg_delivery_time} min")
        lines.append("")

        if alerts:
            lines.append("*Alerts:*")
            for alert in alerts[:5]:
                level_icon = {"critical": "!!", "warning": "!", "info": "i"}.get(alert.level, "-")
                lines.append(f"[{level_icon}] {alert.title}")
        else:
            lines.append("No alerts today")

    else:
        # General summary
        lines.append("*OPERATIONS UPDATE*")
        lines.append(f"Time: {datetime.now().strftime('%H:%M')}")
        lines.append("")
        lines.append(f"On-Time: {kpis.on_time_rate}%")
        lines.append(f"Complaints: {kpis.complaint_rate}%")

        if alerts:
            lines.append("")
            lines.append(f"Alerts: {len(alerts)}")

    return "\n".join(lines)


def generate_staff_summary(df: pd.DataFrame) -> str:
    """
    Generate a staff performance summary for WhatsApp.

    Args:
        df: Orders dataframe

    Returns:
        Staff summary text
    """
    lines = []
    lines.append("*STAFF PERFORMANCE*")
    lines.append(datetime.now().strftime('%d %B %Y'))
    lines.append("")

    # Chef performance
    if "chef_name" in df.columns and "total_process_time" in df.columns:
        lines.append("*Chefs (Avg Time):*")
        chef_stats = df.groupby("chef_name")["total_process_time"].agg(["mean", "count"]).sort_values("mean")
        for chef, row in chef_stats.head(5).iterrows():
            lines.append(f"- {chef}: {row['mean']:.1f} min ({int(row['count'])} orders)")
        lines.append("")

    # Driver performance
    if "driver_name" in df.columns and "delivery_duration" in df.columns:
        lines.append("*Drivers (Avg Delivery):*")
        driver_stats = df.groupby("driver_name")["delivery_duration"].agg(["mean", "count"]).sort_values("mean")
        for driver, row in driver_stats.head(5).iterrows():
            lines.append(f"- {driver}: {row['mean']:.1f} min ({int(row['count'])} deliveries)")

    return "\n".join(lines)


def _calculate_basic_kpis(df: pd.DataFrame):
    """Fallback KPI calculation if analytics module unavailable."""
    class BasicKPIs:
        total_orders = len(df)
        on_time_rate = df["delivery_target_met"].mean() * 100 if "delivery_target_met" in df.columns else 0
        complaint_rate = df["complaint"].mean() * 100 if "complaint" in df.columns else 0
        avg_delivery_time = df["total_process_time"].mean() if "total_process_time" in df.columns else 0

    return BasicKPIs()


def render_whatsapp_export_section(df: pd.DataFrame):
    """
    Render the WhatsApp export section in Streamlit.

    Args:
        df: Orders dataframe
    """
    st.markdown("### Share via WhatsApp")
    st.markdown("Generate a text summary to share with your team.")

    # Options
    col1, col2 = st.columns(2)
    with col1:
        include_issues = st.checkbox("Include Top Issues", value=True)
    with col2:
        include_actions = st.checkbox("Include Quick Actions", value=True)

    # Summary type
    summary_type = st.radio(
        "Summary Type",
        ["General Summary", "Daily Report", "Staff Performance"],
        horizontal=True
    )

    # Generate button
    if st.button("Generate Summary", type="primary", use_container_width=True):
        if summary_type == "General Summary":
            summary = generate_whatsapp_summary(df, include_issues, include_actions)
        elif summary_type == "Daily Report":
            summary = generate_alert_message(df, "daily_report")
        else:
            summary = generate_staff_summary(df)

        st.session_state.whatsapp_summary = summary

    # Display summary if available
    if "whatsapp_summary" in st.session_state:
        st.text_area(
            "Copy this text:",
            st.session_state.whatsapp_summary,
            height=300,
            key="whatsapp_text"
        )

        # Copy button (uses clipboard API via JS)
        st.markdown("""
        <p style="font-size: 0.8rem; color: #666;">
        Select all text above (Ctrl+A) and copy (Ctrl+C), then paste in WhatsApp.
        </p>
        """, unsafe_allow_html=True)

        # Clear button
        if st.button("Clear", key="clear_whatsapp"):
            del st.session_state.whatsapp_summary
            st.rerun()
