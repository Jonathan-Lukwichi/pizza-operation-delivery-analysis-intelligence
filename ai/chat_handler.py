"""
Chat Handler
============

Manages chat conversations and message history for the AI interface.
"""

import streamlit as st
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field
import pandas as pd

from .service import AIService, AIMessage, AIResponse, get_ai_service


@dataclass
class ChatSession:
    """A chat session with history and metadata."""
    id: str
    messages: List[AIMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    total_cost: float = 0.0
    title: str = "New Chat"


class ChatHandler:
    """
    Handles chat sessions and message management.

    Features:
    - Session management
    - Message history
    - Suggested prompts
    - Context injection
    """

    SUGGESTED_PROMPTS = [
        "What's our delivery performance today?",
        "Why are complaints increasing?",
        "Which area has the slowest deliveries?",
        "Who are our top performing drivers?",
        "What bottlenecks should we address first?",
        "How can we reduce delivery times?",
        "What's causing cold food complaints?",
        "Recommend staffing for peak hours",
        "Analyze this week vs last week",
        "What should I focus on today?",
    ]

    def __init__(self):
        self.ai_service = get_ai_service()
        self._init_session_state()

    def _init_session_state(self):
        """Initialize Streamlit session state for chat."""
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []

        if "chat_session_id" not in st.session_state:
            st.session_state.chat_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        if "chat_total_cost" not in st.session_state:
            st.session_state.chat_total_cost = 0.0

    def get_messages(self) -> List[AIMessage]:
        """Get all messages in current session."""
        return st.session_state.chat_messages

    def add_user_message(self, content: str) -> AIMessage:
        """Add a user message to the history."""
        message = AIMessage(role="user", content=content)
        st.session_state.chat_messages.append(message)
        return message

    def add_assistant_message(self, content: str, cost: float = 0.0) -> AIMessage:
        """Add an assistant message to the history."""
        message = AIMessage(
            role="assistant",
            content=content,
            metadata={"cost": cost}
        )
        st.session_state.chat_messages.append(message)
        st.session_state.chat_total_cost += cost
        return message

    def clear_history(self):
        """Clear chat history."""
        st.session_state.chat_messages = []
        st.session_state.chat_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.chat_total_cost = 0.0

    def send_message(
        self,
        message: str,
        df: Optional[pd.DataFrame] = None
    ) -> AIResponse:
        """
        Send a message and get a response.

        Args:
            message: User message
            df: Optional dataframe for context

        Returns:
            AIResponse from the AI service
        """
        # Add user message
        self.add_user_message(message)

        # Get AI response
        history = self.get_messages()[:-1]  # Exclude the message we just added
        response = self.ai_service.chat(message, history, df)

        # Add assistant response
        if response.success:
            self.add_assistant_message(response.content, response.cost)

        return response

    def get_suggestions(self, df: Optional[pd.DataFrame] = None) -> List[str]:
        """
        Get context-aware prompt suggestions.

        Args:
            df: Optional dataframe for contextual suggestions

        Returns:
            List of suggested prompts
        """
        base_suggestions = self.SUGGESTED_PROMPTS.copy()

        # Add contextual suggestions based on data
        if df is not None and len(df) > 0:
            contextual = []

            # Check on-time rate
            if "delivery_target_met" in df.columns:
                on_time = df["delivery_target_met"].mean() * 100
                if on_time < 85:
                    contextual.append(f"Why is on-time rate only {on_time:.1f}%?")

            # Check complaint rate
            if "complaint" in df.columns:
                complaint_rate = df["complaint"].mean() * 100
                if complaint_rate > 5:
                    contextual.append(f"How can we reduce the {complaint_rate:.1f}% complaint rate?")

            # Check for areas
            if "delivery_area" in df.columns:
                areas = df["delivery_area"].unique()
                if len(areas) > 0:
                    contextual.append(f"Compare performance across Area {areas[0]} and Area {areas[-1]}")

            # Add contextual to beginning
            return contextual[:3] + base_suggestions

        return base_suggestions[:8]

    def get_session_stats(self) -> dict:
        """Get statistics about the current chat session."""
        messages = self.get_messages()
        return {
            "total_messages": len(messages),
            "user_messages": sum(1 for m in messages if m.role == "user"),
            "assistant_messages": sum(1 for m in messages if m.role == "assistant"),
            "total_cost": st.session_state.chat_total_cost,
            "session_id": st.session_state.chat_session_id,
        }
