"""
Page: Actions
Purpose: Recommendations and action items with WhatsApp export
Works: Offline (Lite mode) with AI enhancement (Pro mode)
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add project root to path for Streamlit Cloud
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import get_config, is_pro_mode
from core.local_analytics import get_local_analytics
from reports.whatsapp_export import generate_whatsapp_summary, render_whatsapp_export_section
from ui.layout import page_header, spacer, render_empty_state
from ui.theme import COLORS, NEON

# Try to import AI components (for Pro mode)
try:
    from ai.business_analyst import get_business_analyst_agent
    from ai.budget_tracker import get_budget_tracker, check_budget_before_query
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


# ── Page Config ──
st.set_page_config(page_title="Actions | PizzaOps", page_icon="💡", layout="wide")

config = get_config()
page_header(
    title="Actions & Recommendations",
    icon="💡",
    description="Prioritized improvements and next steps"
)

# ── Guard: Check Data Loaded ──
if "df" not in st.session_state or st.session_state.df is None:
    render_empty_state(
        title="No Actions Available",
        message="Upload data to get actionable recommendations",
        icon="⚡",
        cta_text="Upload Data",
        cta_page="0_Home"
    )
    st.stop()

if not st.session_state.get("data_is_clean", False):
    render_empty_state(
        title="Data Needs Cleaning",
        message="Complete data validation to generate actions",
        icon="🧹",
        cta_text="Clean Data",
        cta_page="0_Home"
    )
    st.stop()

# ── Load Data ──
df = st.session_state.df.copy()

# Get local analytics (works offline)
analytics = get_local_analytics()
recommendations = analytics.generate_recommendations(df)
kpis = analytics.get_kpis(df)

# Mode indicator
mode_text = "Pro Mode (Smart Automation)" if is_pro_mode() else "Lite Mode (Offline)"
st.caption(f"Mode: {mode_text}")

spacer("1rem")

# ══════════════════════════════════════════════════════════════════════════════
# QUICK SUMMARY - ESTONIA STYLE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Quick Summary")

# Extract colors to local variables to avoid f-string issues
text_secondary = COLORS["text_secondary"]
text_muted = COLORS["text_muted"]
text_primary = COLORS["text_primary"]
primary_color = COLORS["primary"]
secondary_color = COLORS["secondary"]

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
# PRIORITIZED RECOMMENDATIONS (LOCAL) - ESTONIA STYLE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Recommended Actions")

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

            # Build HTML as a single continuous string with local color variables
            html_content = f'<div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%); border-left: 4px solid {p_color}; padding: 1.25rem; border-radius: 0 12px 12px 0; backdrop-filter: blur(12px);"><span style="background: {p_color}20; color: {p_color}; padding: 0.3rem 0.75rem; border-radius: 20px; font-size: 0.7rem; font-weight: bold; letter-spacing: 0.05em; border: 1px solid {p_color}40;">{p_label}</span><h4 style="color: {text_primary}; margin: 1rem 0 0.75rem 0; font-size: 1.1rem;">{rec_title}</h4><p style="color: {text_secondary}; margin: 0 0 0.75rem 0; line-height: 1.6;"><strong style="color: {primary_color};">Action:</strong> {rec_action}</p><p style="color: {text_secondary}; margin: 0 0 0.75rem 0; line-height: 1.6;"><strong style="color: {primary_color};">Expected Impact:</strong> {rec_impact}</p><p style="color: {text_muted}; margin: 0; font-size: 0.85rem; font-style: italic;">Evidence: {rec_evidence}</p></div>'
            st.markdown(html_content, unsafe_allow_html=True)
else:
    st.success("No urgent actions required - all metrics within targets!")

spacer("1.5rem")

# ══════════════════════════════════════════════════════════════════════════════
# PRO MODE: SMART RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════
if is_pro_mode():
    st.markdown("### Smart Recommendations")

    if AI_AVAILABLE:
        # Show button only if budget available
        if check_budget_before_query("operations_analysis"):
            if st.button("⚡ Get Smart Recommendations", type="primary", use_container_width=True):
                with st.spinner("Generating smart recommendations..."):
                    try:
                        agent = get_business_analyst_agent()
                        result = agent.analyze(df)

                        if result.success and result.recommendations:
                            st.session_state.ai_recommendations = result.recommendations
                            st.session_state.ai_analysis_content = result.content

                            # Track cost
                            if result.cost > 0:
                                get_budget_tracker().add_cost(result.cost)

                            st.success(f"Generated {len(result.recommendations)} smart recommendations!")
                        elif result.success:
                            # AI returned but no recommendations
                            st.session_state.ai_analysis_content = result.content
                            st.info("Analysis complete. See insights below.")
                        else:
                            st.warning("Couldn't generate additional recommendations")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        # Display AI content if available (outside budget check so it persists)
        if "ai_analysis_content" in st.session_state and st.session_state.ai_analysis_content:
            with st.expander("Analysis Summary", expanded=False):
                st.markdown(st.session_state.ai_analysis_content)

        # Display AI recommendations if available (outside budget check so it persists)
        if "ai_recommendations" in st.session_state and st.session_state.ai_recommendations:
            st.markdown("#### Smart Recommendations")

            for rec in st.session_state.ai_recommendations[:5]:
                priority = rec.get("priority", "medium")
                priority_colors = {
                    "high": (COLORS["danger"], f"{COLORS['danger']}20"),
                    "medium": (COLORS["warning"], f"{COLORS['warning']}20"),
                    "quick_win": (COLORS["success"], f"{COLORS['success']}20")
                }
                p_color, p_bg = priority_colors.get(priority, (COLORS["primary"], f"{COLORS['primary']}20"))
                rec_title = rec.get('title', 'Recommendation')
                rec_action = rec.get('action', '')
                rec_impact = rec.get('expected_impact', '')
                rec_evidence = rec.get('evidence', '')

                # Build HTML with more details
                impact_html = f'<p style="color: {text_muted}; margin: 0.5rem 0 0 0; font-size: 0.85rem;"><strong>Impact:</strong> {rec_impact}</p>' if rec_impact else ''
                evidence_html = f'<p style="color: {text_muted}; margin: 0.25rem 0 0 0; font-size: 0.8rem; font-style: italic;">Evidence: {rec_evidence}</p>' if rec_evidence else ''

                ai_rec_html = f'<div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 16px; padding: 1.25rem; margin-bottom: 0.75rem; backdrop-filter: blur(12px);"><div style="display: flex; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;"><span style="background: {p_bg}; color: {p_color}; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.7rem; font-weight: bold; border: 1px solid {p_color}40;">{priority.upper()}</span><strong style="color: {text_primary}; flex: 1;">{rec_title}</strong><span style="background: rgba(139, 92, 246, 0.2); color: {secondary_color}; padding: 0.2rem 0.5rem; border-radius: 12px; font-size: 0.7rem;">⚡ Smart</span></div><p style="color: {text_secondary}; margin: 0; line-height: 1.6;">{rec_action}</p>{impact_html}{evidence_html}</div>'
                st.markdown(ai_rec_html, unsafe_allow_html=True)

            if st.button("Clear Recommendations", key="clear_ai_recs"):
                if "ai_recommendations" in st.session_state:
                    del st.session_state.ai_recommendations
                if "ai_analysis_content" in st.session_state:
                    del st.session_state.ai_analysis_content
                st.rerun()
    else:
        st.info("Smart automation not available. Configure API key in Settings.")

spacer("1.5rem")

# ══════════════════════════════════════════════════════════════════════════════
# WHATSAPP EXPORT SECTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("### Share Summary")
st.markdown("Generate a text summary to share with your team via WhatsApp")

render_whatsapp_export_section(df)

spacer("1rem")

# ══════════════════════════════════════════════════════════════════════════════
# GENERATE CHECKLIST ITEMS (needed for both display and PDF export)
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
st.markdown("### Download Report")
st.markdown("Generate a professional PDF report to print or share via email")

from datetime import datetime

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
st.markdown("### Today's Checklist")

for item in checklist_items:
    st.checkbox(item, key=f"check_{item[:20]}")

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
spacer("2rem")
footer_html = f'<div style="text-align: center; padding: 1.5rem; border-top: 1px solid rgba(59, 130, 246, 0.15);"><p style="color: {primary_color}; font-size: 0.85rem; margin: 0 0 0.25rem 0;">Recommendations generated by Smart Analytics (Pro mode)</p><p style="color: {text_muted}; font-size: 0.8rem; margin: 0;">Share your summary via WhatsApp for team coordination</p></div>'
st.markdown(footer_html, unsafe_allow_html=True)
