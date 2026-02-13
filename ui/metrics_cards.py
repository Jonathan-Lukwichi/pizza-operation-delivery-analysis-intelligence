"""
KPI card components for PizzaOps Intelligence.
Futuristic Tech Design System - Glassmorphism with cyan accents.
"""

import streamlit as st
from typing import Optional, Union, List, Tuple

from ui.theme import COLORS, NEON


def render_tech_kpi_card(
    title: str,
    value: Union[str, int, float],
    delta: Optional[str] = None,
    delta_is_good: bool = True,
    status: str = "neutral",
    icon: Optional[str] = None,
    target: Optional[str] = None,
    suffix: str = ""
):
    """
    Render a Tech-style KPI card with clean glassmorphism.
    Uses inline styles for maximum compatibility.
    """
    # Status colors for borders and accents
    status_colors = {
        "good": (COLORS["success"], "rgba(0, 229, 160, 0.3)"),
        "warning": (COLORS["warning"], "rgba(245, 158, 11, 0.3)"),
        "danger": (COLORS["danger"], "rgba(255, 107, 107, 0.3)"),
        "neutral": (COLORS["primary"], "rgba(0, 180, 255, 0.2)"),
    }

    accent_color, border_color = status_colors.get(status, status_colors["neutral"])

    # Format value
    if isinstance(value, float):
        formatted_value = f"{value:.1f}{suffix}"
    elif isinstance(value, int):
        formatted_value = f"{value:,}{suffix}"
    else:
        formatted_value = f"{value}{suffix}"

    # Build label with icon
    label = f"{icon} {title}" if icon else title

    # Get colors as local variables to avoid f-string quote issues
    text_muted = COLORS["text_muted"]
    primary_light = COLORS["primary_light"]

    # Build delta HTML
    delta_html = ""
    if delta:
        delta_color = COLORS["success"] if delta_is_good else COLORS["danger"]
        delta_bg = "rgba(0, 229, 160, 0.1)" if delta_is_good else "rgba(255, 107, 107, 0.1)"
        delta_html = f'<div style="display: inline-block; margin-top: 0.75rem; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; color: {delta_color}; background: {delta_bg};">{delta}</div>'

    # Build target HTML
    target_html = ""
    if target:
        target_html = f'<div style="color: {text_muted}; font-size: 0.75rem; margin-top: 0.5rem;">{target}</div>'

    # Build card with all inline styles - using local variables for colors
    full_html = f'''<div style="background: rgba(10, 25, 60, 0.6); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-radius: 12px; padding: 1.5rem; border: 1px solid {border_color}; margin-bottom: 0.75rem; position: relative; overflow: hidden;"><div style="position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, {accent_color}, {primary_light});"></div><div style="color: {text_muted}; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.75rem; font-weight: 500;">{label}</div><div style="font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #FFFFFF 0%, {accent_color} 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; line-height: 1.1;">{formatted_value}</div>{delta_html}{target_html}</div>'''

    st.markdown(full_html, unsafe_allow_html=True)


def render_kpi_card(
    title: str,
    value: Union[str, int, float],
    delta: Optional[str] = None,
    delta_is_good: bool = True,
    status: str = "neutral",
    icon: Optional[str] = None,
    target: Optional[str] = None,
    suffix: str = ""
):
    """
    Render a styled KPI card.
    Uses Futuristic Tech design system for consistency.
    """
    return render_tech_kpi_card(
        title=title,
        value=value,
        delta=delta,
        delta_is_good=delta_is_good,
        status=status,
        icon=icon,
        target=target,
        suffix=suffix
    )


def render_kpi_row(kpis: list):
    """Render a row of KPI cards."""
    cols = st.columns(len(kpis))
    for col, kpi in zip(cols, kpis):
        with col:
            render_kpi_card(**kpi)


def render_metric_native(
    label: str,
    value: Union[str, int, float],
    delta: Optional[str] = None,
    delta_color: str = "normal"
):
    """Use Streamlit's native metric component."""
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def render_scorecard(
    title: str,
    metrics: List[Tuple[str, str]],
    status: str = "neutral"
):
    """
    Render a scorecard with multiple metrics - Tech style.
    """
    status_colors = {
        "good": COLORS["success"],
        "warning": COLORS["warning"],
        "danger": COLORS["danger"],
        "neutral": COLORS["primary"]
    }
    accent_color = status_colors.get(status, COLORS["primary"])

    # Get colors as local variables
    text_primary = COLORS["text_primary"]
    text_secondary = COLORS["text_secondary"]

    card_id = f"scorecard_{hash(title) % 10000}"

    # Build metrics rows
    metrics_html = ""
    for label, value in metrics:
        metrics_html += f'<div class="metric-row"><span class="metric-label">{label}</span><span class="metric-value">{value}</span></div>'

    css = f"""<style>
#{card_id} {{background: rgba(10, 25, 60, 0.6); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-radius: 12px; padding: 1.25rem; border: 1px solid rgba(0, 180, 255, 0.12); border-top: 3px solid {accent_color}; margin-bottom: 1rem; transition: all 0.3s ease;}}
#{card_id}:hover {{border-color: rgba(0, 180, 255, 0.3); box-shadow: 0 4px 25px rgba(0, 180, 255, 0.1);}}
#{card_id} .title {{color: {text_primary}; font-weight: 600; margin-bottom: 0.75rem;}}
#{card_id} .metric-row {{display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid rgba(0, 180, 255, 0.08);}}
#{card_id} .metric-row:last-child {{border-bottom: none;}}
#{card_id} .metric-label {{color: {text_secondary};}}
#{card_id} .metric-value {{color: {text_primary}; font-weight: 600;}}
</style>"""

    full_html = f'{css}<div id="{card_id}"><div class="title">{title}</div>{metrics_html}</div>'
    st.markdown(full_html, unsafe_allow_html=True)


