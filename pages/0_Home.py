"""
Page: Home
Purpose: Data upload, cleaning, and initial dashboard
Operations Analytics Platform for Food Delivery Businesses
by JLWanalytics - Africa's Premier Data Refinery
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Ensure parent directory is in path for agents module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from data.loader import load_and_validate, get_summary_stats
from data.transformer import transform_data
from ui.theme import COLORS, CUSTOM_CSS
from ui.layout import page_header, render_alert, spacer, footer
from ui.metrics_cards import render_kpi_card
from ui.charts import (
    bar_chart, box_plot, donut_chart, heatmap, scatter_plot,
    histogram_chart, correlation_heatmap, missing_values_chart, gauge_chart
)

# Import configuration and SA market optimization modules
from core.config import get_config, is_pro_mode, is_lite_mode, set_mode, get_mode
from core.local_analytics import get_local_analytics
from core.data_profiler import get_data_profiler
from ai.budget_tracker import get_budget_tracker, render_budget_widget, check_budget_before_query

# Try to import AI components
try:
    from ui.ai_components import render_ai_status_badge, render_ai_chat_widget
    from ai.service import get_ai_service
    from ai.data_quality_agent import get_data_quality_agent
    from ai.business_analyst import get_business_analyst_agent
    from ui.ai_dashboards import render_quality_dashboard, render_business_analyst_dashboard
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


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
        # Get config for branding
        config = get_config()
        st.markdown(f'<div style="text-align:center;padding:1rem 0;"><h1 style="color:{COLORS["primary"]};font-size:1.5rem;margin:0;">🍕 {config.business_name}</h1><p style="color:{COLORS["text_secondary"]};font-size:0.875rem;margin:0;">{config.tagline}</p></div>', unsafe_allow_html=True)

        # ── Mode Selector (Lite/Pro) ──
        st.markdown("#### Mode")
        mode_col1, mode_col2 = st.columns(2)
        with mode_col1:
            lite_selected = is_lite_mode()
            if st.button(
                "Lite",
                type="primary" if lite_selected else "secondary",
                use_container_width=True,
                help="Offline mode - works without internet"
            ):
                set_mode("lite")
                st.rerun()
        with mode_col2:
            pro_selected = is_pro_mode()
            if st.button(
                "Pro",
                type="primary" if pro_selected else "secondary",
                use_container_width=True,
                help="Smart automation (requires API key)"
            ):
                set_mode("pro")
                st.rerun()

        # Mode description
        if is_lite_mode():
            st.caption("Works offline during load shedding")
        else:
            st.caption("Smart automation enabled")

        st.markdown("---")

        # ── Budget Widget (Pro mode only) ──
        if is_pro_mode():
            render_budget_widget()
            st.markdown("---")

        # ── Automation Status (Pro mode only) ──
        if is_pro_mode() and AI_AVAILABLE:
            ai = get_ai_service()
            if ai.is_available():
                st.markdown(f"""
                <div style="
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: {COLORS['success']}15;
                    border: 1px solid {COLORS['success']}30;
                    border-radius: 8px;
                    padding: 0.5rem;
                    margin-bottom: 0.5rem;
                ">
                    <span style="color: {COLORS['success']}; font-size: 0.8rem;">✓ Automation Ready</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: {COLORS['warning']}15;
                    border: 1px solid {COLORS['warning']}30;
                    border-radius: 8px;
                    padding: 0.5rem;
                    margin-bottom: 0.5rem;
                ">
                    <span style="color: {COLORS['warning']}; font-size: 0.8rem;">⚠️ Configure Automation</span>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Configure Automation", use_container_width=True, type="secondary"):
                    st.switch_page("pages/1_Process Configuration.py")
            st.markdown("---")

        # ── Data Status ──
        if "df" in st.session_state and st.session_state.df is not None:
            st.success(f"✓ Data loaded: {len(st.session_state.df):,} orders")
            if st.session_state.get("data_is_clean", False):
                st.info("Data has been cleaned.")
            else:
                st.warning("Data cleaning pending.")
        else:
            st.info("📊 Upload data to begin")

    # ── Main Content ──
    page_header(
        title="Upload & Prepare Data",
        icon="📁",
        description="Upload your order data to get started with analytics"
    )

    # ── Conditional Rendering: Upload or Tabs ──
    if "df" not in st.session_state or st.session_state.df is None:
        render_upload_section()
    else:
        # New tabbed interface after data is loaded
        cleaning_tab, eda_tab, dashboard_tab = st.tabs([
            "1. Data Quality & Cleaning",
            "2. Exploratory Analysis",
            "3. Dashboard Overview"
        ])

        with cleaning_tab:
            render_cleaning_tab()

        with eda_tab:
            if st.session_state.get("data_is_clean", False):
                render_eda_section()
            else:
                st.info("Complete data cleaning first to access exploratory analysis.")
                st.markdown(f'<div style="background-color:{COLORS["bg_card"]};border-radius:12px;padding:2rem;text-align:center;"><p style="color:{COLORS["text_secondary"]};">The EDA section will appear here once the data is cleaned and confirmed.</p></div>', unsafe_allow_html=True)

        with dashboard_tab:
            if st.session_state.get("data_is_clean", False):
                render_dashboard_tab()
            else:
                st.info("Please complete the data cleaning steps and click 'Confirm & Proceed' to view the dashboard.")
                st.markdown(f'<div style="background-color:{COLORS["bg_card"]};border-radius:12px;padding:2rem;text-align:center;"><p style="color:{COLORS["text_secondary"]};">The dashboard will appear here once the data is cleaned and confirmed.</p></div>', unsafe_allow_html=True)

    spacer("2rem")
    footer()


