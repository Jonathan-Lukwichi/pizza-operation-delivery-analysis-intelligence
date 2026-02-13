"""
Styled table components for PizzaOps Intelligence.
Using simplified HTML for reliable Streamlit rendering.
"""

import streamlit as st
import pandas as pd
from typing import Optional, List, Dict

from ui.theme import COLORS


def styled_dataframe(
    df: pd.DataFrame,
    title: Optional[str] = None,
    height: int = 400,
    column_config: Optional[Dict] = None
):
    """
    Render a styled dataframe with Streamlit's native component.
    """
    if title:
        st.markdown(f'<div style="color:{COLORS["text_primary"]};font-weight:600;margin-bottom:0.75rem;">{title}</div>', unsafe_allow_html=True)

    st.dataframe(
        df,
        use_container_width=True,
        height=height,
        column_config=column_config
    )


def ranking_table(
    df: pd.DataFrame,
    rank_column: str,
    value_column: str,
    label_column: str,
    title: str = "",
    ascending: bool = False,
    top_n: int = 10,
    value_format: str = "{:.1f}",
    show_bars: bool = True
):
    """
    Render a ranking table with optional bar indicators.
    """
    sorted_df = df.sort_values(rank_column, ascending=ascending).head(top_n)

    if title:
        st.markdown(f'<div style="color:{COLORS["text_primary"]};font-weight:600;margin-bottom:0.75rem;">{title}</div>', unsafe_allow_html=True)

    max_val = sorted_df[value_column].max()

    rows_html = ""
    for i, (_, row) in enumerate(sorted_df.iterrows()):
        rank = i + 1
        label = row[label_column]
        value = row[value_column]
        formatted_value = value_format.format(value)
        bar_width = (value / max_val * 100) if max_val > 0 else 0

        bar_html = f'<div style="background-color:{COLORS["bg_dark"]};border-radius:4px;height:6px;margin-top:4px;overflow:hidden;"><div style="background-color:{COLORS["primary"]};width:{bar_width}%;height:100%;border-radius:4px;"></div></div>' if show_bars else ""

        rows_html += f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.75rem 0;border-bottom:1px solid {COLORS["border"]};"><div style="display:flex;align-items:center;"><span style="background-color:{COLORS["bg_dark"]};color:{COLORS["text_secondary"]};padding:0.25rem 0.5rem;border-radius:4px;font-size:0.75rem;margin-right:0.75rem;min-width:24px;text-align:center;">{rank}</span><span style="color:{COLORS["text_primary"]};">{label}</span></div><div style="text-align:right;min-width:100px;"><span style="color:{COLORS["text_primary"]};font-weight:600;">{formatted_value}</span>{bar_html}</div></div>'

    st.markdown(f'<div style="background-color:{COLORS["bg_card"]};border-radius:8px;padding:1rem;border:1px solid {COLORS["border"]};">{rows_html}</div>', unsafe_allow_html=True)


def comparison_table(
    data: List[Dict],
    columns: List[str],
    title: str = "",
    highlight_best: bool = True
):
    """
    Render a comparison table with optional highlighting.
    """
    if title:
        st.markdown(f'<div style="color:{COLORS["text_primary"]};font-weight:600;margin-bottom:0.75rem;">{title}</div>', unsafe_allow_html=True)

    header_html = "<tr>"
    for col in columns:
        header_html += f'<th style="background-color:{COLORS["bg_dark"]};color:{COLORS["text_secondary"]};padding:0.75rem;text-align:left;font-size:0.75rem;text-transform:uppercase;">{col}</th>'
    header_html += "</tr>"

    rows_html = ""
    for row_data in data:
        rows_html += "<tr>"
        for col in columns:
            value = row_data.get(col, "")
            rows_html += f'<td style="padding:0.75rem;border-bottom:1px solid {COLORS["border"]};color:{COLORS["text_primary"]};">{value}</td>'
        rows_html += "</tr>"

    st.markdown(f'<table style="width:100%;border-collapse:collapse;background-color:{COLORS["bg_card"]};border-radius:8px;overflow:hidden;"><thead>{header_html}</thead><tbody>{rows_html}</tbody></table>', unsafe_allow_html=True)


