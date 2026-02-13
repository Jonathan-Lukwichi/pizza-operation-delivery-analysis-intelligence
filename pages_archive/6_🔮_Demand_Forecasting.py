"""
Page: Demand Forecasting
Purpose: Predict future order volumes using time-series ML
Target User: Operations Manager + Store Owner
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta

from ui.layout import page_header, section_header, spacer, render_info_box
from ui.metrics_cards import render_kpi_card
from ui.charts import line_chart, bar_chart, time_series_with_forecast
from ui.filters import render_global_filters, apply_filters
from ui.theme import COLORS
from data.transformer import aggregate_by_date


# ── Page Config ──
st.set_page_config(page_title="Demand Forecasting | PizzaOps", page_icon="🔮", layout="wide")

page_header(
    title="Demand Forecasting",
    icon="🔮",
    description="Predict future order volumes for staffing and inventory planning"
)

# ── Guard: Check Data Loaded ──
if "df" not in st.session_state or st.session_state.df is None:
    st.warning("⚠️ Please upload data on the Home page first.")
    st.stop()

# ── Load Data ──
df = st.session_state.df.copy()

# Don't apply filters for forecasting - we need full history
spacer("1rem")

# ── Check data sufficiency ──
if "order_date" not in df.columns:
    st.error("Order date column required for forecasting")
    st.stop()

date_range = (df["order_date"].max() - df["order_date"].min()).days
if date_range < 14:
    st.warning("At least 14 days of data recommended for accurate forecasting")

# ── Forecast Settings ──
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### Forecast Settings")
    forecast_horizon = st.slider(
        "Forecast Horizon (days)",
        min_value=1,
        max_value=30,
        value=7,
        help="Number of days to forecast"
    )

    granularity = st.radio(
        "Granularity",
        options=["Daily", "Hourly"],
        index=0,
        help="Daily forecasts are more stable; hourly provides more detail"
    )

spacer("1rem")

# ── Historical Pattern Analysis ──
section_header("Historical Demand Patterns", "Understanding your order patterns")

# Aggregate data
daily_data = aggregate_by_date(df, freq='D')

col1, col2 = st.columns([2, 1])

with col1:
    if len(daily_data) > 0 and "order_count" in daily_data.columns:
        fig = line_chart(
            daily_data,
            x="order_date",
            y="order_count",
            title="Daily Order Volume",
            color=COLORS["primary"],
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    # Quick stats
    if "order_count" in daily_data.columns:
        avg_daily = daily_data["order_count"].mean()
        max_daily = daily_data["order_count"].max()
        min_daily = daily_data["order_count"].min()
        std_daily = daily_data["order_count"].std()

        st.markdown(f'<div style="background-color:{COLORS["bg_card"]};border-radius:8px;padding:1.5rem;border:1px solid {COLORS["border"]};"><h4 style="color:{COLORS["text_primary"]};margin-bottom:1rem;">Daily Statistics</h4><div style="margin-bottom:0.75rem;"><div style="color:{COLORS["text_muted"]};">Average</div><div style="color:{COLORS["text_primary"]};font-size:1.5rem;font-weight:700;">{avg_daily:.0f} orders/day</div></div><div style="margin-bottom:0.75rem;"><div style="color:{COLORS["text_muted"]};">Peak Day</div><div style="color:{COLORS["warning"]};font-size:1.25rem;">{max_daily:.0f} orders</div></div><div style="margin-bottom:0.75rem;"><div style="color:{COLORS["text_muted"]};">Slowest Day</div><div style="color:{COLORS["text_secondary"]};font-size:1.25rem;">{min_daily:.0f} orders</div></div><div><div style="color:{COLORS["text_muted"]};">Variability (Std Dev)</div><div style="color:{COLORS["text_secondary"]};font-size:1.25rem;">±{std_daily:.0f} orders</div></div></div>', unsafe_allow_html=True)

spacer("1.5rem")

# ── Day of Week Pattern ──
section_header("Weekly Patterns", "Order volume by day of week")

if "day_of_week" in df.columns:
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_data = df.groupby("day_of_week").size().reset_index(name="orders")
    dow_data["day_of_week"] = pd.Categorical(dow_data["day_of_week"], categories=dow_order, ordered=True)
    dow_data = dow_data.sort_values("day_of_week")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = bar_chart(
            dow_data,
            x="day_of_week",
            y="orders",
            title="",
            show_values=True,
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        busiest_day = dow_data.loc[dow_data["orders"].idxmax(), "day_of_week"]
        slowest_day = dow_data.loc[dow_data["orders"].idxmin(), "day_of_week"]

        render_info_box(
            "Weekly Pattern",
            f"Busiest day: {busiest_day}. Slowest day: {slowest_day}. "
            f"Plan staffing accordingly.",
            COLORS["info"]
        )

spacer("1.5rem")

# ── Hourly Pattern ──
section_header("Hourly Patterns", "Peak hours identification")

if "hour_of_day" in df.columns:
    hourly_data = df.groupby("hour_of_day").size().reset_index(name="orders")
    hourly_avg = hourly_data["orders"].mean()

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = bar_chart(
            hourly_data,
            x="hour_of_day",
            y="orders",
            title="",
            height=300
        )
        fig.add_hline(y=hourly_avg, line_dash="dash", line_color=COLORS["info"],
                     annotation_text=f"Avg: {hourly_avg:.0f}")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        peak_hours = hourly_data[hourly_data["orders"] > hourly_avg * 1.3]
        if len(peak_hours) > 0:
            peak_list = ", ".join([f"{int(h):02d}:00" for h in peak_hours["hour_of_day"]])
            render_info_box(
                "Peak Hours",
                f"High demand periods: {peak_list}. Ensure adequate staffing during these times.",
                COLORS["warning"]
            )

spacer("1.5rem")

# ── Simple Forecast (Using Moving Average) ──
section_header("Demand Forecast", f"Next {forecast_horizon} days prediction")

st.info("Using exponential smoothing for forecasting. For production use, integrate Prophet or ARIMA models from the ML module.")

if len(daily_data) >= 7:
    # Simple exponential smoothing forecast
    historical = daily_data[["order_date", "order_count"]].copy()
    historical = historical.sort_values("order_date")

    # Calculate smoothed values
    alpha = 0.3
    historical["smoothed"] = historical["order_count"].ewm(alpha=alpha).mean()

    # Generate forecast
    last_date = historical["order_date"].max()
    last_smoothed = historical["smoothed"].iloc[-1]

    # Calculate trend
    if len(historical) >= 14:
        recent_trend = (historical["smoothed"].iloc[-1] - historical["smoothed"].iloc[-7]) / 7
    else:
        recent_trend = 0

    # Calculate day-of-week factors
    if "day_of_week" in df.columns:
        dow_factors = df.groupby(df["order_date"].dt.day_name()).size()
        dow_avg = dow_factors.mean()
        dow_factors = (dow_factors / dow_avg).to_dict()
    else:
        dow_factors = {}

    # Generate forecast dates
    forecast_dates = pd.date_range(last_date + timedelta(days=1), periods=forecast_horizon, freq='D')

    forecast_values = []
    lower_bound = []
    upper_bound = []

    for i, date in enumerate(forecast_dates):
        base = last_smoothed + (recent_trend * (i + 1))
        dow_name = date.day_name()
        factor = dow_factors.get(dow_name, 1.0)
        forecast = max(0, base * factor)

        # Confidence interval (simple approximation)
        std = historical["order_count"].std()
        ci_width = std * 1.96 * (1 + 0.1 * i)  # Widening CI

        forecast_values.append(forecast)
        lower_bound.append(max(0, forecast - ci_width))
        upper_bound.append(forecast + ci_width)

    forecast_df = pd.DataFrame({
        "date": forecast_dates,
        "forecast": forecast_values,
        "lower": lower_bound,
        "upper": upper_bound
    })

    # Plot
    fig = time_series_with_forecast(
        historical.rename(columns={"order_date": "date", "order_count": "actual"}),
        forecast_df.rename(columns={"date": "date", "forecast": "forecast"}),
        x="date",
        y_actual="actual",
        y_forecast="forecast",
        y_lower="lower",
        y_upper="upper",
        title="",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    # Forecast table
    st.markdown("**Forecast Details:**")
    forecast_display = forecast_df.copy()
    forecast_display["day"] = forecast_display["date"].dt.day_name()
    forecast_display["forecast"] = forecast_display["forecast"].round(0).astype(int)
    forecast_display["lower"] = forecast_display["lower"].round(0).astype(int)
    forecast_display["upper"] = forecast_display["upper"].round(0).astype(int)
    forecast_display["date"] = forecast_display["date"].dt.strftime("%Y-%m-%d")

    st.dataframe(
        forecast_display[["date", "day", "forecast", "lower", "upper"]].rename(columns={
            "date": "Date",
            "day": "Day",
            "forecast": "Forecast",
            "lower": "Lower Bound",
            "upper": "Upper Bound"
        }),
        use_container_width=True,
        hide_index=True
    )

spacer("1.5rem")

# ── Staffing Recommendations ──
section_header("Staffing Recommendations", "Based on forecast demand")

# Simple staffing rules
ORDERS_PER_PREP_STAFF = 10  # orders per hour per prep staff
ORDERS_PER_DRIVER = 5  # orders per hour per driver

st.markdown(f'<div style="background-color:{COLORS["bg_card"]};border-radius:8px;padding:1.5rem;border:1px solid {COLORS["border"]};"><h4 style="color:{COLORS["text_primary"]};margin-bottom:1rem;">Staffing Guide</h4><p style="color:{COLORS["text_secondary"]};margin-bottom:1rem;">Based on your forecast, here are staffing recommendations:</p>', unsafe_allow_html=True)

if len(forecast_df) > 0:
    avg_forecast = forecast_df["forecast"].mean()
    peak_forecast = forecast_df["forecast"].max()

    # Assuming 12-hour operating day
    daily_orders = avg_forecast
    peak_hourly = daily_orders / 8  # Concentrated in 8 active hours

    prep_staff_avg = max(2, int(np.ceil(peak_hourly / ORDERS_PER_PREP_STAFF)))
    drivers_avg = max(2, int(np.ceil(peak_hourly / ORDERS_PER_DRIVER)))

    peak_daily_orders = peak_forecast
    peak_hourly_max = peak_daily_orders / 6  # Peak days more concentrated

    prep_staff_peak = max(2, int(np.ceil(peak_hourly_max / ORDERS_PER_PREP_STAFF)))
    drivers_peak = max(2, int(np.ceil(peak_hourly_max / ORDERS_PER_DRIVER)))

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<div style="text-align:center;padding:1rem;"><div style="color:{COLORS["text_muted"]};">Average Day</div><div style="font-size:1.25rem;color:{COLORS["text_primary"]};margin:0.5rem 0;">{prep_staff_avg} prep staff + {drivers_avg} drivers</div><div style="color:{COLORS["text_muted"]};font-size:0.875rem;">For ~{daily_orders:.0f} orders/day</div></div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div style="text-align:center;padding:1rem;"><div style="color:{COLORS["warning"]};">Peak Days</div><div style="font-size:1.25rem;color:{COLORS["text_primary"]};margin:0.5rem 0;">{prep_staff_peak} prep staff + {drivers_peak} drivers</div><div style="color:{COLORS["text_muted"]};font-size:0.875rem;">For ~{peak_forecast:.0f} orders/day</div></div>', unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

spacer("1rem")

render_info_box(
    "Advanced Forecasting",
    "For more accurate predictions, the ML module includes Prophet and XGBoost ensemble models. "
    "These can capture holidays, promotions, and complex seasonal patterns.",
    COLORS["info"]
)