def render_simple_metric_card(label: str, value: str, color: str = None):
    """Render a simple metric card - Tech style."""
    if color is None:
        color = COLORS["text_primary"]

    text_muted = COLORS["text_muted"]
    card_id = f"simple_{hash(label) % 10000}"

    css = f"""<style>
#{card_id} {{background: rgba(10, 25, 60, 0.6); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-radius: 12px; padding: 1.25rem; text-align: center; border: 1px solid rgba(0, 180, 255, 0.12); transition: all 0.3s ease;}}
#{card_id}:hover {{border-color: rgba(0, 180, 255, 0.3); transform: translateY(-2px);}}
#{card_id} .label {{color: {text_muted}; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;}}
#{card_id} .value {{color: {color}; font-size: 1.5rem; font-weight: 700;}}
</style>"""

    full_html = f'{css}<div id="{card_id}"><div class="label">{label}</div><div class="value">{value}</div></div>'
    st.markdown(full_html, unsafe_allow_html=True)


def render_stat_card(label: str, value: str, subtitle: str = "", status: str = "neutral"):
    """Render a stat card with optional subtitle - Tech style."""
    status_colors = {
        "good": COLORS["success"],
        "warning": COLORS["warning"],
        "danger": COLORS["danger"],
        "neutral": COLORS["text_primary"]
    }
    value_color = status_colors.get(status, COLORS["text_primary"])
    text_muted = COLORS["text_muted"]

    card_id = f"stat_{hash(label) % 10000}"

    subtitle_html = f'<div class="subtitle">{subtitle}</div>' if subtitle else ''

    css = f"""<style>
#{card_id} {{background: rgba(10, 25, 60, 0.6); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-radius: 12px; padding: 1.25rem; border: 1px solid rgba(0, 180, 255, 0.12); transition: all 0.3s ease;}}
#{card_id}:hover {{border-color: rgba(0, 180, 255, 0.3); transform: translateY(-2px); box-shadow: 0 4px 25px rgba(0, 180, 255, 0.1);}}
#{card_id} .label {{color: {text_muted}; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;}}
#{card_id} .value {{color: {value_color}; font-size: 1.75rem; font-weight: 700;}}
#{card_id} .subtitle {{color: {text_muted}; font-size: 0.75rem; margin-top: 0.25rem;}}
</style>"""

    full_html = f'{css}<div id="{card_id}"><div class="label">{label}</div><div class="value">{value}</div>{subtitle_html}</div>'
    st.markdown(full_html, unsafe_allow_html=True)


def render_gradient_stat(
    label: str,
    value: str,
    gradient_from: str = None,
    gradient_to: str = None
):
    """Render a stat with gradient value text - Tech style."""
    if gradient_from is None:
        gradient_from = COLORS["primary"]
    if gradient_to is None:
        gradient_to = COLORS["secondary"]

    text_muted = COLORS["text_muted"]
    card_id = f"gradient_{hash(label) % 10000}"

    css = f"""<style>
#{card_id} {{background: rgba(10, 25, 60, 0.6); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(0, 180, 255, 0.12); text-align: center; transition: all 0.3s ease;}}
#{card_id}:hover {{border-color: rgba(0, 180, 255, 0.3); transform: translateY(-2px); box-shadow: 0 4px 25px rgba(0, 180, 255, 0.15);}}
#{card_id} .label {{color: {text_muted}; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.75rem;}}
#{card_id} .value {{font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, {gradient_from} 0%, {gradient_to} 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;}}
</style>"""

    full_html = f'{css}<div id="{card_id}"><div class="label">{label}</div><div class="value">{value}</div></div>'
    st.markdown(full_html, unsafe_allow_html=True)


def render_icon_stat_card(
    icon: str,
    label: str,
    value: str,
    color: str = None
):
    """Render a stat card with prominent icon - Tech style."""
    if color is None:
        color = COLORS["primary"]

    text_muted = COLORS["text_muted"]
    text_primary = COLORS["text_primary"]
    card_id = f"icon_{hash(label) % 10000}"

    css = f"""<style>
#{card_id} {{background: rgba(10, 25, 60, 0.6); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(0, 180, 255, 0.12); display: flex; align-items: center; gap: 1rem; transition: all 0.3s ease;}}
#{card_id}:hover {{border-color: rgba(0, 180, 255, 0.3); transform: translateY(-2px); box-shadow: 0 4px 25px rgba(0, 180, 255, 0.15);}}
#{card_id} .icon {{font-size: 2rem; width: 3.5rem; height: 3.5rem; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, {color}20 0%, {color}10 100%); border-radius: 12px; border: 1px solid {color}30;}}
#{card_id} .content {{flex: 1;}}
#{card_id} .label {{color: {text_muted}; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.25rem;}}
#{card_id} .value {{color: {text_primary}; font-size: 1.5rem; font-weight: 700;}}
</style>"""

    full_html = f'{css}<div id="{card_id}"><div class="icon">{icon}</div><div class="content"><div class="label">{label}</div><div class="value">{value}</div></div></div>'
    st.markdown(full_html, unsafe_allow_html=True)
