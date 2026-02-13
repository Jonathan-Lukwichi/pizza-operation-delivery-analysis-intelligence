"""
Page: Executive Dashboard
Purpose: High-level health check for daily operations monitoring
Target User: Store Owner (strategic view)
"""

import streamlit as st
import pandas as pd

from core.kpi_engine import calculate_overview_kpis, complaint_analysis, calculate_trends
from core.alert_rules import generate_alerts, format_alert_for_display
from ui.layout import page_header, section_header, spacer, render_alert
from ui.metrics_cards import render_kpi_card
from ui.charts import line_chart, donut_chart, bar_chart
from ui.filters import render_global_filters, apply_filters, get_filter_summary
from ui.theme import COLORS
from data.transformer import aggregate_by_date


# ── Page Config ──
st.set_page_config(page_title="Executive Dashboard | PizzaOps", page_icon="📊", layout="wide")

page_header(
    title="Executive Dashboard",
    icon="📊",
    description="High-level operational health check - Answer: How is my business doing?"
)

# ── Guard: Check Data Loaded ──
if "df" not in st.session_state or st.session_state.df is None:
    st.warning("⚠️ Please upload data on the Home page first.")
    st.stop()

# ── Load & Filter Data ──
df = st.session_state.df.copy()
filters = render_global_filters(df)
df_filtered = apply_filters(df, filters)

# Show filter summary
filter_summary = get_filter_summary(filters, st.session_state.df, df_filtered)
st.caption(filter_summary)

spacer("1rem")

# ── Calculate KPIs ──
kpis = calculate_overview_kpis(df_filtered)

# ── KPI Row ──
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    render_kpi_card(
        title="Total Orders",
        value=kpis.get("total_orders", 0),
        icon="📦",
        status="neutral"
    )

with col2:
    on_time_pct = kpis.get("on_time_pct", 0)
    trend = calculate_trends(df_filtered, "delivery_target_met")
    delta = f"{trend['change_pct']:+.1f}%" if trend['change_pct'] else None
    render_kpi_card(
        title="On-Time Delivery",
        value=on_time_pct,
        suffix="%",
        delta=delta,
        delta_is_good=True,
        icon="⏱️",
        status=kpis.get("on_time_status", "neutral"),
        target="Target: 85%"
    )

with col3:
    complaint_rate = kpis.get("complaint_rate", 0)
    render_kpi_card(
        title="Complaint Rate",
        value=complaint_rate,
        suffix="%",
        icon="😤",
        status=kpis.get("complaint_status", "neutral"),
        target="Target: <5%"
    )

with col4:
    avg_time = kpis.get("avg_delivery_time", 0)
    render_kpi_card(
        title="Avg Delivery",
        value=avg_time,
        suffix=" min",
        icon="🚚",
        status=kpis.get("avg_delivery_status", "neutral"),
        target="Target: 25 min"
    )

with col5:
    peak_hour = kpis.get("peak_hour")
    peak_load = kpis.get("peak_hour_load", 0)
    render_kpi_card(
        title="Peak Hour Load",
        value=f"{peak_hour}:00" if peak_hour else "N/A",
        icon="🔥",
        status="warning" if peak_load > 30 else "neutral",
        target=f"{peak_load} orders/hr" if peak_load else None
    )

spacer("1.5rem")

# ── Charts Row ──
col1, col2 = st.columns([2, 1])

with col1:
    section_header("Delivery Time Trend", "Daily average delivery time over selected period")

    daily_data = aggregate_by_date(df_filtered, freq='D')
    if len(daily_data) > 0 and "total_process_time" in daily_data.columns:
        fig = line_chart(
            daily_data,
            x="order_date",
            y="total_process_time",
            title="",
            target_line=30,
            color=COLORS["primary"],
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data for trend chart")

with col2:
    section_header("Complaint Breakdown", "Distribution by complaint reason")

    if "complaint" in df_filtered.columns and "complaint_reason" in df_filtered.columns:
        complaint_df = df_filtered[df_filtered["complaint"] == True]
        if len(complaint_df) > 0:
            reason_counts = complaint_df["complaint_reason"].value_counts().reset_index()
            reason_counts.columns = ["reason", "count"]
            reason_counts = reason_counts[reason_counts["reason"].notna()]

            if len(reason_counts) > 0:
                fig = donut_chart(
                    reason_counts,
                    names="reason",
                    values="count",
                    title="",
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No complaint reasons recorded")
        else:
            st.info("No complaints in selected period")
    else:
        st.info("Complaint data not available")

spacer("1rem")

# ── Second Row: Area Performance & Alerts ──
col1, col2 = st.columns([1, 1])

with col1:
    section_header("Orders by Area", "Volume and average delivery time per area")

    if "delivery_area" in df_filtered.columns:
        area_data = df_filtered.groupby("delivery_area").agg({
            "order_id": "count",
            "delivery_duration": "mean" if "delivery_duration" in df_filtered.columns else lambda x: 0
        }).reset_index()
        area_data.columns = ["area", "orders", "avg_delivery"]

        fig = bar_chart(
            area_data,
            x="area",
            y="orders",
            title="",
            show_values=True,
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

        # Show avg delivery time as table
        if "delivery_duration" in df_filtered.columns:
            st.markdown("**Average Delivery Time by Area:**")
            area_time = df_filtered.groupby("delivery_area")["delivery_duration"].mean().round(1)
            cols = st.columns(len(area_time))
            for i, (area, time) in enumerate(area_time.items()):
                color = COLORS["danger"] if time > 35 else COLORS["warning"] if time > 30 else COLORS["success"]
                with cols[i]:
                    st.markdown(f'<div style="text-align:center;padding:0.5rem;"><div style="font-weight:bold;color:{COLORS["text_primary"]};">Area {area}</div><div style="font-size:1.25rem;color:{color};">{time} min</div></div>', unsafe_allow_html=True)

with col2:
    section_header("Today's Alerts", "Issues requiring attention")

    alerts = generate_alerts(df_filtered, kpis)

    if alerts:
        for alert in alerts[:5]:  # Show top 5 alerts
            display = format_alert_for_display(alert)
            st.markdown(f'<div style="background-color:{COLORS["bg_card"]};border-left:4px solid {display["color"]};padding:0.75rem 1rem;border-radius:0 8px 8px 0;margin-bottom:0.5rem;"><div style="color:{display["color"]};font-weight:600;">{display["icon"]} {display["title"]}</div><div style="color:{COLORS["text_secondary"]};font-size:0.875rem;">{display["message"]}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background-color:{COLORS["bg_card"]};border-left:4px solid {COLORS["success"]};padding:1rem;border-radius:0 8px 8px 0;"><div style="color:{COLORS["success"]};font-weight:600;">🟢 All Clear</div><div style="color:{COLORS["text_secondary"]};">No critical alerts at this time</div></div>', unsafe_allow_html=True)

spacer("1.5rem")

# ── Hourly Distribution ──
section_header("Order Volume by Hour", "Identify peak times for staffing optimization")

if "hour_of_day" in df_filtered.columns:
    hourly_data = df_filtered.groupby("hour_of_day").agg({
        "order_id": "count"
    }).reset_index()
    hourly_data.columns = ["hour", "orders"]

    fig = bar_chart(
        hourly_data,
        x="hour",
        y="orders",
        title="",
        color=COLORS["primary"],
        height=250
    )
    st.plotly_chart(fig, use_container_width=True)
