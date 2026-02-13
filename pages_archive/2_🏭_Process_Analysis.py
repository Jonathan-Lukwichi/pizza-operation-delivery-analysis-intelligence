"""
Page: Process Analysis
Purpose: Deep-dive into the preparation pipeline to identify bottlenecks
Target User: Operations Manager
"""

import streamlit as st
import pandas as pd

from core.process_mining import (
    get_stage_breakdown, detect_bottlenecks, stage_by_hour_heatmap,
    oven_temp_analysis, calculate_stage_contributions, get_process_recommendations
)
from ui.layout import page_header, section_header, spacer, render_info_box
from ui.metrics_cards import render_kpi_card
from ui.charts import box_plot, heatmap, stacked_bar_chart, scatter_plot, bar_chart
from ui.filters import render_global_filters, apply_filters
from ui.theme import COLORS


# ── Page Config ──
st.set_page_config(page_title="Process Analysis | PizzaOps", page_icon="🏭", layout="wide")

page_header(
    title="Process Analysis",
    icon="🏭",
    description="Deep-dive into the preparation pipeline - Answer: Where are the bottlenecks?"
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

# ── Stage Breakdown KPIs ──
stage_stats = get_stage_breakdown(df_filtered)

if len(stage_stats) > 0:
    section_header("Pipeline Stage Overview", "Average duration for each preparation stage")

    cols = st.columns(len(stage_stats))
    stage_colors = {
        "dough_prep": COLORS["stage_dough_prep"],
        "styling": COLORS["stage_styling"],
        "oven": COLORS["stage_oven"],
        "boxing": COLORS["stage_boxing"],
    }

    for i, (_, row) in enumerate(stage_stats.iterrows()):
        with cols[i]:
            stage_name = row["stage"].replace("_", " ").title()
            target = row.get("target")
            status = "good" if target and row["mean"] <= target else "warning" if target and row["mean"] <= target * 1.2 else "danger"

            render_kpi_card(
                title=stage_name,
                value=row["mean"],
                suffix=" min",
                status=status,
                target=f"Target: {target} min" if target else None
            )

spacer("1.5rem")

# ── Stage Contribution Chart ──
col1, col2 = st.columns([1, 1])

with col1:
    section_header("Stage Contribution", "Percentage of total prep time by stage")

    contributions = calculate_stage_contributions(df_filtered)
    if len(contributions) > 0:
        fig = bar_chart(
            contributions,
            x="stage",
            y="contribution_pct",
            title="",
            show_values=True,
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    section_header("Stage Duration Distribution", "Box plot showing variability")

    # Prepare data for box plot
    stage_cols = ["dough_prep_time", "styling_time", "oven_time", "boxing_time"]
    available_cols = [col for col in stage_cols if col in df_filtered.columns]

    if available_cols:
        melted_df = df_filtered[available_cols].melt(var_name="stage", value_name="duration")
        melted_df["stage"] = melted_df["stage"].str.replace("_time", "").str.replace("_", " ").str.title()

        fig = box_plot(
            melted_df,
            x="stage",
            y="duration",
            title="",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

spacer("1.5rem")

# ── Bottleneck Detection ──
section_header("Bottleneck Detection", "Stages exceeding performance benchmarks")

bottlenecks = detect_bottlenecks(df_filtered)

if bottlenecks:
    for bn in bottlenecks:
        severity_color = COLORS["danger"] if bn["severity"] == "high" else COLORS["warning"]
        severity_icon = "🔴" if bn["severity"] == "high" else "🟡"
        stage_name = bn["stage"].replace("_", " ").title()
        peak_hours_str = ', '.join(str(h) + ':00' for h in bn["peak_hours"][:5]) if bn["peak_hours"] else 'All hours'

        st.markdown(f'<div style="background-color:{COLORS["bg_card"]};border-left:4px solid {severity_color};padding:1rem;border-radius:0 8px 8px 0;margin-bottom:0.75rem;"><div style="display:flex;justify-content:space-between;align-items:center;"><div><span style="color:{severity_color};font-weight:600;">{severity_icon} {stage_name} Stage</span><span style="color:{COLORS["text_muted"]};margin-left:1rem;">P95: {bn["actual_p95"]} min (benchmark: {bn["benchmark_p95"]} min)</span></div><div style="color:{COLORS["text_secondary"]};">Affects {bn["affected_orders_pct"]}% of orders</div></div><div style="color:{COLORS["text_secondary"]};font-size:0.875rem;margin-top:0.5rem;">Peak hours affected: {peak_hours_str}</div></div>', unsafe_allow_html=True)
else:
    render_info_box(
        "All Clear",
        "All pipeline stages are operating within acceptable benchmarks.",
        COLORS["success"]
    )

spacer("1.5rem")

# ── Heatmap: Stage Duration by Hour ──
section_header("Stage Performance Heatmap", "Average duration by hour of day - Red indicates bottlenecks")

heatmap_data = stage_by_hour_heatmap(df_filtered)
if len(heatmap_data) > 0:
    # Convert to format suitable for heatmap
    heatmap_melted = heatmap_data.reset_index().melt(
        id_vars="hour_of_day",
        var_name="stage",
        value_name="duration"
    )

    fig = heatmap(
        heatmap_melted,
        x="hour_of_day",
        y="stage",
        z="duration",
        title="",
        colorscale="RdYlGn_r",
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

spacer("1.5rem")

# ── Oven Temperature Analysis ──
section_header("Oven Temperature Analysis", "Correlation between temperature and quality")

oven_analysis = oven_temp_analysis(df_filtered)

if oven_analysis:
    col1, col2 = st.columns([1, 1])

    with col1:
        # Temperature stats
        mean_temp = oven_analysis.get("mean_temp", "N/A")
        std_temp = oven_analysis.get("std_temp", "N/A")
        min_temp = oven_analysis.get("min_temp", "N/A")
        max_temp = oven_analysis.get("max_temp", "N/A")

        st.markdown(f'<div style="background-color:{COLORS["bg_card"]};border-radius:8px;padding:1rem;border:1px solid {COLORS["border"]};"><h4 style="color:{COLORS["text_primary"]};margin-bottom:1rem;">Temperature Statistics</h4><div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;"><div><div style="color:{COLORS["text_muted"]};font-size:0.75rem;">Average</div><div style="color:{COLORS["text_primary"]};font-size:1.25rem;font-weight:600;">{mean_temp}°C</div></div><div><div style="color:{COLORS["text_muted"]};font-size:0.75rem;">Std Dev</div><div style="color:{COLORS["text_primary"]};font-size:1.25rem;font-weight:600;">{std_temp}°C</div></div><div><div style="color:{COLORS["text_muted"]};font-size:0.75rem;">Min</div><div style="color:{COLORS["text_primary"]};font-size:1.25rem;font-weight:600;">{min_temp}°C</div></div><div><div style="color:{COLORS["text_muted"]};font-size:0.75rem;">Max</div><div style="color:{COLORS["text_primary"]};font-size:1.25rem;font-weight:600;">{max_temp}°C</div></div></div></div>', unsafe_allow_html=True)

        # Complaint rate by zone
        zone_rates = oven_analysis.get("complaint_rate_by_zone", {})
        if zone_rates:
            spacer("1rem")
            st.markdown("**Complaint Rate by Temperature Zone:**")
            zone_cols = st.columns(len(zone_rates))
            for i, (zone, rate) in enumerate(zone_rates.items()):
                color = COLORS["danger"] if rate > 10 else COLORS["warning"] if rate > 5 else COLORS["success"]
                with zone_cols[i]:
                    st.markdown(f'<div style="text-align:center;padding:0.5rem;background-color:{COLORS["bg_card"]};border-radius:8px;"><div style="font-weight:bold;color:{COLORS["text_primary"]};">{zone.title()}</div><div style="font-size:1.25rem;color:{color};">{rate:.1f}%</div></div>', unsafe_allow_html=True)

    with col2:
        # Scatter plot: Temperature vs Oven Time
        if "oven_temperature" in df_filtered.columns and "oven_time" in df_filtered.columns:
            sample_df = df_filtered[["oven_temperature", "oven_time", "complaint"]].dropna()
            if len(sample_df) > 1000:
                sample_df = sample_df.sample(1000)

            if len(sample_df) > 0:
                fig = scatter_plot(
                    sample_df,
                    x="oven_temperature",
                    y="oven_time",
                    title="Temperature vs Cooking Time",
                    color_column="complaint",
                    trendline="ols",
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Oven temperature data not available")

spacer("1.5rem")

# ── Recommendations ──
section_header("Recommendations", "AI-generated improvement suggestions")

recommendations = get_process_recommendations(bottlenecks, oven_analysis)
for i, rec in enumerate(recommendations):
    icon = "💡" if "continue" in rec.lower() else "⚠️"
    color = COLORS["info"] if "continue" in rec.lower() else COLORS["warning"]
    st.markdown(f'<div style="background-color:{COLORS["bg_card"]};border-left:4px solid {color};padding:1rem;border-radius:0 8px 8px 0;margin-bottom:0.5rem;"><span style="color:{COLORS["text_primary"]};">{icon} {rec}</span></div>', unsafe_allow_html=True)
