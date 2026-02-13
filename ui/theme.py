"""
Color palette, fonts, and Plotly template for PizzaOps Intelligence.
Provides consistent styling across all visualizations.

FUTURISTIC TECH DESIGN SYSTEM:
- Deep navy backgrounds (#0a0e27 → #0d1b3e → #0a1628)
- Cyan/Electric Blue accent (#00b4ff)
- Teal glow secondary (#00e5ff)
- Glassmorphism cards with subtle cyan borders
- Premium dark corporate tech aesthetic
"""

import streamlit as st

# ── Primary Brand Colors (Futuristic Tech) ──
COLORS = {
    # Primary (Cyan/Electric Blue)
    "primary": "#00b4ff",
    "primary_dark": "#0090cc",
    "primary_light": "#00e5ff",
    "secondary": "#00e5ff",

    # Backgrounds
    "bg_dark": "#0a0e27",
    "bg_mid": "#0d1b3e",
    "bg_card": "rgba(10, 25, 60, 0.7)",
    "bg_elevated": "rgba(10, 25, 60, 0.85)",
    "sidebar": "#060d20",

    # Accents
    "accent_cyan": "#00b4ff",
    "accent_teal": "#00e5ff",
    "accent_purple": "#8b5cf6",

    # Status
    "success": "#00e5a0",
    "warning": "#f59e0b",
    "danger": "#ff6b6b",
    "info": "#00b4ff",

    # Text
    "text_primary": "#ffffff",
    "text_secondary": "#a8c4e0",
    "text_muted": "#6889a8",
    "placeholder": "#4a6a8a",

    # Borders
    "border": "rgba(0, 180, 255, 0.15)",
    "border_hover": "rgba(0, 180, 255, 0.3)",

    # Glow
    "glow": "rgba(0, 180, 255, 0.4)",
    "glow_soft": "rgba(0, 180, 255, 0.15)",

    # Pizza brand (keep for identity)
    "pizza_orange": "#FF6B35",

    # Chart palette
    "chart_palette": [
        "#00b4ff", "#00e5ff", "#00e5a0", "#ff6b6b",
        "#ffd93d", "#c084fc", "#f59e0b", "#84cc16"
    ],

    # Stage colors
    "stage_dough_prep": "#00b4ff",
    "stage_styling": "#00e5ff",
    "stage_oven": "#f59e0b",
    "stage_boxing": "#00e5a0",
    "stage_delivery": "#c084fc",

    # Area colors
    "area_A": "#00b4ff",
    "area_B": "#00e5a0",
    "area_C": "#f59e0b",
    "area_D": "#00e5ff",
    "area_E": "#ff6b6b",

    # Delay category colors
    "delay_on_time": "#00e5a0",
    "delay_at_risk": "#f59e0b",
    "delay_late": "#ff6b6b",
    "delay_critical": "#7F1D1D",
}

# ── Neon/Accent Colors ──
NEON = {
    "cyan": "#00b4ff",
    "teal": "#00e5ff",
    "green": "#00e5a0",
    "purple": "#c084fc",
    "pink": "#f472b6",
    "orange": "#f59e0b",
    "red": "#ff6b6b",
    "white": "#ffffff",
}

# Status to color mapping
NEON_STATUS = {
    "good": NEON["green"],
    "warning": NEON["orange"],
    "danger": NEON["red"],
    "neutral": NEON["cyan"],
    "info": NEON["teal"],
}

# ── Plotly Template ──
PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {
            "color": "#a8c4e0",
            "family": "Segoe UI, Roboto, sans-serif",
            "size": 12
        },
        "title": {
            "text": "",
            "font": {
                "color": "#ffffff",
                "size": 16
            }
        },
        "xaxis": {
            "gridcolor": "rgba(0, 180, 255, 0.08)",
            "linecolor": "rgba(0, 180, 255, 0.2)",
            "zerolinecolor": "rgba(0, 180, 255, 0.1)",
            "tickfont": {"color": "#a8c4e0"}
        },
        "yaxis": {
            "gridcolor": "rgba(0, 180, 255, 0.08)",
            "linecolor": "rgba(0, 180, 255, 0.2)",
            "zerolinecolor": "rgba(0, 180, 255, 0.1)",
            "tickfont": {"color": "#a8c4e0"}
        },
        "colorway": COLORS["chart_palette"],
        "margin": {"l": 40, "r": 20, "t": 50, "b": 40},
        "legend": {
            "bgcolor": "rgba(0,0,0,0)",
            "font": {"color": "#a8c4e0"}
        },
        "hoverlabel": {
            "bgcolor": "#0d1b3e",
            "font": {"color": "#ffffff"},
            "bordercolor": "#00b4ff"
        }
    }
}


def get_stage_color(stage: str) -> str:
    """Get color for a pipeline stage."""
    stage_key = f"stage_{stage.lower().replace(' ', '_')}"
    return COLORS.get(stage_key, COLORS["primary"])


def get_area_color(area: str) -> str:
    """Get color for a delivery area."""
    area_key = f"area_{area.upper()}"
    return COLORS.get(area_key, COLORS["primary"])


