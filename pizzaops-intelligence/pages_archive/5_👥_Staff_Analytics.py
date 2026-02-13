"""
Page: Staff Analytics
Purpose: Performance tracking per staff member
Target User: Operations Manager
"""

import streamlit as st
import pandas as pd
import numpy as np

from ui.layout import page_header, section_header, spacer, render_info_box
from ui.metrics_cards import render_kpi_card, render_scorecard
from ui.charts import box_plot, bar_chart, heatmap, horizontal_bar_chart
from ui.filters import render_global_filters, apply_filters
from ui.theme import COLORS


# ── Page Config ──
st.set_page_config(page_title="Staff Analytics | PizzaOps", page_icon="👥", layout="wide")

page_header(
    title="Staff Analytics",
    icon="👥",
    description="Performance tracking per staff member - Identify training opportunities and best performers"
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

# ── Staff Role Selector ──
staff_roles = {
    "Order Taker": "order_taker",
    "Dough Prep": "dough_prep_staff",
    "Stylist": "stylist",
    "Oven Operator": "oven_operator",
    "Boxer": "boxer",
    "Delivery Driver": "delivery_driver"
}

available_roles = {k: v for k, v in staff_roles.items() if v in df_filtered.columns}

if not available_roles:
    st.warning("No staff data available in the dataset")
    st.stop()

selected_role = st.selectbox(
    "Select Staff Role to Analyze",
    options=list(available_roles.keys()),
    index=len(available_roles) - 1  # Default to delivery driver
)

role_col = available_roles[selected_role]

spacer("1rem")

# ── Staff Performance Table ──
section_header(f"{selected_role} Performance", "Individual metrics for each staff member")

# Determine metrics based on role
if role_col == "delivery_driver":
    metric_col = "delivery_duration"
    metric_name = "Delivery Time"
elif role_col in ["dough_prep_staff"]:
    metric_col = "dough_prep_time"
    metric_name = "Prep Time"
elif role_col == "stylist":
    metric_col = "styling_time"
    metric_name = "Styling Time"
elif role_col == "oven_operator":
    metric_col = "oven_time"
    metric_name = "Oven Time"
elif role_col == "boxer":
    metric_col = "boxing_time"
    metric_name = "Boxing Time"
else:
    metric_col = "total_prep_time" if "total_prep_time" in df_filtered.columns else None
    metric_name = "Prep Time"

# Calculate staff metrics
staff_metrics = df_filtered.groupby(role_col).agg({
    "order_id": "count",
}).reset_index()
staff_metrics.columns = ["staff", "orders"]

if metric_col and metric_col in df_filtered.columns:
    time_metrics = df_filtered.groupby(role_col)[metric_col].agg(["mean", "median", lambda x: x.quantile(0.95)]).reset_index()
    time_metrics.columns = ["staff", "avg_time", "median_time", "p95_time"]
    staff_metrics = staff_metrics.merge(time_metrics, on="staff")

if "complaint" in df_filtered.columns:
    complaint_metrics = df_filtered.groupby(role_col)["complaint"].agg(["sum", "mean"]).reset_index()
    complaint_metrics.columns = ["staff", "complaints", "complaint_rate"]
    complaint_metrics["complaint_rate"] = (complaint_metrics["complaint_rate"] * 100).round(2)
    staff_metrics = staff_metrics.merge(complaint_metrics, on="staff")

# Sort by average time (best first)
if "avg_time" in staff_metrics.columns:
    staff_metrics = staff_metrics.sort_values("avg_time")

# Display as cards
if len(staff_metrics) > 0:
    cols = st.columns(min(4, len(staff_metrics)))

    for i, (_, row) in enumerate(staff_metrics.iterrows()):
        col_idx = i % len(cols)

        # Determine status
        overall_avg = df_filtered[metric_col].mean() if metric_col and metric_col in df_filtered.columns else 0
        staff_avg = row.get("avg_time", 0)
        complaint_rate = row.get("complaint_rate", 0)

        if staff_avg > overall_avg * 1.2 or complaint_rate > 10:
            status = "danger"
        elif staff_avg > overall_avg * 1.1 or complaint_rate > 5:
            status = "warning"
        else:
            status = "good"

        metrics_list = [("Orders", int(row["orders"]))]

        if "avg_time" in row:
            metrics_list.append((f"Avg {metric_name}", f"{row['avg_time']:.1f} min"))
        if "p95_time" in row:
            metrics_list.append(("P95 Time", f"{row['p95_time']:.1f} min"))
        if "complaint_rate" in row:
            metrics_list.append(("Complaint %", f"{row['complaint_rate']:.1f}%"))

        with cols[col_idx]:
            render_scorecard(
                title=row["staff"],
                metrics=metrics_list,
                status=status
            )

spacer("1.5rem")

# ── Performance Comparison Chart ──
col1, col2 = st.columns([1, 1])

with col1:
    section_header("Performance by Staff", f"Average {metric_name}")

    if "avg_time" in staff_metrics.columns:
        fig = horizontal_bar_chart(
            staff_metrics.sort_values("avg_time", ascending=True),
            x="avg_time",
            y="staff",
            title="",
            color=COLORS["primary"],
            height=max(200, len(staff_metrics) * 40)
        )

        # Add overall average line
        if metric_col and metric_col in df_filtered.columns:
            overall_avg = df_filtered[metric_col].mean()
            fig.add_vline(x=overall_avg, line_dash="dash", line_color=COLORS["warning"],
                         annotation_text=f"Avg: {overall_avg:.1f}")

        st.plotly_chart(fig, use_container_width=True)

with col2:
    section_header("Duration Distribution", "Box plot by staff member")

    if metric_col and metric_col in df_filtered.columns:
        fig = box_plot(
            df_filtered,
            x=role_col,
            y=metric_col,
            title="",
            height=max(200, len(staff_metrics) * 40)
        )
        st.plotly_chart(fig, use_container_width=True)

spacer("1.5rem")

# ── Staff Combination Analysis (for multi-role workflows) ──
if role_col in ["stylist", "oven_operator"]:
    section_header("Staff Combination Analysis", "Performance when different staff work together")

    combo_cols = ["stylist", "oven_operator"]
    if all(col in df_filtered.columns for col in combo_cols) and "total_prep_time" in df_filtered.columns:
        combo_metrics = df_filtered.groupby(combo_cols)["total_prep_time"].mean().reset_index()
        combo_metrics.columns = ["stylist", "oven_operator", "avg_prep_time"]

        # Create pivot for heatmap
        pivot = combo_metrics.pivot(index="stylist", columns="oven_operator", values="avg_prep_time")

        if len(pivot) > 0:
            # Melt for heatmap function
            melted = combo_metrics.copy()
            melted["avg_prep_time"] = melted["avg_prep_time"].round(1)

            fig = heatmap(
                melted,
                x="oven_operator",
                y="stylist",
                z="avg_prep_time",
                title="Average Prep Time by Stylist × Oven Operator",
                colorscale="RdYlGn_r",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)

            # Find best and worst combinations
            best_combo = combo_metrics.loc[combo_metrics["avg_prep_time"].idxmin()]
            worst_combo = combo_metrics.loc[combo_metrics["avg_prep_time"].idxmax()]

            col1, col2 = st.columns(2)
            with col1:
                render_info_box(
                    "Best Combination",
                    f"Stylist: {best_combo['stylist']} + Oven: {best_combo['oven_operator']} "
                    f"= {best_combo['avg_prep_time']:.1f} min avg prep time",
                    COLORS["success"]
                )
            with col2:
                render_info_box(
                    "Needs Improvement",
                    f"Stylist: {worst_combo['stylist']} + Oven: {worst_combo['oven_operator']} "
                    f"= {worst_combo['avg_prep_time']:.1f} min avg prep time",
                    COLORS["warning"]
                )

spacer("1.5rem")

# ── Performance by Hour (Fatigue Analysis) ──
section_header("Performance by Hour", "Does performance degrade over time? (Fatigue analysis)")

if "hour_of_day" in df_filtered.columns and metric_col and metric_col in df_filtered.columns:
    hourly_staff = df_filtered.groupby([role_col, "hour_of_day"])[metric_col].mean().reset_index()
    hourly_staff.columns = ["staff", "hour", "avg_time"]

    # Get top performers to highlight
    top_staff = staff_metrics.head(3)["staff"].tolist() if len(staff_metrics) >= 3 else staff_metrics["staff"].tolist()
    hourly_top = hourly_staff[hourly_staff["staff"].isin(top_staff)]

    if len(hourly_top) > 0:
        import plotly.express as px

        fig = px.line(
            hourly_top,
            x="hour",
            y="avg_time",
            color="staff",
            title="",
            markers=True
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLORS["text_secondary"]),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

        # Check for fatigue patterns
        for staff in top_staff:
            staff_hourly = hourly_staff[hourly_staff["staff"] == staff]
            if len(staff_hourly) >= 4:
                early_avg = staff_hourly[staff_hourly["hour"] < 14]["avg_time"].mean()
                late_avg = staff_hourly[staff_hourly["hour"] >= 17]["avg_time"].mean()

                if late_avg > early_avg * 1.2:
                    render_info_box(
                        f"Fatigue Pattern: {staff}",
                        f"Performance degrades from {early_avg:.1f} min (morning) to {late_avg:.1f} min (evening). "
                        f"Consider rotation or break scheduling.",
                        COLORS["warning"]
                    )

spacer("1.5rem")

# ── Recommendations ──
section_header("Staff Recommendations", "Optimization suggestions based on performance data")

recommendations = []

# Identify underperformers
if "avg_time" in staff_metrics.columns:
    overall_avg = df_filtered[metric_col].mean() if metric_col and metric_col in df_filtered.columns else 0
    underperformers = staff_metrics[staff_metrics["avg_time"] > overall_avg * 1.15]

    for _, row in underperformers.iterrows():
        recommendations.append({
            "type": "Training",
            "staff": row["staff"],
            "detail": f"{row['staff']} averages {row['avg_time']:.1f} min vs team avg of {overall_avg:.1f} min. "
                     f"May benefit from additional training or process review.",
            "icon": "📚"
        })

# Identify high complaint staff
if "complaint_rate" in staff_metrics.columns:
    overall_rate = df_filtered["complaint"].mean() * 100 if "complaint" in df_filtered.columns else 0
    high_complaint = staff_metrics[staff_metrics["complaint_rate"] > overall_rate * 1.5]

    for _, row in high_complaint.iterrows():
        recommendations.append({
            "type": "Quality",
            "staff": row["staff"],
            "detail": f"{row['staff']} has {row['complaint_rate']:.1f}% complaint rate vs team avg of {overall_rate:.1f}%. "
                     f"Review quality procedures.",
            "icon": "⚠️"
        })

# Identify top performers
if "avg_time" in staff_metrics.columns:
    top_performer = staff_metrics.iloc[0]
    recommendations.append({
        "type": "Recognition",
        "staff": top_performer["staff"],
        "detail": f"{top_performer['staff']} is the top performer with {top_performer['avg_time']:.1f} min average. "
                 f"Consider mentorship role.",
        "icon": "⭐"
    })

for rec in recommendations:
    color = COLORS["warning"] if rec["type"] in ["Training", "Quality"] else COLORS["success"]
    st.markdown(f'<div style="background-color:{COLORS["bg_card"]};border-left:4px solid {color};padding:1rem;border-radius:0 8px 8px 0;margin-bottom:0.5rem;"><div style="display:flex;justify-content:space-between;"><span style="color:{COLORS["text_primary"]};font-weight:600;">{rec["icon"]} {rec["staff"]}</span><span style="color:{color};font-size:0.75rem;">{rec["type"]}</span></div><div style="color:{COLORS["text_secondary"]};font-size:0.875rem;margin-top:0.25rem;">{rec["detail"]}</div></div>', unsafe_allow_html=True)

# Important framing note
spacer("1rem")
st.markdown(f'<div style="background-color:{COLORS["bg_card"]};border-radius:8px;padding:1rem;border:1px solid {COLORS["info"]};"><div style="color:{COLORS["info"]};font-weight:600;margin-bottom:0.5rem;">ℹ️ Note on Staff Analytics</div><div style="color:{COLORS["text_secondary"]};font-size:0.875rem;">Staff insights are provided for optimization, not blame. Performance variations may be due to factors beyond individual control (peak hours, equipment issues, order complexity). Use this data to support staff development and process improvement.</div></div>', unsafe_allow_html=True)
