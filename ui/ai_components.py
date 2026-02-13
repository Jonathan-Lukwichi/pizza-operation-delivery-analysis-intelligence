"""
AI UI Components
================

Reusable AI-powered UI components for the dashboard.
"""

import streamlit as st
import pandas as pd
from typing import Optional, List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.theme import COLORS


def render_ai_status_badge():
    """Render a small AI status indicator."""
    try:
        from ai.service import get_ai_service
        ai = get_ai_service()
        if ai.is_available():
            st.markdown(f"""
            <div style="
                display: inline-flex;
                align-items: center;
                background: {COLORS['success']}20;
                color: {COLORS['success']};
                padding: 0.25rem 0.75rem;
                border-radius: 12px;
                font-size: 0.75rem;
                margin-bottom: 0.5rem;
            ">
                <span style="
                    width: 6px;
                    height: 6px;
                    background: {COLORS['success']};
                    border-radius: 50%;
                    margin-right: 0.5rem;
                "></span>
                Automation Active
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="
                display: inline-flex;
                align-items: center;
                background: {COLORS['text_muted']}20;
                color: {COLORS['text_muted']};
                padding: 0.25rem 0.75rem;
                border-radius: 12px;
                font-size: 0.75rem;
                margin-bottom: 0.5rem;
            ">
                <span style="
                    width: 6px;
                    height: 6px;
                    background: {COLORS['text_muted']};
                    border-radius: 50%;
                    margin-right: 0.5rem;
                "></span>
                Offline Mode
            </div>
            """, unsafe_allow_html=True)
    except:
        pass


def render_ai_insight_expander(
    df: pd.DataFrame,
    context: str = "overview",
    title: str = "Smart Insights"
):
    """
    Render an expandable AI insights section.

    Args:
        df: Dataframe to analyze
        context: Context type (overview, delivery, process, quality, staff)
        title: Title for the expander
    """
    try:
        from ai.service import get_ai_service

        ai = get_ai_service()
        if not ai.is_available():
            return

        with st.expander(f"🤖 {title}", expanded=False):
            if st.button("Generate Insights", key=f"ai_insight_{context}"):
                with st.spinner("Analyzing..."):
                    response = ai.generate_insights(df, context)
                    if response.success:
                        st.markdown(response.content)
                        st.caption(f"Cost: ${response.cost:.4f}")
                    else:
                        st.error(response.content)
    except ImportError:
        pass


def render_ai_ask_button(df: pd.DataFrame, default_question: str = ""):
    """
    Render an AI ask button with question input.

    Args:
        df: Dataframe for context
        default_question: Default question to show
    """
    try:
        from ai.service import get_ai_service

        ai = get_ai_service()
        if not ai.is_available():
            return

        col1, col2 = st.columns([4, 1])
        with col1:
            question = st.text_input(
                "Ask a question",
                value=default_question,
                placeholder="Ask a question about this data...",
                label_visibility="collapsed"
            )
        with col2:
            ask_clicked = st.button("⚡ Ask", use_container_width=True)

        if ask_clicked and question:
            with st.spinner("Thinking..."):
                response = ai.query(question, df)
                if response.success:
                    st.markdown("### Response")
                    st.markdown(response.content)
                else:
                    st.error(response.content)
    except ImportError:
        pass