def get_delay_color(category: str) -> str:
    """Get color for a delay category."""
    delay_key = f"delay_{category.lower()}"
    return COLORS.get(delay_key, COLORS["text_muted"])


def get_status_color(status: str) -> str:
    """Get color based on status (good/warning/danger)."""
    return COLORS.get(status, COLORS["text_muted"])


def apply_plotly_theme(fig):
    """Apply the PizzaOps theme to a Plotly figure."""
    fig.update_layout(**PLOTLY_TEMPLATE["layout"])
    return fig


def get_plotly_theme() -> dict:
    """Return Plotly layout dict for consistent chart styling."""
    return PLOTLY_TEMPLATE["layout"].copy()


def inject_custom_css():
    """Inject all custom CSS styles into the page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def styled_metric_card(title: str, value: str, delta: str = None, status: str = "neutral") -> str:
    """
    Generate HTML for a styled metric card with the tech theme.

    Args:
        title: The metric label
        value: The metric value
        delta: Optional delta/change indicator
        status: 'good', 'warning', 'danger', or 'neutral'

    Returns:
        HTML string for the metric card
    """
    status_colors = {
        "good": COLORS["success"],
        "warning": COLORS["warning"],
        "danger": COLORS["danger"],
        "neutral": COLORS["primary"]
    }
    accent_color = status_colors.get(status, COLORS["primary"])

    delta_html = ""
    if delta:
        delta_html = f'<p style="color: {accent_color}; font-size: 0.85rem; margin: 0.5rem 0 0 0;">{delta}</p>'

    return f"""
    <div style="
        background: rgba(10, 25, 60, 0.6);
        border: 1px solid rgba(0, 180, 255, 0.12);
        border-radius: 12px;
        padding: 1.25rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, {accent_color}, {COLORS['primary_light']});
        "></div>
        <p style="
            color: {COLORS['text_muted']};
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin: 0 0 0.5rem 0;
            font-weight: 500;
        ">{title}</p>
        <h2 style="
            background: linear-gradient(135deg, #ffffff 0%, {accent_color} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2rem;
            font-weight: 800;
            margin: 0;
            line-height: 1.1;
        ">{value}</h2>
        {delta_html}
    </div>
    """


def styled_header(text: str, subtitle: str = "") -> str:
    """
    Generate HTML for a page header with cyan glow effect.

    Args:
        text: Main header text
        subtitle: Optional subtitle

    Returns:
        HTML string for the header
    """
    subtitle_html = ""
    if subtitle:
        subtitle_html = f'<p style="color: {COLORS["text_secondary"]}; font-size: 1rem; margin: 0.5rem 0 0 0;">{subtitle}</p>'

    return f"""
    <div style="margin-bottom: 1.5rem;">
        <h1 style="
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #ffffff 0%, {COLORS['primary']} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 40px rgba(0, 180, 255, 0.3);
            margin: 0;
            letter-spacing: -0.02em;
        ">{text}</h1>
        {subtitle_html}
    </div>
    """


# ── CSS Styles for Streamlit (Futuristic Tech Design System) ──
CUSTOM_CSS = """
<style>
/* ===== IMPORT FONTS ===== */
@import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;500;600;700;800&family=Roboto:wght@400;500;700&display=swap');

/* ===== KEYFRAME ANIMATIONS ===== */
@keyframes gradient-shift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
}

@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 20px rgba(0, 180, 255, 0.2); }
    50% { box-shadow: 0 0 40px rgba(0, 180, 255, 0.4); }
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

