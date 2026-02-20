"""
Page: Dashboard
Purpose: Comprehensive operational dashboard with KPIs, trends, alerts, and leaderboards
Works: 100% offline (Lite mode)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os
from datetime import datetime

# Add project root to path for Streamlit Cloud
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import get_config
from core.local_analytics import get_local_analytics
from ui.layout import (
    spacer, render_empty_state, render_section_title, inject_custom_css,
    render_hero_header, render_alert_card, render_stage_bar,
    render_leaderboard, render_channel_stats, render_complaint_breakdown
)
from ui.metrics_cards import render_kpi_card
from ui.theme import COLORS, apply_plotly_theme
from ui.filters import render_global_filters, apply_filters
from ui.charts import (
    dual_axis_trend_chart, hourly_heatmap_chart, stage_comparison_chart,
    performance_radar_chart, hourly_volume_chart, area_ontime_chart
)


# ── Page Config ──
st.set_page_config(page_title="Dashboard | PizzaOps", page_icon="📊", layout="wide")

config = get_config()

# Inject CSS first
inject_custom_css()


# ── Guard: Check Data Loaded ──
if "df" not in st.session_state or st.session_state.df is None:
    render_empty_state(
        title="No Data Available",
        message="Upload your pizza order data to see analytics",
        icon="📊",
        cta_text="Upload Data",
        cta_page="1_Home"
    )
    st.stop()

if not st.session_state.get("data_is_clean", False):
    render_empty_state(
        title="Data Needs Cleaning",
        message="Complete data validation on the Home page first",
        icon="🧹",
        cta_text="Clean Data",
        cta_page="1_Home"
    )
    st.stop()


# ── Load & Filter Data ──
df = st.session_state.df.copy()
filters = render_global_filters(df)
df_filtered = apply_filters(df, filters)

# Get local analytics (works offline)
analytics = get_local_analytics()
kpis = analytics.get_kpis(df_filtered)

# Get today's date string
today_str = datetime.now().strftime("%B %d, %Y")

# Calculate today's orders if date column exists
today_orders = 0
if "order_date" in df_filtered.columns:
    df_temp = df_filtered.copy()
    df_temp["order_date"] = pd.to_datetime(df_temp["order_date"])
    today = pd.Timestamp.now().normalize()
    today_orders = len(df_temp[df_temp["order_date"].dt.normalize() == today])


# ══════════════════════════════════════════════════════════════════════════════
# HERO HEADER
# ══════════════════════════════════════════════════════════════════════════════
render_hero_header(
    title="Daily Performance Dashboard",
    subtitle="Real-time operations analytics for your pizza delivery business",
    today_str=today_str,
    total_records=len(df_filtered),
    today_orders=today_orders
)

spacer("1rem")


# ══════════════════════════════════════════════════════════════════════════════
# KEY PERFORMANCE INDICATORS - 8 KPIs in 2 rows
# ══════════════════════════════════════════════════════════════════════════════
render_section_title("Key Metrics", "Real-time operational KPIs", "📊")

# Row 1: 4 KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    render_kpi_card(
        title="Total Orders",
        value=kpis.total_orders,
        icon="📦",
        status="neutral"
    )

with col2:
    on_time_status = "good" if kpis.on_time_rate >= config.on_time_target_pct else (
        "warning" if kpis.on_time_rate >= config.on_time_target_pct - 10 else "danger"
    )
    render_kpi_card(
        title="On-Time Rate",
        value=kpis.on_time_rate,
        suffix="%",
        icon="⏱️",
        status=on_time_status,
        target=f"Target: {config.on_time_target_pct}%"
    )

with col3:
    complaint_status = "good" if kpis.complaint_rate < config.complaint_target_pct else (
        "warning" if kpis.complaint_rate < config.complaint_target_pct + 5 else "danger"
    )
    render_kpi_card(
        title="Complaint Rate",
        value=kpis.complaint_rate,
        suffix="%",
        icon="⚠️",
        status=complaint_status,
        target=f"Target: <{config.complaint_target_pct}%"
    )

with col4:
    time_status = "good" if kpis.avg_delivery_time <= config.delivery_target_minutes else (
        "warning" if kpis.avg_delivery_time <= config.delivery_target_minutes + 5 else "danger"
    )
    render_kpi_card(
        title="Avg Delivery",
        value=kpis.avg_delivery_time,
        suffix=" min",
        icon="🚚",
        status=time_status,
        target=f"Target: {config.delivery_target_minutes} min"
    )

# Row 2: 4 more KPIs
col5, col6, col7, col8 = st.columns(4)

# Get stage breakdown for additional KPIs
stage_breakdown = analytics.get_stage_breakdown(df_filtered)

with col5:
    prep_time = stage_breakdown.get("Dough Prep", 0) + stage_breakdown.get("Styling", 0)
    render_kpi_card(
        title="Prep Time",
        value=round(prep_time, 1),
        suffix=" min",
        icon="👨‍🍳",
        status="good" if prep_time <= 8 else ("warning" if prep_time <= 10 else "danger"),
        target="Target: <8 min"
    )

with col6:
    oven_time = stage_breakdown.get("Oven", 0)
    render_kpi_card(
        title="Oven Time",
        value=round(oven_time, 1),
        suffix=" min",
        icon="🔥",
        status="good" if oven_time <= 10 else ("warning" if oven_time <= 12 else "danger"),
        target="Target: <10 min"
    )

with col7:
    boxing_time = stage_breakdown.get("Boxing", 0)
    render_kpi_card(
        title="Boxing Time",
        value=round(boxing_time, 1),
        suffix=" min",
        icon="📦",
        status="good" if boxing_time <= 2 else ("warning" if boxing_time <= 3 else "danger"),
        target="Target: <2 min"
    )

with col8:
    delivery_time = stage_breakdown.get("Delivery", 0)
    render_kpi_card(
        title="Delivery Time",
        value=round(delivery_time, 1),
        suffix=" min",
        icon="🛵",
        status="good" if delivery_time <= 10 else ("warning" if delivery_time <= 15 else "danger"),
        target="Target: <10 min"
    )

spacer("1.5rem")


# ══════════════════════════════════════════════════════════════════════════════
# TABBED SECTIONS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Trends & Alerts",
    "⚙️ Stage Analysis",
    "🗺️ Area Performance",
    "🏆 Leaderboard"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: TRENDS & ALERTS
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    spacer("1rem")

    col_trend, col_alerts = st.columns([2, 1])

    with col_trend:
        render_section_title("30-Day Performance Trend", "Orders volume and on-time delivery rate")

        trend_data = analytics.get_trend_data(df_filtered, days=30)

        if trend_data["dates"] and len(trend_data["dates"]) > 0:
            # Create DataFrame for the chart
            trend_df = pd.DataFrame({
                "date": trend_data["dates"],
                "orders": trend_data["orders"],
                "on_time_pct": trend_data["on_time"]
            })

            fig = dual_axis_trend_chart(
                df=trend_df,
                x="date",
                y_bar="orders",
                y_line="on_time_pct",
                title="",
                y_bar_name="Orders",
                y_line_name="On-Time %",
                target_line=config.on_time_target_pct,
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data for trend analysis")

    with col_alerts:
        # Alerts Section
        render_section_title("Active Alerts", "Issues requiring attention", "🔔")

        alerts = analytics.generate_alerts(df_filtered)

        if alerts:
            for alert in alerts[:3]:  # Show top 3 alerts
                severity_map = {"critical": "danger", "warning": "warning", "info": "info"}
                icon_map = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}
                render_alert_card(
                    icon=icon_map.get(alert.level, "ℹ️"),
                    title=alert.title,
                    description=alert.description,
                    severity=severity_map.get(alert.level, "info")
                )
        else:
            st.success("All systems operational - no alerts!")

        spacer("1rem")

        # Order Channels
        render_section_title("Order Channels", "Distribution by source", "📱")

        channel_data = analytics.get_channel_breakdown(df_filtered)
        if channel_data:
            render_channel_stats(channel_data)
        else:
            st.info("Order mode data not available")

        spacer("1rem")

        # Complaint Breakdown
        render_section_title("Complaint Reasons", "Top issues", "📋")

        complaint_data = analytics.get_complaint_breakdown(df_filtered)
        if complaint_data:
            render_complaint_breakdown(complaint_data[:5])  # Top 5 reasons
        else:
            st.success("No complaints recorded!")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: STAGE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    spacer("1rem")

    col_stages, col_heatmap = st.columns(2)

    with col_stages:
        render_section_title("Stage Performance", "Actual vs benchmark times", "⏱️")

        if stage_breakdown:
            benchmarks = config.get_stage_benchmarks()

            # Map stage names to benchmark keys
            stage_map = {
                "Dough Prep": "dough_prep_time",
                "Styling": "styling_time",
                "Oven": "oven_time",
                "Boxing": "boxing_time",
                "Delivery": "delivery_duration"
            }

            for stage_name, stage_time in stage_breakdown.items():
                bench_key = stage_map.get(stage_name, "")
                bench_value = benchmarks.get(bench_key, stage_time)
                render_stage_bar(stage_name, stage_time, bench_value)

            spacer("1rem")

            # Stage comparison chart
            fig = stage_comparison_chart(
                stage_names=list(stage_breakdown.keys()),
                actuals=list(stage_breakdown.values()),
                benchmarks=[benchmarks.get(stage_map.get(s, ""), v) for s, v in stage_breakdown.items()],
                title="Stage Time Comparison",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Stage data not available")

    with col_heatmap:
        render_section_title("Hourly Order Heatmap", "Order volume by day and hour", "🗓️")

        heatmap_data = analytics.get_hourly_heatmap_data(df_filtered, days=7)

        if not heatmap_data.empty:
            fig = hourly_heatmap_chart(
                df=heatmap_data,
                date_col=None,  # Already pivoted
                hour_col=None,
                title="",
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data for heatmap")

        spacer("1rem")

        # Hourly volume chart
        render_section_title("Orders by Hour", "Peak hour identification", "📊")

        if "hour_of_day" in df_filtered.columns:
            fig = hourly_volume_chart(
                df=df_filtered,
                hour_col="hour_of_day",
                title="",
                height=250
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Hour data not available")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: AREA PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    spacer("1rem")

    area_performance = analytics.get_area_performance(df_filtered)

    if area_performance:
        col_ontime, col_volume = st.columns(2)

        with col_ontime:
            render_section_title("On-Time Rate by Area", "Performance vs target", "🎯")

            if "delivery_area" in df_filtered.columns and "delivery_target_met" in df_filtered.columns:
                fig = area_ontime_chart(
                    df=df_filtered,
                    area_col="delivery_area",
                    ontime_col="delivery_target_met",
                    target=config.on_time_target_pct,
                    title="",
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("On-time data not available")

        with col_volume:
            render_section_title("Order Volume by Area", "Distribution analysis", "📊")

            areas = [a["area"] for a in area_performance]
            orders = [a.get("orders", 0) for a in area_performance]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=areas,
                y=orders,
                text=orders,
                textposition="auto",
                marker_color=COLORS["primary"]
            ))
            fig.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=20, b=40),
                xaxis_title="Delivery Area",
                yaxis_title="Order Count"
            )
            apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

        spacer("1rem")

        # Area details table
        render_section_title("Area Performance Details", "Complete breakdown", "📋")

        area_df = pd.DataFrame(area_performance)
        if not area_df.empty:
            # Format columns
            display_cols = {
                "area": "Area",
                "orders": "Orders",
                "avg_time": "Avg Time (min)",
                "on_time_rate": "On-Time %",
                "complaint_rate": "Complaint %"
            }
            available_cols = [c for c in display_cols.keys() if c in area_df.columns]
            area_df = area_df[available_cols].rename(columns=display_cols)
            st.dataframe(area_df, use_container_width=True, hide_index=True)
    else:
        st.info("Area data not available - ensure 'delivery_area' column exists")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4: LEADERBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    spacer("1rem")

    col_drivers, col_chefs = st.columns(2)

    with col_drivers:
        render_section_title("Driver Leaderboard", "Ranked by on-time delivery rate", "🚗")

        driver_data = analytics.get_driver_leaderboard(df_filtered, limit=10)

        if driver_data:
            # Format for leaderboard component
            driver_rows = [
                {
                    "rank": d["rank"],
                    "name": d["name"],
                    "value": f"{d['on_time_rate']}%",
                    "detail": d["detail"],
                    "progress": d["on_time_rate"]
                }
                for d in driver_data
            ]
            render_leaderboard("Top Drivers", "By on-time rate", driver_rows)
        else:
            st.info("Driver data not available - ensure 'driver_name' column exists")

    with col_chefs:
        render_section_title("Chef Leaderboard", "Ranked by average prep time", "👨‍🍳")

        chef_data = analytics.get_chef_leaderboard(df_filtered, limit=10)

        if chef_data:
            # For chefs, lower time is better - invert progress
            max_time = max(c["avg_prep_time"] for c in chef_data) if chef_data else 30
            chef_rows = [
                {
                    "rank": c["rank"],
                    "name": c["name"],
                    "value": f"{c['avg_prep_time']} min",
                    "detail": c["detail"],
                    "progress": max(0, 100 - (c["avg_prep_time"] / max_time * 100))  # Invert: faster = higher bar
                }
                for c in chef_data
            ]
            render_leaderboard("Top Chefs", "By prep efficiency", chef_rows)
        else:
            st.info("Chef data not available - ensure 'chef_name' column exists")

    spacer("1.5rem")

    # Performance Radar Chart
    render_section_title("Performance Radar", "Multi-dimensional performance score", "🎯")

    radar_data = analytics.get_performance_radar_data(df_filtered)

    if radar_data:
        fig = performance_radar_chart(
            categories=list(radar_data.keys()),
            values=list(radar_data.values()),
            target=80,  # Target line at 80%
            title="Overall Performance Score",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        # Performance summary
        avg_score = sum(radar_data.values()) / len(radar_data) if radar_data else 0
        score_color = COLORS["success"] if avg_score >= 80 else (COLORS["warning"] if avg_score >= 60 else COLORS["danger"])

        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: rgba(10, 25, 60, 0.6); border-radius: 12px; border: 1px solid rgba(0, 180, 255, 0.15);">
            <p style="color: {COLORS['text_muted']}; margin: 0 0 0.5rem 0; font-size: 0.9rem;">Overall Performance Score</p>
            <p style="color: {score_color}; font-size: 2.5rem; font-weight: 700; margin: 0;">{avg_score:.0f}%</p>
            <p style="color: {COLORS['text_secondary']}; margin: 0.5rem 0 0 0; font-size: 0.85rem;">Based on 6 performance dimensions</p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
spacer("2rem")
st.markdown(f'''
<div style="text-align: center; padding: 2rem; border-top: 1px solid rgba(0, 180, 255, 0.15); position: relative;">
    <div style="position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 60px; height: 3px; background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["secondary"]}); border-radius: 2px;"></div>
    <p style="color: {COLORS['primary']}; font-size: 0.85rem; margin: 0 0 0.5rem 0; font-weight: 500;">Powered by Local Analytics Engine</p>
    <p style="color: {COLORS['text_muted']}; font-size: 0.75rem; margin: 0;">Navigate to <strong style="color: {COLORS["text_secondary"]};">Problems</strong> or <strong style="color: {COLORS["text_secondary"]};">Actions</strong> for deeper insights</p>
</div>
''', unsafe_allow_html=True)
