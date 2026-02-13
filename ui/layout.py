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
