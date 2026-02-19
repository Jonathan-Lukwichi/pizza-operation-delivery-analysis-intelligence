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

    Args:
        title: Main title text
        logo_text: Single letter for logo badge
        logo_color: Color for the logo (default: primary)
        is_live: Whether to show live indicator
        live_text: Text for live indicator
    """
    inject_custom_css()

    if logo_color is None:
        logo_color = COLORS["primary"]

    live_html = ""
    if is_live:
        live_html = f'''
        <div style="
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(0, 229, 160, 0.1);
            border: 1px solid rgba(0, 229, 160, 0.3);
            border-radius: 20px;
            padding: 0.35rem 1rem;
        ">
            <div style="
                width: 8px;
                height: 8px;
                background: {COLORS["success"]};
                border-radius: 50%;
                animation: pulse-glow 2s ease-in-out infinite;
                box-shadow: 0 0 8px {COLORS["success"]};
            "></div>
            <span style="
                color: {COLORS["success"]};
                font-size: 0.7rem;
                font-weight: 600;
                letter-spacing: 0.1em;
                text-transform: uppercase;
            ">{live_text}</span>
        </div>
        '''

    header_html = f'''
    <style>
        @keyframes pulse-glow {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.6; transform: scale(1.1); }}
        }}
    </style>
    <div style="
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid rgba(0, 180, 255, 0.15);
    ">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="
                width: 56px;
                height: 56px;
                background: linear-gradient(135deg, {logo_color} 0%, {COLORS["secondary"]} 100%);
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.75rem;
                font-weight: 800;
                color: white;
                box-shadow: 0 8px 25px rgba(0, 180, 255, 0.3);
                border: 2px solid rgba(255, 255, 255, 0.1);
            ">{logo_text}</div>
            <div>
                <h1 style="
                    font-size: 1.75rem;
                    font-weight: 700;
                    color: {COLORS["text_primary"]};
                    margin: 0;
                    line-height: 1.2;
                ">{title}</h1>
                <p style="
                    color: {COLORS["text_muted"]};
                    font-size: 0.85rem;
                    margin: 0.25rem 0 0 0;
                ">Real-time operational insights</p>
            </div>
        </div>
        {live_html}
    </div>
    '''
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

        items_html += f'''
        <div style="
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.6rem 1rem;
            background: {bg};
            border: 1px solid {border};
            border-radius: 10px;
            transition: all 0.3s ease;
            box-shadow: {glow};
        ">
            <span style="font-size: 1rem;">{icon}</span>
            <span style="
                color: {text_color};
                font-size: 0.75rem;
                font-weight: 600;
                letter-spacing: 0.05em;
                text-transform: uppercase;
            ">{label}</span>
        </div>
        '''

    st.markdown(f'''
    <div style="
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    ">{items_html}</div>
    ''', unsafe_allow_html=True)


def render_section_title(title: str, subtitle: str = "", icon: str = ""):
    """
    Render an enhanced section title with optional icon and subtitle.
    """
    icon_html = f'<span style="margin-right: 0.5rem;">{icon}</span>' if icon else ""
    subtitle_html = f'<p style="color: {COLORS["text_muted"]}; font-size: 0.85rem; margin: 0.25rem 0 0 0;">{subtitle}</p>' if subtitle else ""

    st.markdown(f'''
    <div style="margin: 2rem 0 1.25rem 0;">
        <h3 style="
            color: {COLORS["text_primary"]};
            font-size: 1.15rem;
            font-weight: 600;
            margin: 0;
            display: flex;
            align-items: center;
        ">
            {icon_html}
            {title}
        </h3>
        {subtitle_html}
    </div>
    ''', unsafe_allow_html=True)


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