def render_ai_metric_insight(
    df: pd.DataFrame,
    metric_name: str,
    current_value: float,
    target_value: float,
    is_higher_better: bool = True
):
    """
    Render AI insight for a specific metric.

    Args:
        df: Dataframe for context
        metric_name: Name of the metric
        current_value: Current value
        target_value: Target value
        is_higher_better: Whether higher values are better
    """
    try:
        from ai.service import get_ai_service

        ai = get_ai_service()
        if not ai.is_available():
            return

        # Determine if this is an issue
        if is_higher_better:
            is_issue = current_value < target_value
        else:
            is_issue = current_value > target_value

        if not is_issue:
            return  # Only show insights for issues

        # Cache key to avoid repeated API calls
        cache_key = f"metric_insight_{metric_name}_{int(current_value)}"
        if cache_key not in st.session_state:
            # Generate insight on demand
            if st.button(f"💡 Why is {metric_name} off-target?", key=f"insight_{metric_name}"):
                with st.spinner("Analyzing..."):
                    prompt = f"{metric_name} is {current_value:.1f} vs target of {target_value:.1f}. Why might this be? Give 2-3 specific causes in under 100 words."
                    response = ai.query(prompt, df, max_tokens=200)
                    if response.success:
                        st.session_state[cache_key] = response.content

        # Display cached insight
        if cache_key in st.session_state:
            st.markdown(f"""
            <div style="
                background: {COLORS['warning']}10;
                border-left: 3px solid {COLORS['warning']};
                padding: 0.75rem 1rem;
                border-radius: 0 8px 8px 0;
                margin-top: 0.5rem;
                font-size: 0.85rem;
                color: {COLORS['text_secondary']};
            ">
                <strong style="color: {COLORS['warning']};">💡 Insight:</strong>
                {st.session_state[cache_key]}
            </div>
            """, unsafe_allow_html=True)
    except ImportError:
        pass


def render_ai_recommendations_panel(df: pd.DataFrame):
    """
    Render a panel with AI-generated recommendations.

    Args:
        df: Dataframe to analyze
    """
    try:
        from ai.service import get_ai_service

        ai = get_ai_service()
        if not ai.is_available():
            return

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {COLORS['primary']}10 0%, {COLORS['primary']}05 100%);
            border: 1px solid {COLORS['primary']}30;
            border-radius: 12px;
            padding: 1.25rem;
            margin: 1rem 0;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem; margin-right: 0.75rem;">🤖</span>
                <h3 style="color: {COLORS['text_primary']}; margin: 0;">Smart Recommendations</h3>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Generate Recommendations", key="gen_recommendations"):
            with st.spinner("Analyzing data and generating recommendations..."):
                response = ai.query(
                    """Based on this data, provide exactly 3 prioritized recommendations:
                    1. [HIGH PRIORITY] - Most impactful improvement
                    2. [MEDIUM PRIORITY] - Important but less urgent
                    3. [QUICK WIN] - Easy to implement

                    For each, include: specific action, expected impact, and effort level.""",
                    df,
                    max_tokens=800
                )
                if response.success:
                    st.session_state["ai_recommendations"] = response.content

        if "ai_recommendations" in st.session_state:
            st.markdown(st.session_state["ai_recommendations"])

        st.markdown("</div>", unsafe_allow_html=True)
    except ImportError:
        pass


def render_ai_chat_widget(df: Optional[pd.DataFrame] = None):
    """
    Render a compact chat widget for quick AI interactions.

    Args:
        df: Optional dataframe for context
    """
    try:
        from ai.service import get_ai_service
        from ai.chat_handler import ChatHandler

        ai = get_ai_service()
        if not ai.is_available():
            return

        chat = ChatHandler()

        # Compact widget container
        st.markdown(f"""
        <div style="
            background: {COLORS['bg_card']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 0.75rem;">
                <span style="font-size: 1.25rem; margin-right: 0.5rem;">💬</span>
                <strong style="color: {COLORS['text_primary']};">Quick Ask</strong>
            </div>
        """, unsafe_allow_html=True)

        question = st.text_input(
            "Ask a question",
            placeholder="Ask anything about your data...",
            label_visibility="collapsed",
            key="quick_ai_input"
        )

        col1, col2, col3 = st.columns(3)
        quick_prompts = [
            "Performance summary",
            "Top issues",
            "Quick wins"
        ]

        for i, (col, prompt) in enumerate(zip([col1, col2, col3], quick_prompts)):
            with col:
                if st.button(prompt, key=f"quick_{i}", use_container_width=True):
                    question = prompt

        if question:
            with st.spinner("Thinking..."):
                response = ai.query(question, df, max_tokens=500)
                if response.success:
                    st.markdown(f"""
                    <div style="
                        background: {COLORS['bg_hover']};
                        border-radius: 8px;
                        padding: 1rem;
                        margin-top: 0.75rem;
                        color: {COLORS['text_secondary']};
                        font-size: 0.9rem;
                        line-height: 1.5;
                    ">
                        {response.content}
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
    except ImportError:
        pass
