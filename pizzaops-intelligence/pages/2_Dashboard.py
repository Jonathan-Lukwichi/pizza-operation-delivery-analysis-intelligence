"""
Page: Dashboard
Purpose: Quick operational overview - KPIs, trends, alerts
Works: 100% offline (Lite mode)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from core.config import get_config, is_pro_mode
from core.local_analytics import get_local_analytics
from ui.layout import page_header, spacer, footer, render_empty_state
from ui.metrics_cards import render_kpi_card
from ui.theme import COLORS, NEON, apply_plotly_theme
from ui.filters import render_global_filters, apply_filters


# ── Page Config ──
st.set_page_config(page_title="Dashboard | PizzaOps", page_icon="📊", layout="wide")

config = get_config()
page_header(
    title="Dashboard",
    icon="📊",
    description=f"Operational overview for {config.business_name}"
)

# ── Guard: Check Data Loaded ──
if "df" not in st.session_state or st.session_state.df is None:
    render_empty_state(
        title="No Data Available",
        message="Upload your pizza order data to see analytics",
        icon="📊",
        cta_text="Upload Data",
        cta_page="0_Home"
    )
    st.stop()

if not st.session_state.get("data_is_clean", False):
    render_empty_state(
        title="Data Needs Cleaning",
        message="Complete data validation on the Home page first",
        icon="🧹",
        cta_text="Clean Data",
        cta_page="0_Home"
    )
    st.stop()

# ── Load & Filter Data ──
df = st.session_state.df.copy()
filters = render_global_filters(df)
df_filtered = apply_filters(df, filters)

# Get local analytics (works offline)
analytics = get_local_analytics()
kpis = analytics.get_kpis(df_filtered)

# Mode indicator
mode_text = "Pro Mode" if is_pro_mode() else "Lite Mode (Offline)"
st.caption(f"Mode: {mode_text} | {len(df_filtered):,} orders")

spacer("1rem")

# ══════════════════════════════════════════════════════════════════════════════
# NEON KPI CARDS
# ══════════════════════════════════════════════════════════════════════════════
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

spacer("1.5rem")

# ══════════════════════════════════════════════════════════════════════════════
# ALERTS SECTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Alerts")

alerts = analytics.generate_alerts(df_filtered)

if alerts:
    for alert in alerts[:5]:  # Show top 5 alerts
        alert_color = {
            "critical": COLORS["danger"],
            "warning": COLORS["warning"],
            "info": COLORS["info"]
        }.get(alert.level, COLORS["info"])

        alert_icon = {
            "critical": "!!",
            "warning": "!",
            "info": "i"
        }.get(alert.level, "i")

        st.markdown(f"""
        <div style="
            background: {alert_color}10;
            border-left: 4px solid {alert_color};
            padding: 0.75rem 1rem;
            border-radius: 0 8px 8px 0;
            margin-bottom: 0.5rem;
        ">
            <div style="display: flex; align-items: center;">
                <span style="
                    background: {alert_color};
                    color: white;
                    padding: 0.1rem 0.4rem;
                    border-radius: 4px;
                    font-size: 0.7rem;
                    font-weight: bold;
                    margin-right: 0.75rem;
                ">{alert.level.upper()}</span>
                <strong style="color: {COLORS['text_primary']};">{alert.title}</strong>
            </div>
            <p style="color: {COLORS['text_secondary']}; margin: 0.25rem 0 0 0; font-size: 0.875rem;">
                {alert.description}
            </p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.success("No alerts - operations are within targets!")

spacer("1.5rem")

# ══════════════════════════════════════════════════════════════════════════════
# STAGE BREAKDOWN CHART
# ══════════════════════════════════════════════════════════════════════════════
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Stage Performance")

    stage_breakdown = analytics.get_stage_breakdown(df_filtered)

    if stage_breakdown:
        # Get benchmarks from config
        benchmarks = config.get_stage_benchmarks()

        stage_names = list(stage_breakdown.keys())
        stage_values = list(stage_breakdown.values())
        benchmark_values = [benchmarks.get(s.lower().replace(" ", "_") + "_time", v) for s, v in stage_breakdown.items()]

        # Bar chart comparing actual vs benchmark
        fig = go.Figure()

        fig.add_trace(go.Bar(
            name="Actual",
            x=stage_names,
            y=stage_values,
            marker_color=COLORS["primary"]
        ))

        fig.add_trace(go.Bar(
            name="Target",
            x=stage_names,
            y=benchmark_values,
            marker_color=COLORS["text_muted"],
            opacity=0.5
        ))

        fig.update_layout(
            barmode="group",
            height=300,
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        apply_plotly_theme(fig)

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Stage data not available")

with col2:
    st.markdown("### Area Performance")

    area_performance = analytics.get_area_performance(df_filtered)

    if area_performance:
        areas = [a["area"] for a in area_performance]
        times = [a.get("avg_time", 0) for a in area_performance]
        orders = [a.get("orders", 0) for a in area_performance]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=areas,
            y=times,
            text=[f"{t:.1f} min" for t in times],
            textposition="auto",
            marker_color=[
                COLORS["success"] if t <= config.delivery_target_minutes else
                COLORS["warning"] if t <= config.delivery_target_minutes + 5 else
                COLORS["danger"]
                for t in times
            ]
        ))

        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis_title="Delivery Area",
            yaxis_title="Avg Time (min)"
        )
        apply_plotly_theme(fig)

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Area data not available")

spacer("1.5rem")

# ══════════════════════════════════════════════════════════════════════════════
# TREND CHART (Last 7 Days)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### 7-Day Trend")

trend_data = analytics.get_trend_data(df_filtered, days=7)

if trend_data["dates"]:
    fig = go.Figure()

    # Orders line
    fig.add_trace(go.Scatter(
        x=trend_data["dates"],
        y=trend_data["orders"],
        mode="lines+markers",
        name="Orders",
        line=dict(color=COLORS["primary"], width=2),
        yaxis="y"
    ))

    # On-time rate line
    if trend_data["on_time"]:
        fig.add_trace(go.Scatter(
            x=trend_data["dates"],
            y=trend_data["on_time"],
            mode="lines+markers",
            name="On-Time %",
            line=dict(color=COLORS["success"], width=2, dash="dash"),
            yaxis="y2"
        ))

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=60, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        yaxis=dict(title="Orders"),
        yaxis2=dict(title="On-Time %", overlaying="y", side="right", range=[0, 100]),
    )
    apply_plotly_theme(fig)

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Not enough data for trend analysis")

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
spacer("2rem")
st.markdown(f"""
<div style="
    text-align: center;
    padding: 1.5rem;
    border-top: 1px solid rgba(59, 130, 246, 0.15);
">
    <p style="color: {COLORS['primary']}; font-size: 0.85rem; margin: 0 0 0.25rem 0;">
        Dashboard powered by LocalAnalytics - works offline!
    </p>
    <p style="color: {COLORS['text_muted']}; font-size: 0.8rem; margin: 0;">
        Use the sidebar to switch between Lite and Pro modes.
    </p>
</div>
""", unsafe_allow_html=True)
