"""
Page: Home - Executive Dashboard
Purpose: Data upload, one-click preparation, and executive-level analytics
Operations Analytics Platform for Food Delivery Businesses
by JLWanalytics - Africa's Premier Data Refinery
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Ensure project root is in path for local modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.loader import load_and_validate, get_summary_stats
from data.transformer import transform_data
from ui.theme import COLORS, CUSTOM_CSS
from ui.layout import page_header, spacer, footer
from ui.metrics_cards import render_kpi_card
from ui.charts import bar_chart, donut_chart

# Import configuration and analytics modules
from core.config import get_config
from core.local_analytics import get_local_analytics
from core.pipeline import prepare_data


# ── Page Config ──
st.set_page_config(
    page_title="Home | PizzaOps",
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Inject Custom CSS ──
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def main():
    """Main application entry point."""

    # ── Sidebar Branding & Data Status ──
    with st.sidebar:
        config = get_config()
        st.markdown(f'<div style="text-align:center;padding:1rem 0;"><h1 style="color:{COLORS["primary"]};font-size:1.5rem;margin:0;">🍕 {config.business_name}</h1><p style="color:{COLORS["text_secondary"]};font-size:0.875rem;margin:0;">{config.tagline}</p></div>', unsafe_allow_html=True)
        st.markdown("---")

        # ── Data Status ──
        if "df_original" in st.session_state and st.session_state.df_original is not None:
            if st.session_state.get("data_is_clean", False):
                st.success(f"✓ Data ready: {len(st.session_state.df):,} orders")
            else:
                st.warning(f"📊 {len(st.session_state.df_original):,} orders loaded")
                st.info("🚀 Ready for preparation")
        else:
            st.info("📊 Upload data to begin")

    # ── Main Content ──
    if "df_original" not in st.session_state or st.session_state.df_original is None:
        # No data uploaded yet
        page_header(
            title="Upload Your Data",
            icon="📁",
            description="Upload order data to get started with analytics"
        )
        render_upload_section()
    elif not st.session_state.get("data_is_clean", False):
        # Data uploaded but not prepared
        page_header(
            title="Prepare Your Data",
            icon="⚡",
            description="One click to transform raw data into insights"
        )
        render_one_click_prepare()
    else:
        # Data is ready - show executive dashboard
        render_executive_dashboard()

    spacer("2rem")
    footer()


def render_upload_section():
    """Render the data upload interface - clean full width layout."""
    st.markdown(f'''
    <div style="text-align: center; padding: 2rem; margin-bottom: 1rem;">
        <p style="color: {COLORS["text_secondary"]}; font-size: 1rem; margin: 0;">
            Upload a CSV or Excel file with your order data to get started
        </p>
    </div>
    ''', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["csv", "xlsx", "xls"],
        help="Upload your order data in CSV or Excel format",
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        with st.spinner("Processing data..."):
            df, report = load_and_validate(uploaded_file)
            if report["status"] == "error":
                st.error(f"Error loading file: {report['warnings']}")
            else:
                df = transform_data(df)
                st.session_state.df_original = df.copy()
                st.session_state.df = None
                st.session_state.data_report = report
                st.session_state.upload_time = datetime.now()
                st.session_state.data_is_clean = False
                st.success(f"✅ Loaded {len(df):,} rows × {len(df.columns)} columns")
                st.rerun()


def render_one_click_prepare():
    """Render the one-click data preparation interface."""
    df = st.session_state.df_original
    config = get_config()

    # Hero section
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {COLORS['bg_dark']} 0%, #1e293b 100%); border-radius: 20px; padding: 2.5rem; margin-bottom: 2rem; border: 1px solid {COLORS['primary']}40; position: relative; overflow: hidden;">
        <div style="position: absolute; top: -50px; right: -50px; width: 200px; height: 200px; background: radial-gradient(circle, {COLORS['primary']}20 0%, transparent 70%); border-radius: 50%;"></div>
        <div style="position: relative; z-index: 1; text-align: center;">
            <div style="display: inline-block; background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%); padding: 0.5rem 1.5rem; border-radius: 20px; margin-bottom: 1rem;">
                <span style="color: white; font-weight: 600; font-size: 0.875rem;">⚡ INTELLIGENT PIPELINE</span>
            </div>
            <h1 style="color: {COLORS['text_primary']}; margin: 0 0 0.75rem 0; font-size: 2rem; font-weight: 700;">One-Click Data Preparation</h1>
            <p style="color: {COLORS['text_secondary']}; margin: 0; font-size: 1.1rem;">Transform raw data into analysis-ready insights in seconds</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Data summary cards
    missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100)
    missing_color = COLORS['success'] if missing_pct < 1 else COLORS['warning'] if missing_pct < 5 else COLORS['danger']

    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 2rem;">
        <div style="background: {COLORS['bg_card']}; border-radius: 12px; padding: 1.25rem; border: 1px solid {COLORS['border']}; text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.25rem;">📊</div>
            <div style="color: {COLORS['text_primary']}; font-size: 1.75rem; font-weight: 700;">{len(df):,}</div>
            <div style="color: {COLORS['text_muted']}; font-size: 0.875rem; text-transform: uppercase;">Records</div>
        </div>
        <div style="background: {COLORS['bg_card']}; border-radius: 12px; padding: 1.25rem; border: 1px solid {COLORS['border']}; text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.25rem;">📋</div>
            <div style="color: {COLORS['text_primary']}; font-size: 1.75rem; font-weight: 700;">{len(df.columns)}</div>
            <div style="color: {COLORS['text_muted']}; font-size: 0.875rem; text-transform: uppercase;">Columns</div>
        </div>
        <div style="background: {COLORS['bg_card']}; border-radius: 12px; padding: 1.25rem; border: 1px solid {COLORS['border']}; text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.25rem;">🔍</div>
            <div style="color: {missing_color}; font-size: 1.75rem; font-weight: 700;">{missing_pct:.1f}%</div>
            <div style="color: {COLORS['text_muted']}; font-size: 0.875rem; text-transform: uppercase;">Missing Data</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Pipeline steps preview
    st.markdown(f"""
    <div style="background: {COLORS['bg_card']}; border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; border: 1px solid {COLORS['border']};">
        <h4 style="color: {COLORS['text_primary']}; margin: 0 0 1rem 0; font-size: 1rem;">What happens when you click Prepare:</h4>
        <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.5rem;">
            <div style="text-align: center; padding: 0.75rem 0.5rem; background: {COLORS['primary']}10; border-radius: 8px;">
                <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">🔍</div>
                <div style="color: {COLORS['text_primary']}; font-size: 0.75rem; font-weight: 600;">Detect Schema</div>
            </div>
            <div style="text-align: center; padding: 0.75rem 0.5rem; background: {COLORS['info']}10; border-radius: 8px;">
                <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">🏷️</div>
                <div style="color: {COLORS['text_primary']}; font-size: 0.75rem; font-weight: 600;">Map Columns</div>
            </div>
            <div style="text-align: center; padding: 0.75rem 0.5rem; background: {COLORS['warning']}10; border-radius: 8px;">
                <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">🧹</div>
                <div style="color: {COLORS['text_primary']}; font-size: 0.75rem; font-weight: 600;">Clean Data</div>
            </div>
            <div style="text-align: center; padding: 0.75rem 0.5rem; background: {COLORS['secondary']}10; border-radius: 8px;">
                <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">✨</div>
                <div style="color: {COLORS['text_primary']}; font-size: 0.75rem; font-weight: 600;">Add Metrics</div>
            </div>
            <div style="text-align: center; padding: 0.75rem 0.5rem; background: {COLORS['success']}10; border-radius: 8px;">
                <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">✅</div>
                <div style="color: {COLORS['text_primary']}; font-size: 0.75rem; font-weight: 600;">Validate</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Action button
    prepare_clicked = st.button(
        "🚀 PREPARE DATA AUTOMATICALLY",
        type="primary",
        use_container_width=True,
        help="Run the intelligent pipeline to clean and transform your data"
    )

    if prepare_clicked:
        st.markdown("---")
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(step_num, total_steps, step_name):
            progress_bar.progress(step_num / total_steps)
            status_text.markdown(f"**Step {step_num}/{total_steps}:** {step_name}")

        pipeline_config = {"delivery_target_minutes": config.delivery_target_minutes}
        result = prepare_data(df, pipeline_config, update_progress)

        if result.success:
            progress_bar.progress(1.0)
            status_text.empty()

            st.session_state.df = result.df
            st.session_state.pipeline_result = result.to_dict()
            st.session_state.data_is_clean = True

            summary = result.summary
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {COLORS['success']}15 0%, {COLORS['success']}05 100%); border-radius: 16px; padding: 2rem; margin: 1rem 0; border: 1px solid {COLORS['success']}40; text-align: center;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🎉</div>
                <h2 style="color: {COLORS['success']}; margin: 0 0 0.5rem 0;">Data Preparation Complete!</h2>
                <p style="color: {COLORS['text_secondary']}; margin: 0 0 1.5rem 0;">Your data is now ready for analysis</p>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; max-width: 600px; margin: 0 auto;">
                    <div style="background: {COLORS['bg_card']}; border-radius: 8px; padding: 1rem;">
                        <div style="color: {COLORS['success']}; font-size: 1.5rem; font-weight: 700;">{result.quality_score:.0f}%</div>
                        <div style="color: {COLORS['text_muted']}; font-size: 0.75rem;">Quality</div>
                    </div>
                    <div style="background: {COLORS['bg_card']}; border-radius: 8px; padding: 1rem;">
                        <div style="color: {COLORS['primary']}; font-size: 1.5rem; font-weight: 700;">{summary.get('columns_mapped', 0)}</div>
                        <div style="color: {COLORS['text_muted']}; font-size: 0.75rem;">Mapped</div>
                    </div>
                    <div style="background: {COLORS['bg_card']}; border-radius: 8px; padding: 1rem;">
                        <div style="color: {COLORS['warning']}; font-size: 1.5rem; font-weight: 700;">{summary.get('cleaning_actions', 0)}</div>
                        <div style="color: {COLORS['text_muted']}; font-size: 0.75rem;">Cleaned</div>
                    </div>
                    <div style="background: {COLORS['bg_card']}; border-radius: 8px; padding: 1rem;">
                        <div style="color: {COLORS['secondary']}; font-size: 1.5rem; font-weight: 700;">{summary.get('columns_added', 0)}</div>
                        <div style="color: {COLORS['text_muted']}; font-size: 0.75rem;">Enriched</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.balloons()

            spacer("1rem")
            if st.button("📊 View Executive Dashboard →", type="primary", use_container_width=True):
                st.rerun()

        else:
            st.error("Pipeline failed. Please check your data format.")
            for step in result.steps:
                if step.status == "failed":
                    st.error(f"Failed at {step.name}: {step.message}")

    # Preview data
    spacer("1rem")
    with st.expander("📋 Preview Raw Data", expanded=False):
        st.dataframe(df.head(15), use_container_width=True, height=300)


