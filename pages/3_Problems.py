"""
Page: Problems
Purpose: Identify bottlenecks, performance gaps, and issues
Works: Offline (Lite mode) with optional AI enhancement (Pro mode)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add project root to path for Streamlit Cloud
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import get_config, is_pro_mode
from core.local_analytics import get_local_analytics
from ui.layout import page_header, spacer, render_empty_state
from ui.theme import COLORS, NEON, apply_plotly_theme
from ui.filters import render_global_filters, apply_filters

# Try to import AI components (for Pro mode)
try:
    from ai.business_analyst import get_business_analyst_agent
    from ai.budget_tracker import get_budget_tracker, check_budget_before_query
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


# ── Page Config ──
st.set_page_config(page_title="Problems | PizzaOps", page_icon="🔍", layout="wide")

config = get_config()
page_header(
    title="Problems & Issues",
    icon="🔍",
    description="Identify bottlenecks, performance gaps, and root causes"
)

# ── Guard: Check Data Loaded ──
if "df" not in st.session_state or st.session_state.df is None:
    render_empty_state(
        title="No Problems to Display",
        message="Upload data to identify operational issues",
        icon="🔍",
        cta_text="Upload Data",
        cta_page="0_Home"
    )
    st.stop()

if not st.session_state.get("data_is_clean", False):
    render_empty_state(
        title="Data Needs Cleaning",
        message="Complete data validation to analyze problems",
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

# Mode indicator
mode_text = "Pro Mode (AI Available)" if is_pro_mode() else "Lite Mode (Offline)"
st.caption(f"Mode: {mode_text} | Analyzing {len(df_filtered):,} orders")

spacer("1rem")

# ══════════════════════════════════════════════════════════════════════════════
# BOTTLENECKS SECTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Pipeline Bottlenecks")
st.markdown("Stages that are slower than benchmarks:")

bottlenecks = analytics.detect_bottlenecks(df_filtered)

if bottlenecks:
    for i, bottleneck in enumerate(bottlenecks):
        severity_color = {
            "critical": COLORS["danger"],
            "high": COLORS["danger"],
            "medium": COLORS["warning"],
            "low": COLORS["success"]
        }.get(bottleneck.severity, COLORS["warning"])

        rank_icon = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i] if i < 5 else "📌"

        with st.expander(f"{rank_icon} {bottleneck.area} - {bottleneck.severity.upper()}", expanded=i < 2):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Current",
                    f"{bottleneck.current_value:.1f} min",
                    delta=f"+{bottleneck.variance_pct:.0f}%",
                    delta_color="inverse"
                )

            with col2:
                st.metric("Benchmark", f"{bottleneck.benchmark:.1f} min")

            with col3:
                st.markdown(f"""
                <div style="
                    background: {severity_color}20;
                    padding: 0.5rem;
                    border-radius: 8px;
                    text-align: center;
                ">
                    <span style="color: {severity_color}; font-weight: bold;">
                        {bottleneck.severity.upper()}
                    </span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"**Impact:** {bottleneck.impact_description}")
            st.markdown(f"**Suggested Action:** {bottleneck.suggested_action}")
else:
    st.success("No significant bottlenecks detected - all stages within benchmarks!")

spacer("1.5rem")

# ══════════════════════════════════════════════════════════════════════════════
# AREA PERFORMANCE ISSUES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Area Performance Issues")

area_performance = analytics.get_area_performance(df_filtered)

