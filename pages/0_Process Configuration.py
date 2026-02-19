"""
Page: Process Configuration
Purpose: Configure delivery process parameters, thresholds, and targets
         Set up BEFORE detecting problems for accurate analysis
"""

import streamlit as st
import json
import sys
import os

# Add project root to path for Streamlit Cloud
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import (
    get_config, save_config, BusinessConfig, StageConfig,
    export_config_json, import_config_json
)
from ui.layout import (
    page_header, spacer,
    render_dashboard_header, render_section_title, inject_custom_css
)
from ui.theme import COLORS

# ── Page Config ──
st.set_page_config(page_title="Process Configuration | PizzaOps", page_icon="⚙️", layout="wide")

# Inject CSS first
inject_custom_css()

# Professional dashboard header
render_dashboard_header(
    title="Process Configuration",
    logo_text="⚙",
    logo_color=COLORS["secondary"],
    is_live=False,
    live_text=""
)

# Description with styled box
st.markdown(f'''
<div style="
    background: rgba(10, 25, 60, 0.6);
    border: 1px solid rgba(0, 229, 255, 0.2);
    border-left: 4px solid {COLORS["secondary"]};
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.25rem;
    margin-bottom: 1.5rem;
">
    <p style="color: {COLORS["text_secondary"]}; margin: 0; font-size: 0.9rem;">
        <strong style="color: {COLORS["secondary"]};">Important:</strong>
        Configure your delivery targets and thresholds before analyzing data for accurate problem detection.
    </p>
</div>
''', unsafe_allow_html=True)

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