# ════════════════════════════════════════════════════════════════════════════════
# EXECUTIVE DASHBOARD - Single View for Managers
# ════════════════════════════════════════════════════════════════════════════════

def render_executive_dashboard():
    """Render the executive dashboard - single clean view for managers."""
    df = st.session_state.df
    config = get_config()
    analytics = get_local_analytics()

    # Section 1: Executive Header
    render_exec_header(df, config, analytics)

    spacer("1.5rem")

    # Section 2: Key Business KPIs
    render_kpi_row(df)

    spacer("1.5rem")

    # Section 3: Operations Health Status
    render_health_status(df, analytics)

    spacer("1.5rem")

    # Section 4: Issues & Actions (2-column)
    render_issues_actions(df, analytics)

    spacer("1.5rem")

    # Section 5: Quick Performance Chart
    render_quick_chart(df, analytics)

    spacer("1.5rem")

    # Section 6: Advanced Analysis (collapsed)
    render_advanced_section(df)

    spacer("1rem")

    # Clear data button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🗑️ Clear Data & Start Over", type="secondary", use_container_width=True):
            keys_to_clear = ['df', 'df_original', 'data_report', 'upload_time',
                            'data_is_clean', 'pipeline_result']
            for key in list(st.session_state.keys()):
                if key.startswith('df') or key.startswith('data_profile_') or key in keys_to_clear:
                    del st.session_state[key]
            st.rerun()


