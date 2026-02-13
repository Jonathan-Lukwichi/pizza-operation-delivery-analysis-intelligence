"""
Page: Report Generator
Purpose: Auto-generate client-ready PDF or PowerPoint reports
Target User: Analyst / Consultant
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

from core.kpi_engine import calculate_overview_kpis, complaint_analysis, delivery_by_area
from core.process_mining import detect_bottlenecks, get_process_recommendations, oven_temp_analysis
from ui.layout import page_header, section_header, spacer, render_info_box
from ui.theme import COLORS
from reports.pdf_builder import generate_executive_report, FPDF_AVAILABLE
from reports.pptx_builder import generate_executive_presentation, PPTX_AVAILABLE


# ── Page Config ──
st.set_page_config(page_title="Report Generator | PizzaOps", page_icon="📋", layout="wide")

page_header(
    title="Report Generator",
    icon="📋",
    description="Generate professional PDF or PowerPoint reports for stakeholders"
)

# --- Proactive Dependency Check ---
missing_libs = []
if not FPDF_AVAILABLE:
    missing_libs.append("fpdf2")
if not PPTX_AVAILABLE:
    missing_libs.append("python-pptx")

if missing_libs:
    libs_str = " and ".join(missing_libs)
    install_cmd = f"pip install {' '.join(missing_libs)}"
    st.info(f"To enable all report formats, please install the missing libraries by running: `{install_cmd}`")


# ── Guard: Check Data Loaded ──
if "df" not in st.session_state or st.session_state.df is None:
    st.warning("⚠️ Please upload data on the Home page first.")
    st.stop()

# ── Load Data ──
df = st.session_state.df.copy()

spacer("1rem")

# ── Report Configuration ──
section_header("Report Configuration", "Customize your report content")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("**Report Format**")

    # Gracefully handle missing libraries in the UI
    report_options = ["PDF", "PowerPoint"]
    
    def format_report_option(option):
        """Adds a suffix if the library for that option is not available."""
        if option == "PDF" and not FPDF_AVAILABLE:
            return f"{option} (Not Installed)"
        if option == "PowerPoint" and not PPTX_AVAILABLE:
            return f"{option} (Not Installed)"
        return option

    report_format = st.radio(
        "Select format",
        options=report_options,
        format_func=format_report_option,
        horizontal=True,
        label_visibility="collapsed"
    )

    # Prevent proceeding if a disabled option is selected
    if (report_format == "PDF" and not FPDF_AVAILABLE) or \
       (report_format == "PowerPoint" and not PPTX_AVAILABLE):
        st.error(f"{report_format} generation is unavailable. Please install the required library shown above.")
        st.stop()

    st.markdown("**Date Range**")
    if "order_date" in df.columns:
        min_date = df["order_date"].min()
        max_date = df["order_date"].max()

        date_range = st.date_input(
            "Select date range",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date(),
            label_visibility="collapsed"
        )
    else:
        date_range = None

with col2:
    st.markdown("**Include Sections**")
    include_executive = st.checkbox("Executive Summary", value=True)
    include_insights = st.checkbox("Data Insights & Charts", value=True)
    include_complaints = st.checkbox("Complaint Root Cause Analysis", value=True)
    include_recommendations = st.checkbox("Recommendations", value=True)
    include_forecast = st.checkbox("Demand Forecast", value=False)
    include_staff = st.checkbox("Staff Analytics", value=False)

spacer("1rem")

# ── Preview Section ──
section_header("Report Preview", "Preview of report content")

# Filter data by date range
if date_range and len(date_range) == 2:
    df_report = df[
        (df["order_date"] >= pd.Timestamp(date_range[0])) &
        (df["order_date"] <= pd.Timestamp(date_range[1]))
    ]
else:
    df_report = df

# Calculate all metrics
kpis = calculate_overview_kpis(df_report)
complaints = complaint_analysis(df_report)
bottlenecks = detect_bottlenecks(df_report)
oven_analysis = oven_temp_analysis(df_report)
recommendations = get_process_recommendations(bottlenecks, oven_analysis)
area_metrics = delivery_by_area(df_report)

# ── Executive Summary Preview ──
if include_executive:
    with st.expander("📊 Executive Summary", expanded=True):
        st.markdown(f"""
        ### PizzaOps Performance Report

        **Report Period:** {date_range[0].strftime('%d %B %Y') if date_range else 'All Time'} - {date_range[1].strftime('%d %B %Y') if date_range else 'Present'}

        **Generated:** {datetime.now().strftime('%d %B %Y at %H:%M')}

        ---

        #### Key Metrics

        | Metric | Value | Status |
        |--------|-------|--------|
        | Total Orders | {kpis.get('total_orders', 0):,} | - |
        | On-Time Delivery | {kpis.get('on_time_pct', 0):.1f}% | {'✅ On Target' if kpis.get('on_time_pct', 0) >= 85 else '⚠️ Below Target'} |
        | Complaint Rate | {kpis.get('complaint_rate', 0):.1f}% | {'✅ On Target' if kpis.get('complaint_rate', 0) <= 5 else '⚠️ Above Target'} |
        | Avg Delivery Time | {kpis.get('avg_delivery_time', 0):.1f} min | {'✅ On Target' if kpis.get('avg_delivery_time', 0) <= 25 else '⚠️ Above Target'} |

        #### Key Findings

        1. **Delivery Performance:** {'Meeting targets' if kpis.get('on_time_pct', 0) >= 85 else 'Requires improvement - currently at ' + str(round(kpis.get('on_time_pct', 0), 1)) + '% vs 85% target'}

        2. **Quality Issues:** {f"{complaints.get('on_time_complaint_pct', 0):.1f}% of complaints occur on ON-TIME deliveries, indicating quality issues beyond speed" if complaints.get('on_time_complaint_pct', 0) > 20 else 'Complaint rate within acceptable range'}

        3. **Operational Bottlenecks:** {f"Identified {len(bottlenecks)} bottleneck(s) in the preparation pipeline" if bottlenecks else 'No significant bottlenecks detected'}
        """)

# ── Data Insights Preview ──
if include_insights:
    with st.expander("📈 Data Insights", expanded=False):
        st.markdown("""
        ### Performance Analysis

        #### Delivery Performance by Area
        """)

        if len(area_metrics) > 0:
            display_cols = ["delivery_area", "order_count", "avg_delivery_time", "on_time_pct"]
            available_cols = [col for col in display_cols if col in area_metrics.columns]
            st.dataframe(
                area_metrics[available_cols].rename(columns={
                    "delivery_area": "Area",
                    "order_count": "Orders",
                    "avg_delivery_time": "Avg Time (min)",
                    "on_time_pct": "On-Time %"
                }),
                use_container_width=True,
                hide_index=True
            )

        st.markdown("""
        #### Pipeline Stage Analysis
        """)

        if bottlenecks:
            for bn in bottlenecks:
                st.markdown(f"- **{bn['stage'].replace('_', ' ').title()}:** P95 = {bn['actual_p95']} min (benchmark: {bn['benchmark_p95']} min)")
        else:
            st.markdown("All pipeline stages operating within benchmarks.")

# ── Complaint Analysis Preview ──
if include_complaints:
    with st.expander("😤 Complaint Root Cause Analysis", expanded=False):
        st.markdown("""
        ### Complaint Analysis

        #### The Key Finding

        **Complaints don't only happen when delivery is late.** A significant portion of complaints come from ON-TIME deliveries, indicating quality issues:

        - Cold food (oven temperature issues)
        - Wrong orders (order accuracy)
        - Poor quality (ingredient/preparation issues)

        """)

        if complaints.get("by_reason"):
            st.markdown("#### Complaint Reasons")
            for reason, count in sorted(complaints["by_reason"].items(), key=lambda x: -x[1])[:5]:
                st.markdown(f"- {reason}: {count} complaints")

        if complaints.get("on_time_complaint_pct"):
            st.markdown(f"""
            #### Critical Insight

            **{complaints['on_time_complaint_pct']:.1f}%** of all complaints came from orders delivered ON TIME.

            This means improving delivery speed alone will NOT solve the complaint problem.
            Focus areas should include:
            - Oven temperature monitoring
            - Order accuracy verification
            - Food quality at preparation
            """)

# ── Recommendations Preview ──
if include_recommendations:
    with st.expander("💡 Recommendations", expanded=False):
        st.markdown("""
        ### Actionable Recommendations

        Based on the data analysis, here are prioritized recommendations:
        """)

        priority_map = {0: "🔴 High", 1: "🟡 Medium", 2: "🟢 Low"}

        for i, rec in enumerate(recommendations[:5]):
            priority = priority_map.get(min(i, 2), "🟢 Low")
            st.markdown(f"""
            **{priority} Priority**

            {rec}

            ---
            """)

        st.markdown("""
        ### Implementation Roadmap

        | Action | Timeline | Expected Impact |
        |--------|----------|-----------------|
        | Oven temperature protocols | Week 1 | -20% quality complaints |
        | Staff training refresh | Week 2-3 | -15% prep time variability |
        | Route optimization for Area E/C | Week 2-4 | -10% delivery time |
        | Peak hour staffing adjustment | Ongoing | +5% on-time rate |
        """)

spacer("1.5rem")

# ── Generate Report Button ──
st.markdown("---")

col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("🔨 Generate Report", type="primary", use_container_width=True):
        with st.spinner(f"Generating {report_format} report..."):
            # Format date range for reporting
            report_date_str = "All Time"
            if date_range and len(date_range) == 2:
                report_date_str = f"{date_range[0].strftime('%d %b %Y')} - {date_range[1].strftime('%d %b %Y')}"

            # --- Select and run the correct report builder ---
            if report_format == "PDF":
                try:
                    pdf_bytes = generate_executive_report(
                        kpis=kpis,
                        area_metrics=area_metrics,
                        bottlenecks=bottlenecks,
                        recommendations=recommendations,
                        date_range=report_date_str
                    )
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"PizzaOps_Executive_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except ImportError:
                    st.error("Could not generate PDF. The 'fpdf2' library is missing. Please install it using 'pip install fpdf2'.")
                except Exception as e:
                    st.error(f"An error occurred while generating the PDF: {e}")

            elif report_format == "PowerPoint":
                try:
                    pptx_bytes = generate_executive_presentation(
                        kpis=kpis,
                        area_metrics=area_metrics,
                        bottlenecks=bottlenecks,
                        complaint_analysis=complaints,
                        recommendations=recommendations,
                        date_range=report_date_str
                    )
                    st.download_button(
                        label="⬇️ Download PowerPoint Report",
                        data=pptx_bytes,
                        file_name=f"PizzaOps_Executive_Presentation_{datetime.now().strftime('%Y%m%d')}.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        use_container_width=True
                    )
                except ImportError:
                    st.error("Could not generate PowerPoint. The 'python-pptx' library is missing. Please install it using 'pip install python-pptx'.")
                except Exception as e:
                    st.error(f"An error occurred while generating the PowerPoint: {e}")

spacer("1rem")