def staff_scorecard_table(df: pd.DataFrame, metrics: List[str], staff_col: str = "staff"):
    """
    Render a staff performance scorecard table.
    """
    st.markdown(f'<div style="color:{COLORS["text_primary"]};font-weight:600;margin-bottom:0.75rem;">Staff Performance Scorecards</div>', unsafe_allow_html=True)

    cols = st.columns(min(4, len(df)))

    for i, (_, row) in enumerate(df.iterrows()):
        col_idx = i % len(cols)

        metrics_html = ""
        for metric in metrics:
            value = row.get(metric, "N/A")
            if isinstance(value, float):
                value = f"{value:.1f}"
            metric_label = metric.replace('_', ' ').title()
            metrics_html += f'<div style="display:flex;justify-content:space-between;padding:0.5rem 0;border-bottom:1px solid {COLORS["border"]};"><span style="color:{COLORS["text_secondary"]};font-size:0.875rem;">{metric_label}</span><span style="color:{COLORS["text_primary"]};font-weight:600;">{value}</span></div>'

        with cols[col_idx]:
            staff_name = row[staff_col]
            st.markdown(f'<div style="background-color:{COLORS["bg_card"]};border-radius:8px;padding:1rem;border:1px solid {COLORS["border"]};margin-bottom:1rem;"><div style="color:{COLORS["text_primary"]};font-weight:600;margin-bottom:0.75rem;font-size:1rem;">{staff_name}</div>{metrics_html}</div>', unsafe_allow_html=True)


def render_scorecard(
    title: str,
    metrics: List[tuple],
    status: str = "neutral"
):
    """
    Render a scorecard with multiple metrics.
    """
    status_colors = {
        "good": "#10B981",
        "warning": "#F59E0B",
        "danger": "#EF4444",
        "neutral": "#334155"
    }
    border_color = status_colors.get(status, "#334155")

    metrics_rows = ""
    for label, value in metrics:
        metrics_rows += f'<div style="display:flex;justify-content:space-between;padding:0.5rem 0;border-bottom:1px solid #334155;"><span style="color:#94A3B8;">{label}</span><span style="color:#FAFAFA;font-weight:600;">{value}</span></div>'

    card_html = f'<div style="background-color:#1A1F2E;border-radius:12px;padding:1rem;border:1px solid #334155;border-top:3px solid {border_color};margin-bottom:1rem;"><div style="color:#FAFAFA;font-weight:600;margin-bottom:0.75rem;">{title}</div>{metrics_rows}</div>'
    st.markdown(card_html, unsafe_allow_html=True)


def driver_performance_card(
    driver_name: str,
    metrics: Dict[str, str],
    status: str = "neutral"
):
    """
    Render a driver performance card.
    """
    status_colors = {
        "good": "#10B981",
        "warning": "#F59E0B",
        "danger": "#EF4444",
        "neutral": "#94A3B8"
    }
    border_color = status_colors.get(status, "#94A3B8")

    metrics_html = ""
    for label, value in metrics.items():
        metrics_html += f'<div style="display:flex;justify-content:space-between;padding:0.5rem 0;border-bottom:1px solid #334155;"><span style="color:#94A3B8;font-size:0.875rem;">{label}</span><span style="color:#FAFAFA;font-weight:600;">{value}</span></div>'

    card_html = f'<div style="background-color:#1A1F2E;border-radius:12px;padding:1rem;border:1px solid #334155;border-left:4px solid {border_color};"><div style="color:#FAFAFA;font-weight:700;font-size:1.1rem;margin-bottom:0.75rem;">{driver_name}</div>{metrics_html}</div>'
    st.markdown(card_html, unsafe_allow_html=True)
