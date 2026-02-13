"""
AI Service Module
=================

Central AI service that powers all AI features in PizzaOps Intelligence.
Integrates with Claude API and manages agent orchestration.
"""

import os
import sys
import json
import asyncio
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import pandas as pd
import streamlit as st

# Add parent directory to path for agents import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()


@dataclass
class AIMessage:
    """A message in the AI conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIResponse:
    """Response from the AI service."""
    content: str
    success: bool = True
    data: Optional[Dict] = None
    suggestions: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    cost: float = 0.0


class AIService:
    """
    Central AI service for PizzaOps Intelligence.

    Provides:
    - Natural language querying of data
    - Automated insights generation
    - Conversational analytics
    - Smart recommendations
    """

    def __init__(self):
        self.api_key = self._get_api_key()
        self.model = self._get_model()
        self._client = None
        self._initialized = False

    def _get_api_key(self):
        """Get API key from environment, session state, or Streamlit secrets."""
        # First try environment variable
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key and api_key != "your_api_key_here":
            return api_key

        # Then try session state (user-entered key via Settings)
        try:
            if hasattr(st, 'session_state') and st.session_state.get('user_api_key'):
                return st.session_state.user_api_key
        except:
            pass

        # Finally try Streamlit secrets (for Streamlit Cloud)
        try:
            if hasattr(st, 'secrets') and 'ANTHROPIC_API_KEY' in st.secrets:
                return st.secrets['ANTHROPIC_API_KEY']
        except:
            pass

        return None

    def _get_model(self):
        """Get model name from environment or Streamlit secrets."""
        model = os.getenv("CLAUDE_MODEL")
        if model:
            return model
        try:
            if hasattr(st, 'secrets') and 'CLAUDE_MODEL' in st.secrets:
                return st.secrets['CLAUDE_MODEL']
        except:
            pass
        return "claude-sonnet-4-20250514"

    def is_available(self) -> bool:
        """Check if AI service is available."""
        # Re-check API key in case user added it via Settings
        current_key = self._get_api_key()
        if current_key and current_key != self.api_key:
            self.api_key = current_key
            self._client = None  # Reset client to use new key
        return bool(self.api_key)

    def _get_client(self):
        """Get or create the Anthropic client."""
        if self._client is None and self.api_key:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
                self._initialized = True
            except ImportError:
                st.warning("Anthropic package not installed. Run: pip install anthropic")
                return None
            except Exception as e:
                st.error(f"Failed to initialize AI: {e}")
                return None
        return self._client

    def _build_system_prompt(self, df: Optional[pd.DataFrame] = None) -> str:
        """Build a context-aware system prompt."""
        base_prompt = """You are an AI-powered business analyst for PizzaOps Intelligence,
a pizza delivery operations analytics platform. You help analyze delivery performance,
identify bottlenecks, predict issues, and provide actionable recommendations.

Your personality:
- Expert in operations analytics and food delivery logistics
- Data-driven and precise with numbers
- Proactive in identifying issues and opportunities
- Clear and actionable in recommendations
- Friendly but professional tone