/* ===== FUTURISTIC TECH BACKGROUND ===== */
.stApp {
    background: linear-gradient(135deg, #0a0e27 0%, #0d1b3e 40%, #0a1628 100%);
    font-family: 'Segoe UI', 'Roboto', sans-serif;
}

/* Radial glow overlay at top */
.stApp::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(ellipse at 50% 0%, rgba(0, 180, 255, 0.08) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

/* Subtle grid overlay */
.stApp::after {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image:
        linear-gradient(rgba(0, 180, 255, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 180, 255, 0.02) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
    z-index: 0;
}

/* ===== NATIVE METRIC COMPONENT ===== */
[data-testid="stMetric"] {
    background: rgba(10, 25, 60, 0.6);
    backdrop-filter: blur(12px);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    border: 1px solid rgba(0, 180, 255, 0.12);
    transition: all 0.3s ease;
}

[data-testid="stMetric"]:hover {
    border-color: rgba(0, 180, 255, 0.3);
    box-shadow: 0 4px 25px rgba(0, 180, 255, 0.15);
    transform: translateY(-2px);
}

[data-testid="stMetricLabel"] {
    color: #6889a8 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 500;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}

[data-testid="stMetricDelta"] {
    font-size: 0.875rem !important;
}

/* ===== TECH CARDS ===== */
.tech-card {
    background: rgba(10, 25, 60, 0.6);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(0, 180, 255, 0.12);
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.3s ease;
}

.tech-card:hover {
    border-color: rgba(0, 180, 255, 0.3);
    box-shadow: 0 4px 25px rgba(0, 180, 255, 0.15);
    transform: translateY(-2px);
}

/* KPI Card (Tech) */
.kpi-card-tech {
    background: rgba(10, 25, 60, 0.6);
    border: 1px solid rgba(0, 180, 255, 0.12);
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.kpi-card-tech::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00b4ff, #00e5ff);
}

.kpi-card-tech:hover {
    border-color: rgba(0, 180, 255, 0.3);
    box-shadow: 0 4px 25px rgba(0, 180, 255, 0.2);
    transform: translateY(-3px);
}

.kpi-value-tech {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #FFFFFF 0%, #00b4ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
}

.kpi-value-tech.good {
    background: linear-gradient(135deg, #FFFFFF 0%, #00e5a0 100%);
    -webkit-background-clip: text;
    background-clip: text;
}

.kpi-value-tech.warning {
    background: linear-gradient(135deg, #FFFFFF 0%, #f59e0b 100%);
    -webkit-background-clip: text;
    background-clip: text;
}

.kpi-value-tech.danger {
    background: linear-gradient(135deg, #FFFFFF 0%, #ff6b6b 100%);
    -webkit-background-clip: text;
    background-clip: text;
}

.kpi-label-tech {
    color: #6889a8;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

/* ===== GRADIENT TEXT ===== */
.gradient-text {
    background: linear-gradient(135deg, #00b4ff 0%, #00e5ff 50%, #00e5a0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.gradient-text-cyan {
    background: linear-gradient(135deg, #FFFFFF 0%, #00b4ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ===== TECH BUTTONS ===== */
.stButton > button {
    background: linear-gradient(90deg, #00b4ff, #0090cc);
    border: none;
    border-radius: 25px;
    color: white;
    font-weight: 600;
    letter-spacing: 0.02em;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 180, 255, 0.3);
    padding: 0.625rem 1.5rem;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 20px rgba(0, 180, 255, 0.5);
    filter: brightness(1.1);
}

.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #00b4ff, #00e5ff);
    box-shadow: 0 4px 20px rgba(0, 180, 255, 0.4);
}

.stButton > button[kind="primary"]:hover {
    box-shadow: 0 0 25px rgba(0, 180, 255, 0.6);
}

.stButton > button[kind="secondary"] {
    background: transparent;
    border: 1px solid rgba(0, 180, 255, 0.5);
    color: #00b4ff;
    box-shadow: none;
}

.stButton > button[kind="secondary"]:hover {
    background: rgba(0, 180, 255, 0.1);
    border-color: #00b4ff;
}

/* ===== TECH HEADERS ===== */
h1, h2, h3 {
    background: linear-gradient(135deg, #ffffff 0%, #00b4ff 50%, #00e5ff 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
}

h1 {
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em;
}

h2 {
    font-size: 1.75rem !important;
    font-weight: 700 !important;
}

h3 {
    font-size: 1.25rem !important;
    font-weight: 600 !important;
}

/* ===== STATUS BADGES ===== */
.status-badge {
    display: inline-block;
    padding: 0.35rem 1rem;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.status-good {
    background: rgba(0, 229, 160, 0.15);
    color: #00e5a0;
    border: 1px solid rgba(0, 229, 160, 0.3);
}

.status-warning {
    background: rgba(245, 158, 11, 0.15);
    color: #f59e0b;
    border: 1px solid rgba(245, 158, 11, 0.3);
}

.status-danger {
    background: rgba(255, 107, 107, 0.15);
    color: #ff6b6b;
    border: 1px solid rgba(255, 107, 107, 0.3);
}

/* ===== ALERT CARDS ===== */
.alert-card {
    padding: 1.25rem;
    border-radius: 12px;
    margin-bottom: 0.75rem;
    border-left: 4px solid;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.alert-card:hover {
    transform: translateX(4px);
}

.alert-danger {
    background: linear-gradient(135deg, rgba(255, 107, 107, 0.08) 0%, rgba(255, 107, 107, 0.03) 100%);
    border-color: #ff6b6b;
}

.alert-warning {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(245, 158, 11, 0.03) 100%);
    border-color: #f59e0b;
}

.alert-success {
    background: linear-gradient(135deg, rgba(0, 229, 160, 0.08) 0%, rgba(0, 229, 160, 0.03) 100%);
    border-color: #00e5a0;
}

.alert-info {
    background: linear-gradient(135deg, rgba(0, 180, 255, 0.08) 0%, rgba(0, 180, 255, 0.03) 100%);
    border-color: #00b4ff;
}

/* ===== TABLE STYLING ===== */
.styled-table {
    width: 100%;
    border-collapse: collapse;
    background: rgba(10, 25, 60, 0.4);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    overflow: hidden;
}

.styled-table th {
    background: rgba(0, 180, 255, 0.15);
    color: #ffffff;
    text-align: left;
    padding: 1rem;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.08em;
    border-bottom: 1px solid rgba(0, 180, 255, 0.1);
}

.styled-table td {
    padding: 1rem;
    border-bottom: 1px solid rgba(0, 180, 255, 0.08);
    color: #a8c4e0;
    transition: all 0.2s ease;
}

.styled-table tr:nth-child(odd) {
    background: rgba(10, 25, 60, 0.4);
}

.styled-table tr:nth-child(even) {
    background: rgba(10, 25, 60, 0.2);
}

.styled-table tr:hover td {
    background: rgba(0, 180, 255, 0.05);
    color: #ffffff;
}

/* Streamlit dataframe styling */
.stDataFrame th {
    background: rgba(0, 180, 255, 0.15) !important;
    color: white !important;
    font-weight: bold !important;
}

.stDataFrame tr:nth-child(odd) {
    background: rgba(10, 25, 60, 0.4) !important;
}

.stDataFrame tr:nth-child(even) {
    background: rgba(10, 25, 60, 0.2) !important;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background-color: #060d20;
    border-right: 1px solid rgba(0, 180, 255, 0.1);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #a8c4e0;
}

/* ===== HIDE STREAMLIT BRANDING ===== */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #060d20;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #00b4ff, #00e5ff);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #00e5ff, #00b4ff);
}

/* ===== EXPANDER ===== */
.streamlit-expanderHeader {
    background: rgba(10, 25, 60, 0.6) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(0, 180, 255, 0.12) !important;
    transition: all 0.3s ease !important;
    color: #ffffff !important;
}

.streamlit-expanderHeader:hover {
    border-color: rgba(0, 180, 255, 0.3) !important;
}

details[open] .streamlit-expanderHeader {
    border-color: rgba(0, 180, 255, 0.3) !important;
}

/* ===== SECTION DIVIDERS ===== */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0, 180, 255, 0.3), transparent);
    margin: 2rem 0;
}

/* ===== INPUT STYLING ===== */
input, textarea, select {
    background: rgba(8, 18, 45, 0.8) !important;
    border: 1px solid rgba(0, 180, 255, 0.2) !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    transition: all 0.3s ease !important;
}

input:focus, textarea:focus, select:focus {
    border-color: #00b4ff !important;
    box-shadow: 0 0 10px rgba(0, 180, 255, 0.2) !important;
    outline: none !important;
}

input::placeholder {
    color: #4a6a8a !important;
}

/* ===== SELECTBOX ===== */
[data-baseweb="select"] {
    background: rgba(8, 18, 45, 0.8) !important;
}

[data-baseweb="select"] > div {
    background: rgba(8, 18, 45, 0.8) !important;
    border: 1px solid rgba(0, 180, 255, 0.2) !important;
    border-radius: 8px !important;
}

[data-baseweb="select"]:focus-within > div {
    border-color: #00b4ff !important;
    box-shadow: 0 0 10px rgba(0, 180, 255, 0.2) !important;
}

/* ===== MULTISELECT ===== */
[data-baseweb="tag"] {
    background: rgba(0, 180, 255, 0.2) !important;
    border: 1px solid rgba(0, 180, 255, 0.3) !important;
    color: #00b4ff !important;
}

/* ===== HERO SECTION ===== */
.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 0%, #00b4ff 50%, #00e5ff 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradient-shift 6s ease infinite;
    text-align: center;
    letter-spacing: -0.02em;
    text-shadow: 0 0 60px rgba(0, 180, 255, 0.3);
}

.hero-tagline {
    font-size: 1.25rem;
    color: #00b4ff;
    text-align: center;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    font-weight: 500;
}

/* ===== FEATURE CARDS ===== */
.feature-card {
    background: rgba(10, 25, 60, 0.6);
    backdrop-filter: blur(15px);
    border-radius: 16px;
    padding: 2rem;
    border: 1px solid rgba(0, 180, 255, 0.12);
    transition: all 0.4s ease;
    position: relative;
    overflow: hidden;
}

.feature-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00b4ff, #00e5ff, #00e5a0);
}

.feature-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 50px rgba(0, 180, 255, 0.15);
    border-color: rgba(0, 180, 255, 0.3);
}

.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.feature-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.5rem;
}

.feature-desc {
    color: #a8c4e0;
    font-size: 0.9rem;
    line-height: 1.6;
}

/* ===== CTA BUTTON ===== */
.cta-button {
    display: inline-block;
    padding: 1rem 2.5rem;
    font-size: 1rem;
    font-weight: 600;
    color: white;
    background: linear-gradient(90deg, #00b4ff 0%, #00e5ff 100%);
    border: none;
    border-radius: 50px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 20px rgba(0, 180, 255, 0.4);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.cta-button:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 30px rgba(0, 180, 255, 0.6);
}

/* ===== GLASS CONTAINER ===== */
.glass-container {
    background: rgba(10, 25, 60, 0.6);
    backdrop-filter: blur(20px);
    border-radius: 16px;
    padding: 2rem;
    border: 1px solid rgba(0, 180, 255, 0.1);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

/* ===== MODE SELECTOR ===== */
.mode-button {
    flex: 1;
    padding: 1rem;
    border-radius: 12px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 600;
    letter-spacing: 0.02em;
}

.mode-button.lite {
    background: rgba(0, 229, 160, 0.1);
    border: 2px solid rgba(0, 229, 160, 0.4);
    color: #00e5a0;
}

.mode-button.lite:hover {
    background: rgba(0, 229, 160, 0.15);
    transform: translateY(-2px);
}

.mode-button.pro {
    background: rgba(0, 180, 255, 0.1);
    border: 2px solid rgba(0, 180, 255, 0.4);
    color: #00b4ff;
}

.mode-button.pro:hover {
    background: rgba(0, 180, 255, 0.15);
    transform: translateY(-2px);
}

.mode-button.active {
    transform: scale(1.02);
}

.mode-button.lite.active {
    background: rgba(0, 229, 160, 0.2);
    box-shadow: 0 0 20px rgba(0, 229, 160, 0.2);
}

.mode-button.pro.active {
    background: rgba(0, 180, 255, 0.2);
    box-shadow: 0 0 20px rgba(0, 180, 255, 0.2);
}

/* ===== BUDGET INDICATOR ===== */
.budget-indicator {
    background: rgba(10, 25, 60, 0.6);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    border: 1px solid rgba(0, 180, 255, 0.12);
}

.budget-bar {
    height: 6px;
    background: rgba(10, 25, 60, 0.8);
    border-radius: 3px;
    overflow: hidden;
    margin-top: 0.75rem;
}

.budget-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.5s ease;
}

.budget-fill.ok {
    background: linear-gradient(90deg, #00e5a0 0%, #00ffc8 100%);
}

.budget-fill.warning {
    background: linear-gradient(90deg, #f59e0b 0%, #fcd34d 100%);
}

.budget-fill.danger {
    background: linear-gradient(90deg, #ff6b6b 0%, #fca5a5 100%);
}

/* ===== TABS ===== */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: transparent;
}

.stTabs [data-baseweb="tab"] {
    background-color: rgba(10, 25, 60, 0.6);
    border: 1px solid rgba(0, 180, 255, 0.12);
    border-radius: 8px;
    color: #a8c4e0;
    padding: 0.5rem 1rem;
}

.stTabs [data-baseweb="tab"]:hover {
    background-color: rgba(0, 180, 255, 0.1);
    border-color: rgba(0, 180, 255, 0.3);
}

.stTabs [aria-selected="true"] {
    background-color: rgba(0, 180, 255, 0.2) !important;
    border-color: #00b4ff !important;
    color: #00b4ff !important;
}

/* ===== CHECKBOX ===== */
.stCheckbox label {
    color: #a8c4e0 !important;
}

.stCheckbox [data-testid="stCheckbox"] > label > div:first-child {
    border-color: rgba(0, 180, 255, 0.3) !important;
}

.stCheckbox [data-testid="stCheckbox"] > label > div:first-child[data-checked="true"] {
    background-color: #00b4ff !important;
    border-color: #00b4ff !important;
}

/* ===== SLIDER ===== */
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background-color: #00b4ff !important;
}

.stSlider [data-baseweb="slider"] [data-testid="stTickBar"] > div {
    background: linear-gradient(90deg, #00b4ff, #00e5ff) !important;
}

/* ===== FILE UPLOADER ===== */
[data-testid="stFileUploader"] {
    background: rgba(10, 25, 60, 0.4);
    border: 2px dashed rgba(0, 180, 255, 0.3);
    border-radius: 12px;
    padding: 1rem;
}

[data-testid="stFileUploader"]:hover {
    border-color: rgba(0, 180, 255, 0.5);
    background: rgba(10, 25, 60, 0.6);
}

/* ===== PROGRESS BAR ===== */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #00b4ff, #00e5ff) !important;
}

/* ===== MOBILE RESPONSIVE ===== */
@media (max-width: 768px) {
    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        gap: 0.75rem !important;
    }

    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }

    .kpi-card-tech, .tech-card {
        padding: 1rem;
        margin-bottom: 0.5rem;
    }

    .kpi-value-tech {
        font-size: 1.75rem;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
    }

    .stButton > button {
        min-height: 48px !important;
        font-size: 0.95rem !important;
        padding: 0.75rem 1.25rem !important;
    }

    h1 {
        font-size: 1.75rem !important;
    }

    h2 {
        font-size: 1.35rem !important;
    }

    h3 {
        font-size: 1.1rem !important;
    }

    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .hero-title {
        font-size: 2.25rem;
    }

    .feature-card {
        padding: 1.5rem;
    }
}

@media (max-width: 480px) {
    .kpi-value-tech {
        font-size: 1.5rem;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.25rem !important;
    }

    .main .block-container {
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }

    .hero-title {
        font-size: 1.75rem;
    }
}

/* ===== MOBILE-FIRST ENHANCEMENTS ===== */

/* Force column stacking on mobile */
@media (max-width: 640px) {
    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        gap: 0.75rem !important;
    }

    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
}

/* Small phone optimizations (480px and below) */
@media (max-width: 480px) {
    /* Typography scaling */
    h1 {
        font-size: 1.5rem !important;
        line-height: 1.3 !important;
    }

    h2 {
        font-size: 1.25rem !important;
    }

    h3 {
        font-size: 1.1rem !important;
    }

    /* Tighter padding for cards */
    .tech-card, .kpi-card-tech, [data-testid="stMetric"] {
        padding: 0.875rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* KPI values smaller */
    .kpi-value-tech {
        font-size: 1.35rem !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.15rem !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.65rem !important;
    }

    /* Container breathing room */
    .main .block-container {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        padding-top: 1rem !important;
    }

    /* Buttons touch-friendly */
    .stButton > button {
        min-height: 48px !important;
        font-size: 0.9rem !important;
        padding: 0.75rem 1rem !important;
    }

    /* Expander headers readable */
    .streamlit-expanderHeader, [data-testid="stExpander"] summary {
        font-size: 0.9rem !important;
        padding: 0.75rem 1rem !important;
    }

    /* Sidebar nav cards smaller */
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
        padding: 0.65rem 0.75rem !important;
        margin: 0.35rem 0.5rem !important;
        font-size: 0.85rem !important;
    }

    /* File uploader compact */
    [data-testid="stFileUploader"] {
        padding: 1rem !important;
    }

    /* Tabs scroll horizontally if needed */
    .stTabs [data-baseweb="tab-list"] {
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 0.75rem !important;
        font-size: 0.8rem !important;
        white-space: nowrap !important;
    }

    /* Checkbox/radio touch targets */
    .stCheckbox label, .stRadio label {
        padding: 0.5rem 0 !important;
        min-height: 44px !important;
        display: flex !important;
        align-items: center !important;
    }

    /* Alert messages compact */
    [data-testid="stAlert"] {
        padding: 0.75rem 1rem !important;
        font-size: 0.85rem !important;
    }

    /* Selectbox compact */
    [data-baseweb="select"] > div {
        min-height: 44px !important;
    }
}

/* Very small phones (360px) */
@media (max-width: 360px) {
    h1 {
        font-size: 1.35rem !important;
    }

    h2 {
        font-size: 1.15rem !important;
    }

    .kpi-value-tech, [data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
    }

    .main .block-container {
        padding-left: 0.35rem !important;
        padding-right: 0.35rem !important;
    }

    .stButton > button {
        font-size: 0.85rem !important;
    }
}

/* Landscape phone optimization */
@media (max-height: 500px) and (orientation: landscape) {
    .main .block-container {
        padding-top: 0.5rem !important;
    }

    [data-testid="stMetric"] {
        padding: 0.5rem !important;
    }
}

/* ===== CAPTION STYLING ===== */
.stCaption {
    color: #6889a8 !important;
    font-size: 0.75rem !important;
}

/* ===== FIX FOR EMBEDDED HTML ===== */
.stMarkdown div[style] {
    max-width: 100%;
}

/* ===== CONTAINER STYLING ===== */
[data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > [data-testid="stVerticalBlock"] {
    gap: 0.75rem;
}

/* ===== TOAST/NOTIFICATIONS ===== */
[data-testid="stToast"] {
    background: rgba(10, 25, 60, 0.95) !important;
    border: 1px solid rgba(0, 180, 255, 0.3) !important;
    border-radius: 12px !important;
}

/* ===== SPINNER ===== */
.stSpinner > div {
    border-top-color: #00b4ff !important;
}

/* ===== SUCCESS/ERROR/WARNING/INFO BOXES ===== */
.stSuccess {
    background-color: rgba(0, 229, 160, 0.1) !important;
    border-left: 4px solid #00e5a0 !important;
    color: #a8c4e0 !important;
}

.stError {
    background-color: rgba(255, 107, 107, 0.1) !important;
    border-left: 4px solid #ff6b6b !important;
    color: #a8c4e0 !important;
}

.stWarning {
    background-color: rgba(245, 158, 11, 0.1) !important;
    border-left: 4px solid #f59e0b !important;
    color: #a8c4e0 !important;
}

.stInfo {
    background-color: rgba(0, 180, 255, 0.1) !important;
    border-left: 4px solid #00b4ff !important;
    color: #a8c4e0 !important;
}

/* ===== POLISH: ENHANCED ALERTS ===== */
[data-testid="stAlert"] {
    backdrop-filter: blur(10px) !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    margin-bottom: 1rem !important;
}

/* ===== POLISH: FILE UPLOADER ENHANCEMENT ===== */
[data-testid="stFileUploader"] {
    background: rgba(10, 25, 60, 0.4) !important;
    border: 2px dashed rgba(0, 180, 255, 0.3) !important;
    border-radius: 16px !important;
    padding: 2rem !important;
    transition: all 0.3s ease !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: rgba(0, 180, 255, 0.6) !important;
    background: rgba(10, 25, 60, 0.6) !important;
    box-shadow: 0 0 20px rgba(0, 180, 255, 0.15) !important;
}

[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
}

/* ===== POLISH: SIDEBAR ENHANCEMENTS ===== */
[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-checked="true"] {
    background: rgba(0, 180, 255, 0.15) !important;
    border-left: 3px solid #00b4ff !important;
    padding-left: 0.75rem !important;
}

[data-testid="stSidebar"] a[href] {
    color: #a8c4e0 !important;
    transition: all 0.2s ease !important;
}

[data-testid="stSidebar"] a[href]:hover {
    color: #00b4ff !important;
    padding-left: 4px !important;
}

/* ===== FLUORESCENT SIDEBAR NAVIGATION CARDS ===== */
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
    display: block !important;
    margin: 0.5rem 0.75rem !important;
    padding: 0.875rem 1rem !important;
    background: rgba(10, 25, 60, 0.6) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(0, 180, 255, 0.15) !important;
    color: #a8c4e0 !important;
    text-decoration: none !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
    position: relative !important;
    overflow: hidden !important;
}

/* Fluorescent glow on hover */
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
    background: rgba(0, 180, 255, 0.12) !important;
    border-color: rgba(0, 180, 255, 0.4) !important;
    color: #00e5ff !important;
    box-shadow:
        0 0 15px rgba(0, 180, 255, 0.3),
        0 0 30px rgba(0, 180, 255, 0.2),
        inset 0 0 20px rgba(0, 180, 255, 0.05) !important;
    transform: translateX(4px) !important;
}

/* Active/current page styling with stronger glow */
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"],
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a.active {
    background: linear-gradient(135deg, rgba(0, 180, 255, 0.15) 0%, rgba(0, 229, 255, 0.08) 100%) !important;
    border-color: rgba(0, 180, 255, 0.5) !important;
    color: #00e5ff !important;
    box-shadow:
        0 0 20px rgba(0, 180, 255, 0.4),
        0 0 40px rgba(0, 180, 255, 0.2),
        inset 0 0 30px rgba(0, 180, 255, 0.08) !important;
}

/* Top gradient accent line on hover */
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a::before {
    content: '' !important;
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    height: 2px !important;
    background: linear-gradient(90deg, transparent, rgba(0, 180, 255, 0.6), transparent) !important;
    opacity: 0 !important;
    transition: opacity 0.3s ease !important;
}

[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover::before,
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"]::before {
    opacity: 1 !important;
}

/* Icon styling in sidebar nav */
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a span[data-testid="stIconMaterial"],
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a svg {
    color: #00b4ff !important;
    filter: drop-shadow(0 0 4px rgba(0, 180, 255, 0.4)) !important;
    transition: all 0.3s ease !important;
}

[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover span[data-testid="stIconMaterial"],
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover svg {
    filter: drop-shadow(0 0 8px rgba(0, 180, 255, 0.6)) !important;
}

/* Page title text glow on hover */
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover span {
    text-shadow: 0 0 10px rgba(0, 180, 255, 0.5) !important;
}

/* Sidebar container padding adjustment */
[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
    padding: 0.5rem 0 !important;
}

/* Pulsing glow animation for active page */
@keyframes sidebar-pulse {
    0%, 100% {
        box-shadow:
            0 0 15px rgba(0, 180, 255, 0.3),
            0 0 30px rgba(0, 180, 255, 0.15);
    }
    50% {
        box-shadow:
            0 0 25px rgba(0, 180, 255, 0.5),
            0 0 50px rgba(0, 180, 255, 0.25);
    }
}

[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
    animation: sidebar-pulse 3s ease-in-out infinite !important;
}

/* ===== POLISH: EXPANDER ENHANCEMENT ===== */
[data-testid="stExpander"] {
    background: rgba(10, 25, 60, 0.5) !important;
    border: 1px solid rgba(0, 180, 255, 0.12) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

[data-testid="stExpander"] summary {
    padding: 1rem 1.25rem !important;
    color: #ffffff !important;
    font-weight: 500 !important;
}

[data-testid="stExpander"] summary:hover {
    background: rgba(0, 180, 255, 0.05) !important;
}

[data-testid="stExpander"][open] {
    border-color: rgba(0, 180, 255, 0.25) !important;
}

[data-testid="stExpander"] svg {
    color: #00b4ff !important;
}

/* ===== POLISH: NUMBER INPUT ===== */
[data-testid="stNumberInput"] input {
    background: rgba(8, 18, 45, 0.8) !important;
    border: 1px solid rgba(0, 180, 255, 0.2) !important;
    border-radius: 8px !important;
    color: #ffffff !important;
}

[data-testid="stNumberInput"] button {
    background: rgba(0, 180, 255, 0.15) !important;
    border: 1px solid rgba(0, 180, 255, 0.2) !important;
    color: #00b4ff !important;
}

[data-testid="stNumberInput"] button:hover {
    background: rgba(0, 180, 255, 0.25) !important;
}

.stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] {
    background: #00b4ff !important;
    color: white !important;
}

/* ===== POLISH: THIN SCROLLBAR ===== */
::-webkit-scrollbar {
    width: 6px !important;
    height: 6px !important;
}

::-webkit-scrollbar-track {
    background: rgba(6, 13, 32, 0.5) !important;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #00b4ff, #0090cc) !important;
    border-radius: 3px !important;
}

/* ===== POLISH: TOOLTIP STYLING ===== */
[data-testid="stTooltipIcon"] {
    color: #00b4ff !important;
}

div[data-baseweb="tooltip"] {
    background: rgba(13, 27, 62, 0.95) !important;
    border: 1px solid rgba(0, 180, 255, 0.3) !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
}

/* ===== POLISH: SPINNER & PROGRESS ===== */
.stSpinner > div > div {
    border-color: rgba(0, 180, 255, 0.2) !important;
    border-top-color: #00b4ff !important;
}

.stProgress > div > div {
    background: rgba(10, 25, 60, 0.6) !important;
    border-radius: 10px !important;
}

.stProgress > div > div > div {
    background: linear-gradient(90deg, #00b4ff, #00e5ff) !important;
    border-radius: 10px !important;
    box-shadow: 0 0 10px rgba(0, 180, 255, 0.4) !important;
}

/* ===== POLISH: TOAST ENHANCEMENT ===== */
[data-testid="stToast"] {
    background: rgba(10, 25, 60, 0.95) !important;
    backdrop-filter: blur(15px) !important;
    border: 1px solid rgba(0, 180, 255, 0.25) !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
}

/* ===== POLISH: DROPDOWN MENUS ===== */
[data-baseweb="popover"] {
    background: rgba(13, 27, 62, 0.98) !important;
    border: 1px solid rgba(0, 180, 255, 0.2) !important;
    border-radius: 8px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5) !important;
}

[data-baseweb="popover"] li {
    color: #a8c4e0 !important;
}

[data-baseweb="popover"] li:hover {
    background: rgba(0, 180, 255, 0.15) !important;
    color: #ffffff !important;
}

[data-baseweb="popover"] li[aria-selected="true"] {
    background: rgba(0, 180, 255, 0.25) !important;
    color: #00b4ff !important;
}

/* ===== POLISH: TEXT INPUT FOCUS GLOW ===== */
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #00b4ff !important;
    box-shadow: 0 0 0 2px rgba(0, 180, 255, 0.15), 0 0 15px rgba(0, 180, 255, 0.2) !important;
}

/* ===== POLISH: TABS ENHANCEMENT ===== */
.stTabs [data-baseweb="tab"] {
    transition: all 0.2s ease !important;
    position: relative !important;
}

.stTabs [aria-selected="true"]::after {
    content: '' !important;
    position: absolute !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    height: 2px !important;
    background: linear-gradient(90deg, #00b4ff, #00e5ff) !important;
}

/* ===== POLISH: METRIC HOVER GLOW ===== */
[data-testid="stMetric"]:hover {
    box-shadow: 0 0 25px rgba(0, 180, 255, 0.2) !important;
}

/* ===== POLISH: DATAFRAME STYLING ===== */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid rgba(0, 180, 255, 0.12) !important;
}

[data-testid="stDataFrame"] th {
    background: rgba(0, 180, 255, 0.12) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.05em !important;
}

[data-testid="stDataFrame"] td {
    color: #a8c4e0 !important;
    border-bottom: 1px solid rgba(0, 180, 255, 0.06) !important;
}

[data-testid="stDataFrame"] tr:hover td {
    background: rgba(0, 180, 255, 0.08) !important;
}

/* ===== POLISH: DIVIDERS ===== */
hr, [data-testid="stMarkdown"] hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(0, 180, 255, 0.25), transparent) !important;
    margin: 2rem 0 !important;
}

