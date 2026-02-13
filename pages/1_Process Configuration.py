"""
Page: Process Configuration
Purpose: Configure delivery process parameters, thresholds, and targets
         Set up BEFORE detecting problems for accurate analysis
"""

import streamlit as st
import json

from core.config import (
    get_config, save_config, BusinessConfig, StageConfig,
    export_config_json, import_config_json, set_mode, get_mode
)
from ui.layout import page_header, spacer
from ui.theme import COLORS, NEON

# Try to import budget tracker
try:
    from ai.budget_tracker import get_budget_tracker
    BUDGET_AVAILABLE = True
except ImportError:
    BUDGET_AVAILABLE = False


# ── Page Config ──
st.set_page_config(page_title="Process Configuration | PizzaOps", page_icon="⚙️", layout="wide")

page_header(
    title="Process Configuration",
    icon="⚙️",
    description="Define your delivery targets and thresholds before detecting problems"
)

# Get current config
config = get_config()

spacer("1rem")

# ══════════════════════════════════════════════════════════════════════════════
# BUSINESS BRANDING
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("Business Branding", expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        new_business_name = st.text_input(
            "Business Name",
            value=config.business_name,
            help="Your pizza business name"
        )

    with col2:
        new_tagline = st.text_input(
            "Tagline",
            value=config.tagline,
            help="Short description shown in sidebar"
        )

# ══════════════════════════════════════════════════════════════════════════════
# DELIVERY TARGETS
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("Delivery Targets", expanded=True):
    st.markdown("Set your target times and thresholds")

    col1, col2, col3 = st.columns(3)

    with col1:
        new_delivery_target = st.number_input(
            "Target Delivery Time (min)",
            min_value=10,
            max_value=120,
            value=config.delivery_target_minutes,
            help="Maximum acceptable delivery time"
        )

    with col2:
        new_warning_time = st.number_input(
            "Warning Threshold (min)",
            min_value=10,
            max_value=120,
            value=config.delivery_warning_minutes,
            help="At-risk threshold"
        )

    with col3:
        new_critical_time = st.number_input(
            "Critical Threshold (min)",
            min_value=10,
            max_value=120,
            value=config.delivery_critical_minutes,
            help="Unacceptable delivery time"
        )

# ══════════════════════════════════════════════════════════════════════════════
# KPI THRESHOLDS
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("KPI Thresholds", expanded=True):
    st.markdown("Set your performance targets")

    col1, col2, col3 = st.columns(3)

    with col1:
        new_on_time_target = st.slider(
            "On-Time Target (%)",
            min_value=50,
            max_value=100,
            value=int(config.on_time_target_pct),
            help="Target percentage of on-time deliveries"
        )

    with col2:
        new_complaint_target = st.slider(
            "Max Complaint Rate (%)",
            min_value=1,
            max_value=20,
            value=int(config.complaint_target_pct),
            help="Maximum acceptable complaint rate"
        )

    with col3:
        new_avg_target = st.number_input(
            "Avg Delivery Target (min)",
            min_value=10,
            max_value=60,
            value=int(config.avg_delivery_target_min),
            help="Target average delivery time"
        )

# ══════════════════════════════════════════════════════════════════════════════
# PEAK HOURS
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("Peak Hours", expanded=False):
    st.markdown("Define your rush hours for analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Lunch Rush**")
        lunch_col1, lunch_col2 = st.columns(2)
        with lunch_col1:
            new_lunch_start = st.number_input("Start", min_value=0, max_value=23, value=config.peak_lunch_start, key="lunch_start")
        with lunch_col2:
            new_lunch_end = st.number_input("End", min_value=0, max_value=23, value=config.peak_lunch_end, key="lunch_end")

    with col2:
        st.markdown("**Dinner Rush**")
        dinner_col1, dinner_col2 = st.columns(2)
        with dinner_col1:
            new_dinner_start = st.number_input("Start", min_value=0, max_value=23, value=config.peak_dinner_start, key="dinner_start")
        with dinner_col2:
            new_dinner_end = st.number_input("End", min_value=0, max_value=23, value=config.peak_dinner_end, key="dinner_end")

# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE STAGES
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("Pipeline Stages", expanded=False):
    st.markdown("Configure your production stages and targets")

    new_stages = []
    for i, stage in enumerate(config.stages):
        st.markdown(f"**Stage {i+1}: {stage.name}**")
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

        with col1:
            stage_name = st.text_input(
                "Name",
                value=stage.name,
                key=f"stage_name_{i}",
                label_visibility="collapsed"
            )

        with col2:
            stage_target = st.number_input(
                "Target (min)",
                min_value=1,
                max_value=60,
                value=int(stage.target_minutes),
                key=f"stage_target_{i}"
            )

        with col3:
            stage_p95 = st.number_input(
                "P95 Max (min)",
                min_value=1,
                max_value=60,
                value=int(stage.p95_max_minutes),
                key=f"stage_p95_{i}"
            )

        with col4:
            stage_color = st.color_picker(
                "Color",
                value=stage.color,
                key=f"stage_color_{i}"
            )

        new_stages.append(StageConfig(
            id=stage.id,
            name=stage_name,
            column_name=stage.column_name,
            target_minutes=stage_target,
            p95_max_minutes=stage_p95,
            color=stage_color
        ))

        if i < len(config.stages) - 1:
            st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# AI API KEY CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("AI API Key (Pro Mode)", expanded=False):
    st.markdown("Configure your Anthropic API key for AI-powered features")

    # Check current API key status
    import os
    from dotenv import load_dotenv
    load_dotenv()

    env_key = os.getenv("ANTHROPIC_API_KEY")
    session_key = st.session_state.get("user_api_key", "")

    # Determine current key source
    if env_key and env_key != "your_api_key_here":
        st.success("✓ API key configured via environment variable")
        key_source = "environment"
    elif session_key:
        st.info("API key configured for this session only")
        key_source = "session"
    else:
        st.warning("No API key configured - AI features disabled")
        key_source = None

    st.markdown("---")

    # API Key input
    new_api_key = st.text_input(
        "Anthropic API Key",
        value=session_key,
        type="password",
        placeholder="sk-ant-api03-...",
        help="Get your key at https://console.anthropic.com/"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save API Key (Session)", use_container_width=True):
            if new_api_key and new_api_key.startswith("sk-"):
                st.session_state.user_api_key = new_api_key
                st.success("API key saved! AI features now available.")
                st.rerun()
            elif new_api_key:
                st.error("Invalid API key format. Should start with 'sk-'")
            else:
                st.warning("Please enter an API key")

    with col2:
        if st.button("🗑️ Clear API Key", use_container_width=True):
            if "user_api_key" in st.session_state:
                del st.session_state.user_api_key
                st.success("API key cleared")
                st.rerun()

    # Help text
    st.markdown("---")
    st.markdown(f"""
    <div style="background: rgba(0, 180, 255, 0.1); border: 1px solid rgba(0, 180, 255, 0.3); border-radius: 8px; padding: 1rem;">
        <p style="color: {COLORS['primary']}; font-weight: bold; margin: 0 0 0.5rem 0;">💡 For permanent setup:</p>
        <ol style="color: {COLORS['text_secondary']}; font-size: 0.85rem; margin: 0; padding-left: 1.25rem;">
            <li>Create a <code>.env</code> file in the project root</li>
            <li>Add: <code>ANTHROPIC_API_KEY=your_key_here</code></li>
            <li>Restart the app</li>
        </ol>
        <p style="color: {COLORS['text_muted']}; font-size: 0.8rem; margin: 0.75rem 0 0 0;">
            Or set it in Streamlit Cloud secrets for deployment.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# AI BUDGET (PRO MODE)
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("AI Budget (Pro Mode)", expanded=False):
    st.markdown("Control your AI spending in South African Rand")

    col1, col2 = st.columns(2)

    with col1:
        new_budget = st.number_input(
            "Daily Budget (ZAR)",
            min_value=0.0,
            max_value=500.0,
            value=config.daily_budget_zar,
            step=10.0,
            help="Set to 0 to disable AI features"
        )
        st.caption("R50 is approximately $2.70 USD")

    with col2:
        if BUDGET_AVAILABLE:
            tracker = get_budget_tracker()
            status = tracker.get_status()
            st.metric("Spent Today", f"R{status.spent_zar:.2f}")
            st.metric("Remaining", f"R{status.remaining_zar:.2f}")

            if st.button("Reset Daily Budget"):
                st.session_state.session_cost_usd = 0.0
                st.session_state.session_queries = 0
                st.success("Budget reset!")
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# MODE SELECTION - NEON STYLE
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("App Mode", expanded=False):
    st.markdown("Choose between Lite (offline) and Pro (AI-powered) modes")

    current_mode = get_mode()

    col1, col2 = st.columns(2)

    with col1:
        lite_active = current_mode == 'lite'
        lite_bg = 'rgba(34, 197, 94, 0.1)' if lite_active else 'linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%)'
        lite_border = COLORS['success'] if lite_active else 'rgba(34, 197, 94, 0.3)'

        st.markdown(f"""
        <div style="
            background: {lite_bg};
            border: 1px solid {lite_border};
            border-radius: 16px;
            padding: 1.25rem;
            transition: all 0.3s ease;
        ">
            <h4 style="color: {COLORS['success']}; margin: 0 0 0.75rem 0;">⚡ Lite Mode</h4>
            <ul style="color: {COLORS['text_secondary']}; font-size: 0.85rem; padding-left: 1.25rem; margin: 0; line-height: 1.8;">
                <li>Works offline (load shedding safe)</li>
                <li>No API costs</li>
                <li>Basic analytics</li>
                <li>WhatsApp export</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Use Lite Mode", use_container_width=True, disabled=current_mode == "lite"):
            set_mode("lite")
            st.rerun()

    with col2:
        pro_active = current_mode == 'pro'
        pro_bg = 'rgba(139, 92, 246, 0.1)' if pro_active else 'linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%)'
        pro_border = COLORS['secondary'] if pro_active else 'rgba(139, 92, 246, 0.3)'

        st.markdown(f"""
        <div style="
            background: {pro_bg};
            border: 1px solid {pro_border};
            border-radius: 16px;
            padding: 1.25rem;
            transition: all 0.3s ease;
        ">
            <h4 style="color: {COLORS['secondary']}; margin: 0 0 0.75rem 0;">🤖 Pro Mode</h4>
            <ul style="color: {COLORS['text_secondary']}; font-size: 0.85rem; padding-left: 1.25rem; margin: 0; line-height: 1.8;">
                <li>AI-powered insights</li>
                <li>Smart recommendations</li>
                <li>Root cause analysis</li>
                <li>Budget controlled (ZAR)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Use Pro Mode", use_container_width=True, disabled=current_mode == "pro"):
            set_mode("pro")
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# EXPORT/IMPORT CONFIG
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("Export / Import Configuration", expanded=False):
    st.markdown("Save or restore your settings")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Export Settings**")
        if st.button("Generate Config JSON"):
            config_json = export_config_json(config)
            st.text_area("Copy this JSON:", config_json, height=200)
            st.download_button(
                "Download config.json",
                config_json,
                file_name="pizzaops_config.json",
                mime="application/json"
            )

    with col2:
        st.markdown("**Import Settings**")
        uploaded_config = st.file_uploader("Upload config.json", type=["json"])
        if uploaded_config:
            try:
                config_data = json.loads(uploaded_config.read().decode())
                imported_config = BusinessConfig.from_dict(config_data)
                save_config(imported_config)
                st.success("Configuration imported successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error importing config: {str(e)}")

# ══════════════════════════════════════════════════════════════════════════════
# SAVE BUTTON
# ══════════════════════════════════════════════════════════════════════════════
spacer("1rem")
st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("💾 Save All Settings", type="primary", use_container_width=True):
        # Build updated config
        updated_config = BusinessConfig(
            business_name=new_business_name,
            tagline=new_tagline,
            delivery_target_minutes=new_delivery_target,
            delivery_warning_minutes=new_warning_time,
            delivery_critical_minutes=new_critical_time,
            on_time_target_pct=float(new_on_time_target),
            complaint_target_pct=float(new_complaint_target),
            avg_delivery_target_min=float(new_avg_target),
            peak_lunch_start=new_lunch_start,
            peak_lunch_end=new_lunch_end,
            peak_dinner_start=new_dinner_start,
            peak_dinner_end=new_dinner_end,
            daily_budget_zar=new_budget,
            stages=new_stages,
        )

        save_config(updated_config)
        st.success("Settings saved successfully!")
        st.balloons()

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
spacer("2rem")
st.markdown(f"""
<div style="
    text-align: center;
    padding: 1.5rem;
    border-top: 1px solid rgba(59, 130, 246, 0.15);
">
    <p style="color: {COLORS['primary']}; font-size: 0.85rem; margin: 0 0 0.25rem 0;">
        Settings are stored in your browser session
    </p>
    <p style="color: {COLORS['text_muted']}; font-size: 0.8rem; margin: 0;">
        Export to save permanently
    </p>
</div>
""", unsafe_allow_html=True)
