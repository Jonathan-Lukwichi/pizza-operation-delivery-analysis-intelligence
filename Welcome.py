"""
PizzaOps Intelligence - Welcome Page (Entry Point)
Operations Analytics Platform for Food Delivery Businesses
by JLWanalytics - Africa's Premier Data Refinery

FUTURISTIC TECH DESIGN SYSTEM - Dark Navy with Cyan Accents
"""

import streamlit as st
import sys
import os

# Add project root to path for Streamlit Cloud
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.theme import COLORS, CUSTOM_CSS

# ── Page Config ──
st.set_page_config(
    page_title="PizzaOps Intelligence",
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject base theme CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# WELCOME PAGE SPECIFIC CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ===== HIDE SIDEBAR ON WELCOME PAGE ===== */
[data-testid="stSidebar"] {
    display: none !important;
}
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* ===== ANIMATIONS ===== */
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

/* ===== HERO SECTION ===== */
.hero-container {
    text-align: center;
    padding: 2rem 1rem 3rem 1rem;
    position: relative;
}

.hero-row {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    margin-top: 1rem;
}

.hero-pizza {
    font-size: 4.5rem;
    margin-bottom: 1rem;
    filter: drop-shadow(0 4px 20px rgba(0, 180, 255, 0.4));
    animation: float 3s ease-in-out infinite;
}

.hero-title {
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(135deg, #FFFFFF 0%, #00b4ff 50%, #00e5ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.2;
    text-align: center;
    text-shadow: 0 0 60px rgba(0, 180, 255, 0.3);
}

.hero-tagline {
    font-size: 1.25rem;
    color: #00b4ff;
    letter-spacing: 0.12em;
    margin: 0 0 1.5rem 0;
    text-transform: uppercase;
    font-weight: 500;
}

.hero-description {
    font-size: 1.1rem;
    color: #a8c4e0;
    max-width: 600px;
    margin: 0;
    padding: 1.25rem 2rem;
    line-height: 1.6;
    text-align: center;
    background: rgba(10, 25, 60, 0.6);
    border: 1px solid rgba(0, 180, 255, 0.2);
    border-radius: 12px;
    backdrop-filter: blur(12px);
}

.hero-divider {
    width: 120px;
    height: 3px;
    background: linear-gradient(90deg, transparent, #00b4ff, #00e5ff, transparent);
    margin: 2rem auto;
    border-radius: 2px;
}

/* ===== SOCIAL PROOF / METRICS SECTION ===== */
.metrics-container {
    display: flex;
    justify-content: center;
    gap: 3rem;
    margin: 1.5rem auto 2rem auto;
    max-width: 700px;
    flex-wrap: wrap;
}

.metric-item {
    text-align: center;
    padding: 0.5rem 1rem;
}

.metric-value {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #FFFFFF 0%, #00b4ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}

.metric-label {
    font-size: 0.8rem;
    color: #a8c4e0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0.25rem 0 0 0;
}

/* ===== SECTION HEADERS ===== */
.section-title {
    font-size: 1.6rem;
    color: #ffffff;
    margin-bottom: 1.25rem;
    text-align: center;
}

.section-title-gradient {
    font-size: 1.6rem;
    background: linear-gradient(135deg, #FFFFFF 0%, #00b4ff 50%, #00e5ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
    text-align: center;
}

.section-subtitle {
    color: #a8c4e0;
    font-size: 0.95rem;
    text-align: center;
    margin-bottom: 1.5rem;
}

/* ===== PROBLEM CARDS ===== */
.problem-card-red {
    background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 107, 107, 0.05) 100%);
    border: 1px solid rgba(255, 107, 107, 0.3);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    min-height: 140px;
    backdrop-filter: blur(8px);
    transition: all 0.3s ease;
}
.problem-card-red:hover { transform: translateY(-2px); border-color: rgba(255, 107, 107, 0.5); }

.problem-card-orange {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
    border: 1px solid rgba(245, 158, 11, 0.3);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    min-height: 140px;
    backdrop-filter: blur(8px);
    transition: all 0.3s ease;
}
.problem-card-orange:hover { transform: translateY(-2px); border-color: rgba(245, 158, 11, 0.5); }

.problem-card-cyan {
    background: linear-gradient(135deg, rgba(0, 180, 255, 0.1) 0%, rgba(0, 180, 255, 0.05) 100%);
    border: 1px solid rgba(0, 180, 255, 0.3);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    min-height: 140px;
    backdrop-filter: blur(8px);
    transition: all 0.3s ease;
}
.problem-card-cyan:hover { transform: translateY(-2px); border-color: rgba(0, 180, 255, 0.5); }

.problem-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

.problem-title-red {
    color: #ff6b6b;
    font-size: 1.1rem;
    margin: 0 0 0.5rem 0;
    font-weight: 600;
}

.problem-title-orange {
    color: #f59e0b;
    font-size: 1.1rem;
    margin: 0 0 0.5rem 0;
    font-weight: 600;
}

.problem-title-cyan {
    color: #00b4ff;
    font-size: 1.1rem;
    margin: 0 0 0.5rem 0;
    font-weight: 600;
}

.problem-desc {
    color: #a8c4e0;
    font-size: 0.85rem;
    margin: 0;
    line-height: 1.5;
}

/* ===== FEATURE CARDS - TECH GLASSMORPHISM ===== */
.feature-card {
    background: rgba(10, 25, 60, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 12px;
    padding: 1.75rem;
    margin-bottom: 1.25rem;
    position: relative;
    overflow: hidden;
    min-height: 240px;
    display: flex;
    flex-direction: column;
    border: 1px solid rgba(0, 180, 255, 0.12);
    transition: all 0.3s ease;
}
.feature-card:hover {
    transform: translateY(-4px);
    border-color: rgba(0, 180, 255, 0.3);
    box-shadow: 0 4px 30px rgba(0, 180, 255, 0.15);
}

.feature-card-cyan { border-color: rgba(0, 180, 255, 0.3); }
.feature-card-teal { border-color: rgba(0, 229, 255, 0.3); }
.feature-card-green { border-color: rgba(0, 229, 160, 0.3); }

.feature-bar-cyan {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00b4ff, #00e5ff);
}

.feature-bar-teal {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00e5ff, #00b4ff);
}

.feature-bar-green {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00e5a0, #00ffc8);
}

.feature-icon { font-size: 2.5rem; margin-bottom: 0.75rem; }

.feature-title {
    color: #ffffff;
    font-size: 1.15rem;
    margin: 0 0 0.6rem 0;
    font-weight: 600;
}

.feature-desc {
    color: #a8c4e0;
    font-size: 0.9rem;
    line-height: 1.6;
    margin: 0;
    flex-grow: 1;
}

.feature-badge-cyan {
    margin-top: auto;
    padding-top: 0.75rem;
    color: #00b4ff;
    font-size: 0.8rem;
    font-weight: 500;
}

.feature-badge-teal {
    margin-top: auto;
    padding-top: 0.75rem;
    color: #00e5ff;
    font-size: 0.8rem;
    font-weight: 500;
}

.feature-badge-green {
    margin-top: auto;
    padding-top: 0.75rem;
    color: #00e5a0;
    font-size: 0.8rem;
    font-weight: 500;
}

/* ===== MODE CARDS ===== */
.mode-card-green {
    background: linear-gradient(135deg, rgba(0, 229, 160, 0.08) 0%, rgba(0, 229, 160, 0.03) 100%);
    border: 1px solid rgba(0, 229, 160, 0.3);
    border-radius: 12px;
    padding: 1.75rem;
    text-align: center;
    min-height: 280px;
    backdrop-filter: blur(8px);
    transition: all 0.3s ease;
}
.mode-card-green:hover { transform: translateY(-2px); border-color: rgba(0, 229, 160, 0.5); }

.mode-card-cyan {
    background: linear-gradient(135deg, rgba(0, 180, 255, 0.08) 0%, rgba(0, 180, 255, 0.03) 100%);
    border: 1px solid rgba(0, 180, 255, 0.3);
    border-radius: 12px;
    padding: 1.75rem;
    text-align: center;
    min-height: 280px;
    backdrop-filter: blur(8px);
    transition: all 0.3s ease;
}
.mode-card-cyan:hover { transform: translateY(-2px); border-color: rgba(0, 180, 255, 0.5); }

.mode-icon { font-size: 2.25rem; margin-bottom: 0.75rem; }

.mode-title-green {
    color: #00e5a0;
    font-size: 1.35rem;
    margin: 0 0 0.25rem 0;
    font-weight: 700;
}

.mode-title-cyan {
    color: #00b4ff;
    font-size: 1.35rem;
    margin: 0 0 0.25rem 0;
    font-weight: 700;
}

.mode-subtitle-green {
    color: #00ffc8;
    font-size: 0.85rem;
    margin-bottom: 1.25rem;
}

.mode-subtitle-cyan {
    color: #00e5ff;
    font-size: 0.85rem;
    margin-bottom: 1.25rem;
}

.mode-list {
    text-align: left;
    color: #a8c4e0;
    list-style: none;
    padding: 0;
    margin: 0;
}

.mode-list-item-green {
    padding: 0.4rem 0;
    border-bottom: 1px solid rgba(0, 229, 160, 0.15);
    font-size: 0.9rem;
}

.mode-list-item-cyan {
    padding: 0.4rem 0;
    border-bottom: 1px solid rgba(0, 180, 255, 0.15);
    font-size: 0.9rem;
}

.mode-check-green { color: #00e5a0; margin-right: 0.5rem; }
.mode-check-cyan { color: #00b4ff; margin-right: 0.5rem; }

/* ===== CTA SECTION ===== */
.cta-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 3rem 2rem;
    background: linear-gradient(135deg, rgba(0, 180, 255, 0.1) 0%, rgba(0, 229, 255, 0.08) 100%);
    border-radius: 16px;
    border: 1px solid rgba(0, 180, 255, 0.2);
    margin: 1.5rem auto;
    backdrop-filter: blur(8px);
    max-width: 800px;
}

.cta-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 1rem 0;
    text-align: center;
    width: 100%;
}

.cta-desc {
    color: #a8c4e0;
    font-size: 1rem;
    margin: 0;
    max-width: 500px;
    line-height: 1.6;
    text-align: center;
}

/* ===== TESTIMONIAL ===== */
.testimonial-container {
    text-align: center;
    padding: 1.5rem;
    max-width: 600px;
    margin: 0 auto 2rem auto;
}

.testimonial-quote {
    font-size: 1rem;
    color: #a8c4e0;
    font-style: italic;
    margin: 0 0 0.75rem 0;
    line-height: 1.6;
}

.testimonial-author {
    color: #00b4ff;
    font-size: 0.85rem;
    margin: 0;
    font-weight: 500;
}

/* ===== FOOTER ===== */
.welcome-footer {
    text-align: center;
    padding: 1.5rem 0;
    border-top: 1px solid rgba(0, 180, 255, 0.15);
    margin-top: 1.5rem;
}

.footer-line1 {
    color: #6889a8;
    font-size: 0.8rem;
    margin: 0 0 0.35rem 0;
}

.footer-line2 {
    color: #a8c4e0;
    font-size: 0.85rem;
    margin: 0;
}

.footer-brand {
    background: linear-gradient(135deg, #00b4ff, #00e5ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: bold;
}

/* ===== UTILITY SPACERS ===== */
.spacer-1 { height: 0.75rem; }
.spacer-2 { height: 1.5rem; }
.spacer-3 { height: 2.5rem; }

/* ===== MOBILE RESPONSIVE ===== */
@media (max-width: 768px) {
    .hero-row { gap: 0.75rem; }
    .hero-title { font-size: 2.25rem; }
    .hero-tagline { font-size: 1rem; }
    .hero-description { font-size: 1rem; padding: 1rem 1.25rem; max-width: 100%; }
    .metrics-container { gap: 1.5rem; }
    .metric-value { font-size: 1.5rem; }
    .feature-card { min-height: auto; padding: 1.5rem; }
    .mode-card-green, .mode-card-cyan { min-height: auto; }
}

/* ===== TABLET & SMALL LAPTOP (640px) ===== */
@media (max-width: 640px) {
    .hero-pizza { font-size: 2.5rem; }
    .hero-title { font-size: 1.75rem; }
    .hero-tagline { font-size: 0.9rem; letter-spacing: 0.08em; }
    .hero-description { font-size: 0.9rem; padding: 0.875rem 1rem; }
    .hero-divider { width: 80px; }
    .metrics-container { gap: 1rem; }
    .metric-value { font-size: 1.35rem; }
    .metric-label { font-size: 0.7rem; }
    .section-title { font-size: 1.25rem; }
}

/* ===== PHONE (480px) ===== */
@media (max-width: 480px) {
    .hero-container { padding: 1.5rem 0.5rem 2rem 0.5rem; }
    .hero-pizza { font-size: 2rem; }
    .hero-title { font-size: 1.5rem; }
    .hero-tagline { font-size: 0.8rem; }
    .hero-description { font-size: 0.85rem; padding: 0.75rem 0.875rem; }

    .problem-card-red, .problem-card-orange, .problem-card-cyan {
        padding: 1rem !important;
        min-height: auto !important;
    }
    .problem-title-red, .problem-title-orange, .problem-title-cyan { font-size: 0.95rem; }
    .problem-desc { font-size: 0.8rem; }
    .problem-icon { font-size: 1.5rem; }

    .feature-card { padding: 1.25rem !important; min-height: auto !important; }
    .feature-icon { font-size: 2rem; }
    .feature-title { font-size: 1rem; }
    .feature-desc { font-size: 0.85rem; }

    .mode-card-green, .mode-card-cyan { padding: 1.25rem !important; min-height: auto !important; }
    .mode-title { font-size: 1.1rem; }
    .mode-desc { font-size: 0.85rem; }
    .mode-list { font-size: 0.8rem; }
    .mode-list li { padding: 0.3rem 0; }

    .cta-container { padding: 1.5rem 1rem; }
    .cta-title { font-size: 1.25rem; }
    .cta-desc { font-size: 0.9rem; }

    .testimonial-quote { font-size: 0.9rem; }
    .testimonial-author { font-size: 0.8rem; }

    .metrics-container { gap: 0.75rem; flex-wrap: wrap; justify-content: center; }
    .metric-item { min-width: 80px; padding: 0.35rem 0.5rem; }
    .metric-value { font-size: 1.2rem; }
    .metric-label { font-size: 0.65rem; }

    .section-title { font-size: 1.1rem; margin-bottom: 1rem; }
}

/* ===== SMALL PHONE (360px) ===== */
@media (max-width: 360px) {
    .hero-pizza { font-size: 1.75rem; }
    .hero-title { font-size: 1.35rem; }
    .hero-tagline { font-size: 0.75rem; }
    .hero-description { font-size: 0.8rem; }
    .metric-value { font-size: 1.1rem; }
    .cta-title { font-size: 1.15rem; }
    .feature-title { font-size: 0.95rem; }
    .mode-title { font-size: 1rem; }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HERO SECTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-container">
    <div class="hero-pizza">🍕</div>
    <p class="hero-tagline">Real-Time Operations Analytics</p>
    <div class="hero-row">
        <h1 class="hero-title">PizzaOps Intelligence</h1>
        <p class="hero-description">Transform your pizza business with AI-powered insights, offline analytics, and instant team communication</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SOCIAL PROOF - KEY METRICS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="metrics-container">
    <div class="metric-item">
        <p class="metric-value">10,000+</p>
        <p class="metric-label">Orders Analyzed</p>
    </div>
    <div class="metric-item">
        <p class="metric-value">35%</p>
        <p class="metric-label">Faster Insights</p>
    </div>
    <div class="metric-item">
        <p class="metric-value">98%</p>
        <p class="metric-label">User Satisfaction</p>
    </div>
</div>
<div class="hero-divider"></div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PROBLEM STATEMENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<h2 class="section-title">Running a Pizza Business is Hard...</h2>', unsafe_allow_html=True)

prob_col1, prob_col2, prob_col3 = st.columns(3)

with prob_col1:
    st.markdown("""
    <div class="problem-card-red">
        <div class="problem-icon">⏰</div>
        <h4 class="problem-title-red">Late Deliveries</h4>
        <p class="problem-desc">Customers waiting too long, reputation suffering</p>
    </div>
    """, unsafe_allow_html=True)

with prob_col2:
    st.markdown("""
    <div class="problem-card-orange">
        <div class="problem-icon">😤</div>
        <h4 class="problem-title-orange">Complaints Rising</h4>
        <p class="problem-desc">No visibility into what's going wrong</p>
    </div>
    """, unsafe_allow_html=True)

with prob_col3:
    st.markdown("""
    <div class="problem-card-cyan">
        <div class="problem-icon">🔄</div>
        <h4 class="problem-title-cyan">Hidden Bottlenecks</h4>
        <p class="problem-desc">Slow stages in your pipeline you can't see</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="spacer-2"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SOLUTION - FEATURE CARDS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<h2 class="section-title-gradient">The Solution</h2>
<p class="section-subtitle">Four powerful tools to transform your operations</p>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card feature-card-cyan">
        <div class="feature-bar-cyan"></div>
        <div class="feature-icon">📊</div>
        <h3 class="feature-title">Dashboard</h3>
        <p class="feature-desc">Real-time KPIs at a glance. Track orders, on-time rates, complaints, and delivery times with beautiful visualizations.</p>
        <div class="feature-badge-cyan">✓ Works 100% Offline</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card feature-card-teal">
        <div class="feature-bar-teal"></div>
        <div class="feature-icon">💡</div>
        <h3 class="feature-title">Actions & Recommendations</h3>
        <p class="feature-desc">Get prioritized action items. Know exactly what to fix first for maximum impact on your business.</p>
        <div class="feature-badge-teal">✓ AI-Powered Insights</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card feature-card-cyan">
        <div class="feature-bar-cyan"></div>
        <div class="feature-icon">🔍</div>
        <h3 class="feature-title">Problems & Root Cause</h3>
        <p class="feature-desc">Identify bottlenecks instantly. See which stage is slowing you down and which areas need attention.</p>
        <div class="feature-badge-cyan">✓ Automatic Detection</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card feature-card-green">
        <div class="feature-bar-green"></div>
        <div class="feature-icon">📱</div>
        <h3 class="feature-title">WhatsApp Export</h3>
        <p class="feature-desc">Share summaries with your team instantly. One click to copy formatted reports for your staff group.</p>
        <div class="feature-badge-green">✓ Team Communication</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="spacer-2"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MODES COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<h2 class="section-title">Choose Your Mode</h2>
<p class="section-subtitle">Pick what works best for your business</p>
""", unsafe_allow_html=True)

mode_col1, mode_col2 = st.columns(2)

with mode_col1:
    st.markdown("""
    <div class="mode-card-green">
        <div class="mode-icon">⚡</div>
        <h3 class="mode-title-green">Lite Mode</h3>
        <p class="mode-subtitle-green">Works Offline</p>
        <div class="mode-list">
            <p class="mode-list-item-green"><span class="mode-check-green">✓</span> Load Shedding Safe</p>
            <p class="mode-list-item-green"><span class="mode-check-green">✓</span> No Internet Required</p>
            <p class="mode-list-item-green"><span class="mode-check-green">✓</span> Zero API Costs</p>
            <p class="mode-list-item-green" style="border: none;"><span class="mode-check-green">✓</span> Basic Analytics</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with mode_col2:
    st.markdown("""
    <div class="mode-card-cyan">
        <div class="mode-icon">🤖</div>
        <h3 class="mode-title-cyan">Pro Mode</h3>
        <p class="mode-subtitle-cyan">AI-Powered</p>
        <div class="mode-list">
            <p class="mode-list-item-cyan"><span class="mode-check-cyan">✓</span> Smart Recommendations</p>
            <p class="mode-list-item-cyan"><span class="mode-check-cyan">✓</span> Deep Root Cause Analysis</p>
            <p class="mode-list-item-cyan"><span class="mode-check-cyan">✓</span> Budget Controlled (ZAR)</p>
            <p class="mode-list-item-cyan" style="border: none;"><span class="mode-check-cyan">✓</span> Advanced Insights</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="spacer-2"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SOCIAL PROOF - TESTIMONIAL
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="testimonial-container">
    <p class="testimonial-quote">"PizzaOps helped us cut delivery complaints by 40% in just 2 weeks. The insights were eye-opening."</p>
    <p class="testimonial-author">— Operations Manager, Pretoria</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CTA SECTION
# ══════════════════════════════════════════════════════════════════════════════
cta_col1, cta_col2, cta_col3 = st.columns([1, 3, 1])
with cta_col2:
    st.markdown("""
    <div class="cta-container">
        <h2 class="cta-title">Ready to Transform Your Operations?</h2>
        <p class="cta-desc">Upload your data and get instant insights. No technical knowledge required.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="spacer-1"></div>', unsafe_allow_html=True)

    if st.button("🚀 Get Started Now", type="primary", use_container_width=True):
        st.switch_page("pages/0_Home.py")

    st.markdown('<div class="spacer-1"></div>', unsafe_allow_html=True)

    if st.button("📖 Learn How It Works", type="secondary", use_container_width=True):
        st.switch_page("pages/0_Home.py")

st.markdown('<div class="spacer-2"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="welcome-footer">
    <p class="footer-line1">Designed for South African Pizza Businesses</p>
    <p class="footer-line2">Built by <span class="footer-brand">JLWanalytics</span> | Africa's Premier Data Refinery</p>
</div>
""", unsafe_allow_html=True)