When analyzing data:
- Always cite specific numbers and percentages
- Compare against targets (85% on-time, <5% complaints, 30 min delivery)
- Identify root causes, not just symptoms
- Prioritize recommendations by impact
- Use emojis sparingly for visual clarity (✅ ❌ ⚠️ 📈 📉)
"""

        if df is not None and len(df) > 0:
            # Add data context
            data_context = self._get_data_context(df)
            base_prompt += f"\n\nCURRENT DATA CONTEXT:\n{data_context}"

        return base_prompt

    def _get_data_context(self, df: pd.DataFrame) -> str:
        """Extract key context from the dataframe."""
        context_parts = []

        # Basic stats
        context_parts.append(f"- Total orders: {len(df):,}")

        # Date range
        if "order_date" in df.columns:
            try:
                dates = pd.to_datetime(df["order_date"])
                context_parts.append(f"- Date range: {dates.min().date()} to {dates.max().date()}")
            except:
                pass

        # On-time rate
        if "delivery_target_met" in df.columns:
            on_time = df["delivery_target_met"].mean() * 100
            context_parts.append(f"- On-time delivery rate: {on_time:.1f}% (target: 85%)")

        # Complaint rate
        if "complaint" in df.columns:
            complaint_rate = df["complaint"].mean() * 100
            context_parts.append(f"- Complaint rate: {complaint_rate:.1f}% (target: <5%)")

        # Average delivery time
        if "total_process_time" in df.columns:
            avg_time = df["total_process_time"].mean()
            context_parts.append(f"- Average delivery time: {avg_time:.1f} min (target: 30 min)")

        # Areas
        if "delivery_area" in df.columns:
            areas = df["delivery_area"].value_counts()
            context_parts.append(f"- Delivery areas: {', '.join(areas.head(5).index.tolist())}")

        # Top issues (if available)
        if "delay_category" in df.columns:
            delays = df["delay_category"].value_counts()
            late_pct = (delays.get("late", 0) + delays.get("critical", 0)) / len(df) * 100
            context_parts.append(f"- Late/Critical deliveries: {late_pct:.1f}%")

        return "\n".join(context_parts)

    def _get_detailed_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get detailed statistics from the dataframe."""
        stats = {
            "total_orders": len(df),
        }

        # Time-based metrics
        time_cols = ["dough_prep_time", "styling_time", "oven_time", "boxing_time", "delivery_duration"]
        for col in time_cols:
            if col in df.columns:
                stats[f"{col}_avg"] = df[col].mean()
                stats[f"{col}_median"] = df[col].median()

        # Performance metrics
        if "delivery_target_met" in df.columns:
            stats["on_time_pct"] = df["delivery_target_met"].mean() * 100

        if "complaint" in df.columns:
            stats["complaint_rate"] = df["complaint"].mean() * 100

        # Area breakdown
        if "delivery_area" in df.columns and "total_process_time" in df.columns:
            area_stats = df.groupby("delivery_area")["total_process_time"].agg(["mean", "count"]).to_dict()
            stats["area_breakdown"] = area_stats

        return stats

    def query(
        self,
        question: str,
        df: Optional[pd.DataFrame] = None,
        context: Optional[str] = None,
        max_tokens: int = 1500
    ) -> AIResponse:
        """
        Query the AI with a question about the data.

        Args:
            question: The user's question
            df: Optional dataframe for context
            context: Additional context string
            max_tokens: Maximum response tokens

        Returns:
            AIResponse with the answer
        """
        client = self._get_client()
        if not client:
            return AIResponse(
                content="AI service is not available. Please check your API key.",
                success=False
            )

        try:
            # Build prompt with data context
            system_prompt = self._build_system_prompt(df)

            # Add detailed stats if dataframe provided
            user_message = question
            if df is not None and len(df) > 0:
                stats = self._get_detailed_stats(df)
                stats_str = json.dumps(stats, indent=2, default=str)
                user_message = f"""Based on this data summary:
```json
{stats_str}
```

User question: {question}

Provide a clear, actionable answer with specific numbers where relevant."""

            if context:
                user_message = f"{context}\n\n{user_message}"

            # Call Claude
            response = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )

            content = response.content[0].text

            # Calculate cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = (input_tokens * 0.003 + output_tokens * 0.015) / 1000

            # Extract suggestions if present
            suggestions = []
            if "recommend" in content.lower() or "suggest" in content.lower():
                # Simple extraction of numbered items
                lines = content.split("\n")
                for line in lines:
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith("-") or line.startswith("•")):
                        if len(line) > 10:  # Filter out short lines
                            suggestions.append(line)

            return AIResponse(
                content=content,
                success=True,
                suggestions=suggestions[:5],  # Top 5 suggestions
                cost=cost
            )

        except Exception as e:
            return AIResponse(
                content=f"Error processing your question: {str(e)}",
                success=False
            )

    def generate_insights(
        self,
        df: pd.DataFrame,
        focus_area: str = "overview"
    ) -> AIResponse:
        """
        Generate automated insights for a specific focus area.

        Args:
            df: The dataframe to analyze
            focus_area: One of "overview", "delivery", "process", "quality", "staff"

        Returns:
            AIResponse with insights
        """
        prompts = {
            "overview": """Analyze this pizza delivery data and provide:
1. Overall performance assessment (1-2 sentences)
2. Top 3 issues requiring attention
3. Top 3 positive trends or wins
4. Priority action for today

Keep it concise and actionable. Use bullet points.""",

            "delivery": """Analyze the delivery performance and provide:
1. Delivery time assessment vs 30-min target
2. Which areas are underperforming and why
3. Driver efficiency observations
4. 2 specific recommendations to improve delivery times

Focus on actionable insights.""",

            "process": """Analyze the process/pipeline stages and provide:
1. Which stage is the biggest bottleneck?
2. How does it compare to benchmarks?
3. Peak hour impact on each stage
4. 2 specific process improvements

Be specific with numbers.""",

            "quality": """Analyze complaint and quality data:
1. Current complaint rate vs 5% target
2. Top complaint reasons and root causes
3. Correlation between delivery time and complaints
4. 2 preventive measures to reduce complaints

Focus on prevention, not just reaction.""",

            "staff": """Analyze staff performance:
1. Top performers and what makes them effective
2. Staff members needing support/training
3. Staffing patterns during peak hours
4. 2 recommendations for staff optimization

Be constructive, not critical."""
        }

        prompt = prompts.get(focus_area, prompts["overview"])
        return self.query(prompt, df)

    def chat(
        self,
        message: str,
        history: List[AIMessage],
        df: Optional[pd.DataFrame] = None
    ) -> AIResponse:
        """
        Continue a conversation with context.

        Args:
            message: The new user message
            history: Previous conversation messages
            df: Optional dataframe for context

        Returns:
            AIResponse with the reply
        """
        client = self._get_client()
        if not client:
            return AIResponse(
                content="AI service is not available.",
                success=False
            )

        try:
            system_prompt = self._build_system_prompt(df)

            # Build messages list with history
            messages = []
            for msg in history[-10:]:  # Last 10 messages for context
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # Add current message
            messages.append({"role": "user", "content": message})

            response = client.messages.create(
                model=self.model,
                max_tokens=1500,
                system=system_prompt,
                messages=messages
            )

            content = response.content[0].text
            cost = (response.usage.input_tokens * 0.003 + response.usage.output_tokens * 0.015) / 1000

            return AIResponse(
                content=content,
                success=True,
                cost=cost
            )

        except Exception as e:
            return AIResponse(
                content=f"Error: {str(e)}",
                success=False
            )

    def analyze_anomaly(
        self,
        df: pd.DataFrame,
        metric: str,
        value: float,
        threshold: float
    ) -> AIResponse:
        """
        Analyze a detected anomaly and explain it.

        Args:
            df: The dataframe for context
            metric: The metric name
            value: The anomalous value
            threshold: The normal threshold

        Returns:
            AIResponse with analysis
        """
        prompt = f"""An anomaly was detected:

Metric: {metric}
Current Value: {value}
Normal Threshold: {threshold}
Deviation: {((value - threshold) / threshold * 100):.1f}%

Analyze this anomaly:
1. What could cause this deviation?
2. Is this a concern or opportunity?
3. What immediate action should be taken?
4. How to prevent/replicate this in future?

Be specific and actionable."""

        return self.query(prompt, df)


# Singleton instance
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """
    Get the AI service instance.

    Creates a new instance if:
    - No instance exists
    - API key status has changed (user added/removed key via Settings)
    """
    global _ai_service

    # Check if we need to create or refresh the instance
    if _ai_service is None:
        _ai_service = AIService()
    else:
        # Check if API key status changed (user may have added one)
        current_key = _ai_service._get_api_key()
        if current_key != _ai_service.api_key:
            # API key changed - create fresh instance
            _ai_service = AIService()

    return _ai_service
