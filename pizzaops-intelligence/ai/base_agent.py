"""
Base Agent Module
=================

Shared base class for AI agents using Claude API.
Provides common functionality for data analysis agents.
"""

import os
import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
import pandas as pd

from dotenv import load_dotenv
load_dotenv()


def get_api_key():
    """Get API key from environment, session state, or Streamlit secrets."""
    # First try environment variable
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key and api_key != "your_api_key_here":
        return api_key

    # Then try session state (user-entered key via Settings)
    try:
        import streamlit as st
        if hasattr(st, 'session_state') and st.session_state.get('user_api_key'):
            return st.session_state.user_api_key
    except:
        pass

    # Finally try Streamlit secrets (for Streamlit Cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'ANTHROPIC_API_KEY' in st.secrets:
            return st.secrets['ANTHROPIC_API_KEY']
    except:
        pass

    return None


def get_model():
    """Get model name from environment or Streamlit secrets."""
    # First try environment variable
    model = os.getenv("CLAUDE_MODEL")
    if model:
        return model

    # Then try Streamlit secrets
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'CLAUDE_MODEL' in st.secrets:
            return st.secrets['CLAUDE_MODEL']
    except:
        pass

    return "claude-sonnet-4-20250514"  # Default model


@dataclass
class AgentResponse:
    """Structured response from an AI agent."""
    success: bool
    content: str
    data: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[Dict[str, str]] = field(default_factory=list)
    issues: List[Dict[str, Any]] = field(default_factory=list)
    score: Optional[float] = None
    cost: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class QualityIssue:
    """A data quality issue found by the agent."""
    type: str  # missing, duplicate, outlier, type_error, invalid
    column: str
    severity: str  # low, medium, high, critical
    count: int
    description: str
    suggested_fix: str
    auto_fixable: bool = True


@dataclass
class Bottleneck:
    """A bottleneck identified in operations."""
    area: str  # oven, delivery, prep, etc.
    severity: str  # low, medium, high, critical
    metric_name: str
    current_value: float
    benchmark_value: float
    impact_description: str
    root_cause: str


@dataclass
class Recommendation:
    """A prioritized recommendation."""
    priority: str  # high, medium, quick_win
    title: str
    action: str
    expected_impact: str
    effort_level: str  # low, medium, high
    evidence: str
    timeline: str  # today, this_week, this_month