def render_upload_section():
    """Render the data upload interface - clean full width layout."""
    # Upload section header
    st.markdown(f'''
    <div style="text-align: center; padding: 2rem; margin-bottom: 1rem;">
        <p style="color: {COLORS["text_secondary"]}; font-size: 1rem; margin: 0;">
            Upload a CSV or Excel file with your order data to get started
        </p>
    </div>
    ''', unsafe_allow_html=True)

    # File uploader (full width)
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
                # Initialize session state for cleaning workflow
                st.session_state.df_original = df.copy()
                st.session_state.df = df.copy()
                st.session_state.data_report = report
                st.session_state.upload_time = datetime.now()
                st.session_state.data_is_clean = False  # IMPORTANT: Initialize cleaning status
                st.success("Data loaded successfully! Proceed to the 'Data Quality & Cleaning' tab.")
                st.rerun()


def render_smart_profiler(df: pd.DataFrame):
    """
    Render the intelligent data profiler that automatically scans the dataset,
    identifies column types, detects issues, and suggests cleaning actions.
    Works with ANY dataset - fully adaptive.
    """
    profiler = get_data_profiler()

    # Profile the dataset (cache in session state)
    profile_key = f"data_profile_{len(df)}_{len(df.columns)}"
    if profile_key not in st.session_state:
        with st.spinner("Scanning dataset..."):
            st.session_state[profile_key] = profiler.profile_dataset(df)

    profile = st.session_state[profile_key]
    summary = profile["summary"]

    # ── Summary Cards ──
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {COLORS['primary']}15 0%, {COLORS['primary']}05 100%);
        border: 1px solid {COLORS['primary']}30;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
    ">
        <h4 style="color: {COLORS['text_primary']}; margin: 0 0 1rem 0;">
            🔬 Intelligent Data Profiler
        </h4>
        <p style="color: {COLORS['text_secondary']}; margin: 0; font-size: 0.9rem;">
            Automatically scanned {profile['total_columns']} columns and detected {summary['total_issues']} issues in {summary['columns_with_issues']} columns.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Type Distribution ──
    type_icons = {
        'numeric': '🔢',
        'categorical': '🏷️',
        'datetime': '📅',
        'boolean': '✓',
        'id': '🔑',
        'text': '📝',
        'unknown': '❓'
    }

    type_dist = summary.get('type_distribution', {})
    if type_dist:
        type_cols = st.columns(len(type_dist))
        for i, (col_type, count) in enumerate(type_dist.items()):
            with type_cols[i]:
                icon = type_icons.get(col_type, '📊')
                st.markdown(f"""
                <div style="
                    background: {COLORS['bg_card']};
                    border-radius: 8px;
                    padding: 0.75rem;
                    text-align: center;
                    border: 1px solid {COLORS['border']};
                ">
                    <div style="font-size: 1.5rem;">{icon}</div>
                    <div style="color: {COLORS['text_primary']}; font-weight: 600;">{count}</div>
                    <div style="color: {COLORS['text_muted']}; font-size: 0.75rem; text-transform: uppercase;">{col_type}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("")

    # ── Columns with Issues ──
    columns_with_issues = [(name, p) for name, p in profile["columns"].items() if p.issues]

    if columns_with_issues:
        st.markdown("#### Columns Requiring Attention")

        for col_name, col_profile in columns_with_issues:
            # Determine severity color
            max_severity = max([i['severity'] for i in col_profile.issues], key=lambda x: {'critical': 3, 'warning': 2, 'info': 1}.get(x, 0))
            severity_colors = {
                'critical': COLORS['danger'],
                'warning': COLORS['warning'],
                'info': COLORS['primary']
            }
            border_color = severity_colors.get(max_severity, COLORS['primary'])
            type_icon = type_icons.get(col_profile.inferred_type, '📊')

            with st.expander(f"{type_icon} {col_name} — {len(col_profile.issues)} issue(s)", expanded=False):
                # Column info
                st.markdown(f"""
                <div style="
                    display: flex;
                    gap: 1rem;
                    flex-wrap: wrap;
                    margin-bottom: 1rem;
                ">
                    <span style="background: {COLORS['bg_card']}; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.8rem;">
                        Type: <strong>{col_profile.inferred_type}</strong>
                    </span>
                    <span style="background: {COLORS['bg_card']}; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.8rem;">
                        Unique: <strong>{col_profile.unique_count:,}</strong>
                    </span>
                    <span style="background: {COLORS['bg_card']}; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.8rem;">
                        Missing: <strong>{col_profile.missing_pct}%</strong>
                    </span>
                </div>
                """, unsafe_allow_html=True)

                # Show sample values
                if col_profile.sample_values:
                    sample_str = ", ".join([str(v)[:30] for v in col_profile.sample_values[:3]])
                    st.caption(f"Sample values: {sample_str}")

                # Show issues
                for issue in col_profile.issues:
                    issue_color = severity_colors.get(issue['severity'], COLORS['primary'])
                    st.markdown(f"""
                    <div style="
                        background: {issue_color}10;
                        border-left: 3px solid {issue_color};
                        padding: 0.5rem 0.75rem;
                        border-radius: 0 6px 6px 0;
                        margin-bottom: 0.5rem;
                    ">
                        <span style="color: {COLORS['text_primary']};">{issue['description']}</span>
                        <span style="color: {issue_color}; font-size: 0.75rem; margin-left: 0.5rem;">{issue['severity'].upper()}</span>
                    </div>
                    """, unsafe_allow_html=True)

                # Suggested actions with buttons
                if col_profile.suggested_actions:
                    st.markdown("**Quick Fixes:**")
                    for j, action in enumerate(col_profile.suggested_actions):
                        recommended = action.get('recommended', False)
                        btn_label = f"{'⭐ ' if recommended else ''}{action['description']}"
                        btn_type = "primary" if recommended else "secondary"
                        btn_key = f"fix_{col_name}_{action['action']}_{action['method']}_{j}"

                        if st.button(btn_label, key=btn_key, type=btn_type):
                            # Apply the fix
                            try:
                                df_fixed = profiler.apply_action(st.session_state.df, col_name, action)
                                st.session_state.df = df_fixed
                                # Clear profile cache to re-scan
                                for key in list(st.session_state.keys()):
                                    if key.startswith("data_profile_"):
                                        del st.session_state[key]
                                st.success(f"Applied: {action['description']}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error applying fix: {str(e)}")
    else:
        st.success("All columns look good! No issues detected.")

    # ── All Columns Overview (collapsed) ──
    with st.expander("📋 All Columns Overview", expanded=False):
        # Create a summary table
        overview_data = []
        for col_name, col_profile in profile["columns"].items():
            overview_data.append({
                "Column": col_name,
                "Type": col_profile.inferred_type,
                "Unique": col_profile.unique_count,
                "Missing %": col_profile.missing_pct,
                "Issues": len(col_profile.issues)
            })

        overview_df = pd.DataFrame(overview_data)
        st.dataframe(overview_df, use_container_width=True, hide_index=True)

    st.markdown("---")


def render_cleaning_tab():
    """Render the UI for the data cleaning workbench with AI Data Quality Agent."""
    st.header("Data Quality & Cleaning Workbench")

    if 'df' not in st.session_state:
        st.warning("No data loaded.")
        return

    df = st.session_state.df
    df_original = st.session_state.df_original

    st.markdown("Inspect data quality and apply cleaning actions before proceeding to analysis.")

    # Show summary
    st.subheader("Dataset Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Original Rows", len(df_original))
    col2.metric("Current Rows", len(df), delta=len(df) - len(df_original))
    col3.metric("Columns", len(df.columns))
    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════════
    # INTELLIGENT DATA PROFILER SECTION
    # ══════════════════════════════════════════════════════════════════════════
    render_smart_profiler(df)

    # ══════════════════════════════════════════════════════════════════════════
    # AI DATA QUALITY AGENT SECTION (Pro Mode Only)
    # ══════════════════════════════════════════════════════════════════════════
    if is_pro_mode() and AI_AVAILABLE:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {COLORS['primary']}15 0%, {COLORS['primary']}05 100%);
            border: 1px solid {COLORS['primary']}30;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <span style="font-size: 2rem; margin-right: 1rem;">🔬</span>
                <div>
                    <h3 style="color: {COLORS['text_primary']}; margin: 0;">Smart Data Quality Analyst</h3>
                    <p style="color: {COLORS['text_secondary']}; margin: 0; font-size: 0.9rem;">
                        Let automation examine your dataset and suggest cleaning actions
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Check budget before showing AI button
        if check_budget_before_query("data_quality"):
            if st.button("🔬 Analyze Data Quality", type="primary", use_container_width=True, key="ai_quality_btn"):
                with st.spinner("Analyzing your data quality..."):
                    try:
                        agent = get_data_quality_agent()
                        result = agent.analyze(df)
                        st.session_state.quality_report = result
                        # Track cost
                        if result.cost > 0:
                            get_budget_tracker().add_cost(result.cost)
                    except Exception as e:
                        st.error(f"Analysis error: {str(e)}")

        st.markdown("</div>", unsafe_allow_html=True)
    elif is_lite_mode():
        # Show local analysis option in Lite mode
        st.info("Switch to Pro mode in the sidebar for smart data quality analysis.")

    # ══════════════════════════════════════════════════════════════════════════
    # AI QUALITY DASHBOARD (displays if report exists, regardless of mode)
    # ══════════════════════════════════════════════════════════════════════════
    if "quality_report" in st.session_state and AI_AVAILABLE:
        report = st.session_state.quality_report
        if report.success:
            render_quality_dashboard(report, df)
        else:
            st.error(f"Quality analysis failed: {report.content}")

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════════
    # MANUAL CLEANING OPTIONS (existing functionality)
    # ══════════════════════════════════════════════════════════════════════════
    with st.expander("Manual Cleaning Options", expanded=False):
        # 1. Handle Duplicates
        st.subheader("Duplicate Rows")
        num_duplicates = df.duplicated().sum()
        if num_duplicates > 0:
            st.warning(f"Found {num_duplicates} duplicate rows.")
            if st.button("Remove Duplicates"):
                st.session_state.df = df.drop_duplicates()
                st.rerun()
        else:
            st.success("No duplicate rows found.")
        st.markdown("---")

        # 2. Handle Missing Values
        st.subheader("Missing Values")
        missing_data = df.isnull().sum()
        missing_cols = missing_data[missing_data > 0]
        if not missing_cols.empty:
            st.warning(f"Found missing values in {len(missing_cols)} columns.")
            selected_col = st.selectbox("Select column to clean:", options=missing_cols.index)
            st.write(f"Column **{selected_col}** has **{missing_cols[selected_col]}** missing values.")

            # Detect column type and show appropriate options
            is_numeric = pd.api.types.is_numeric_dtype(df[selected_col])

            if is_numeric:
                st.caption("📊 Numeric column detected")
                imputation_options = [
                    "Drop rows with missing values",
                    "Fill with mean",
                    "Fill with median",
                    "Fill with mode"
                ]
            else:
                st.caption("📝 Text/Categorical column detected")
                imputation_options = [
                    "Drop rows with missing values",
                    "Fill with mode (most common value)",
                    "Fill with 'Unknown'"
                ]

            imputation_method = st.radio(
                "Choose cleaning method:",
                imputation_options,
                key=f"impute_{selected_col}"
            )

            if st.button(f"Apply to '{selected_col}'"):
                df_cleaned = st.session_state.df.copy()

                if "Drop" in imputation_method:
                    df_cleaned.dropna(subset=[selected_col], inplace=True)
                    st.toast(f"Dropped rows with missing values in '{selected_col}'.")
                elif "mean" in imputation_method.lower():
                    fill_value = df_cleaned[selected_col].mean()
                    df_cleaned[selected_col].fillna(fill_value, inplace=True)
                    st.toast(f"Filled with mean: {fill_value:.2f}")
                elif "median" in imputation_method.lower():
                    fill_value = df_cleaned[selected_col].median()
                    df_cleaned[selected_col].fillna(fill_value, inplace=True)
                    st.toast(f"Filled with median: {fill_value:.2f}")
                elif "mode" in imputation_method.lower():
                    fill_value = df_cleaned[selected_col].mode()[0]
                    df_cleaned[selected_col].fillna(fill_value, inplace=True)
                    st.toast(f"Filled with mode: '{fill_value}'")
                elif "Unknown" in imputation_method:
                    df_cleaned[selected_col].fillna("Unknown", inplace=True)
                    st.toast(f"Filled with 'Unknown'")

                st.session_state.df = df_cleaned
                st.rerun()
        else:
            st.success("No missing values found.")

        st.markdown("---")

        # 3. Create Indicator Variables (Binary 0/1)
        st.subheader("Create Indicator Variables")
        st.caption("🔢 Create binary columns (0 or 1) from text categories for analysis")

        # Find text/object columns
        text_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if text_cols:
            encode_col = st.selectbox("Select column with text values:", options=text_cols, key="encode_col_select")

            if encode_col:
                unique_values = df[encode_col].dropna().unique().tolist()
                st.write(f"**{encode_col}** has **{len(unique_values)}** unique values")

                # Let user select which values to create indicators for
                st.write("Select values to create indicator columns for:")
                selected_values = st.multiselect(
                    "Each selected value becomes a new column (1 = present, 0 = not present)",
                    options=unique_values,
                    default=unique_values[:5] if len(unique_values) > 5 else unique_values,
                    key="indicator_values"
                )

                if selected_values:
                    # Preview what will be created
                    st.caption("Will create these columns:")
                    for val in selected_values:
                        clean_name = str(val).lower().replace(" ", "_").replace("-", "_")
                        st.caption(f"  • `is_{clean_name}` → 1 if '{val}', 0 otherwise")

                    if st.button("Create Indicator Columns", key="create_indicators"):
                        df_encoded = st.session_state.df.copy()
                        created_cols = []

                        for val in selected_values:
                            # Create clean column name
                            clean_name = str(val).lower().replace(" ", "_").replace("-", "_")
                            new_col = f"is_{clean_name}"

                            # Create binary indicator: 1 if value matches, 0 otherwise
                            df_encoded[new_col] = (df_encoded[encode_col] == val).astype(int)
                            created_cols.append(new_col)

                        st.session_state.df = df_encoded
                        st.success(f"Created {len(created_cols)} indicator columns: {', '.join(created_cols)}")
                        st.rerun()
                else:
                    st.warning("Select at least one value to create indicator columns")
        else:
            st.success("No text columns found - all columns are already numeric!")

    # Data Preview & Clear Button
    with st.expander("Preview Cleaned Data"):
        st.dataframe(st.session_state.df.head(50), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Data & Upload New File", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key.startswith('df') or key in ['data_report', 'upload_time', 'data_is_clean', 'quality_report', 'selected_fixes', 'operations_report']:
                    del st.session_state[key]
            st.rerun()

    with col2:
        # Proceed Button
        if st.button("✅ Confirm & Proceed to Dashboard", type="primary", use_container_width=True):
            st.session_state.data_is_clean = True
            st.balloons()
            st.rerun()


def render_eda_section():
    """
    Render comprehensive Exploratory Data Analysis section.
    Works offline - no AI required.
    """
    st.header("Exploratory Data Analysis")
    st.markdown("Understand your data before identifying bottlenecks")

    df = st.session_state.df
    analytics = get_local_analytics()

    # ══════════════════════════════════════════════════════════════════════════════
    # SECTION 1: DATASET OVERVIEW (Always visible)
    # ══════════════════════════════════════════════════════════════════════════════
    st.markdown("### Dataset Overview")

    quality_report = analytics.get_data_quality_report(df)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card(
            title="Total Records",
            value=quality_report["total_rows"],
            icon="📊",
            status="neutral"
        )
    with col2:
        date_range = quality_report["date_range"]
        if date_range["start"] and date_range["end"]:
            unique_days = df["order_date"].dt.date.nunique() if "order_date" in df.columns else 0
            render_kpi_card(
                title="Unique Days",
                value=unique_days,
                icon="📅",
                status="neutral"
            )
        else:
            render_kpi_card(title="Date Range", value="N/A", icon="📅", status="neutral")
    with col3:
        render_kpi_card(
            title="Columns",
            value=quality_report["total_columns"],
            icon="📋",
            status="neutral"
        )
    with col4:
        score = quality_report["completeness_score"]
        status = "good" if score >= 95 else "warning" if score >= 80 else "danger"
        render_kpi_card(
            title="Completeness",
            value=f"{score:.1f}",
            suffix="%",
            icon="✓",
            status=status
        )

    spacer("1rem")

    # ══════════════════════════════════════════════════════════════════════════════
    # SECTION 2: NUMERICAL DISTRIBUTIONS
    # ══════════════════════════════════════════════════════════════════════════════
    with st.expander("📈 Numerical Distributions", expanded=False):
        st.markdown("Analyze the distribution of time-based metrics")

        time_cols = ["dough_prep_time", "styling_time", "oven_time",
                     "boxing_time", "delivery_duration", "total_process_time"]
        available_time_cols = [c for c in time_cols if c in df.columns]

        if available_time_cols:
            selected_var = st.selectbox(
                "Select Variable",
                available_time_cols,
                format_func=lambda x: x.replace("_", " ").title(),
                key="eda_num_var"
            )

            col1, col2 = st.columns([2, 1])
            with col1:
                fig = histogram_chart(
                    df, selected_var,
                    title=f"Distribution of {selected_var.replace('_', ' ').title()}",
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Summary statistics
                stats = analytics.get_numerical_stats(df)
                if selected_var in stats:
                    var_stats = stats[selected_var]
                    st.markdown(f"**{selected_var.replace('_', ' ').title()}**")
                    st.markdown(f"""
                    <div style="background: {COLORS['bg_card']}; border-radius: 12px; padding: 1rem; border: 1px solid {COLORS['border']};">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                            <div><span style="color: {COLORS['text_muted']};">Mean:</span> <strong>{var_stats['mean']:.2f}</strong></div>
                            <div><span style="color: {COLORS['text_muted']};">Median:</span> <strong>{var_stats['median']:.2f}</strong></div>
                            <div><span style="color: {COLORS['text_muted']};">Std Dev:</span> <strong>{var_stats['std']:.2f}</strong></div>
                            <div><span style="color: {COLORS['text_muted']};">Min:</span> <strong>{var_stats['min']:.2f}</strong></div>
                            <div><span style="color: {COLORS['text_muted']};">Max:</span> <strong>{var_stats['max']:.2f}</strong></div>
                            <div><span style="color: {COLORS['text_muted']};">Q1:</span> <strong>{var_stats['q1']:.2f}</strong></div>
                            <div><span style="color: {COLORS['text_muted']};">Q3:</span> <strong>{var_stats['q3']:.2f}</strong></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # Box plot comparison of all stages
            st.markdown("#### Stage Time Comparison")
            if len(available_time_cols) > 1:
                # Melt data for box plot
                melt_df = df[available_time_cols].melt(var_name="Stage", value_name="Time (min)")
                melt_df["Stage"] = melt_df["Stage"].str.replace("_", " ").str.title()
                fig = box_plot(melt_df, "Stage", "Time (min)", "Time Distribution by Stage", height=350)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No time columns available for distribution analysis.")

    # ══════════════════════════════════════════════════════════════════════════════
    # SECTION 3: CATEGORICAL ANALYSIS
    # ══════════════════════════════════════════════════════════════════════════════
    with st.expander("📊 Categorical Analysis", expanded=False):
        st.markdown("Understand the breakdown of categorical variables")

        cat_data = analytics.get_categorical_counts(df)

        if cat_data:
            # Show donut charts for top 3 categories
            available_cats = list(cat_data.keys())[:3]
            if available_cats:
                cols = st.columns(len(available_cats))
                for i, cat in enumerate(available_cats):
                    with cols[i]:
                        cat_df = cat_data[cat]
                        fig = donut_chart(
                            cat_df, cat, "count",
                            title=cat.replace("_", " ").title(),
                            height=280
                        )
                        st.plotly_chart(fig, use_container_width=True)

            # Category performance comparison
            st.markdown("#### Performance by Category")
            selected_cat = st.selectbox(
                "Select Category",
                list(cat_data.keys()),
                format_func=lambda x: x.replace("_", " ").title(),
                key="eda_cat_var"
            )

            if "total_process_time" in df.columns:
                cat_perf = df.groupby(selected_cat).agg({
                    "total_process_time": ["mean", "count"]
                }).round(1)
                cat_perf.columns = ["Avg Time (min)", "Orders"]
                cat_perf = cat_perf.reset_index()

                fig = bar_chart(
                    cat_perf, selected_cat, "Avg Time (min)",
                    title=f"Average Time by {selected_cat.replace('_', ' ').title()}",
                    show_values=True,
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No categorical columns available for analysis.")

    # ══════════════════════════════════════════════════════════════════════════════
    # SECTION 4: TEMPORAL PATTERNS
    # ══════════════════════════════════════════════════════════════════════════════
    with st.expander("🕐 Temporal Patterns", expanded=False):
        st.markdown("Discover time-based patterns in your operations")

        temporal = analytics.get_temporal_patterns(df)

        col1, col2 = st.columns(2)

        with col1:
            if "hourly" in temporal and temporal["hourly"]:
                hourly_df = pd.DataFrame({
                    "Hour": list(temporal["hourly"].keys()),
                    "Orders": list(temporal["hourly"].values())
                }).sort_values("Hour")
                fig = bar_chart(
                    hourly_df, "Hour", "Orders",
                    title="Orders by Hour of Day",
                    color=COLORS["primary"],
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if "daily" in temporal and temporal["daily"]:
                daily_df = pd.DataFrame({
                    "Day": list(temporal["daily"].keys()),
                    "Orders": list(temporal["daily"].values())
                })
                fig = bar_chart(
                    daily_df, "Day", "Orders",
                    title="Orders by Day of Week",
                    color=COLORS["secondary"],
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)

        # Heatmap: Hour x Day
        if "hour_of_day" in df.columns and "day_of_week" in df.columns:
            st.markdown("#### Order Volume Heatmap")
            heatmap_data = df.groupby(["day_of_week", "hour_of_day"]).size().reset_index(name="orders")
            fig = heatmap(
                heatmap_data, "hour_of_day", "day_of_week", "orders",
                title="Order Volume: Day vs Hour",
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)

        # Peak vs Off-Peak comparison
        if "peak_comparison" in temporal:
            st.markdown("#### Peak vs Off-Peak Performance")
            peak = temporal["peak_comparison"].get("peak", {})
            off_peak = temporal["peak_comparison"].get("off_peak", {})

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div style="background: {COLORS['warning']}15; border: 1px solid {COLORS['warning']}30; border-radius: 12px; padding: 1rem; text-align: center;">
                    <h4 style="color: {COLORS['warning']}; margin: 0;">Peak Hours</h4>
                    <p style="color: {COLORS['text_secondary']}; margin: 0.5rem 0;">Avg Time: <strong>{peak.get('avg_time', 0):.1f} min</strong></p>
                    <p style="color: {COLORS['text_muted']}; margin: 0;">Orders: {peak.get('count', 0):,}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div style="background: {COLORS['success']}15; border: 1px solid {COLORS['success']}30; border-radius: 12px; padding: 1rem; text-align: center;">
                    <h4 style="color: {COLORS['success']}; margin: 0;">Off-Peak Hours</h4>
                    <p style="color: {COLORS['text_secondary']}; margin: 0.5rem 0;">Avg Time: <strong>{off_peak.get('avg_time', 0):.1f} min</strong></p>
                    <p style="color: {COLORS['text_muted']}; margin: 0;">Orders: {off_peak.get('count', 0):,}</p>
                </div>
                """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════════
    # SECTION 5: STAGE ANALYSIS
    # ══════════════════════════════════════════════════════════════════════════════
    with st.expander("⏱️ Stage Analysis", expanded=False):
        st.markdown("Breakdown of time spent at each process stage")

        stage_breakdown = analytics.get_stage_breakdown(df)

        if stage_breakdown:
            # Stage KPI cards
            stage_cols = st.columns(len(stage_breakdown))
            for i, (stage, avg_time) in enumerate(stage_breakdown.items()):
                with stage_cols[i]:
                    benchmark = analytics.BENCHMARKS.get(
                        stage.lower().replace(" ", "_") + "_time",
                        analytics.BENCHMARKS.get(stage.lower().replace(" ", "_") + "_duration", avg_time)
                    )
                    status = "good" if avg_time <= benchmark * 1.1 else "warning" if avg_time <= benchmark * 1.3 else "danger"
                    render_kpi_card(
                        title=stage,
                        value=f"{avg_time:.1f}",
                        suffix=" min",
                        status=status,
                        target=f"Benchmark: {benchmark} min"
                    )

            # Stage proportion visualization
            st.markdown("#### Time Proportion by Stage")
            stage_df = pd.DataFrame({
                "Stage": list(stage_breakdown.keys()),
                "Time": list(stage_breakdown.values())
            })
            total_time = sum(stage_breakdown.values())
            stage_df["Percentage"] = (stage_df["Time"] / total_time * 100).round(1)

            fig = donut_chart(
                stage_df, "Stage", "Time",
                title="Time Distribution by Stage",
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No stage breakdown available.")

    # ══════════════════════════════════════════════════════════════════════════════
    # SECTION 6: CORRELATION INSIGHTS
    # ══════════════════════════════════════════════════════════════════════════════
    with st.expander("🔗 Correlation Insights", expanded=False):
        st.markdown("Discover relationships between variables")

        corr_matrix = analytics.get_correlation_matrix(df)

        if not corr_matrix.empty:
            # Correlation heatmap
            fig = correlation_heatmap(corr_matrix, title="Variable Correlations", height=400)
            st.plotly_chart(fig, use_container_width=True)

            # Key findings
            st.markdown("#### Key Findings")
            strong_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    val = corr_matrix.iloc[i, j]
                    if abs(val) > 0.5:
                        strong_corr.append({
                            "var1": corr_matrix.columns[i].replace("_", " ").title(),
                            "var2": corr_matrix.columns[j].replace("_", " ").title(),
                            "corr": val
                        })

            if strong_corr:
                for item in strong_corr[:5]:
                    direction = "positive" if item["corr"] > 0 else "negative"
                    color = COLORS["success"] if item["corr"] > 0 else COLORS["danger"]
                    st.markdown(f"""
                    <div style="background: {color}10; border-left: 3px solid {color}; padding: 0.5rem 1rem; margin-bottom: 0.5rem; border-radius: 0 8px 8px 0;">
                        <strong>{item['var1']}</strong> ↔ <strong>{item['var2']}</strong>:
                        <span style="color: {color};">{item['corr']:.2f} ({direction})</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("No strong correlations (>0.5) found between variables.")

            # Interactive scatter plot
            st.markdown("#### Explore Relationships")
            num_cols = corr_matrix.columns.tolist()
            col1, col2 = st.columns(2)
            with col1:
                x_var = st.selectbox("X Variable", num_cols, key="eda_scatter_x",
                                     format_func=lambda x: x.replace("_", " ").title())
            with col2:
                y_var = st.selectbox("Y Variable", num_cols, index=1 if len(num_cols) > 1 else 0,
                                     key="eda_scatter_y",
                                     format_func=lambda x: x.replace("_", " ").title())

            if x_var != y_var:
                fig = scatter_plot(
                    df, x_var, y_var,
                    title=f"{x_var.replace('_', ' ').title()} vs {y_var.replace('_', ' ').title()}",
                    trendline="ols",
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough numeric columns for correlation analysis.")

    # ══════════════════════════════════════════════════════════════════════════════
    # SECTION 7: DATA QUALITY SUMMARY
    # ══════════════════════════════════════════════════════════════════════════════
    with st.expander("✅ Data Quality Summary", expanded=False):
        st.markdown("Overview of data completeness and potential issues")

        col1, col2 = st.columns([1, 2])

        with col1:
            # Quality score gauge
            fig = gauge_chart(
                quality_report["completeness_score"],
                title="Data Completeness",
                thresholds={
                    "danger": (0, 80),
                    "warning": (80, 95),
                    "good": (95, 100)
                },
                height=250
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Missing values chart
            fig = missing_values_chart(
                quality_report["missing_pct"],
                title="Missing Values by Column",
                height=250
            )
            st.plotly_chart(fig, use_container_width=True)

        # Outlier detection
        st.markdown("#### Outlier Detection (IQR Method)")
        outliers = analytics.detect_outliers_iqr(df)

        if outliers:
            total_outliers = sum(outliers.values())
            if total_outliers > 0:
                st.warning(f"Found {total_outliers:,} potential outliers across {len([v for v in outliers.values() if v > 0])} columns")

                outlier_df = pd.DataFrame({
                    "Column": [k.replace("_", " ").title() for k in outliers.keys()],
                    "Outliers": list(outliers.values()),
                    "% of Data": [round(v / len(df) * 100, 1) for v in outliers.values()]
                })
                outlier_df = outlier_df[outlier_df["Outliers"] > 0].sort_values("Outliers", ascending=False)

                st.dataframe(outlier_df, use_container_width=True, hide_index=True)
            else:
                st.success("No outliers detected using IQR method!")
        else:
            st.info("No numeric columns available for outlier detection.")

    spacer("1rem")
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; background: {COLORS['bg_card']}; border-radius: 12px; border: 1px solid {COLORS['border']};">
        <p style="color: {COLORS['text_secondary']}; margin: 0;">
            Proceed to <strong>Dashboard Overview</strong> tab for KPIs and bottleneck analysis
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_dashboard_tab():
    """Render the main dashboard overview with AI Business Analyst Agent."""
    st.header("Dashboard Overview")
    df = st.session_state.df

    st.markdown("### Quick Stats")
    stats = get_summary_stats(df)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card(title="Total Orders", value=stats["total_orders"], icon="📦", status="neutral")
    with col2:
        if "delivery_target_met" in df.columns:
            on_time_pct = df["delivery_target_met"].mean() * 100
            status = "good" if on_time_pct >= 85 else "warning" if on_time_pct >= 70 else "danger"
            render_kpi_card(title="On-Time Delivery", value=f"{on_time_pct:.1f}", suffix="%", icon="⏱️", status=status, target="Target: 85%")
    with col3:
        if "complaint" in df.columns:
            complaint_rate = df["complaint"].mean() * 100
            status = "good" if complaint_rate <= 5 else "warning" if complaint_rate <= 10 else "danger"
            render_kpi_card(title="Complaint Rate", value=f"{complaint_rate:.1f}", suffix="%", icon="😤", status=status, target="Target: <5%")
    with col4:
        if "total_process_time" in df.columns:
            avg_time = df["total_process_time"].mean()
            status = "good" if avg_time <= 25 else "warning" if avg_time <= 30 else "danger"
            render_kpi_card(title="Avg Delivery Time", value=f"{avg_time:.1f}", suffix=" min", icon="🚚", status=status, target="Target: 25 min")

    spacer("1.5rem")

    # ══════════════════════════════════════════════════════════════════════════
    # AI BUSINESS ANALYST AGENT SECTION (Pro Mode Only)
    # ══════════════════════════════════════════════════════════════════════════
    if is_pro_mode() and AI_AVAILABLE:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {COLORS['primary']}15 0%, {COLORS['primary']}05 100%);
            border: 1px solid {COLORS['primary']}30;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <span style="font-size: 2rem; margin-right: 1rem;">📊</span>
                <div>
                    <h3 style="color: {COLORS['text_primary']}; margin: 0;">Smart Business Analyst</h3>
                    <p style="color: {COLORS['text_secondary']}; margin: 0; font-size: 0.9rem;">
                        Analyze your operations, find bottlenecks, and get recommendations
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Check budget before showing AI button
        if check_budget_before_query("operations_analysis"):
            if st.button("📊 Analyze Operations", type="primary", use_container_width=True, key="ai_analyst_btn"):
                with st.spinner("Analyzing your operations..."):
                    try:
                        agent = get_business_analyst_agent()
                        result = agent.analyze(df)
                        st.session_state.operations_report = result
                        # Track cost
                        if result.cost > 0:
                            get_budget_tracker().add_cost(result.cost)
                    except Exception as e:
                        st.error(f"Analysis error: {str(e)}")

        st.markdown("</div>", unsafe_allow_html=True)
    elif is_lite_mode():
        # Show local analysis in Lite mode
        st.markdown(f"""
        <div style="
            background: {COLORS['bg_card']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        ">
            <h4 style="color: {COLORS['text_primary']}; margin: 0 0 0.5rem 0;">💡 Lite Mode Active</h4>
            <p style="color: {COLORS['text_secondary']}; margin: 0; font-size: 0.9rem;">
                Using offline analytics. Switch to Pro mode for smart automation.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Show local analytics results
        analytics = get_local_analytics()
        bottlenecks = analytics.detect_bottlenecks(df)
        if bottlenecks:
            st.markdown("#### Detected Bottlenecks (Offline Analysis)")
            for b in bottlenecks[:3]:
                severity_color = COLORS['danger'] if b.severity in ['critical', 'high'] else COLORS['warning']
                st.markdown(f"""
                <div style="
                    background: {severity_color}10;
                    border-left: 3px solid {severity_color};
                    padding: 0.75rem 1rem;
                    border-radius: 0 8px 8px 0;
                    margin-bottom: 0.5rem;
                ">
                    <strong style="color: {COLORS['text_primary']};">{b.area}</strong>
                    <span style="color: {severity_color}; font-size: 0.8rem; margin-left: 0.5rem;">{b.severity.upper()}</span>
                    <p style="color: {COLORS['text_secondary']}; margin: 0.25rem 0 0 0; font-size: 0.875rem;">
                        {b.impact_description}
                    </p>
                </div>
                """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # AI BUSINESS ANALYST DASHBOARD (displays if report exists, regardless of mode)
    # ══════════════════════════════════════════════════════════════════════════
    if "operations_report" in st.session_state and AI_AVAILABLE:
        report = st.session_state.operations_report
        if report.success:
            render_business_analyst_dashboard(report, df)
        else:
            st.error(f"Operations analysis failed: {report.content}")

    st.markdown("---")

    # Quick Ask Section (existing functionality)
    ai = get_ai_service()
    if ai.is_available():
        st.markdown("### 💬 Quick Ask")

        ai_col1, ai_col2 = st.columns([3, 1])

        with ai_col1:
            user_question = st.text_input(
                "Ask about your data",
                placeholder="e.g., Why are complaints higher than target?",
                label_visibility="collapsed",
                key="home_ai_question"
            )

        with ai_col2:
            ask_button = st.button("⚡ Ask", use_container_width=True, key="home_ask_ai")

        # Quick action buttons
        qa_col1, qa_col2, qa_col3, qa_col4 = st.columns(4)
        with qa_col1:
            if st.button("📊 Summary", use_container_width=True, key="qa_summary"):
                user_question = "Give me a quick performance summary"
        with qa_col2:
            if st.button("🎯 Priorities", use_container_width=True, key="qa_priorities"):
                user_question = "What are my top 3 priorities today?"
        with qa_col3:
            if st.button("⚠️ Issues", use_container_width=True, key="qa_issues"):
                user_question = "What issues need immediate attention?"
        with qa_col4:
            if st.button("💡 Quick Wins", use_container_width=True, key="qa_wins"):
                user_question = "What quick wins can I implement today?"

        # Process question
        if (ask_button or user_question) and user_question:
            with st.spinner("Thinking..."):
                response = ai.query(user_question, df)
                if response.success:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, {COLORS['primary']}10 0%, {COLORS['primary']}05 100%);
                        border-left: 4px solid {COLORS['primary']};
                        border-radius: 0 12px 12px 0;
                        padding: 1.25rem;
                        margin: 1rem 0;
                    ">
                        <div style="display: flex; align-items: center; margin-bottom: 0.75rem;">
                            <span style="font-size: 1.25rem; margin-right: 0.5rem;">🤖</span>
                            <strong style="color: {COLORS['text_primary']};">Response</strong>
                            <span style="
                                margin-left: auto;
                                background: {COLORS['primary']}20;
                                color: {COLORS['primary']};
                                padding: 0.2rem 0.6rem;
                                border-radius: 12px;
                                font-size: 0.7rem;
                            ">Cost: ${response.cost:.4f}</span>
                        </div>
                        <div style="color: {COLORS['text_secondary']}; line-height: 1.6;">
                            {response.content.replace(chr(10), '<br>')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(response.content)

        spacer("1rem")

    st.markdown(f'<div style="background-color:{COLORS["bg_card"]};border-radius:12px;padding:1.5rem;border-left:4px solid {COLORS["primary"]};text-align:center;"><h3 style="color:{COLORS["text_primary"]};margin-bottom:0.5rem;">🚀 Analysis Ready</h3><p style="color:{COLORS["text_secondary"]};">Use the sidebar to navigate to other detailed analysis pages.</p></div>', unsafe_allow_html=True)
    spacer("1.5rem")

    with st.expander("📋 Preview Final Data", expanded=False):
        st.dataframe(df.head(100), use_container_width=True, height=400)


if __name__ == "__main__":
    main()