def render_exec_header(df: pd.DataFrame, config, analytics):
    """Render executive summary header with key stats."""
    quality_report = analytics.get_data_quality_report(df)
    quality_score = quality_report["completeness_score"]

    # Determine quality badge color
    if quality_score >= 95:
        badge_color = COLORS['success']
        badge_text = "EXCELLENT"
    elif quality_score >= 80:
        badge_color = COLORS['warning']
        badge_text = "GOOD"
    else:
        badge_color = COLORS['danger']
        badge_text = "NEEDS REVIEW"

    # Get date range
    date_range = quality_report.get("date_range", {})
    start_date = date_range.get("start", "")
    end_date = date_range.get("end", "")
    date_str = f"{start_date} - {end_date}" if start_date and end_date else "N/A"

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {COLORS['bg_dark']} 0%, #1e293b 100%); border-radius: 20px; padding: 2rem; margin-bottom: 0; border: 1px solid {COLORS['primary']}30; position: relative; overflow: hidden;">
        <div style="position: absolute; top: -30px; right: -30px; width: 150px; height: 150px; background: radial-gradient(circle, {COLORS['primary']}15 0%, transparent 70%); border-radius: 50%;"></div>
        <div style="position: relative; z-index: 1;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <h1 style="color: {COLORS['text_primary']}; margin: 0 0 0.25rem 0; font-size: 1.75rem; font-weight: 700;">🍕 {config.business_name}</h1>
                    <p style="color: {COLORS['text_secondary']}; margin: 0; font-size: 1rem;">{config.tagline}</p>
                </div>
                <div style="text-align: right;">
                    <div style="display: inline-block; background: {badge_color}20; border: 1px solid {badge_color}; padding: 0.25rem 0.75rem; border-radius: 20px; margin-bottom: 0.5rem;">
                        <span style="color: {badge_color}; font-weight: 600; font-size: 0.75rem;">{badge_text} • {quality_score:.0f}%</span>
                    </div>
                    <p style="color: {COLORS['text_muted']}; margin: 0; font-size: 0.8rem;">Data Quality Score</p>
                </div>
            </div>
            <div style="display: flex; gap: 2rem; margin-top: 1.25rem; flex-wrap: wrap;">
                <div>
                    <span style="color: {COLORS['text_muted']}; font-size: 0.8rem;">Period:</span>
                    <span style="color: {COLORS['text_primary']}; font-size: 0.9rem; margin-left: 0.5rem;">{date_str}</span>
                </div>
                <div>
                    <span style="color: {COLORS['text_muted']}; font-size: 0.8rem;">Total Orders:</span>
                    <span style="color: {COLORS['text_primary']}; font-size: 0.9rem; font-weight: 600; margin-left: 0.5rem;">{len(df):,}</span>
                </div>
                <div>
                    <span style="color: {COLORS['text_muted']}; font-size: 0.8rem;">Last Updated:</span>
                    <span style="color: {COLORS['text_primary']}; font-size: 0.9rem; margin-left: 0.5rem;">{datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_row(df: pd.DataFrame):
    """Render 4 key business KPIs in a row."""
    st.markdown(f'<h3 style="color: {COLORS["text_primary"]}; margin-bottom: 1rem;">Key Performance Indicators</h3>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    # KPI 1: Total Orders
    with col1:
        render_kpi_card(
            title="Total Orders",
            value=f"{len(df):,}",
            icon="📦",
            status="neutral"
        )

    # KPI 2: On-Time Delivery Rate
    with col2:
        if "delivery_target_met" in df.columns:
            on_time_pct = df["delivery_target_met"].mean() * 100
            status = "good" if on_time_pct >= 85 else "warning" if on_time_pct >= 70 else "danger"
            render_kpi_card(
                title="On-Time Delivery",
                value=f"{on_time_pct:.1f}",
                suffix="%",
                icon="⏱️",
                status=status,
                target="Target: 85%"
            )
        else:
            render_kpi_card(title="On-Time Delivery", value="N/A", icon="⏱️", status="neutral")

    # KPI 3: Complaint Rate
    with col3:
        if "complaint" in df.columns:
            complaint_rate = df["complaint"].mean() * 100
            status = "good" if complaint_rate <= 5 else "warning" if complaint_rate <= 10 else "danger"
            render_kpi_card(
                title="Complaint Rate",
                value=f"{complaint_rate:.1f}",
                suffix="%",
                icon="😤",
                status=status,
                target="Target: <5%"
            )
        else:
            render_kpi_card(title="Complaint Rate", value="N/A", icon="😤", status="neutral")

    # KPI 4: Average Delivery Time
    with col4:
        if "total_process_time" in df.columns:
            avg_time = df["total_process_time"].mean()
            status = "good" if avg_time <= 25 else "warning" if avg_time <= 30 else "danger"
            render_kpi_card(
                title="Avg Delivery Time",
                value=f"{avg_time:.1f}",
                suffix=" min",
                icon="🚚",
                status=status,
                target="Target: 25 min"
            )
        else:
            render_kpi_card(title="Avg Delivery Time", value="N/A", icon="🚚", status="neutral")


def render_health_status(df: pd.DataFrame, analytics):
    """Render overall operations health status - simple traffic light."""
    # Calculate health metrics
    on_time_pct = df["delivery_target_met"].mean() * 100 if "delivery_target_met" in df.columns else 0
    complaint_pct = df["complaint"].mean() * 100 if "complaint" in df.columns else 0
    avg_time = df["total_process_time"].mean() if "total_process_time" in df.columns else 0

    # Determine overall health
    issues = 0
    if on_time_pct < 85:
        issues += 1
    if complaint_pct > 5:
        issues += 1
    if avg_time > 30:
        issues += 1

    if issues == 0:
        status = "HEALTHY"
        status_color = COLORS['success']
        status_icon = "✅"
        message = "Your delivery operations are performing excellently. All key metrics are within target ranges."
    elif issues == 1:
        status = "NEEDS ATTENTION"
        status_color = COLORS['warning']
        status_icon = "⚠️"
        message = "Your operations are mostly on track, but one area needs improvement. Review the issues below."
    else:
        status = "CRITICAL"
        status_color = COLORS['danger']
        status_icon = "🚨"
        message = "Multiple areas require immediate attention. Focus on the priority issues listed below."

    st.markdown(f"""
    <div style="background: {status_color}10; border: 1px solid {status_color}40; border-radius: 16px; padding: 1.5rem; display: flex; align-items: center; gap: 1.5rem;">
        <div style="font-size: 3rem;">{status_icon}</div>
        <div style="flex: 1;">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                <span style="color: {status_color}; font-size: 1.25rem; font-weight: 700;">{status}</span>
                <span style="background: {status_color}20; color: {status_color}; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.75rem;">Operations Health</span>
            </div>
            <p style="color: {COLORS['text_secondary']}; margin: 0; font-size: 0.95rem;">{message}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_issues_actions(df: pd.DataFrame, analytics):
    """Render issues and recommended actions in 2-column layout."""
    col1, col2 = st.columns(2)

    # LEFT: Top Issues (Bottlenecks)
    with col1:
        st.markdown(f'<h3 style="color: {COLORS["text_primary"]}; margin-bottom: 1rem;">🔴 Top Issues</h3>', unsafe_allow_html=True)

        bottlenecks = analytics.detect_bottlenecks(df)

        if bottlenecks:
            for i, b in enumerate(bottlenecks[:3], 1):
                severity_color = COLORS['danger'] if b.severity in ['critical', 'high'] else COLORS['warning'] if b.severity == 'medium' else COLORS['primary']
                st.markdown(f"""
                <div style="background: {COLORS['bg_card']}; border-left: 4px solid {severity_color}; border-radius: 0 12px 12px 0; padding: 1rem; margin-bottom: 0.75rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                        <span style="background: {severity_color}20; color: {severity_color}; padding: 0.15rem 0.5rem; border-radius: 8px; font-size: 0.7rem; font-weight: 600;">{b.severity.upper()}</span>
                        <strong style="color: {COLORS['text_primary']}; font-size: 0.95rem;">{b.area}</strong>
                    </div>
                    <p style="color: {COLORS['text_secondary']}; margin: 0; font-size: 0.85rem;">{b.impact_description}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: {COLORS['success']}10; border: 1px solid {COLORS['success']}30; border-radius: 12px; padding: 1.5rem; text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎉</div>
                <p style="color: {COLORS['success']}; margin: 0; font-weight: 600;">No Critical Issues</p>
                <p style="color: {COLORS['text_muted']}; margin: 0.25rem 0 0 0; font-size: 0.85rem;">Your operations are running smoothly!</p>
            </div>
            """, unsafe_allow_html=True)

    # RIGHT: Recommended Actions
    with col2:
        st.markdown(f'<h3 style="color: {COLORS["text_primary"]}; margin-bottom: 1rem;">✅ Recommended Actions</h3>', unsafe_allow_html=True)

        recommendations = analytics.generate_recommendations(df)

        if recommendations:
            for i, rec in enumerate(recommendations[:3], 1):
                priority = rec.get('priority', 'medium')
                priority_color = COLORS['danger'] if priority == 'high' else COLORS['warning'] if priority == 'medium' else COLORS['success']
                title = rec.get('title', f'Action {i}')
                description = rec.get('description', '')

                st.markdown(f"""
                <div style="background: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                        <span style="background: {priority_color}20; color: {priority_color}; padding: 0.15rem 0.5rem; border-radius: 8px; font-size: 0.7rem; font-weight: 600;">{priority.upper()}</span>
                        <strong style="color: {COLORS['text_primary']}; font-size: 0.95rem;">{title}</strong>
                    </div>
                    <p style="color: {COLORS['text_secondary']}; margin: 0; font-size: 0.85rem;">{description}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 12px; padding: 1.5rem; text-align: center;">
                <p style="color: {COLORS['text_muted']}; margin: 0;">Upload more data to generate recommendations.</p>
            </div>
            """, unsafe_allow_html=True)


def render_quick_chart(df: pd.DataFrame, analytics):
    """Render a single performance chart - stage performance bars."""
    st.markdown(f'<h3 style="color: {COLORS["text_primary"]}; margin-bottom: 1rem;">📊 Stage Performance vs Benchmarks</h3>', unsafe_allow_html=True)

    stage_breakdown = analytics.get_stage_breakdown(df)

    if stage_breakdown:
        # Build chart data with benchmarks
        benchmarks = analytics.BENCHMARKS
        chart_data = []

        for stage, avg_time in stage_breakdown.items():
            # Map stage names to benchmark keys
            benchmark_key = stage.lower().replace(" ", "_")
            if not benchmark_key.endswith("_time") and not benchmark_key.endswith("_duration"):
                benchmark_key = benchmark_key + "_time"

            benchmark = benchmarks.get(benchmark_key, benchmarks.get(stage.lower().replace(" ", "_") + "_duration", avg_time))

            chart_data.append({
                "Stage": stage,
                "Actual": round(avg_time, 1),
                "Benchmark": benchmark
            })

        chart_df = pd.DataFrame(chart_data)

        # Render as horizontal progress bars
        for _, row in chart_df.iterrows():
            actual = row["Actual"]
            benchmark = row["Benchmark"]
            pct = min((actual / benchmark) * 100, 150) if benchmark > 0 else 0
            color = COLORS['success'] if actual <= benchmark else COLORS['warning'] if actual <= benchmark * 1.2 else COLORS['danger']

            st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                    <span style="color: {COLORS['text_primary']}; font-weight: 500;">{row['Stage']}</span>
                    <span style="color: {color}; font-weight: 600;">{actual} min <span style="color: {COLORS['text_muted']}; font-weight: 400;">/ {benchmark} min target</span></span>
                </div>
                <div style="background: {COLORS['bg_card']}; border-radius: 8px; height: 12px; overflow: hidden;">
                    <div style="background: {color}; height: 100%; width: {min(pct, 100)}%; border-radius: 8px; transition: width 0.3s;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Stage performance data not available.")


def render_advanced_section(df: pd.DataFrame):
    """Render advanced analysis section - collapsed by default for technical users."""
    with st.expander("🔬 Advanced Analysis (Technical Users)", expanded=False):
        st.markdown(f"""
        <div style="background: {COLORS['bg_card']}; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; border: 1px solid {COLORS['border']};">
            <p style="color: {COLORS['text_secondary']}; margin: 0; font-size: 0.9rem;">
                This section contains detailed technical analysis for data analysts and technical users.
                Most managers can skip this section.
            </p>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["Data Preview", "Column Summary", "Quick Stats"])

        with tab1:
            st.dataframe(df.head(100), use_container_width=True, height=400)

        with tab2:
            # Column types summary
            col_summary = []
            for col in df.columns:
                dtype = str(df[col].dtype)
                missing = df[col].isna().sum()
                unique = df[col].nunique()
                col_summary.append({
                    "Column": col,
                    "Type": dtype,
                    "Missing": missing,
                    "Unique": unique
                })
            st.dataframe(pd.DataFrame(col_summary), use_container_width=True, hide_index=True)

        with tab3:
            # Basic statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                st.dataframe(df[numeric_cols].describe().round(2), use_container_width=True)
            else:
                st.info("No numeric columns found.")


if __name__ == "__main__":
    main()
