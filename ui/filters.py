"""
Global filter components for PizzaOps Intelligence.
Sidebar filters that persist via session state.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

from core.constants import DELIVERY_AREAS, ORDER_MODES


def render_global_filters(df: pd.DataFrame) -> dict:
    """
    Render global filters in the sidebar.

    Args:
        df: DataFrame to get filter options from

    Returns:
        dict with filter selections
    """
    with st.sidebar:
        st.markdown("### Filters")

        filters = {}

        # Date range filter
        if "order_date" in df.columns:
            min_date = df["order_date"].min()
            max_date = df["order_date"].max()

            if pd.notna(min_date) and pd.notna(max_date):
                date_range = st.date_input(
                    "Date Range",
                    value=(min_date.date(), max_date.date()),
                    min_value=min_date.date(),
                    max_value=max_date.date(),
                    key="filter_date_range"
                )

                if len(date_range) == 2:
                    filters["date_from"] = pd.Timestamp(date_range[0])
                    filters["date_to"] = pd.Timestamp(date_range[1])

        # Area filter
        if "delivery_area" in df.columns:
            available_areas = sorted(df["delivery_area"].dropna().unique().tolist())
            selected_areas = st.multiselect(
                "Delivery Areas",
                options=available_areas,
                default=available_areas,
                key="filter_areas"
            )
            filters["areas"] = selected_areas

        # Order mode filter
        if "order_mode" in df.columns:
            available_modes = sorted(df["order_mode"].dropna().unique().tolist())
            selected_modes = st.multiselect(
                "Order Modes",
                options=available_modes,
                default=available_modes,
                key="filter_modes"
            )
            filters["order_modes"] = selected_modes

        # Peak hours toggle
        st.markdown("---")
        filters["peak_only"] = st.checkbox(
            "Peak Hours Only",
            value=False,
            key="filter_peak_only",
            help="Show only orders during lunch (11-14) and dinner (17-21) hours"
        )

        # Complaints toggle
        filters["complaints_only"] = st.checkbox(
            "Complaints Only",
            value=False,
            key="filter_complaints_only",
            help="Show only orders with complaints"
        )

        # Reset filters button
        st.markdown("---")
        if st.button("Reset Filters", key="reset_filters"):
            # Clear filter-related session state
            for key in list(st.session_state.keys()):
                if key.startswith("filter_"):
                    del st.session_state[key]
            st.rerun()

    return filters


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Apply filters to a DataFrame.

    Args:
        df: DataFrame to filter
        filters: dict with filter selections

    Returns:
        Filtered DataFrame
    """
    df = df.copy()

    # Date range
    if "date_from" in filters and "order_date" in df.columns:
        df = df[df["order_date"] >= filters["date_from"]]

    if "date_to" in filters and "order_date" in df.columns:
        df = df[df["order_date"] <= filters["date_to"]]

    # Areas
    if "areas" in filters and filters["areas"] and "delivery_area" in df.columns:
        df = df[df["delivery_area"].isin(filters["areas"])]

    # Order modes
    if "order_modes" in filters and filters["order_modes"] and "order_mode" in df.columns:
        df = df[df["order_mode"].isin(filters["order_modes"])]

    # Peak hours only
    if filters.get("peak_only") and "is_peak_hour" in df.columns:
        df = df[df["is_peak_hour"] == True]

    # Complaints only
    if filters.get("complaints_only") and "complaint" in df.columns:
        df = df[df["complaint"] == True]

    return df


def render_page_filters(
    df: pd.DataFrame,
    show_date: bool = True,
    show_area: bool = True,
    show_staff: bool = False,
    staff_role: Optional[str] = None
) -> dict:
    """
    Render page-specific filters (not in sidebar).

    Args:
        df: DataFrame to get filter options from
        show_date: Whether to show date filter
        show_area: Whether to show area filter
        show_staff: Whether to show staff filter
        staff_role: Specific staff role column to filter

    Returns:
        dict with filter selections
    """
    filters = {}

    col1, col2, col3 = st.columns(3)

    # Date filter
    if show_date and "order_date" in df.columns:
        with col1:
            min_date = df["order_date"].min()
            max_date = df["order_date"].max()

            if pd.notna(min_date) and pd.notna(max_date):
                date_range = st.date_input(
                    "Date Range",
                    value=(min_date.date(), max_date.date()),
                    min_value=min_date.date(),
                    max_value=max_date.date()
                )

                if len(date_range) == 2:
                    filters["date_from"] = pd.Timestamp(date_range[0])
                    filters["date_to"] = pd.Timestamp(date_range[1])

    # Area filter
    if show_area and "delivery_area" in df.columns:
        with col2:
            available_areas = sorted(df["delivery_area"].dropna().unique().tolist())
            selected_areas = st.multiselect(
                "Areas",
                options=available_areas,
                default=available_areas
            )
            filters["areas"] = selected_areas

    # Staff filter
    if show_staff and staff_role and staff_role in df.columns:
        with col3:
            available_staff = sorted(df[staff_role].dropna().unique().tolist())
            selected_staff = st.multiselect(
                f"{staff_role.replace('_', ' ').title()}",
                options=available_staff,
                default=available_staff
            )
            filters["staff"] = selected_staff
            filters["staff_role"] = staff_role

    return filters


def render_quick_filters(df: pd.DataFrame) -> dict:
    """
    Render quick filter chips/buttons.

    Args:
        df: DataFrame to get filter options from

    Returns:
        dict with selected quick filters
    """
    filters = {}

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Today", use_container_width=True):
            filters["quick"] = "today"

    with col2:
        if st.button("This Week", use_container_width=True):
            filters["quick"] = "week"

    with col3:
        if st.button("This Month", use_container_width=True):
            filters["quick"] = "month"

    with col4:
        if st.button("All Time", use_container_width=True):
            filters["quick"] = "all"

    return filters


def get_filter_summary(filters: dict, df_original: pd.DataFrame, df_filtered: pd.DataFrame) -> str:
    """
    Generate a summary of active filters.

    Args:
        filters: Current filter dict
        df_original: Original unfiltered DataFrame
        df_filtered: Filtered DataFrame

    Returns:
        Summary string
    """
    original_count = len(df_original)
    filtered_count = len(df_filtered)

    if original_count == filtered_count:
        return "Showing all data"

    percentage = (filtered_count / original_count * 100) if original_count > 0 else 0
    return f"Showing {filtered_count:,} of {original_count:,} orders ({percentage:.1f}%)"
