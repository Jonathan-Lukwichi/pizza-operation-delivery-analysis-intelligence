"""
Page: Actions
Purpose: Recommendations and action items with WhatsApp export
Works: 100% offline with automated analytics
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

# Add project root to path for Streamlit Cloud
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import get_config
from core.local_analytics import get_local_analytics
from reports.whatsapp_export import render_whatsapp_export_section
from ui.layout import (
    page_header, spacer, render_empty_state,
    render_dashboard_header, render_status_row, render_section_title,
    inject_custom_css
)
from ui.theme import COLORS


# ── Page Config ──
st.set_page_config(page_title="Actions | PizzaOps", page_icon="💡", layout="wide")

config = get_config()

# Inject CSS first
inject_custom_css()

# Professional dashboard header
render_dashboard_header(
    title="Actions & Recommendations",
    logo_text="✓",
    logo_color=COLORS["success"],
    is_live=True,
    live_text="ACTION CENTER"
)

# ── Guard: Check Data Loaded ──
if "df" not in st.session_state or st.session_state.df is None:
    render_empty_state(
        title="No Actions Available",
        message="Upload data to get actionable recommendations",
        icon="⚡",
        cta_text="Upload Data",
        cta_page="1_Home"
    )
    st.stop()

if not st.session_state.get("data_is_clean", False):
    render_empty_state(
        title="Data Needs Cleaning",
        message="Complete data validation to generate actions",
        icon="🧹",
        cta_text="Clean Data",
        cta_page="1_Home"
    )
    st.stop()

# ── Load Data ──
df = st.session_state.df.copy()

# Get local analytics (works offline)
analytics = get_local_analytics()
recommendations = analytics.generate_recommendations(df)
kpis = analytics.get_kpis(df)

# Status indicators row
render_status_row([
    ("Summary", "📊", True, COLORS["primary"]),
    ("Recommendations", "💡", len(recommendations) > 0, COLORS["success"] if len(recommendations) > 0 else None),
    ("Share", "📤", True, COLORS["secondary"]),
    ("Checklist", "✅", True, COLORS["warning"]),
])

# Data indicator with styled badge
st.markdown(f'''
<div style="
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(10, 25, 60, 0.6);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    border: 1px solid rgba(0, 180, 255, 0.15);
    margin-bottom: 1rem;
">
    <span style="color: {COLORS["text_muted"]}; font-size: 0.8rem;">Analyzing</span>
    <span style="color: {COLORS["primary"]}; font-weight: 700; font-size: 0.9rem;">{len(df):,} orders</span>
</div>
''', unsafe_allow_html=True)

spacer("0.5rem")

# ══════════════════════════════════════════════════════════════════════════════
# QUICK SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
render_section_title("Quick Summary", "Current performance at a glance", "📊")

# Extract colors to local variables
text_secondary = COLORS["text_secondary"]
text_muted = COLORS["text_muted"]
text_primary = COLORS["text_primary"]
primary_color = COLORS["primary"]

col1, col2, col3 = st.columns(3)

with col1:
    on_time_status = COLORS["success"] if kpis.on_time_rate >= config.on_time_target_pct else COLORS["danger"]
    on_time_html = f'<div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%); border: 1px solid {on_time_status}30; border-radius: 16px; padding: 1.25rem; text-align: center; backdrop-filter: blur(12px);"><p style="color: {text_secondary}; margin: 0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em;">ON-TIME RATE</p><h2 style="background: linear-gradient(135deg, #FFFFFF 0%, {on_time_status} 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0.75rem 0; font-size: 2rem; font-weight: 800;">{kpis.on_time_rate:.1f}%</h2><p style="color: {text_muted}; margin: 0; font-size: 0.8rem;">Target: {config.on_time_target_pct}%</p></div>'
    st.markdown(on_time_html, unsafe_allow_html=True)

with col2:
    complaint_status = COLORS["success"] if kpis.complaint_rate < config.complaint_target_pct else COLORS["danger"]
    complaint_html = f'<div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%); border: 1px solid {complaint_status}30; border-radius: 16px; padding: 1.25rem; text-align: center; backdrop-filter: blur(12px);"><p style="color: {text_secondary}; margin: 0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em;">COMPLAINT RATE</p><h2 style="background: linear-gradient(135deg, #FFFFFF 0%, {complaint_status} 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0.75rem 0; font-size: 2rem; font-weight: 800;">{kpis.complaint_rate:.1f}%</h2><p style="color: {text_muted}; margin: 0; font-size: 0.8rem;">Target: &lt;{config.complaint_target_pct}%</p></div>'
    st.markdown(complaint_html, unsafe_allow_html=True)

with col3:
    time_status = COLORS["success"] if kpis.avg_delivery_time <= config.delivery_target_minutes else COLORS["danger"]
    delivery_html = f'<div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%); border: 1px solid {time_status}30; border-radius: 16px; padding: 1.25rem; text-align: center; backdrop-filter: blur(12px);"><p style="color: {text_secondary}; margin: 0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em;">AVG DELIVERY</p><h2 style="background: linear-gradient(135deg, #FFFFFF 0%, {time_status} 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0.75rem 0; font-size: 2rem; font-weight: 800;">{kpis.avg_delivery_time:.1f} min</h2><p style="color: {text_muted}; margin: 0; font-size: 0.8rem;">Target: {config.delivery_target_minutes} min</p></div>'
    st.markdown(delivery_html, unsafe_allow_html=True)

spacer("1.5rem")

# ══════════════════════════════════════════════════════════════════════════════
# PRIORITIZED RECOMMENDATIONS (LOCAL)
# ══════════════════════════════════════════════════════════════════════════════
render_section_title("Recommended Actions", "Prioritized improvements based on data", "💡")

if recommendations:
    for i, rec in enumerate(recommendations):
        priority = rec.get("priority", "medium")
        priority_config = {
            "high": {"color": COLORS["danger"], "label": "HIGH PRIORITY", "icon": "🔴"},
            "medium": {"color": COLORS["warning"], "label": "MEDIUM", "icon": "🟡"},
            "quick_win": {"color": COLORS["success"], "label": "QUICK WIN", "icon": "🟢"}
        }.get(priority, {"color": COLORS["primary"], "label": priority.upper(), "icon": "🔵"})

        with st.expander(f"{priority_config['icon']} {rec.get('title', 'Recommendation')}", expanded=i < 2):
            rec_title = rec.get('title', 'Action Required')
            rec_action = rec.get('action', 'N/A')
            rec_impact = rec.get('expected_impact', 'N/A')
            rec_evidence = rec.get('evidence', 'Based on data analysis')
            p_color = priority_config['color']
            p_label = priority_config['label']

            html_content = f'<div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%); border-left: 4px solid {p_color}; padding: 1.25rem; border-radius: 0 12px 12px 0; backdrop-filter: blur(12px);"><span style="background: {p_color}20; color: {p_color}; padding: 0.3rem 0.75rem; border-radius: 20px; font-size: 0.7rem; font-weight: bold; letter-spacing: 0.05em; border: 1px solid {p_color}40;">{p_label}</span><h4 style="color: {text_primary}; margin: 1rem 0 0.75rem 0; font-size: 1.1rem;">{rec_title}</h4><p style="color: {text_secondary}; margin: 0 0 0.75rem 0; line-height: 1.6;"><strong style="color: {primary_color};">Action:</strong> {rec_action}</p><p style="color: {text_secondary}; margin: 0 0 0.75rem 0; line-height: 1.6;"><strong style="color: {primary_color};">Expected Impact:</strong> {rec_impact}</p><p style="color: {text_muted}; margin: 0; font-size: 0.85rem; font-style: italic;">Evidence: {rec_evidence}</p></div>'
            st.markdown(html_content, unsafe_allow_html=True)
else:
    st.success("No urgent actions required - all metrics within targets!")

spacer("1.5rem")

# ══════════════════════════════════════════════════════════════════════════════
# WHATSAPP EXPORT SECTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
render_section_title("Share Summary", "Generate a text summary for your team", "📤")

render_whatsapp_export_section(df)

spacer("1rem")

# ══════════════════════════════════════════════════════════════════════════════
# GENERATE CHECKLIST ITEMS
# ══════════════════════════════════════════════════════════════════════════════
checklist_items = []

# Generate checklist based on issues
if kpis.on_time_rate < config.on_time_target_pct:
    checklist_items.append("Review delivery routes for slow areas")

if kpis.complaint_rate > config.complaint_target_pct:
    checklist_items.append("Address top complaint reasons with staff")

if kpis.avg_delivery_time > config.delivery_target_minutes:
    checklist_items.append("Identify and resolve bottleneck stage")

bottlenecks = analytics.detect_bottlenecks(df)
if bottlenecks:
    checklist_items.append(f"Focus on {bottlenecks[0].area} - biggest bottleneck")

if not checklist_items:
    checklist_items = ["Monitor operations", "Recognize top performers", "Plan for peak hours"]

# ══════════════════════════════════════════════════════════════════════════════
# PDF EXPORT SECTION
# ══════════════════════════════════════════════════════════════════════════════
render_section_title("Download Report", "Generate a professional PDF report", "📄")

if st.button("📄 Generate PDF Report", type="primary", use_container_width=True):
    with st.spinner("Generating PDF..."):
        try:
            from reports.pdf_builder import generate_recommendations_pdf, FPDF_AVAILABLE

            if FPDF_AVAILABLE:
                pdf_bytes = generate_recommendations_pdf(
                    kpis=kpis,
                    recommendations=recommendations,
                    checklist_items=checklist_items,
                    config=config,
                    date_str=datetime.now().strftime("%Y-%m-%d")
                )
                st.session_state.pdf_report = pdf_bytes
                st.success("PDF generated successfully!")
            else:
                st.error("PDF library (fpdf2) not available. Install with: pip install fpdf2")
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")

# Show download button if PDF is ready
if "pdf_report" in st.session_state and st.session_state.pdf_report:
    st.download_button(
        label="⬇️ Download PDF Report",
        data=st.session_state.pdf_report,
        file_name=f"PizzaOps_Actions_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# ══════════════════════════════════════════════════════════════════════════════
# ACTION CHECKLIST DISPLAY
# ══════════════════════════════════════════════════════════════════════════════
spacer("1.5rem")
st.markdown("---")
render_section_title("Today's Checklist", "Track your progress", "✅")

for item in checklist_items:
    st.checkbox(item, key=f"check_{item[:20]}")

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
spacer("2rem")
footer_html = f'''
<div style="
    text-align: center;
    padding: 2rem;
    border-top: 1px solid rgba(0, 180, 255, 0.15);
    position: relative;
">
    <div style="
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, {COLORS["success"]}, {COLORS["secondary"]});
        border-radius: 2px;
    "></div>
    <p style="
        color: {COLORS["success"]};
        font-size: 0.85rem;
        margin: 0 0 0.5rem 0;
        font-weight: 500;
    ">
        Action Center - Powered by Local Analytics
    </p>
    <p style="
        color: {COLORS["text_muted"]};
        font-size: 0.75rem;
        margin: 0;
    ">
        Share summaries via WhatsApp or download PDF reports
    </p>
</div>
'''
st.markdown(footer_html, unsafe_allow_html=True)
