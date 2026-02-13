"""
AI Assistant Page
=================

Interactive AI-powered analytics assistant for PizzaOps Intelligence.
Chat with your data using natural language.
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.theme import COLORS, CUSTOM_CSS
from ui.layout import page_header, spacer
from ai.service import get_ai_service
from ai.chat_handler import ChatHandler
from ai.insights_generator import render_ai_insight_card, render_ai_quick_actions

# Page config
st.set_page_config(
    page_title="AI Assistant - PizzaOps",
    page_icon="🤖",
    layout="wide"
)

# Apply theme
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_chat_message(role: str, content: str, timestamp: datetime = None):
    """Render a chat message bubble."""
    if role == "user":
        st.markdown(f"""
        <div style="
            display: flex;
            justify-content: flex-end;
            margin: 1rem 0;
        ">
            <div style="
                background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary']}dd 100%);
                color: white;
                padding: 0.875rem 1.25rem;
                border-radius: 18px 18px 4px 18px;
                max-width: 80%;
                font-size: 0.95rem;
                line-height: 1.5;
            ">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="
            display: flex;
            justify-content: flex-start;
            margin: 1rem 0;
        ">
            <div style="
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                color: {COLORS['text_primary']};
                padding: 0.875rem 1.25rem;
                border-radius: 18px 18px 18px 4px;
                max-width: 85%;
                font-size: 0.95rem;
                line-height: 1.6;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.25rem; margin-right: 0.5rem;">🤖</span>
                    <strong style="color: {COLORS['primary']};">AI Assistant</strong>
                </div>
                <div style="color: {COLORS['text_secondary']};">
                    {content}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main AI Assistant page."""

    # Check for data
    df = st.session_state.get("df")

    # Header
    page_header(
        title="AI Assistant",
        icon="🤖",
        description="Chat with your data using natural language. Ask questions, get insights, and receive recommendations."
    )

    # Initialize AI service and chat handler
    ai_service = get_ai_service()
    chat_handler = ChatHandler()

    # Sidebar - AI Status & Controls
    with st.sidebar:
        st.markdown("### 🤖 AI Status")

        if ai_service.is_available():
            st.success("✓ AI Connected")
            st.caption(f"Model: {ai_service.model}")
        else:
            st.error("✗ AI Not Available")
            st.caption("Check ANTHROPIC_API_KEY in .env")
            st.stop()

        st.markdown("---")

        # Session stats
        stats = chat_handler.get_session_stats()
        st.markdown("### 📊 Session Stats")
        col1, col2 = st.columns(2)
        col1.metric("Messages", stats["total_messages"])
        col2.metric("Cost", f"${stats['total_cost']:.4f}")

        st.markdown("---")

        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            chat_handler.clear_history()
            st.rerun()

        # Data status
        st.markdown("---")
        st.markdown("### 📊 Data Status")
        if df is not None:
            st.success(f"✓ {len(df):,} orders loaded")
        else:
            st.warning("No data loaded")
            st.caption("Upload data on the main page for better insights.")

    # Main content area
    if not ai_service.is_available():
        st.error("AI service is not available. Please check your API key.")
        return

    # Two column layout
    chat_col, sidebar_col = st.columns([3, 1])

    with sidebar_col:
        st.markdown("### 💡 Suggested Questions")

        suggestions = chat_handler.get_suggestions(df)
        for suggestion in suggestions[:6]:
            if st.button(suggestion, key=f"suggest_{hash(suggestion)}", use_container_width=True):
                # Process the suggestion
                with st.spinner("Thinking..."):
                    response = chat_handler.send_message(suggestion, df)
                st.rerun()

        spacer("1rem")

        # Quick Actions
        if df is not None:
            st.markdown("### ⚡ Quick Actions")

            if st.button("📊 Full Analysis", use_container_width=True):
                prompt = "Provide a comprehensive analysis of all the data. Include performance metrics, issues, and recommendations."
                with st.spinner("Generating analysis..."):
                    response = chat_handler.send_message(prompt, df)
                st.rerun()

            if st.button("🎯 Today's Priorities", use_container_width=True):
                prompt = "What are the top 3 things I should focus on today based on this data?"
                with st.spinner("Identifying priorities..."):
                    response = chat_handler.send_message(prompt, df)
                st.rerun()

            if st.button("📈 Improvement Plan", use_container_width=True):
                prompt = "Create a prioritized improvement plan with specific actions, expected impact, and timeline."
                with st.spinner("Creating plan..."):
                    response = chat_handler.send_message(prompt, df)
                st.rerun()

    with chat_col:
        # Chat container
        st.markdown(f"""
        <div style="
            background: {COLORS['bg_card']};
            border-radius: 16px;
            padding: 1rem;
            margin-bottom: 1rem;
            min-height: 400px;
            max-height: 600px;
            overflow-y: auto;
        " id="chat-container">
        """, unsafe_allow_html=True)

        # Display chat history
        messages = chat_handler.get_messages()

        if not messages:
            # Welcome message
            st.markdown(f"""
            <div style="
                text-align: center;
                padding: 3rem 2rem;
                color: {COLORS['text_secondary']};
            ">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🤖</div>
                <h3 style="color: {COLORS['text_primary']}; margin-bottom: 0.5rem;">
                    Welcome to AI Assistant
                </h3>
                <p style="margin-bottom: 1.5rem;">
                    I can help you analyze your pizza delivery data, identify issues,
                    and provide actionable recommendations.
                </p>
                <p style="font-size: 0.875rem;">
                    Try asking me:
                </p>
                <div style="
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                    gap: 0.5rem;
                    margin-top: 1rem;
                ">
                    <span style="
                        background: {COLORS['primary']}20;
                        color: {COLORS['primary']};
                        padding: 0.5rem 1rem;
                        border-radius: 20px;
                        font-size: 0.875rem;
                    ">"What's our on-time rate?"</span>
                    <span style="
                        background: {COLORS['primary']}20;
                        color: {COLORS['primary']};
                        padding: 0.5rem 1rem;
                        border-radius: 20px;
                        font-size: 0.875rem;
                    ">"Why are deliveries slow in Area D?"</span>
                    <span style="
                        background: {COLORS['primary']}20;
                        color: {COLORS['primary']};
                        padding: 0.5rem 1rem;
                        border-radius: 20px;
                        font-size: 0.875rem;
                    ">"How can we reduce complaints?"</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in messages:
                render_chat_message(msg.role, msg.content, msg.timestamp)

        st.markdown("</div>", unsafe_allow_html=True)

        # Input area
        st.markdown("---")

        # Chat input
        user_input = st.chat_input("Ask me anything about your data...")

        if user_input:
            with st.spinner("Thinking..."):
                response = chat_handler.send_message(user_input, df)

            if not response.success:
                st.error(response.content)

            st.rerun()

    # Bottom section - AI Insights (if data available)
    if df is not None and len(messages) == 0:
        spacer("2rem")
        st.markdown("---")
        st.markdown("### 🎯 Quick AI Insights")

        # Generate quick insights
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📊 Performance Overview", use_container_width=True, key="overview_btn"):
                with st.spinner("Analyzing..."):
                    response = ai_service.generate_insights(df, "overview")
                    if response.success:
                        st.session_state["quick_insight"] = response.content

        with col2:
            if st.button("🚚 Delivery Analysis", use_container_width=True, key="delivery_btn"):
                with st.spinner("Analyzing..."):
                    response = ai_service.generate_insights(df, "delivery")
                    if response.success:
                        st.session_state["quick_insight"] = response.content

        with col3:
            if st.button("😤 Quality Analysis", use_container_width=True, key="quality_btn"):
                with st.spinner("Analyzing..."):
                    response = ai_service.generate_insights(df, "quality")
                    if response.success:
                        st.session_state["quick_insight"] = response.content

        # Display quick insight if available
        if "quick_insight" in st.session_state:
            spacer("1rem")
            render_ai_insight_card(
                "AI Analysis",
                st.session_state["quick_insight"],
                icon="🤖",
                type="info"
            )


if __name__ == "__main__":
    main()