/* ===== POLISH: LINK STYLING ===== */
.stMarkdown a {
    color: #00b4ff !important;
    text-decoration: none !important;
    transition: all 0.2s ease !important;
}

.stMarkdown a:hover {
    color: #00e5ff !important;
    text-shadow: 0 0 8px rgba(0, 180, 255, 0.4) !important;
}

/* ===== POLISH: CHECKBOX & RADIO ===== */
[data-testid="stCheckbox"] span[data-checked="true"]::before {
    background: linear-gradient(135deg, #00b4ff, #00e5ff) !important;
}

.stRadio [role="radio"][aria-checked="true"] {
    border-color: #00b4ff !important;
}

.stRadio [role="radio"][aria-checked="true"]::before {
    background: #00b4ff !important;
}

/* ===== POLISH: MICRO-ANIMATIONS ===== */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.tech-card, .kpi-card-tech, [data-testid="stMetric"] {
    animation: fadeInUp 0.4s ease-out;
}

button, input, select, textarea, .tech-card, [data-testid="stMetric"] {
    transition: all 0.25s ease !important;
}

/* ===== POLISH: PAGE CONTAINER ===== */
.main .block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1200px !important;
}

/* ===== POLISH: EMPTY STATE ===== */
.empty-state-container {
    text-align: center;
    padding: 4rem 2rem;
    background: rgba(10, 25, 60, 0.4);
    border-radius: 16px;
    border: 1px dashed rgba(0, 180, 255, 0.2);
    animation: fadeInUp 0.5s ease-out;
}

.empty-state-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    opacity: 0.7;
}

.empty-state-title {
    color: #ffffff;
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.empty-state-message {
    color: #6889a8;
    font-size: 1rem;
    margin-bottom: 0;
}

.empty-state-cta {
    display: inline-block;
    margin-top: 1.5rem;
    padding: 0.75rem 2rem;
    background: linear-gradient(90deg, #00b4ff, #00e5ff);
    color: white !important;
    border-radius: 25px;
    text-decoration: none !important;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 180, 255, 0.3);
}

.empty-state-cta:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 25px rgba(0, 180, 255, 0.5);
}
</style>
"""