class BaseAgent(ABC):
    """
    Base class for AI agents.

    Provides common functionality for:
    - Claude API integration
    - Data context building
    - Response parsing
    - Error handling
    """

    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.api_key = get_api_key()
        self.model = get_model()
        self._client = None

    def is_available(self) -> bool:
        """Check if agent is available (API key exists)."""
        return bool(self.api_key)

    def _get_client(self):
        """Get or create the Anthropic client."""
        if self._client is None and self.api_key:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("Anthropic package not installed. Run: pip install anthropic")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Claude client: {e}")
        return self._client

    def _build_data_summary(self, df: pd.DataFrame) -> str:
        """Build a comprehensive data summary for context."""
        summary_parts = []

        # Basic info
        summary_parts.append(f"Dataset Overview:")
        summary_parts.append(f"- Total rows: {len(df):,}")
        summary_parts.append(f"- Total columns: {len(df.columns)}")
        summary_parts.append(f"- Column names: {', '.join(df.columns.tolist())}")

        # Data types
        summary_parts.append(f"\nColumn Types:")
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100
            summary_parts.append(f"- {col}: {dtype} ({null_count} nulls, {null_pct:.1f}%)")

        # Numeric column stats
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary_parts.append(f"\nNumeric Column Statistics:")
            for col in numeric_cols[:10]:  # Limit to first 10
                summary_parts.append(f"- {col}: min={df[col].min():.2f}, max={df[col].max():.2f}, mean={df[col].mean():.2f}, std={df[col].std():.2f}")

        # Sample rows
        summary_parts.append(f"\nSample Data (first 3 rows):")
        sample = df.head(3).to_dict('records')
        for i, row in enumerate(sample):
            summary_parts.append(f"Row {i+1}: {json.dumps(row, default=str)}")

        return "\n".join(summary_parts)

    def _build_performance_context(self, df: pd.DataFrame) -> str:
        """Build performance-specific context for business analysis."""
        context_parts = []

        context_parts.append("Performance Metrics:")

        # On-time rate
        if "delivery_target_met" in df.columns:
            on_time = df["delivery_target_met"].mean() * 100
            status = "OK" if on_time >= 85 else "BELOW TARGET"
            context_parts.append(f"- On-time delivery rate: {on_time:.1f}% (Target: 85%) [{status}]")

        # Complaint rate
        if "complaint" in df.columns:
            complaint_rate = df["complaint"].mean() * 100
            status = "OK" if complaint_rate < 5 else "ABOVE TARGET"
            context_parts.append(f"- Complaint rate: {complaint_rate:.1f}% (Target: <5%) [{status}]")

        # Average delivery time
        if "total_process_time" in df.columns:
            avg_time = df["total_process_time"].mean()
            status = "OK" if avg_time <= 30 else "ABOVE TARGET"
            context_parts.append(f"- Avg total process time: {avg_time:.1f} min (Target: 30 min) [{status}]")

        # Process stage times
        stage_cols = ["dough_prep_time", "styling_time", "oven_time", "boxing_time", "delivery_duration"]
        stage_benchmarks = {"dough_prep_time": 5, "styling_time": 3, "oven_time": 10, "boxing_time": 2, "delivery_duration": 10}

        context_parts.append("\nProcess Stage Breakdown:")
        for col in stage_cols:
            if col in df.columns:
                avg = df[col].mean()
                p95 = df[col].quantile(0.95)
                benchmark = stage_benchmarks.get(col, avg)
                status = "OK" if avg <= benchmark else "SLOW"
                context_parts.append(f"- {col}: avg={avg:.1f}min, p95={p95:.1f}min, benchmark={benchmark}min [{status}]")

        # Area breakdown
        if "delivery_area" in df.columns and "total_process_time" in df.columns:
            context_parts.append("\nBy Delivery Area:")
            area_stats = df.groupby("delivery_area").agg({
                "total_process_time": ["mean", "count"],
                "delivery_target_met": "mean" if "delivery_target_met" in df.columns else "count"
            }).round(2)
            for area in df["delivery_area"].unique():
                if area in area_stats.index:
                    avg_time = df[df["delivery_area"] == area]["total_process_time"].mean()
                    count = len(df[df["delivery_area"] == area])
                    on_time = df[df["delivery_area"] == area]["delivery_target_met"].mean() * 100 if "delivery_target_met" in df.columns else 0
                    context_parts.append(f"- Area {area}: {count} orders, avg {avg_time:.1f}min, {on_time:.0f}% on-time")

        # Peak hours
        if "order_hour" in df.columns and "total_process_time" in df.columns:
            context_parts.append("\nBy Hour (peak detection):")
            hour_stats = df.groupby("order_hour")["total_process_time"].agg(["mean", "count"])
            peak_hour = hour_stats["count"].idxmax()
            peak_count = hour_stats.loc[peak_hour, "count"]
            peak_time = hour_stats.loc[peak_hour, "mean"]
            context_parts.append(f"- Peak hour: {peak_hour}:00 ({peak_count} orders, avg {peak_time:.1f}min)")

        return "\n".join(context_parts)

    def _call_claude(self, prompt: str, max_tokens: int = 2000) -> tuple:
        """
        Call Claude API and return response.

        Returns:
            Tuple of (response_text, cost)
        """
        client = self._get_client()
        if not client:
            raise RuntimeError("Claude client not available")

        response = client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text

        # Calculate cost (Claude Sonnet pricing)
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = (input_tokens * 0.003 + output_tokens * 0.015) / 1000

        return content, cost

    def _parse_json_from_response(self, response: str) -> Optional[Dict]:
        """Try to extract JSON from a response that may contain markdown."""
        # Try to find JSON in code blocks
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end > start:
                try:
                    return json.loads(response[start:end].strip())
                except:
                    pass

        # Try to find JSON in generic code blocks
        if "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                try:
                    return json.loads(response[start:end].strip())
                except:
                    pass

        # Try parsing the whole response
        try:
            return json.loads(response)
        except:
            pass

        return None

    @abstractmethod
    def analyze(self, df: pd.DataFrame) -> AgentResponse:
        """
        Run the agent's analysis on the dataframe.

        Args:
            df: Pandas DataFrame to analyze

        Returns:
            AgentResponse with results
        """
        pass
