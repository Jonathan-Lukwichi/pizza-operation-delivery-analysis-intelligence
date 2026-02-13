"""
Page: Complaint Engine
Purpose: Root cause analysis for complaints - THE MOST IMPORTANT PAGE
Target User: Store Owner + Operations Manager
"""

import streamlit as st
import pandas as pd
import numpy as np

from core.kpi_engine import complaint_analysis
from ui.layout import page_header, section_header, spacer, render_info_box, render_alert
from ui.metrics_cards import render_kpi_card
from ui.charts import horizontal_bar_chart, bar_chart, heatmap, scatter_plot, donut_chart
from ui.filters import render_global_filters, apply_filters
from ui.theme import COLORS


# ── Page Config ──
st.set_page_config(page_title="Complaint Engine | PizzaOps", page_icon="😤", layout="wide")

page_header(
    title="Complaint Intelligence Engine",
    icon="😤",
    description="Root cause analysis - Answer: Why do we get complaints even when delivery is fast?"
)

# ── Guard: Check Data Loaded ──
if "df" not in st.session_state or st.session_state.df is None:
    st.warning("⚠️ Please upload data on the Home page first.")
    st.stop()

# ── Load & Filter Data ──
df = st.session_state.df.copy()
filters = render_global_filters(df)
df_filtered = apply_filters(df, filters)

spacer("1rem")

# ── Complaint KPIs ──
analysis = complaint_analysis(df_filtered)

total_orders = len(df_filtered)
total_complaints = df_filtered["complaint"].sum() if "complaint" in df_filtered.columns else 0
complaint_rate = (total_complaints / total_orders * 100) if total_orders > 0 else 0

# Top reason
top_reason = None
if analysis.get("by_reason"):
    top_reason = max(analysis["by_reason"], key=analysis["by_reason"].get)

# Worst area
worst_area = None
if analysis.get("by_area"):
    worst_area = max(analysis["by_area"], key=analysis["by_area"].get)

col1, col2, col3, col4 = st.columns(4)

with col1:
    status = "good" if complaint_rate <= 5 else "warning" if complaint_rate <= 10 else "danger"
    render_kpi_card(
        title="Total Complaints",
        value=int(total_complaints),
        icon="😤",
        status=status
    )

with col2:
    render_kpi_card(
        title="Complaint Rate",
        value=complaint_rate,
        suffix="%",
        icon="📊",
        status=status,
        target="Target: <5%"
    )

with col3:
    render_kpi_card(
        title="Top Reason",
        value=top_reason.replace("_", " ").title() if top_reason else "N/A",
        icon="🔍",
        status="warning" if top_reason else "neutral"
    )

with col4:
    render_kpi_card(
        title="Worst Area",
        value=f"Area {worst_area}" if worst_area else "N/A",
        icon="📍",
        status="danger" if worst_area else "neutral"
    )

spacer("1.5rem")

# ── Complaints by Reason ──
col1, col2 = st.columns([1, 1])

