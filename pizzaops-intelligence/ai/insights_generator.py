"""
Insights Generator
==================

Generates AI-powered insights for different pages and contexts.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

from .service import get_ai_service, AIResponse


class InsightsGenerator:
    """
    Generates contextual AI insights for different dashboard sections.

    Features:
    - Page-specific insights
    - Cached results for performance
    - Quick insight cards
    - Detailed analysis on demand
    """

    def __init__(self):
        self.ai_service = get_ai_service()

    def _cache_key(self, page: str, df: pd.DataFrame) -> str:
        """Generate a cache key for insights."""
        df_hash = hash(str(len(df)) + str(df.columns.tolist()[:5]))
        return f"insights_{page}_{df_hash}"

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def _generate_cached_insight(_self, prompt: str, data_summary: str) -> str:
        """Generate and cache an insight."""
        ai = get_ai_service()
        if not ai.is_available():
            return "AI insights unavailable. Check API key."

        response = ai.query(prompt, context=data_summary, max_tokens=500)
        return response.content if response.success else "Could not generate insight."

    def get_quick_insight(
        self,
        df: pd.DataFrame,
        metric: str,
        value: float,
        target: Optional[float] = None
    ) -> str:
        """
        Get a quick one-line insight for a metric.

        Args:
            df: Dataframe for context
            metric: Name of the metric
            value: Current value
            target: Optional target value

        Returns:
            A brief insight string
        """
        if not self.ai_service.is_available():
            return ""

        status = ""
        if target:
            if value >= target:
                status = f"above target ({target})"
            else:
                pct_below = ((target - value) / target) * 100
                status = f"{pct_below:.0f}% below target ({target})"

        prompt = f"""In exactly one sentence, explain why {metric} is {value:.1f} {status}.
Be specific about potential causes. No preamble, just the insight."""

        data_summary = f"Total orders: {len(df)}"

        try:
            return self._generate_cached_insight(prompt, data_summary)
        except:
            return ""

    def get_page_insights(
        self,
        page: str,
        df: pd.DataFrame
    ) -> AIResponse:
        """
        Get comprehensive insights for a specific page.

        Args:
            page: Page identifier (executive, process, delivery, etc.)
            df: Dataframe to analyze

        Returns:
            AIResponse with insights
        """
        return self.ai_service.generate_insights(df, page)

    def get_anomaly_explanation(
        self,
        metric: str,
        value: float,
        expected: float,
        df: pd.DataFrame
    ) -> str:
        """
        Explain an anomaly in the data.

        Args:
            metric: The metric name
            value: The anomalous value
            expected: The expected value
            df: Dataframe for context

        Returns:
            Explanation string
        """
        response = self.ai_service.analyze_anomaly(df, metric, value, expected)
        return response.content if response.success else "Could not analyze anomaly."

    def get_recommendation(
        self,
        issue: str,
        df: pd.DataFrame
    ) -> str:
        """
        Get a specific recommendation for an issue.

        Args:
            issue: Description of the issue
            df: Dataframe for context

        Returns:
            Recommendation string
        """
        prompt = f"""Given this issue: "{issue}"

Provide ONE specific, actionable recommendation that can be implemented today.
Include expected impact. Keep it under 100 words."""

        response = self.ai_service.query(prompt, df, max_tokens=300)
        return response.content if response.success else "Could not generate recommendation."


def render_ai_insight_card(
    title: str,
    insight: str,
    icon: str = "💡",
    type: str = "info"
):
    """
    Render an AI insight card in Streamlit.

    Args:
        title: Card title
        insight: The insight text
        icon: Emoji icon
        type: Card type (info, success, warning, danger)
    """
    colors = {
        "info": "#3B82F6",
        "success": "#10B981",
        "warning": "#F59E0B",
        "danger": "#EF4444",
    }
    color = colors.get(type, colors["info"])

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color}15 0%, {color}05 100%);
        border-left: 4px solid {color};
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin: 0.5rem 0;
    ">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-size: 1.25rem; margin-right: 0.5rem;">{icon}</span>
            <strong style="color: #FAFAFA; font-size: 0.9rem;">{title}</strong>
            <span style="
                background: {color}30;
                color: {color};
                font-size: 0.65rem;
                padding: 0.15rem 0.5rem;
                border-radius: 4px;
                margin-left: auto;
            ">AI Generated</span>
        </div>
        <p style="color: #94A3B8; font-size: 0.875rem; margin: 0; line-height: 1.5;">
            {insight}
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_ai_quick_actions(df: pd.DataFrame):
    """
    Render quick AI action buttons.

    Args:
        df: Dataframe for context
    """
    st.markdown("#### 🤖 AI Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Generate Summary", use_container_width=True):
            with st.spinner("Analyzing..."):
                ai = get_ai_service()
                response = ai.generate_insights(df, "overview")
                if response.success:
                    st.markdown("### AI Summary")
                    st.markdown(response.content)
                else:
                    st.error(response.content)

    with col2:
        if st.button("🎯 Top Priorities", use_container_width=True):
            with st.spinner("Identifying priorities..."):
                ai = get_ai_service()
                response = ai.query(
                    "What are the top 3 priorities I should focus on right now? Be specific and actionable.",
                    df
                )
                if response.success:
                    st.markdown("### Top Priorities")
                    st.markdown(response.content)

    with col3:
        if st.button("💡 Quick Wins", use_container_width=True):
            with st.spinner("Finding quick wins..."):
                ai = get_ai_service()
                response = ai.query(
                    "Identify 3 quick wins - improvements that can be made today with minimal effort but good impact.",
                    df
                )
                if response.success:
                    st.markdown("### Quick Wins")
                    st.markdown(response.content)
