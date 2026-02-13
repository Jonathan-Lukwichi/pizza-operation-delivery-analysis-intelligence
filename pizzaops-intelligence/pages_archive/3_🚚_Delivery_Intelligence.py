"""
Page: Delivery Intelligence
Purpose: Analyze delivery performance by area, driver, and time
Target User: Operations Manager
"""

import streamlit as st
import pandas as pd

from core.kpi_engine import delivery_by_area, driver_scorecards, area_hour_matrix, order_mode_comparison
from ui.layout import page_header, section_header, spacer, render_info_box
from ui.metrics_cards import render_kpi_card, render_scorecard
from ui.charts import bar_chart, box_plot, heatmap, line_chart, horizontal_bar_chart
from ui.tables import ranking_table, staff_scorecard_table
from ui.filters import render_global_filters, apply_filters
from ui.theme import COLORS


# ── Page Config ──
st.set_page_config(page_title="Delivery Intelligence | PizzaOps", page_icon="🚚", layout="wide")

page_header(
    title="Delivery Intelligence",
    icon="🚚",
    description="Delivery performance analysis - Answer: Why are some areas always late?"
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

# ── Area Performance Overview ──
section_header("Area Performance Comparison", "Delivery metrics by delivery zone")

area_metrics = delivery_by_area(df_filtered)

if len(area_metrics) > 0:
    col1, col2 = st.columns([1, 1])

    with col1:
        # Bar chart: Average delivery time by area
        fig = bar_chart(
            area_metrics,
            x="delivery_area",
            y="avg_delivery_time",
            title="Average Delivery Time by Area",
            show_values=True,
            height=350
        )
        # Add target line manually
        fig.add_hline(y=30, line_dash="dash", line_color=COLORS["danger"],
                     annotation_text="Target: 30 min")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Bar chart: On-time percentage by area
        if "on_time_pct" in area_metrics.columns:
            fig = bar_chart(
                area_metrics,
                x="delivery_area",
                y="on_time_pct",
                title="On-Time Delivery % by Area",
                show_values=True,
                height=350
            )
            fig.add_hline(y=85, line_dash="dash", line_color=COLORS["success"],
                         annotation_text="Target: 85%")
            st.plotly_chart(fig, use_container_width=True)

    # Area metrics table
    spacer("1rem")
    st.markdown("**Detailed Area Metrics:**")
    display_cols = ["delivery_area", "order_count", "avg_delivery_time", "on_time_pct", "complaint_rate"]
    available_cols = [col for col in display_cols if col in area_metrics.columns]
    st.dataframe(
        area_metrics[available_cols].rename(columns={
            "delivery_area": "Area",
            "order_count": "Orders",
            "avg_delivery_time": "Avg Time (min)",
            "on_time_pct": "On-Time %",
            "complaint_rate": "Complaint %"
        }),
        use_container_width=True,
        hide_index=True
    )

spacer("1.5rem")

# ── Area × Hour Heatmap ──
section_header("Area × Hour Performance Matrix", "Identify problematic area/time combinations")

hour_matrix = area_hour_matrix(df_filtered)
if len(hour_matrix) > 0:
    # Convert to melted format
    hour_matrix_reset = hour_matrix.reset_index()
    melted = hour_matrix_reset.melt(
        id_vars="delivery_area",
        var_name="hour",
        value_name="avg_time"
    )

    fig = heatmap(
        melted,
        x="hour",
        y="delivery_area",
        z="avg_time",
        title="",
        colorscale="RdYlGn_r",
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

    # Insight callout
    worst_combo = melted.loc[melted["avg_time"].idxmax()]
    if worst_combo["avg_time"] > 35:
        render_info_box(
            "Critical Combination Identified",
            f"Area {worst_combo['delivery_area']} at {int(worst_combo['hour']):02d}:00 has average delivery time of {worst_combo['avg_time']:.1f} minutes",
            COLORS["danger"]
        )
else:
    st.info("Insufficient data for area-hour analysis")

spacer("1.5rem")

# ── Driver Performance ──
section_header("Driver Performance Scorecards", "Individual delivery driver metrics")

driver_metrics = driver_scorecards(df_filtered)

if len(driver_metrics) > 0:
    # Sort by avg time (best first)
    if "avg_time" in driver_metrics.columns:
        driver_metrics = driver_metrics.sort_values("avg_time")

    # Display as cards
    cols = st.columns(min(4, len(driver_metrics)))

    for i, (_, row) in enumerate(driver_metrics.iterrows()):
        col_idx = i % len(cols)

        # Determine status
        avg_time = row.get("avg_time", 0)
        on_time = row.get("on_time_pct", 100)
        complaint = row.get("complaint_rate", 0)

        if avg_time > 35 or on_time < 70 or complaint > 10:
            status = "danger"
        elif avg_time > 30 or on_time < 85 or complaint > 5:
            status = "warning"
        else:
            status = "good"

        metrics_list = [
            ("Deliveries", int(row.get("total_deliveries", 0))),
            ("Avg Time", f"{row.get('avg_time', 0):.1f} min"),
            ("On-Time %", f"{row.get('on_time_pct', 0):.1f}%"),
            ("Complaint %", f"{row.get('complaint_rate', 0):.1f}%"),
        ]

        with cols[col_idx]:
            render_scorecard(
                title=row["driver"],
                metrics=metrics_list,
                status=status
            )

    spacer("1rem")

    # Driver comparison bar chart
    if "avg_time" in driver_metrics.columns:
        fig = horizontal_bar_chart(
            driver_metrics,
            x="avg_time",
            y="driver",
            title="Driver Average Delivery Time Comparison",
            color=COLORS["primary"],
            height=max(200, len(driver_metrics) * 40)
        )
        fig.add_vline(x=30, line_dash="dash", line_color=COLORS["danger"])
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Driver data not available")

spacer("1.5rem")

# ── Order Mode Analysis ──
section_header("Order Mode Analysis", "Performance comparison by order channel")

mode_metrics = order_mode_comparison(df_filtered)

if len(mode_metrics) > 0:
    col1, col2 = st.columns([1, 1])

    with col1:
        fig = bar_chart(
            mode_metrics,
            x="order_mode",
            y="avg_total_time",
            title="Average Total Time by Order Mode",
            show_values=True,
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = bar_chart(
            mode_metrics,
            x="order_mode",
            y="order_count",
            title="Order Volume by Mode",
            show_values=True,
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

    # Insight
    if len(mode_metrics) > 1:
        best_mode = mode_metrics.loc[mode_metrics["avg_total_time"].idxmin()]
        worst_mode = mode_metrics.loc[mode_metrics["avg_total_time"].idxmax()]
        diff = worst_mode["avg_total_time"] - best_mode["avg_total_time"]

        if diff > 2:
            render_info_box(
                "Order Mode Insight",
                f"{best_mode['order_mode'].title()} orders average {diff:.1f} minutes faster than {worst_mode['order_mode'].title()} orders. "
                f"This may indicate clearer order information or better preparation flow.",
                COLORS["info"]
            )
else:
    st.info("Order mode data not available")

spacer("1.5rem")

# ── Delivery Time Distribution ──
section_header("Delivery Time Distribution", "Overall delivery duration patterns")

if "delivery_duration" in df_filtered.columns:
    col1, col2 = st.columns([2, 1])

    with col1:
        fig = box_plot(
            df_filtered,
            x="delivery_area" if "delivery_area" in df_filtered.columns else None,
            y="delivery_duration",
            title="Delivery Duration by Area",
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Quick stats
        delivery_data = df_filtered["delivery_duration"].dropna()
        avg_time = delivery_data.mean()
        median_time = delivery_data.median()
        p95_time = delivery_data.quantile(0.95)
        max_time = delivery_data.max()
        st.markdown(f'<div style="background-color:{COLORS["bg_card"]};border-radius:8px;padding:1.5rem;border:1px solid {COLORS["border"]};"><h4 style="color:{COLORS["text_primary"]};margin-bottom:1rem;">Delivery Statistics</h4><div style="margin-bottom:0.75rem;"><div style="color:{COLORS["text_muted"]};">Average</div><div style="color:{COLORS["text_primary"]};font-size:1.5rem;font-weight:700;">{avg_time:.1f} min</div></div><div style="margin-bottom:0.75rem;"><div style="color:{COLORS["text_muted"]};">Median</div><div style="color:{COLORS["text_primary"]};font-size:1.25rem;">{median_time:.1f} min</div></div><div style="margin-bottom:0.75rem;"><div style="color:{COLORS["text_muted"]};">95th Percentile</div><div style="color:{COLORS["warning"]};font-size:1.25rem;">{p95_time:.1f} min</div></div><div><div style="color:{COLORS["text_muted"]};">Max</div><div style="color:{COLORS["danger"]};font-size:1.25rem;">{max_time:.1f} min</div></div></div>', unsafe_allow_html=True)