if area_performance:
    # Identify problem areas (above average)
    overall_avg = sum(a.get("avg_time", 0) for a in area_performance) / len(area_performance) if area_performance else 0
    problem_areas = [a for a in area_performance if a.get("avg_time", 0) > overall_avg * 1.1]

    if problem_areas:
        for area in problem_areas:
            area_name = area["area"]
            avg_time = area.get("avg_time", 0)
            on_time_rate = area.get("on_time_rate", 0)
            complaint_rate = area.get("complaint_rate", 0)
            orders = area.get("orders", 0)

            variance = ((avg_time - overall_avg) / overall_avg) * 100 if overall_avg > 0 else 0

            st.markdown(f"""
            <div style="
                background: {COLORS['warning']}10;
                border-left: 4px solid {COLORS['warning']};
                padding: 1rem;
                border-radius: 0 8px 8px 0;
                margin-bottom: 0.75rem;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="color: {COLORS['text_primary']}; font-size: 1.1rem;">
                        Area {area_name}
                    </strong>
                    <span style="color: {COLORS['warning']}; font-size: 0.8rem;">
                        {variance:.0f}% above average
                    </span>
                </div>
                <div style="display: flex; gap: 2rem; margin-top: 0.75rem;">
                    <div>
                        <span style="color: {COLORS['text_muted']}; font-size: 0.8rem;">Avg Time</span>
                        <p style="color: {COLORS['text_primary']}; margin: 0; font-weight: bold;">{avg_time:.1f} min</p>
                    </div>
                    <div>
                        <span style="color: {COLORS['text_muted']}; font-size: 0.8rem;">On-Time</span>
                        <p style="color: {COLORS['text_primary']}; margin: 0; font-weight: bold;">{on_time_rate:.1f}%</p>
                    </div>
                    <div>
                        <span style="color: {COLORS['text_muted']}; font-size: 0.8rem;">Complaints</span>
                        <p style="color: {COLORS['text_primary']}; margin: 0; font-weight: bold;">{complaint_rate:.1f}%</p>
                    </div>
                    <div>
                        <span style="color: {COLORS['text_muted']}; font-size: 0.8rem;">Orders</span>
                        <p style="color: {COLORS['text_primary']}; margin: 0; font-weight: bold;">{orders}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("All delivery areas performing within acceptable range!")

    # Area comparison chart
    with st.expander("View Area Comparison Chart"):
        areas = [a["area"] for a in area_performance]
        times = [a.get("avg_time", 0) for a in area_performance]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=areas,
            y=times,
            text=[f"{t:.1f}" for t in times],
            textposition="auto",
            marker_color=[
                COLORS["danger"] if t > config.delivery_target_minutes + 5 else
                COLORS["warning"] if t > config.delivery_target_minutes else
                COLORS["success"]
                for t in times
            ]
        ))

        # Add benchmark line
        fig.add_hline(
            y=config.delivery_target_minutes,
            line_dash="dash",
            line_color=COLORS["text_muted"],
            annotation_text=f"Target: {config.delivery_target_minutes} min"
        )

        fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
        apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Area performance data not available")

spacer("1.5rem")

# ══════════════════════════════════════════════════════════════════════════════
# STAFF PERFORMANCE GAPS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Staff Performance Gaps")

# Check for staff columns
staff_cols = ["chef_name", "driver_name", "delivery_driver", "dough_prep_staff", "stylist", "oven_operator"]
available_staff_cols = [col for col in staff_cols if col in df_filtered.columns]

if available_staff_cols and "total_process_time" in df_filtered.columns:
    tabs = st.tabs([col.replace("_", " ").title() for col in available_staff_cols[:3]])

    for i, col in enumerate(available_staff_cols[:3]):
        with tabs[i]:
            staff_stats = df_filtered.groupby(col)["total_process_time"].agg(["mean", "count", "std"]).reset_index()
            staff_stats = staff_stats[staff_stats["count"] >= 5]  # Min 5 orders
            staff_stats = staff_stats.sort_values("mean")

            if len(staff_stats) >= 2:
                best = staff_stats.iloc[0]
                worst = staff_stats.iloc[-1]
                gap = worst["mean"] - best["mean"]

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"""
                    <div style="
                        background: {COLORS['success']}15;
                        border: 1px solid {COLORS['success']}30;
                        border-radius: 8px;
                        padding: 1rem;
                    ">
                        <span style="color: {COLORS['success']}; font-size: 0.8rem;">TOP PERFORMER</span>
                        <h4 style="color: {COLORS['text_primary']}; margin: 0.5rem 0;">{best[col]}</h4>
                        <p style="color: {COLORS['text_secondary']}; margin: 0;">
                            {best['mean']:.1f} min avg | {int(best['count'])} orders
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div style="
                        background: {COLORS['warning']}15;
                        border: 1px solid {COLORS['warning']}30;
                        border-radius: 8px;
                        padding: 1rem;
                    ">
                        <span style="color: {COLORS['warning']}; font-size: 0.8rem;">NEEDS IMPROVEMENT</span>
                        <h4 style="color: {COLORS['text_primary']}; margin: 0.5rem 0;">{worst[col]}</h4>
                        <p style="color: {COLORS['text_secondary']}; margin: 0;">
                            {worst['mean']:.1f} min avg | {int(worst['count'])} orders
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                if gap > 5:
                    st.warning(f"Performance gap of {gap:.1f} minutes. Consider training program.")
            else:
                st.info("Not enough data for staff comparison")
else:
    st.info("Staff performance data not available")

spacer("1.5rem")

# ══════════════════════════════════════════════════════════════════════════════
# COMPLAINT PATTERNS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Complaint Patterns")

if "complaint" in df_filtered.columns:
    kpis = analytics.get_kpis(df_filtered)
    complaint_count = int(df_filtered["complaint"].sum())
    complaint_rate = kpis.complaint_rate

    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric("Total Complaints", complaint_count)
        st.metric("Complaint Rate", f"{complaint_rate:.1f}%")

        if complaint_rate > config.complaint_target_pct:
            st.error(f"Above target ({config.complaint_target_pct}%)")
        else:
            st.success(f"Within target ({config.complaint_target_pct}%)")

    with col2:
        if "complaint_reason" in df_filtered.columns:
            # Complaint reasons breakdown
            reasons = df_filtered[df_filtered["complaint"] == 1]["complaint_reason"].value_counts()

            if len(reasons) > 0:
                fig = px.pie(
                    values=reasons.values,
                    names=reasons.index,
                    title="Complaint Reasons",
                    hole=0.4
                )
                fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
                apply_plotly_theme(fig)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Complaint reason breakdown not available")
else:
    st.info("Complaint data not available")

spacer("1.5rem")

# ══════════════════════════════════════════════════════════════════════════════
# PRO MODE: AI DEEP DIVE
# ══════════════════════════════════════════════════════════════════════════════
if is_pro_mode() and AI_AVAILABLE:
    st.markdown("---")
    st.markdown("### AI Deep Dive Analysis")
    st.markdown("Get AI-powered root cause analysis and insights")

    if check_budget_before_query("operations_analysis"):
        if st.button("🤖 Run AI Analysis", type="primary", use_container_width=True):
            with st.spinner("AI is analyzing root causes..."):
                try:
                    agent = get_business_analyst_agent()
                    result = agent.analyze(df_filtered)

                    if result.success:
                        st.markdown(f"""
                        <div style="
                            background: {COLORS['bg_card']};
                            border: 1px solid {COLORS['primary']}30;
                            border-radius: 12px;
                            padding: 1.5rem;
                        ">
                            <h4 style="color: {COLORS['text_primary']}; margin: 0 0 1rem 0;">AI Analysis</h4>
                            <div style="color: {COLORS['text_secondary']}; line-height: 1.6;">
                                {result.content.replace(chr(10), '<br>')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Track cost
                        if result.cost > 0:
                            get_budget_tracker().add_cost(result.cost)
                            st.caption(f"Analysis cost: R{result.cost * 18.5:.2f}")
                    else:
                        st.error(f"AI analysis failed: {result.content}")
                except Exception as e:
                    st.error(f"AI error: {str(e)}")
elif is_pro_mode() and not AI_AVAILABLE:
    st.info("AI components not available. Check your API key in Settings.")

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
    <p style="color: {COLORS['secondary']}; font-size: 0.85rem; margin: 0 0 0.25rem 0;">
        Problem detection powered by LocalAnalytics
    </p>
    <p style="color: {COLORS['text_muted']}; font-size: 0.8rem; margin: 0;">
        Navigate to Actions page for recommendations
    </p>
</div>
""", unsafe_allow_html=True)