with col1:
    section_header("Complaints by Reason", "Distribution of complaint categories")

    if analysis.get("by_reason"):
        reason_df = pd.DataFrame([
            {"reason": k, "count": v}
            for k, v in analysis["by_reason"].items()
        ]).sort_values("count", ascending=True)

        fig = horizontal_bar_chart(
            reason_df,
            x="count",
            y="reason",
            title="",
            color=COLORS["danger"],
            height=max(250, len(reason_df) * 35)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No complaint reasons recorded")

with col2:
    section_header("Complaints by Hour", "When do complaints occur most?")

    if analysis.get("by_hour"):
        hour_df = pd.DataFrame([
            {"hour": int(k), "rate": v}
            for k, v in analysis["by_hour"].items()
        ]).sort_values("hour")

        fig = bar_chart(
            hour_df,
            x="hour",
            y="rate",
            title="",
            color=COLORS["warning"],
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Hourly complaint data not available")

spacer("1.5rem")

# ── THE KEY INSIGHT: Root Cause Matrix ──
section_header(
    "🔍 Root Cause Matrix - KEY INSIGHT",
    "Critical: Many complaints occur on ON-TIME deliveries - they're QUALITY issues, not speed issues"
)

if "complaint" in df_filtered.columns and "delivery_target_met" in df_filtered.columns:
    # Create cross-tabulation
    complaint_df = df_filtered[df_filtered["complaint"] == True]

    if len(complaint_df) > 0:
        on_time_complaints = analysis.get("on_time_complaints", 0)
        late_complaints = analysis.get("late_complaints", 0)
        on_time_pct = analysis.get("on_time_complaint_pct", 0)

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            st.markdown(f'<div style="background-color:{COLORS["bg_card"]};border-radius:12px;padding:1.5rem;border:2px solid {COLORS["warning"]};text-align:center;"><div style="font-size:3rem;font-weight:700;color:{COLORS["warning"]};">{on_time_pct:.1f}%</div><div style="color:{COLORS["text_primary"]};font-weight:600;">of complaints from ON-TIME deliveries</div><div style="color:{COLORS["text_muted"]};font-size:0.875rem;margin-top:0.5rem;">({on_time_complaints} complaints)</div></div>', unsafe_allow_html=True)

        with col2:
            st.markdown(f'<div style="background-color:{COLORS["bg_card"]};border-radius:12px;padding:1.5rem;border:1px solid {COLORS["border"]};text-align:center;"><div style="font-size:3rem;font-weight:700;color:{COLORS["danger"]};">{100 - on_time_pct:.1f}%</div><div style="color:{COLORS["text_primary"]};font-weight:600;">from LATE deliveries</div><div style="color:{COLORS["text_muted"]};font-size:0.875rem;margin-top:0.5rem;">({late_complaints} complaints)</div></div>', unsafe_allow_html=True)

        with col3:
            st.markdown(f'<div style="background-color:rgba(255,107,53,0.1);border-radius:12px;padding:1.5rem;border:2px solid {COLORS["primary"]};"><div style="color:{COLORS["primary"]};font-weight:600;margin-bottom:0.5rem;">💡 Key Insight</div><div style="color:{COLORS["text_primary"]};font-size:0.875rem;">A significant portion of complaints come from on-time deliveries. These are <strong>QUALITY</strong> issues (cold food, wrong order), not speed issues. Focus on oven temperature and order accuracy.</div></div>', unsafe_allow_html=True)

        spacer("1rem")

        # Breakdown by reason and delivery status
        if "complaint_reason" in complaint_df.columns:
            st.markdown("**Complaint Reasons by Delivery Status:**")

            reason_status = complaint_df.groupby(
                ["complaint_reason", "delivery_target_met"]
            ).size().unstack(fill_value=0)

            if len(reason_status) > 0:
                reason_status.columns = ["Late", "On-Time"]
                reason_status["Total"] = reason_status.sum(axis=1)
                reason_status["On-Time %"] = (
                    reason_status["On-Time"] / reason_status["Total"] * 100
                ).round(1)
                reason_status = reason_status.sort_values("Total", ascending=False)

                st.dataframe(
                    reason_status.reset_index().rename(columns={"complaint_reason": "Reason"}),
                    use_container_width=True,
                    hide_index=True
                )
    else:
        st.info("No complaints in selected period")
else:
    st.info("Required data columns not available")

spacer("1.5rem")

# ── Oven Temperature Correlation ──
section_header("Oven Temperature & Complaints", "Do cold ovens cause more complaints?")

if "oven_temperature" in df_filtered.columns and "complaint" in df_filtered.columns:
    col1, col2 = st.columns([1, 1])

    with col1:
        # Complaint rate by temp zone
        if "oven_temp_zone" in df_filtered.columns:
            zone_data = df_filtered.groupby("oven_temp_zone").agg({
                "complaint": ["sum", "count"]
            }).reset_index()
            zone_data.columns = ["zone", "complaints", "total"]
            zone_data["rate"] = (zone_data["complaints"] / zone_data["total"] * 100).round(2)

            fig = bar_chart(
                zone_data,
                x="zone",
                y="rate",
                title="Complaint Rate by Oven Temperature Zone",
                show_values=True,
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)

            # Highlight insight
            cold_rate = zone_data[zone_data["zone"] == "cold"]["rate"].values
            optimal_rate = zone_data[zone_data["zone"] == "optimal"]["rate"].values

            if len(cold_rate) > 0 and len(optimal_rate) > 0 and cold_rate[0] > optimal_rate[0] * 1.5:
                render_info_box(
                    "Temperature Impact",
                    f"Cold oven orders have {cold_rate[0]:.1f}% complaint rate vs {optimal_rate[0]:.1f}% at optimal temperature. "
                    f"This is a {cold_rate[0]/optimal_rate[0]:.1f}x increase.",
                    COLORS["danger"]
                )

    with col2:
        # Temperature comparison stats
        complaint_temp_avg = df_filtered[df_filtered["complaint"] == True]["oven_temperature"].mean()
        no_complaint_temp_avg = df_filtered[df_filtered["complaint"] == False]["oven_temperature"].mean()
        temp_diff = abs(complaint_temp_avg - no_complaint_temp_avg)

        st.markdown(f'<div style="background-color:{COLORS["bg_card"]};border-radius:8px;padding:1.5rem;border:1px solid {COLORS["border"]};"><h4 style="color:{COLORS["text_primary"]};margin-bottom:1rem;">Temperature Comparison</h4><div style="display:flex;justify-content:space-around;"><div style="text-align:center;"><div style="color:{COLORS["text_muted"]};">Orders WITH Complaints</div><div style="font-size:1.5rem;font-weight:700;color:{COLORS["danger"]};">{complaint_temp_avg:.1f}°C</div></div><div style="text-align:center;"><div style="color:{COLORS["text_muted"]};">Orders WITHOUT Complaints</div><div style="font-size:1.5rem;font-weight:700;color:{COLORS["success"]};">{no_complaint_temp_avg:.1f}°C</div></div></div><div style="text-align:center;margin-top:1rem;color:{COLORS["text_secondary"]};">Difference: {temp_diff:.1f}°C</div></div>', unsafe_allow_html=True)
else:
    st.info("Oven temperature data not available")

spacer("1.5rem")

# ── Staff Correlation ──
section_header("Staff & Complaint Patterns", "Which staff members correlate with higher complaints?")

staff_cols = ["stylist", "oven_operator", "delivery_driver"]
available_staff = [col for col in staff_cols if col in df_filtered.columns]

if available_staff and "complaint" in df_filtered.columns:
    cols = st.columns(len(available_staff))

    for i, col in enumerate(available_staff):
        staff_data = df_filtered.groupby(col).agg({
            "complaint": ["sum", "count"]
        }).reset_index()
        staff_data.columns = ["staff", "complaints", "total"]
        staff_data["rate"] = (staff_data["complaints"] / staff_data["total"] * 100).round(2)
        staff_data = staff_data.sort_values("rate", ascending=False)

        with cols[i]:
            st.markdown(f"**{col.replace('_', ' ').title()}**")
            for _, row in staff_data.iterrows():
                rate = row["rate"]
                color = COLORS["danger"] if rate > 10 else COLORS["warning"] if rate > 5 else COLORS["success"]
                st.markdown(f'<div style="display:flex;justify-content:space-between;padding:0.5rem 0;border-bottom:1px solid {COLORS["border"]};"><span style="color:{COLORS["text_primary"]};">{row["staff"]}</span><span style="color:{color};font-weight:600;">{rate:.1f}%</span></div>', unsafe_allow_html=True)
else:
    st.info("Staff data not available for correlation analysis")

spacer("1.5rem")

# ── Actionable Recommendations ──
section_header("Actionable Recommendations", "Based on complaint analysis")

recommendations = []

# Check oven temperature issues
if "oven_temp_zone" in df_filtered.columns:
    cold_df = df_filtered[df_filtered["oven_temp_zone"] == "cold"]
    if len(cold_df) > 0:
        cold_complaint_rate = cold_df["complaint"].mean() * 100
        if cold_complaint_rate > 8:
            recommendations.append({
                "priority": "High",
                "action": "Implement oven preheating protocols",
                "detail": f"Cold oven orders have {cold_complaint_rate:.1f}% complaint rate. Ensure oven reaches 220°C minimum before cooking.",
                "icon": "🔥"
            })

# Check on-time complaint issue
if analysis.get("on_time_complaint_pct", 0) > 30:
    recommendations.append({
        "priority": "High",
        "action": "Focus on quality, not just speed",
        "detail": f"{analysis['on_time_complaint_pct']:.1f}% of complaints are from on-time orders. Review order accuracy and food quality procedures.",
        "icon": "✅"
    })

# Check worst area
if worst_area and analysis.get("by_area", {}).get(worst_area, 0) > 10:
    recommendations.append({
        "priority": "Medium",
        "action": f"Investigate Area {worst_area} delivery issues",
        "detail": f"Area {worst_area} has {analysis['by_area'][worst_area]:.1f}% complaint rate. Consider route optimization or driver reassignment.",
        "icon": "📍"
    })

# Default recommendation
if not recommendations:
    recommendations.append({
        "priority": "Info",
        "action": "Continue monitoring",
        "detail": "Complaint rates are within acceptable ranges. Maintain current quality standards.",
        "icon": "✓"
    })

for rec in recommendations:
    color = COLORS["danger"] if rec["priority"] == "High" else COLORS["warning"] if rec["priority"] == "Medium" else COLORS["info"]
    st.markdown(f'<div style="background-color:{COLORS["bg_card"]};border-left:4px solid {color};padding:1rem;border-radius:0 8px 8px 0;margin-bottom:0.75rem;"><div style="display:flex;justify-content:space-between;align-items:center;"><span style="color:{color};font-weight:600;">{rec["icon"]} {rec["action"]}</span><span style="background-color:{color}20;color:{color};padding:0.25rem 0.5rem;border-radius:4px;font-size:0.75rem;">{rec["priority"]}</span></div><div style="color:{COLORS["text_secondary"]};font-size:0.875rem;margin-top:0.5rem;">{rec["detail"]}</div></div>', unsafe_allow_html=True)
