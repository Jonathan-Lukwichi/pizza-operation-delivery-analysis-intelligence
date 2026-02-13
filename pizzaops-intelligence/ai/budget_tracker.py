"""
AI Budget Tracker
==================

Track and limit AI spending per session.
Optimized for South African market with ZAR display.
"""

from typing import Optional
from datetime import datetime, date
from dataclasses import dataclass
import streamlit as st


@dataclass
class BudgetStatus:
    """Current budget status."""
    spent_usd: float
    spent_zar: float
    remaining_zar: float
    daily_limit_zar: float
    usage_pct: float
    is_over_budget: bool
    queries_today: int


class BudgetTracker:
    """
    Track and limit AI spending per session.

    Designed for SA market:
    - Displays costs in ZAR
    - Default R50 daily limit
    - Warns before expensive queries
    """

    # Exchange rate (updated periodically)
    USD_TO_ZAR = 18.50

    # Default limits
    DEFAULT_DAILY_LIMIT_ZAR = 50.0  # R50 per day
    WARN_THRESHOLD_PCT = 80  # Warn at 80% usage

    # Cost estimates for different operations
    COST_ESTIMATES = {
        "data_quality": 0.05,  # ~$0.05 per quality analysis
        "operations_analysis": 0.08,  # ~$0.08 per ops analysis
        "quick_query": 0.02,  # ~$0.02 per quick Q&A
        "detailed_analysis": 0.10,  # ~$0.10 for detailed analysis
    }

    def __init__(self, daily_limit_zar: float = None):
        """
        Initialize budget tracker.

        Args:
            daily_limit_zar: Daily spending limit in ZAR (default R50)
        """
        self.daily_limit_zar = daily_limit_zar or self.DEFAULT_DAILY_LIMIT_ZAR
        self._init_session_state()

    def _init_session_state(self):
        """Initialize session state for tracking."""
        if "budget_date" not in st.session_state:
            st.session_state.budget_date = date.today()

        if "session_cost_usd" not in st.session_state:
            st.session_state.session_cost_usd = 0.0

        if "session_queries" not in st.session_state:
            st.session_state.session_queries = 0

        # Reset if new day
        if st.session_state.budget_date != date.today():
            st.session_state.budget_date = date.today()
            st.session_state.session_cost_usd = 0.0
            st.session_state.session_queries = 0

    def get_status(self) -> BudgetStatus:
        """Get current budget status."""
        self._init_session_state()

        spent_usd = st.session_state.session_cost_usd
        spent_zar = spent_usd * self.USD_TO_ZAR
        remaining_zar = max(0, self.daily_limit_zar - spent_zar)
        usage_pct = (spent_zar / self.daily_limit_zar) * 100 if self.daily_limit_zar > 0 else 0

        return BudgetStatus(
            spent_usd=round(spent_usd, 4),
            spent_zar=round(spent_zar, 2),
            remaining_zar=round(remaining_zar, 2),
            daily_limit_zar=self.daily_limit_zar,
            usage_pct=round(usage_pct, 1),
            is_over_budget=spent_zar >= self.daily_limit_zar,
            queries_today=st.session_state.session_queries
        )

    def has_budget(self) -> bool:
        """Check if within daily budget."""
        status = self.get_status()
        return not status.is_over_budget

    def should_warn(self) -> bool:
        """Check if we should warn about budget usage."""
        status = self.get_status()
        return status.usage_pct >= self.WARN_THRESHOLD_PCT and not status.is_over_budget

    def add_cost(self, cost_usd: float):
        """
        Record a cost.

        Args:
            cost_usd: Cost in USD
        """
        self._init_session_state()
        st.session_state.session_cost_usd += cost_usd
        st.session_state.session_queries += 1

    def estimate_cost_zar(self, operation: str) -> float:
        """
        Estimate cost for an operation in ZAR.

        Args:
            operation: Operation type (data_quality, operations_analysis, etc.)

        Returns:
            Estimated cost in ZAR
        """
        cost_usd = self.COST_ESTIMATES.get(operation, 0.05)
        return round(cost_usd * self.USD_TO_ZAR, 2)

    def format_cost_zar(self, cost_usd: float) -> str:
        """
        Format USD cost as ZAR string.

        Args:
            cost_usd: Cost in USD

        Returns:
            Formatted string like "R1.85"
        """
        cost_zar = cost_usd * self.USD_TO_ZAR
        return f"R{cost_zar:.2f}"

    def get_remaining_budget_message(self) -> str:
        """Get a user-friendly remaining budget message."""
        status = self.get_status()

        if status.is_over_budget:
            return "Daily AI budget exceeded. Using offline mode."
        elif status.remaining_zar < 5:
            return f"Low budget: R{status.remaining_zar:.2f} remaining"
        else:
            return f"R{status.remaining_zar:.2f} AI budget remaining"


# Singleton instance
_budget_tracker: Optional[BudgetTracker] = None


def get_budget_tracker(daily_limit_zar: float = None) -> BudgetTracker:
    """Get the singleton BudgetTracker instance."""
    global _budget_tracker
    if _budget_tracker is None:
        _budget_tracker = BudgetTracker(daily_limit_zar)
    return _budget_tracker


def render_budget_widget():
    """
    Render the budget widget in the sidebar.

    Call this from app.py sidebar.
    """
    tracker = get_budget_tracker()
    status = tracker.get_status()

    # Color based on usage
    if status.is_over_budget:
        color = "#EF4444"  # Red
        status_text = "BUDGET EXCEEDED"
    elif status.usage_pct >= 80:
        color = "#F59E0B"  # Orange
        status_text = "LOW BUDGET"
    else:
        color = "#22C55E"  # Green
        status_text = "BUDGET OK"

    st.sidebar.markdown(f"""
    <div style="
        background: {color}15;
        border: 1px solid {color}30;
        border-radius: 8px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="color: {color}; font-size: 0.8rem; font-weight: bold;">AI Budget</span>
            <span style="color: {color}; font-size: 0.7rem;">{status_text}</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
            <span style="color: #666; font-size: 0.75rem;">Spent:</span>
            <span style="color: #333; font-size: 0.75rem;">R{status.spent_zar:.2f}</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="color: #666; font-size: 0.75rem;">Remaining:</span>
            <span style="color: {color}; font-size: 0.75rem; font-weight: bold;">R{status.remaining_zar:.2f}</span>
        </div>
        <div style="
            background: #E5E5E5;
            border-radius: 4px;
            height: 6px;
            overflow: hidden;
        ">
            <div style="
                background: {color};
                height: 100%;
                width: {min(status.usage_pct, 100)}%;
                transition: width 0.3s ease;
            "></div>
        </div>
        <div style="text-align: center; margin-top: 0.5rem;">
            <span style="color: #999; font-size: 0.65rem;">{status.queries_today} queries today</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def check_budget_before_query(operation: str = "quick_query") -> bool:
    """
    Check budget before making an AI query.

    Args:
        operation: Type of operation for cost estimation

    Returns:
        True if query should proceed, False if over budget
    """
    tracker = get_budget_tracker()

    if not tracker.has_budget():
        st.warning("Daily AI budget exceeded. Switching to offline analysis.")
        return False

    if tracker.should_warn():
        estimated = tracker.estimate_cost_zar(operation)
        status = tracker.get_status()
        st.info(f"Budget: R{status.remaining_zar:.2f} remaining. This query may cost ~R{estimated:.2f}")

    return True
