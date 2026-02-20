"""
Layout components for PizzaOps Intelligence.
Page headers, footers, and spacing utilities.
Futuristic Tech Design System - Cyan accents on deep navy.
"""

import streamlit as st
from ui.theme import COLORS, CUSTOM_CSS, NEON


def inject_custom_css():
    """Inject custom CSS styles into the page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def page_header(title: str, icon: str = "", description: str = ""):
    """
    Render a Tech-styled page header with gradient text and glow effect.

    Args:
        title: Page title
        icon: Emoji icon
        description: Page description
    """
    inject_custom_css()

    header_html = f'''
    <div style="margin-bottom: 2.5rem; position: relative;">
        <div style="
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 0.75rem;
        ">
            <span style="
                font-size: 2.5rem;
                filter: drop-shadow(0 4px 8px rgba(0, 180, 255, 0.3));
            ">{icon}</span>
            <h1 style="
                font-size: 2.25rem;
                font-weight: 800;
                background: linear-gradient(135deg, #FFFFFF 0%, {COLORS["primary"]} 50%, {COLORS["secondary"]} 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin: 0;
                line-height: 1.2;
                text-shadow: 0 0 40px rgba(0, 180, 255, 0.3);
            ">{title}</h1>
        </div>
        <p style="
            color: {COLORS["text_secondary"]};
            font-size: 1rem;
            margin: 0;
            letter-spacing: 0.02em;
        ">{description}</p>
        <div style="
            position: absolute;
            bottom: -1rem;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(0, 180, 255, 0.4), transparent);
        "></div>
    </div>
    '''
    st.markdown(header_html, unsafe_allow_html=True)


def section_header(title: str, description: str = ""):
    """
    Render a Tech-styled section header.

    Args:
        title: Section title
        description: Optional description
    """
    desc_html = f'<p style="color: {COLORS["text_secondary"]}; font-size: 0.875rem; margin: 0;">{description}</p>' if description else ""

    section_html = f'''
    <div style="margin: 2.5rem 0 1.25rem 0; position: relative;">
        <h3 style="
            color: {COLORS["text_primary"]};
            margin-bottom: 0.5rem;
            font-size: 1.35rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        ">
            <span style="
                display: inline-block;
                width: 4px;
                height: 1.25rem;
                background: linear-gradient(180deg, {COLORS["primary"]}, {COLORS["secondary"]});
                border-radius: 2px;
            "></span>
            {title}
        </h3>
        {desc_html}
    </div>
    '''
    st.markdown(section_html, unsafe_allow_html=True)


def card_container(content_func, title: str = "", padding: str = "1.5rem"):
    """
    Wrap content in a Tech-styled glassmorphism card.

    Args:
        content_func: Function that renders the content
        title: Optional card title
        padding: CSS padding value
    """
    title_html = f'<div style="color:{COLORS["text_primary"]};font-weight:600;margin-bottom:1rem;font-size:1rem;">{title}</div>' if title else ""

    with st.container():
        st.markdown(f'''
        <div style="
            background: rgba(10, 25, 60, 0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 12px;
            padding: {padding};
            border: 1px solid rgba(0, 180, 255, 0.12);
            margin-bottom: 1rem;
        ">{title_html}''', unsafe_allow_html=True)
        content_func()
        st.markdown("</div>", unsafe_allow_html=True)


def spacer(height: str = "1rem"):
    """Add vertical spacing."""
    st.markdown(f'<div style="height:{height};"></div>', unsafe_allow_html=True)


def divider():
    """Render a styled divider with gradient."""
    st.markdown('''
    <hr style="
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0, 180, 255, 0.3), transparent);
        margin: 1.5rem 0;
    " />
    ''', unsafe_allow_html=True)


def render_alert(message: str, alert_type: str = "info", icon: str = ""):
    """
    Render an alert message - Tech style.

    Args:
        message: Alert message
        alert_type: "success" | "warning" | "danger" | "info"
        icon: Optional emoji icon
    """
    colors = {
        "success": (COLORS["success"], "rgba(0, 229, 160, 0.1)"),
        "warning": (COLORS["warning"], "rgba(245, 158, 11, 0.1)"),
        "danger": (COLORS["danger"], "rgba(255, 107, 107, 0.1)"),
        "info": (COLORS["primary"], "rgba(0, 180, 255, 0.1)")
    }

    border_color, bg_color = colors.get(alert_type, colors["info"])
    st.markdown(f'''
    <div style="
        background: {bg_color};
        border-left: 4px solid {border_color};
        padding: 1rem;
        border-radius: 0 12px 12px 0;
        margin-bottom: 1rem;
        backdrop-filter: blur(8px);
    ">
        <span style="color: {COLORS["text_primary"]};">{icon} {message}</span>
    </div>
    ''', unsafe_allow_html=True)


def render_info_box(title: str, content: str, color: str = None):
    """
    Render an information box - Tech style.

    Args:
        title: Box title
        content: Box content
        color: Optional accent color
    """
    accent_color = color or COLORS["primary"]
    st.markdown(f'''
    <div style="
        background: rgba(10, 25, 60, 0.6);
        backdrop-filter: blur(12px);
        border-radius: 12px;
        padding: 1rem;
        border-left: 4px solid {accent_color};
        margin-bottom: 1rem;
    ">
        <div style="color: {accent_color}; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.875rem;">{title}</div>
        <div style="color: {COLORS["text_secondary"]}; font-size: 0.875rem;">{content}</div>
    </div>
    ''', unsafe_allow_html=True)


def render_stat_row(stats: list):
    """
    Render a row of inline statistics - Tech style.

    Args:
        stats: List of (label, value, color) tuples
    """
    items_html = ""
    for label, value, color in stats:
        color = color or COLORS["text_primary"]
        items_html += f'''
        <div style="text-align: center; padding: 0 1.5rem;">
            <div style="color: {COLORS["text_muted"]}; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.25rem;">{label}</div>
            <div style="color: {color}; font-size: 1.5rem; font-weight: 700;">{value}</div>
        </div>
        '''

    st.markdown(f'''
    <div style="
        display: flex;
        justify-content: space-around;
        background: rgba(10, 25, 60, 0.6);
        backdrop-filter: blur(12px);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(0, 180, 255, 0.12);
    ">{items_html}</div>
    ''', unsafe_allow_html=True)


def footer():
    """Render Tech-styled page footer with branding."""
    footer_html = f'''
    <div style="
        text-align: center;
        padding: 2.5rem 0;
        margin-top: 3rem;
        border-top: 1px solid rgba(0, 180, 255, 0.15);
        position: relative;
    ">
        <div style="
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 1px;
            background: linear-gradient(90deg, transparent, {COLORS["primary"]}, transparent);
        "></div>
        <p style="
            color: {COLORS["text_muted"]};
            font-size: 0.8rem;
            margin: 0 0 0.5rem 0;
        ">PizzaOps Intelligence v1.0</p>
        <p style="
            color: {COLORS["text_secondary"]};
            font-size: 0.85rem;
            margin: 0 0 0.25rem 0;
        ">Built with purpose by <strong style="
            background: linear-gradient(135deg, {COLORS["primary"]}, {COLORS["secondary"]});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        ">JLWanalytics</strong></p>
        <p style="
            color: {COLORS["primary"]};
            font-size: 0.75rem;
            margin: 0;
            letter-spacing: 0.1em;
        ">AFRICA'S PREMIER DATA REFINERY</p>
    </div>
    '''
    st.markdown(footer_html, unsafe_allow_html=True)


def loading_placeholder(message: str = "Loading..."):
    """Show a loading placeholder - Tech style."""
    st.markdown(f'''
    <div style="
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 3rem;
        color: {COLORS["text_muted"]};
    ">
        <div style="font-size: 1.25rem;">{message}</div>
    </div>
    ''', unsafe_allow_html=True)


def empty_state(message: str, icon: str = ""):
    """Show an empty state message - Tech style."""
    st.markdown(f'''
    <div style="
        text-align: center;
        padding: 3rem;
        color: {COLORS["text_muted"]};
    ">
        <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.6;">{icon}</div>
        <div style="font-size: 1rem;">{message}</div>
    </div>
    ''', unsafe_allow_html=True)


def render_empty_state(
    title: str,
    message: str,
    icon: str = "📭",
    cta_text: str = None,
    cta_page: str = None
):
    """
    Render a beautiful empty state with optional CTA button inside the card.

    Args:
        title: Main heading text
        message: Descriptive subtitle
        icon: Emoji icon to display
        cta_text: Button text (optional)
        cta_page: Page name to link to (optional)
    """
    # Start the card container
    st.markdown(f'''<div style="text-align: center; padding: 3rem 2rem 1.5rem 2rem; background: rgba(10, 25, 60, 0.4); border-radius: 16px; border: 1px dashed rgba(0, 180, 255, 0.2);">
        <div style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.7;">{icon}</div>
        <h3 style="color: #ffffff; font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem;">{title}</h3>
        <p style="color: #6889a8; font-size: 1rem; margin-bottom: 1.5rem;">{message}</p>
    </div>''', unsafe_allow_html=True)

    # Render functional CTA button inside the card area using negative margin trick
    if cta_text and cta_page:
        st.markdown('<div style="margin-top: -2.5rem; margin-bottom: 1rem;">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(cta_text, type="primary", use_container_width=True, key=f"cta_{cta_page}"):
                st.switch_page(f"pages/{cta_page}.py")
        st.markdown('</div>', unsafe_allow_html=True)


def gradient_badge(text: str, size: str = "sm"):
    """Render a gradient badge - Tech style."""
    sizes = {
        "sm": ("0.75rem", "0.25rem 0.75rem"),
        "md": ("0.875rem", "0.375rem 1rem"),
        "lg": ("1rem", "0.5rem 1.25rem")
    }
    font_size, padding = sizes.get(size, sizes["sm"])

    st.markdown(f'''
    <span style="
        display: inline-block;
        background: linear-gradient(90deg, {COLORS["primary"]} 0%, {COLORS["secondary"]} 100%);
        color: white;
        font-size: {font_size};
        font-weight: 600;
        padding: {padding};
        border-radius: 20px;
    ">{text}</span>
    ''', unsafe_allow_html=True)


def glass_card(content: str, title: str = ""):
    """Render a glassmorphism card with content - Tech style."""
    title_html = f'<div style="color: {COLORS["text_primary"]}; font-weight: 600; margin-bottom: 0.75rem; font-size: 1rem;">{title}</div>' if title else ""

    st.markdown(f'''
    <div style="
        background: rgba(10, 25, 60, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(0, 180, 255, 0.12);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    ">
        {title_html}
        <div style="color: {COLORS["text_secondary"]};">{content}</div>
    </div>
    ''', unsafe_allow_html=True)


def render_dashboard_header(
    title: str,
    logo_text: str = "P",
    logo_color: str = None,
    is_live: bool = True,
    live_text: str = "LIVE DASHBOARD"
):
    """
    Render a professional dashboard header with logo badge and live indicator.
    Inspired by HealthForecast AI design.
    """
    inject_custom_css()

    if logo_color is None:
        logo_color = COLORS["primary"]

    # Build live indicator HTML (single line to avoid rendering issues)
    live_html = ""
    if is_live:
        success_color = COLORS["success"]
        live_html = f'<div style="display:flex;align-items:center;gap:0.5rem;background:rgba(0,229,160,0.1);border:1px solid rgba(0,229,160,0.3);border-radius:20px;padding:0.35rem 1rem;"><div style="width:8px;height:8px;background:{success_color};border-radius:50%;box-shadow:0 0 8px {success_color};"></div><span style="color:{success_color};font-size:0.7rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;">{live_text}</span></div>'

    # Get colors as variables
    secondary = COLORS["secondary"]
    text_primary = COLORS["text_primary"]
    text_muted = COLORS["text_muted"]

    # Build header HTML
    header_html = f'''<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:2rem;padding-bottom:1.5rem;border-bottom:1px solid rgba(0,180,255,0.15);">
<div style="display:flex;align-items:center;gap:1rem;">
<div style="width:56px;height:56px;background:linear-gradient(135deg,{logo_color} 0%,{secondary} 100%);border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:1.75rem;font-weight:800;color:white;box-shadow:0 8px 25px rgba(0,180,255,0.3);border:2px solid rgba(255,255,255,0.1);">{logo_text}</div>
<div>
<h1 style="font-size:1.75rem;font-weight:700;color:{text_primary};margin:0;line-height:1.2;">{title}</h1>
<p style="color:{text_muted};font-size:0.85rem;margin:0.25rem 0 0 0;">Real-time operational insights</p>
</div>
</div>
{live_html}
</div>'''

    st.markdown(header_html, unsafe_allow_html=True)


def render_status_row(statuses: list):
    """
    Render a row of status indicators (like tabs but visual only).

    Args:
        statuses: List of (label, icon, is_active, color) tuples
    """
    items_html = ""
    for label, icon, is_active, color in statuses:
        if color is None:
            color = COLORS["primary"]

        if is_active:
            bg = f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.15)"
            border = f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.4)"
            text_color = color
            glow = f"0 0 15px rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.3)"
        else:
            bg = "rgba(10, 25, 60, 0.4)"
            border = "rgba(0, 180, 255, 0.12)"
            text_color = COLORS["text_muted"]
            glow = "none"

        # Single-line HTML to avoid rendering issues
        items_html += f'<div style="display:flex;align-items:center;gap:0.5rem;padding:0.6rem 1rem;background:{bg};border:1px solid {border};border-radius:10px;transition:all 0.3s ease;box-shadow:{glow};"><span style="font-size:1rem;">{icon}</span><span style="color:{text_color};font-size:0.75rem;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;">{label}</span></div>'

    row_html = f'<div style="display:flex;flex-wrap:wrap;gap:0.75rem;margin-bottom:1.5rem;">{items_html}</div>'
    st.markdown(row_html, unsafe_allow_html=True)


def render_section_title(title: str, subtitle: str = "", icon: str = ""):
    """
    Render an enhanced section title with optional icon and subtitle.
    """
    icon_html = f'<span style="margin-right:0.5rem;">{icon}</span>' if icon else ""
    subtitle_html = f'<div style="color:{COLORS["text_muted"]};font-size:0.85rem;margin:0.25rem 0 0 0;">{subtitle}</div>' if subtitle else ""

    # Single-line HTML to avoid rendering issues
    section_html = f'<div style="margin:2rem 0 1.25rem 0;"><h3 style="color:{COLORS["text_primary"]};font-size:1.15rem;font-weight:600;margin:0;display:flex;align-items:center;">{icon_html}{title}</h3>{subtitle_html}</div>'
    st.markdown(section_html, unsafe_allow_html=True)


def render_feature_card(
    title: str,
    description: str,
    icon: str,
    color: str = None,
    badge_text: str = ""
):
    """
    Render a feature card with icon badge - inspired by HealthForecast design.

    Args:
        title: Card title
        description: Card description
        icon: Emoji icon
        color: Accent color
        badge_text: Optional badge text
    """
    if color is None:
        color = COLORS["primary"]

    badge_html = ""
    if badge_text:
        badge_html = f'''
        <div style="
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: {color}20;
            color: {color};
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.65rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            border: 1px solid {color}40;
        ">{badge_text}</div>
        '''

    st.markdown(f'''
    <div style="
        background: rgba(10, 25, 60, 0.6);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 1.75rem;
        border: 1px solid rgba(0, 180, 255, 0.12);
        position: relative;
        overflow: hidden;
        transition: all 0.4s ease;
        height: 100%;
    " onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 15px 40px rgba(0, 180, 255, 0.15)'; this.style.borderColor='rgba(0, 180, 255, 0.3)';"
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'; this.style.borderColor='rgba(0, 180, 255, 0.12)';">
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, {color}, {COLORS["secondary"]});
        "></div>
        {badge_html}
        <div style="
            width: 52px;
            height: 52px;
            background: linear-gradient(135deg, {color}20 0%, {color}10 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid {color}30;
        ">{icon}</div>
        <h4 style="
            color: {COLORS["text_primary"]};
            font-size: 1.1rem;
            font-weight: 600;
            margin: 0 0 0.5rem 0;
        ">{title}</h4>
        <p style="
            color: {COLORS["text_secondary"]};
            font-size: 0.875rem;
            line-height: 1.5;
            margin: 0;
        ">{description}</p>
    </div>
    ''', unsafe_allow_html=True)


def render_glowing_button_html(text: str, icon: str = "", is_primary: bool = True):
    """
    Generate HTML for a glowing CTA button (visual only - use with st.button for functionality).
    """
    if is_primary:
        bg = f"linear-gradient(90deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%)"
        shadow = f"0 4px 20px rgba(0, 180, 255, 0.4)"
    else:
        bg = "transparent"
        shadow = "none"

    icon_html = f'<span style="margin-right: 0.5rem;">{icon}</span>' if icon else ""

    return f'''
    <div style="
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.875rem 2rem;
        background: {bg};
        border: {"none" if is_primary else f"1px solid {COLORS['primary']}"};
        border-radius: 25px;
        color: {"white" if is_primary else COLORS["primary"]};
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        box-shadow: {shadow};
        cursor: pointer;
        transition: all 0.3s ease;
    ">
        {icon_html}{text}
    </div>
    '''


def render_metric_with_icon(
    label: str,
    value: str,
    icon: str,
    color: str = None,
    subtitle: str = ""
):
    """
    Render a metric card with a prominent icon.
    """
    if color is None:
        color = COLORS["primary"]

    subtitle_html = f'<div style="color: {COLORS["text_muted"]}; font-size: 0.7rem; margin-top: 0.25rem;">{subtitle}</div>' if subtitle else ""

    st.markdown(f'''
    <div style="
        background: rgba(10, 25, 60, 0.6);
        backdrop-filter: blur(12px);
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid rgba(0, 180, 255, 0.12);
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: all 0.3s ease;
    ">
        <div style="
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, {color}20 0%, {color}10 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            border: 1px solid {color}30;
            flex-shrink: 0;
        ">{icon}</div>
        <div style="flex: 1; min-width: 0;">
            <div style="
                color: {COLORS["text_muted"]};
                font-size: 0.7rem;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                margin-bottom: 0.25rem;
            ">{label}</div>
            <div style="
                color: {COLORS["text_primary"]};
                font-size: 1.35rem;
                font-weight: 700;
                line-height: 1.1;
            ">{value}</div>
            {subtitle_html}
        </div>
        <div style="
            width: 4px;
            height: 40px;
            background: linear-gradient(180deg, {color}, transparent);
            border-radius: 2px;
        "></div>
    </div>
    ''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# NEW DASHBOARD COMPONENTS - Inspired by reference dashboards
# ═══════════════════════════════════════════════════════════════════════════════

def render_hero_header(
    title: str = "Daily Performance Dashboard",
    subtitle: str = "Real-time operations analytics for your pizza delivery business",
    today_str: str = "",
    total_records: int = 0,
    today_orders: int = 0
):
    """
    Render a full hero header with gradient background, version badge, and stats.
    Inspired by PizzaOps Dashboard reference design.
    Mobile-responsive with clamp() for font sizes.
    """
    inject_custom_css()

    primary = COLORS["primary"]
    secondary = COLORS["secondary"]
    text_primary = COLORS["text_primary"]
    text_secondary = COLORS["text_secondary"]
    text_muted = COLORS["text_muted"]

    # Build stats row - wrap on mobile
    stats_html = f'<div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin-top:0.75rem;"><span style="font-family:monospace;font-size:clamp(0.65rem,2vw,0.8rem);color:{text_muted};white-space:nowrap;">📅 {today_str}</span><span style="font-family:monospace;font-size:clamp(0.65rem,2vw,0.8rem);color:{text_muted};white-space:nowrap;">📁 {total_records:,} records</span><span style="font-family:monospace;font-size:clamp(0.65rem,2vw,0.8rem);color:{text_muted};white-space:nowrap;">📦 {today_orders:,} today</span></div>' if today_str else ""

    # Live indicator - smaller on mobile
    live_html = f'<span style="display:inline-flex;align-items:center;gap:4px;font-size:clamp(0.55rem,1.5vw,0.65rem);font-weight:600;padding:2px 6px;border-radius:50px;background:rgba(16,185,129,0.12);color:#34D399;text-transform:uppercase;margin-left:0.5rem;"><span style="width:5px;height:5px;background:#34D399;border-radius:50%;"></span>LIVE</span>'

    # Responsive padding and font sizes using clamp()
    hero_html = f'''<div class="hero-header" style="background:linear-gradient(135deg,#111827 0%,#1A1F35 50%,#111827 100%);border:1px solid #1E293B;border-radius:clamp(12px,3vw,20px);padding:clamp(1rem,4vw,2rem) clamp(1rem,4vw,2.5rem);margin-bottom:1.5rem;position:relative;overflow:hidden;">
<div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,{primary},{secondary},#06B6D4,#10B981);border-radius:20px 20px 0 0;"></div>
<div style="position:absolute;top:-80px;right:-80px;width:150px;height:150px;background:radial-gradient(circle,rgba(59,130,246,0.08) 0%,transparent 70%);border-radius:50%;"></div>
<div style="display:inline-block;background:linear-gradient(135deg,rgba(59,130,246,0.15),rgba(139,92,246,0.15));border:1px solid rgba(59,130,246,0.25);color:#93C5FD;font-size:clamp(0.6rem,1.5vw,0.7rem);font-weight:600;padding:0.2rem 0.6rem;border-radius:50px;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:0.5rem;">🍕 PizzaOps v2.0</div>
<h1 style="font-family:'Plus Jakarta Sans',sans-serif;font-size:clamp(1.25rem,4vw,2rem);font-weight:800;color:{text_primary};margin:0;letter-spacing:-0.5px;display:flex;flex-wrap:wrap;align-items:center;gap:0.5rem;">{title}{live_html}</h1>
<p style="font-family:'Plus Jakarta Sans',sans-serif;font-size:clamp(0.8rem,2.5vw,0.95rem);color:{text_secondary};margin:0.3rem 0 0;">{subtitle}</p>
{stats_html}
</div>'''

    st.markdown(hero_html, unsafe_allow_html=True)


def render_alert_card(icon: str, title: str, description: str, severity: str = "warning"):
    """
    Render an individual alert card with severity-based styling.

    Args:
        icon: Emoji icon
        title: Alert title
        description: Alert description
        severity: "danger" | "warning" | "success" | "info"
    """
    bg_map = {"danger": "rgba(244,63,94,0.06)", "warning": "rgba(245,158,11,0.06)", "success": "rgba(16,185,129,0.06)", "info": "rgba(59,130,246,0.06)"}
    border_map = {"danger": "rgba(244,63,94,0.15)", "warning": "rgba(245,158,11,0.15)", "success": "rgba(16,185,129,0.15)", "info": "rgba(59,130,246,0.15)"}

    bg = bg_map.get(severity, bg_map["info"])
    border = border_map.get(severity, border_map["info"])
    text_primary = COLORS["text_primary"]
    text_secondary = COLORS["text_secondary"]

    alert_html = f'<div style="background:{bg};border:1px solid {border};border-radius:12px;padding:0.9rem 1.1rem;margin-bottom:0.5rem;display:flex;align-items:flex-start;gap:0.7rem;"><span style="font-size:1.05rem;margin-top:2px;">{icon}</span><div><div style="font-size:0.82rem;font-weight:600;color:{text_primary};margin-bottom:2px;">{title}</div><div style="font-size:0.75rem;color:{text_secondary};">{description}</div></div></div>'
    st.markdown(alert_html, unsafe_allow_html=True)


def render_stage_bar(name: str, actual: float, benchmark: float):
    """
    Render a horizontal progress bar showing actual vs benchmark.

    Args:
        name: Stage name
        actual: Actual value (minutes)
        benchmark: Benchmark value (minutes)
    """
    # Determine color based on performance
    if actual <= benchmark * 1.1:
        color = COLORS["success"]
    elif actual <= benchmark * 1.3:
        color = COLORS["warning"]
    else:
        color = COLORS["danger"]

    # Calculate widths (max 25 minutes for scale)
    max_val = 25
    actual_pct = min((actual / max_val) * 100, 100)
    benchmark_pct = min((benchmark / max_val) * 100, 100)

    text_primary = COLORS["text_primary"]
    text_muted = COLORS["text_muted"]

    bar_html = f'''<div style="margin-bottom:12px;">
<div style="display:flex;justify-content:space-between;margin-bottom:4px;">
<span style="font-size:0.82rem;font-weight:600;color:{text_primary};">{name}</span>
<span style="font-family:monospace;font-size:0.82rem;color:{color};">{actual:.1f}m <span style="color:{text_muted};">/ {benchmark:.0f}m</span></span>
</div>
<div style="height:8px;background:rgba(255,255,255,0.04);border-radius:4px;overflow:hidden;position:relative;">
<div style="position:absolute;width:{benchmark_pct}%;height:100%;background:rgba(148,163,184,0.08);border-radius:4px;"></div>
<div style="height:100%;width:{actual_pct}%;background:{color};border-radius:4px;transition:width 0.8s ease;"></div>
</div>
</div>'''
    st.markdown(bar_html, unsafe_allow_html=True)


def render_leaderboard(title: str, subtitle: str, rows: list):
    """
    Render a leaderboard with ranked items.
    Mobile-responsive with flexible widths.

    Args:
        title: Leaderboard title
        subtitle: Subtitle text
        rows: List of dicts with keys: rank, name, detail, value, progress
    """
    text_muted = COLORS["text_muted"]

    # Rank styling
    rank_styles = {
        1: ("rgba(245,158,11,0.15)", "#FCD34D"),  # Gold
        2: ("rgba(148,163,184,0.15)", "#CBD5E1"),  # Silver
        3: ("rgba(180,83,9,0.15)", "#FBBF24")      # Bronze
    }
    default_style = ("rgba(100,116,139,0.1)", text_muted)

    # Header
    header_html = f'<div style="font-size:clamp(0.85rem,2.5vw,0.95rem);font-weight:700;color:#E2E8F0;margin-bottom:4px;">{title}</div>'
    header_html += f'<div style="font-size:clamp(0.7rem,2vw,0.78rem);color:{text_muted};margin-bottom:1rem;">{subtitle}</div>'

    rows_html = ""
    for row in rows:
        rank = row.get("rank", 0)
        name = row.get("name", "")
        detail = row.get("detail", "")
        value = row.get("value", "")
        progress = row.get("progress", 0)

        rbg, rcol = rank_styles.get(rank, default_style)

        # Bar color based on progress
        bar_color = COLORS["success"] if progress >= 85 else COLORS["warning"] if progress >= 60 else COLORS["danger"]

        # Mobile-responsive row with flex-wrap
        rows_html += f'''<div class="leaderboard-row" style="display:flex;align-items:center;gap:clamp(0.4rem,2vw,0.7rem);padding:clamp(0.5rem,2vw,0.6rem) clamp(0.5rem,2vw,0.8rem);background:rgba(255,255,255,0.02);border-radius:10px;margin-bottom:0.35rem;flex-wrap:wrap;">
<div class="rank-badge" style="font-family:monospace;font-size:clamp(0.7rem,2vw,0.82rem);font-weight:700;width:clamp(22px,6vw,26px);height:clamp(22px,6vw,26px);display:flex;align-items:center;justify-content:center;border-radius:8px;background:{rbg};color:{rcol};flex-shrink:0;">{rank}</div>
<div style="flex:1 1 80px;min-width:60px;"><div class="name" style="font-size:clamp(0.75rem,2vw,0.82rem);font-weight:600;color:#E2E8F0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{name}</div><div class="detail" style="font-size:clamp(0.6rem,1.5vw,0.7rem);color:{text_muted};">{detail}</div></div>
<div class="progress-bar" style="flex:1 1 60px;min-width:40px;height:clamp(4px,1vw,6px);background:rgba(255,255,255,0.05);border-radius:3px;overflow:hidden;"><div style="height:100%;width:{progress}%;background:{bar_color};border-radius:3px;"></div></div>
<div class="value" style="font-family:monospace;font-size:clamp(0.7rem,2vw,0.82rem);font-weight:600;color:{bar_color};min-width:40px;text-align:right;flex-shrink:0;">{value}</div>
</div>'''

    st.markdown(header_html + rows_html, unsafe_allow_html=True)


def render_channel_stats(channels: list):
    """
    Render order channel breakdown.
    Mobile-responsive with wrapping.

    Args:
        channels: List of dicts with keys: name, pct, count (optional: color)
    """
    text_secondary = COLORS["text_secondary"]
    primary = COLORS["primary"]

    # Color palette for channels
    colors = [COLORS["primary"], COLORS["success"], COLORS["warning"], COLORS["secondary"]]

    items_html = ""
    for i, channel in enumerate(channels):
        name = channel.get("name", "Unknown")
        pct = channel.get("pct", 0)
        color = channel.get("color", colors[i % len(colors)])

        items_html += f'<div style="flex:1 1 60px;text-align:center;min-width:50px;"><div style="font-family:monospace;font-size:clamp(1rem,3vw,1.25rem);font-weight:700;color:{color};">{pct:.0f}%</div><div style="font-size:clamp(0.6rem,1.8vw,0.7rem);color:{text_secondary};margin-top:2px;">{name}</div></div>'

    container_html = f'<div style="display:flex;flex-wrap:wrap;gap:clamp(6px,2vw,10px);padding:0.75rem 0;justify-content:center;">{items_html}</div>'
    st.markdown(container_html, unsafe_allow_html=True)


def render_complaint_breakdown(reasons: list):
    """
    Render complaint reasons breakdown with mini progress bars.
    Mobile-responsive.

    Args:
        reasons: List of dicts with keys: name, count, pct
    """
    text_primary = COLORS["text_primary"]
    danger = COLORS["danger"]

    html = ""
    for reason in reasons:
        name = reason.get("name", "Unknown")
        count = reason.get("count", 0)
        pct = reason.get("pct", 0)

        html += f'<div style="display:flex;align-items:center;gap:clamp(4px,2vw,8px);margin-bottom:6px;flex-wrap:wrap;"><div style="flex:1 1 80px;font-size:clamp(0.7rem,2vw,0.8rem);color:{text_primary};min-width:60px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{name}</div><div style="flex:0 0 clamp(50px,15vw,80px);height:5px;background:rgba(255,255,255,0.05);border-radius:3px;overflow:hidden;"><div style="height:100%;width:{pct}%;background:{danger};border-radius:3px;"></div></div><div style="font-family:monospace;font-size:clamp(0.65rem,1.8vw,0.75rem);color:#FB7185;min-width:20px;text-align:right;">{count}</div></div>'

    st.markdown(html, unsafe_allow_html=True)
