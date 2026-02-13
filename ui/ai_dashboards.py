"""
AI Dashboard Components
=======================

Visual dashboard rendering functions for AI-powered analytics.
Includes quality dashboards, business analyst dashboards, and simulation visualizations.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Any

from ui.theme import COLORS
from ui.charts import (
    gauge_chart, kpi_gauge_with_target, donut_chart,
    issue_severity_donut, column_health_bar_chart, bottleneck_severity_chart,
    impact_simulation_chart, scenario_waterfall_chart, priority_matrix_chart,
    comparison_bar_chart, bar_chart
)
from ui.scenario_simulator import (
    simulate_quality_fix_impact, simulate_recommendation_impact,
    simulate_combined_recommendations, calculate_fix_priority_matrix,
    create_scenario_comparison_data
)


def render_quality_dashboard(
    quality_report: Any,
    df: pd.DataFrame
) -> None:
    """
    Render the complete AI Data Quality Analyst Dashboard.

    Layout:
    Row 1: Three gauges (Quality Score, Completeness %, Outlier-Free %)
    Row 2: Issue severity donut + Column health bar chart
    Row 3: Fix Impact Simulation section with what-if scenarios

    Args:
        quality_report: AgentResponse from DataQualityAgent
        df: Current dataframe
    """
    # Dashboard header
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {COLORS['primary']}15 0%, {COLORS['primary']}05 100%);
        border: 1px solid {COLORS['primary']}30;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    ">
        <div style="display: flex; align-items: center;">
            <span style="font-size: 2rem; margin-right: 1rem;">🔬</span>
            <div>
                <h3 style="color: {COLORS['text_primary']}; margin: 0;">AI Data Quality Analyst</h3>
                <p style="color: {COLORS['text_secondary']}; margin: 0; font-size: 0.9rem;">
                    Intelligent data quality assessment with actionable insights
                </p>
            </div>
        </div>
        <span style="
            background: {COLORS['primary']}20;
            color: {COLORS['primary']};
            padding: 0.3rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: bold;
        ">AI POWERED</span>
    </div>
    """, unsafe_allow_html=True)

    # Extract data from report
    score = quality_report.score or quality_report.data.get("quality_score", 0)
    stats = quality_report.data.get("stats", {})
    issues = quality_report.issues

    # Calculate metrics
    completeness = 100 - stats.get('missing_pct', 0)
    outlier_free = _calculate_outlier_free_pct(stats)

    # ══════════════════════════════════════════════════════════════════════════════
    # ROW 1: THREE GAUGES
    # ══════════════════════════════════════════════════════════════════════════════
    st.markdown("#### Quality Metrics")

    gauge_col1, gauge_col2, gauge_col3 = st.columns(3)

    with gauge_col1:
        fig = gauge_chart(
            value=score,
            title="Quality Score",
            min_val=0,
            max_val=100,
            thresholds={
                "danger": (0, 60),
                "warning": (60, 80),
                "good": (80, 100)
            },
            height=200
        )
        st.plotly_chart(fig, use_container_width=True)
        _render_confidence_badge(score, 'quality')

    with gauge_col2:
        fig = gauge_chart(
            value=completeness,
            title="Completeness",
            min_val=0,
            max_val=100,
            thresholds={
                "danger": (0, 80),
                "warning": (80, 95),
                "good": (95, 100)
            },
            height=200
        )
        st.plotly_chart(fig, use_container_width=True)
        _render_metric_subtitle(f"{stats.get('total_missing', 0):,} missing values")

    with gauge_col3:
        fig = gauge_chart(
            value=outlier_free,
            title="Outlier-Free",
            min_val=0,
            max_val=100,
            thresholds={
                "danger": (0, 85),
                "warning": (85, 95),
                "good": (95, 100)
            },
            height=200
        )
        st.plotly_chart(fig, use_container_width=True)
        _render_metric_subtitle("Based on IQR method")

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════════════
    # ROW 2: ISSUE BREAKDOWN + COLUMN HEALTH
    # ══════════════════════════════════════════════════════════════════════════════
    st.markdown("#### Issue Analysis")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig = issue_severity_donut(issues, title="Issue Severity Distribution", height=280)
        st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        column_stats = _build_column_health_stats(df, stats)
        fig = column_health_bar_chart(column_stats, title="Column Health Overview", height=280)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════════════
    # ROW 3: FIX IMPACT SIMULATION
    # ══════════════════════════════════════════════════════════════════════════════
    render_fix_impact_simulation(issues, score, stats, df)

    # Show AI content summary
    if quality_report.content:
        with st.expander("AI Analysis Summary", expanded=False):
            st.markdown(quality_report.content)

    # Cost display
    if quality_report.cost > 0:
        st.caption(f"AI Analysis Cost: ${quality_report.cost:.4f}")


def render_fix_impact_simulation(
    issues: List[Dict],
    current_score: float,
    stats: Dict,
    df: pd.DataFrame
) -> None:
    """
    Interactive section for simulating fix impacts.

    Features:
    - Checkbox selection of fixes to apply
    - Real-time projected score calculation
    - Before/after comparison chart
    - Priority matrix visualization
    """
    st.markdown(f"""
    <div style="
        background: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    ">
        <h4 style="color: {COLORS['text_primary']}; margin: 0 0 0.5rem 0;">
            📊 Fix Impact Simulation
        </h4>
        <p style="color: {COLORS['text_secondary']}; margin: 0; font-size: 0.9rem;">
            Select issues to fix and see the projected quality score improvement
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not issues:
        st.success("No issues to fix - your data quality is excellent!")
        return

    # Filter to auto-fixable issues
    fixable_issues = [i for i in issues if i.get('auto_fixable', True)]

    if not fixable_issues:
        st.info("No auto-fixable issues available. Manual review may be required.")
        return

    # Initialize session state for selected fixes
    if 'quality_selected_fixes' not in st.session_state:
        st.session_state.quality_selected_fixes = []

    # Display issues as checkboxes
    sim_col1, sim_col2 = st.columns([2, 1])

    with sim_col1:
        st.markdown("**Select fixes to simulate:**")

        selected_fixes = []
        for i, issue in enumerate(fixable_issues[:8]):  # Limit to 8
            severity = issue.get('severity', 'medium')
            severity_icon = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }.get(severity, '🔵')

            issue_type = issue.get('type', 'unknown')
            column = issue.get('column', 'unknown')
            count = issue.get('count', 0)

            label = f"{severity_icon} {issue_type.title()}: {column} ({count:,} items)"
            key = f"fix_sim_{i}_{issue_type}_{column}"

            if st.checkbox(label, key=key):
                selected_fixes.append(issue)

        st.session_state.quality_selected_fixes = selected_fixes

    with sim_col2:
        # Calculate projected impact
        simulation = simulate_quality_fix_impact(
            current_score, stats, issues, selected_fixes
        )

        projected = simulation['projected_score']
        improvement = simulation['score_improvement']
        confidence = simulation['confidence']

        # Display projection card
        improvement_color = COLORS['success'] if improvement > 0 else COLORS['text_muted']

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {COLORS['primary']}15 0%, {COLORS['primary']}05 100%);
            border: 1px solid {COLORS['primary']}30;
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
        ">
            <p style="color: {COLORS['text_muted']}; margin: 0; font-size: 0.8rem;">PROJECTED SCORE</p>
            <h2 style="
                background: linear-gradient(135deg, #FFFFFF 0%, {improvement_color} 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0.5rem 0;
                font-size: 2.5rem;
            ">{projected:.0f}</h2>
            <p style="color: {improvement_color}; margin: 0; font-size: 1.1rem; font-weight: bold;">
                {'+' if improvement > 0 else ''}{improvement:.1f} points
            </p>
            <p style="color: {COLORS['text_muted']}; margin: 0.5rem 0 0 0; font-size: 0.75rem;">
                Confidence: {confidence.upper()}
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Show before/after comparison chart if fixes selected
    if selected_fixes:
        st.markdown("#### Projected Impact")

        metrics_before = simulation['metrics_before']
        metrics_after = simulation['metrics_after']

        if metrics_before and metrics_after:
            fig = impact_simulation_chart(
                metrics_before, metrics_after,
                title="Quality Metrics: Current vs Projected",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)

        # Fix details
        with st.expander("Fix Impact Details", expanded=False):
            for detail in simulation.get('fix_details', []):
                st.markdown(f"- **{detail['type'].title()}** in `{detail['column']}`: +{detail['impact']:.1f} pts")

    # Priority Matrix
    with st.expander("Priority Matrix (Effort vs Impact)", expanded=False):
        priority_df = calculate_fix_priority_matrix(fixable_issues, stats)
        if not priority_df.empty:
            fig = priority_matrix_chart(priority_df, height=350)
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Quick Wins: High impact, low effort - fix these first!")


def render_business_analyst_dashboard(
    operations_report: Any,
    df: pd.DataFrame
) -> None:
    """
    Render the complete AI Business Analyst Dashboard.

    Layout:
    Row 1: Three KPI gauges vs targets (on-time, complaints, delivery time)
    Row 2: Bottleneck severity chart + Top bottlenecks table
    Row 3: Recommendation cards with impact simulation
    Row 4: What-if scenario explorer

    Args:
        operations_report: AgentResponse from BusinessAnalystAgent
        df: Current dataframe
    """
    # Dashboard header
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {COLORS['secondary']}15 0%, {COLORS['secondary']}05 100%);
        border: 1px solid {COLORS['secondary']}30;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    ">
        <div style="display: flex; align-items: center;">
            <span style="font-size: 2rem; margin-right: 1rem;">📊</span>
            <div>
                <h3 style="color: {COLORS['text_primary']}; margin: 0;">AI Business Analyst Consultant</h3>
                <p style="color: {COLORS['text_secondary']}; margin: 0; font-size: 0.9rem;">
                    Prescriptive analytics with impact simulations
                </p>
            </div>
        </div>
        <span style="
            background: {COLORS['secondary']}20;
            color: {COLORS['secondary']};
            padding: 0.3rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: bold;
        ">AI POWERED</span>
    </div>
    """, unsafe_allow_html=True)

    # Extract data
    data = operations_report.data
    bottlenecks = operations_report.issues
    recommendations = operations_report.recommendations
    metrics = data.get('metrics', {})

    # Build current metrics dict
    current_metrics = {
        'on_time_rate': metrics.get('on_time_rate', {}).get('value', 70),
        'complaint_rate': metrics.get('complaint_rate', {}).get('value', 8),
        'avg_delivery_time': metrics.get('avg_delivery_time', {}).get('value', 35)
    }

    # Get targets
    targets = {
        'on_time_rate': 85,
        'complaint_rate': 5,
        'avg_delivery_time': 30
    }

    # ══════════════════════════════════════════════════════════════════════════════
    # ROW 1: KPI GAUGES VS TARGETS
    # ══════════════════════════════════════════════════════════════════════════════
    st.markdown("#### Performance vs Targets")

    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

    with kpi_col1:
        fig = kpi_gauge_with_target(
            value=current_metrics['on_time_rate'],
            target=targets['on_time_rate'],
            title="On-Time Rate",
            is_lower_better=False,
            unit="%",
            height=200
        )
        st.plotly_chart(fig, use_container_width=True)
        gap = current_metrics['on_time_rate'] - targets['on_time_rate']
        _render_gap_indicator(gap, "% from target", higher_is_better=True)

    with kpi_col2:
        fig = kpi_gauge_with_target(
            value=current_metrics['complaint_rate'],
            target=targets['complaint_rate'],
            title="Complaint Rate",
            is_lower_better=True,
            unit="%",
            height=200
        )
        st.plotly_chart(fig, use_container_width=True)
        gap = current_metrics['complaint_rate'] - targets['complaint_rate']
        _render_gap_indicator(gap, "% from target", higher_is_better=False)

    with kpi_col3:
        fig = kpi_gauge_with_target(
            value=current_metrics['avg_delivery_time'],
            target=targets['avg_delivery_time'],
            title="Avg Delivery Time",
            is_lower_better=True,
            unit=" min",
            height=200
        )
        st.plotly_chart(fig, use_container_width=True)
        gap = current_metrics['avg_delivery_time'] - targets['avg_delivery_time']
        _render_gap_indicator(gap, " min from target", higher_is_better=False)

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════════════
    # ROW 2: BOTTLENECK ANALYSIS
    # ══════════════════════════════════════════════════════════════════════════════
    st.markdown("#### Bottleneck Analysis")

    if bottlenecks:
        fig = bottleneck_severity_chart(bottlenecks, title="Identified Bottlenecks", height=300)
        st.plotly_chart(fig, use_container_width=True)

        # Bottleneck details expander
        with st.expander("Bottleneck Details", expanded=False):
            for i, b in enumerate(bottlenecks[:5]):
                severity = b.get('severity', 'medium')
                severity_color = {
                    'critical': COLORS['danger'],
                    'high': COLORS['warning'],
                    'medium': COLORS['info'],
                    'low': COLORS['success']
                }.get(severity, COLORS['text_muted'])

                st.markdown(f"""
                <div style="
                    background: {severity_color}10;
                    border-left: 3px solid {severity_color};
                    padding: 0.75rem;
                    margin-bottom: 0.5rem;
                    border-radius: 0 8px 8px 0;
                ">
                    <strong style="color: {COLORS['text_primary']};">{b.get('column', 'Unknown')}</strong>
                    <span style="color: {severity_color}; font-size: 0.75rem; margin-left: 0.5rem;">
                        {severity.upper()}
                    </span>
                    <p style="color: {COLORS['text_secondary']}; margin: 0.25rem 0 0 0; font-size: 0.85rem;">
                        {b.get('description', '')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("No significant bottlenecks detected!")

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════════════
    # ROW 3: RECOMMENDATIONS WITH IMPACT SIMULATION
    # ══════════════════════════════════════════════════════════════════════════════
    st.markdown("#### Recommendations with Impact Simulation")

    if recommendations:
        for i, rec in enumerate(recommendations[:5]):
            render_recommendation_with_simulation(rec, current_metrics, df, i)
    else:
        st.info("No recommendations generated. Your operations are performing well!")

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════════════
    # ROW 4: SCENARIO EXPLORER
    # ══════════════════════════════════════════════════════════════════════════════
    render_scenario_explorer(recommendations, current_metrics, df)

    # AI Summary
    if operations_report.content:
        with st.expander("AI Analysis Summary", expanded=False):
            st.markdown(operations_report.content)

    # Cost display
    if operations_report.cost > 0:
        st.caption(f"AI Analysis Cost: ${operations_report.cost:.4f}")


def render_recommendation_with_simulation(
    recommendation: Dict,
    current_metrics: Dict,
    df: pd.DataFrame,
    index: int
) -> None:
    """
    Render a single recommendation card with impact simulation.

    Features:
    - Priority badge (HIGH/MEDIUM/QUICK WIN)
    - Action and evidence text
    - "Simulate Impact" button
    - Before/after comparison chart when clicked
    """
    priority = recommendation.get('priority', 'medium')
    priority_config = {
        'high': {'color': COLORS['danger'], 'label': 'HIGH PRIORITY', 'icon': '🔴'},
        'medium': {'color': COLORS['warning'], 'label': 'MEDIUM', 'icon': '🟡'},
        'quick_win': {'color': COLORS['success'], 'label': 'QUICK WIN', 'icon': '🟢'}
    }.get(priority, {'color': COLORS['primary'], 'label': priority.upper(), 'icon': '🔵'})

    p_color = priority_config['color']
    p_label = priority_config['label']
    p_icon = priority_config['icon']

    title = recommendation.get('title', 'Recommendation')
    action = recommendation.get('action', 'N/A')
    evidence = recommendation.get('evidence', 'Based on data analysis')
    expected_impact = recommendation.get('expected_impact', '')

    # Card container
    with st.container():
        st.markdown(f"""
        <div style="
            background: {COLORS['bg_card']};
            border: 1px solid {COLORS['border']};
            border-left: 4px solid {p_color};
            border-radius: 0 12px 12px 0;
            padding: 1.25rem;
            margin-bottom: 1rem;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 0.75rem;">
                <span style="
                    background: {p_color}20;
                    color: {p_color};
                    padding: 0.25rem 0.75rem;
                    border-radius: 4px;
                    font-size: 0.75rem;
                    font-weight: bold;
                ">{p_icon} {p_label}</span>
                <strong style="color: {COLORS['text_primary']}; margin-left: 0.75rem;">
                    {title}
                </strong>
            </div>
            <p style="color: {COLORS['text_secondary']}; margin: 0 0 0.5rem 0; font-size: 0.9rem;">
                <strong>Action:</strong> {action}
            </p>
            <p style="color: {COLORS['text_muted']}; margin: 0; font-size: 0.85rem; font-style: italic;">
                Evidence: {evidence}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Simulate Impact button
        sim_key = f"sim_rec_{index}_{title[:10]}"
        if st.button(f"📈 Simulate Impact", key=sim_key, use_container_width=True):
            st.session_state[f"show_sim_{index}"] = not st.session_state.get(f"show_sim_{index}", False)

        # Show simulation results if toggled
        if st.session_state.get(f"show_sim_{index}", False):
            impact = simulate_recommendation_impact(current_metrics, recommendation, df)

            sim_col1, sim_col2 = st.columns([1, 2])

            with sim_col1:
                st.markdown(f"""
                <div style="
                    background: {COLORS['primary']}10;
                    border-radius: 8px;
                    padding: 1rem;
                ">
                    <p style="color: {COLORS['text_muted']}; margin: 0 0 0.5rem 0; font-size: 0.75rem;">
                        PROJECTED IMPACT
                    </p>
                """, unsafe_allow_html=True)

                for metric, change in impact['kpi_changes'].items():
                    direction = '↑' if change > 0 else '↓' if change < 0 else '→'
                    color = COLORS['success'] if (
                        (metric == 'on_time_rate' and change > 0) or
                        (metric in ['complaint_rate', 'avg_delivery_time'] and change < 0)
                    ) else COLORS['danger'] if change != 0 else COLORS['text_muted']

                    metric_label = metric.replace('_', ' ').title()
                    st.markdown(f"""
                    <p style="color: {color}; margin: 0.25rem 0; font-size: 0.9rem;">
                        {direction} {metric_label}: {'+' if change > 0 else ''}{change:.1f}{'%' if 'rate' in metric else ' min'}
                    </p>
                    """, unsafe_allow_html=True)

                st.markdown(f"""
                    <p style="color: {COLORS['text_muted']}; margin: 0.75rem 0 0 0; font-size: 0.7rem;">
                        Confidence: {impact['confidence'].upper()}<br>
                        Timeline: {impact['timeline'].replace('_', ' ').title()}
                    </p>
                </div>
                """, unsafe_allow_html=True)

            with sim_col2:
                # Before/after chart
                fig = impact_simulation_chart(
                    impact['current_values'],
                    impact['projected_values'],
                    title="Current vs Projected",
                    height=250
                )
                st.plotly_chart(fig, use_container_width=True)


def render_scenario_explorer(
    recommendations: List[Dict],
    current_metrics: Dict,
    df: pd.DataFrame
) -> None:
    """
    Interactive what-if scenario explorer.

    Features:
    - Multi-select: choose recommendations to simulate together
    - Combined impact calculation
    - Waterfall chart showing cumulative improvements
    - Summary metrics: projected KPIs after all selected changes
    """
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {COLORS['primary']}10 0%, {COLORS['secondary']}10 100%);
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    ">
        <h4 style="color: {COLORS['text_primary']}; margin: 0 0 0.5rem 0;">
            🎯 Scenario Explorer
        </h4>
        <p style="color: {COLORS['text_secondary']}; margin: 0; font-size: 0.9rem;">
            Combine multiple recommendations to see their cumulative impact
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not recommendations:
        st.info("No recommendations available to explore.")
        return

    # Multi-select for recommendations
    rec_options = {f"{r.get('title', 'Recommendation')[:40]}": r for r in recommendations[:6]}

    selected_titles = st.multiselect(
        "Select recommendations to combine:",
        options=list(rec_options.keys()),
        default=[],
        key="scenario_explorer_select"
    )

    selected_recs = [rec_options[t] for t in selected_titles]

    if selected_recs:
        # Calculate combined impact
        combined = simulate_combined_recommendations(current_metrics, selected_recs, df)

        # Display results
        result_col1, result_col2 = st.columns([1, 2])

        with result_col1:
            st.markdown("#### Projected Final State")

            final = combined['projected_final']
            changes = combined['cumulative_changes']

            for metric in ['on_time_rate', 'complaint_rate', 'avg_delivery_time']:
                value = final.get(metric, 0)
                change = changes.get(metric, 0)

                # Determine if this is good or bad
                is_good = (
                    (metric == 'on_time_rate' and change > 0) or
                    (metric in ['complaint_rate', 'avg_delivery_time'] and change < 0)
                )
                color = COLORS['success'] if is_good else COLORS['danger'] if change != 0 else COLORS['text_muted']

                metric_label = metric.replace('_', ' ').title()
                unit = '%' if 'rate' in metric else ' min'

                st.markdown(f"""
                <div style="
                    background: {COLORS['bg_card']};
                    border-radius: 8px;
                    padding: 0.75rem;
                    margin-bottom: 0.5rem;
                    border-left: 3px solid {color};
                ">
                    <p style="color: {COLORS['text_muted']}; margin: 0; font-size: 0.75rem;">{metric_label}</p>
                    <p style="color: {COLORS['text_primary']}; margin: 0; font-size: 1.2rem; font-weight: bold;">
                        {value:.1f}{unit}
                        <span style="color: {color}; font-size: 0.85rem; margin-left: 0.5rem;">
                            ({'+' if change > 0 else ''}{change:.1f})
                        </span>
                    </p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <p style="color: {COLORS['text_muted']}; font-size: 0.75rem; margin-top: 0.5rem;">
                Confidence: {combined['confidence'].upper()}<br>
                {len(selected_recs)} recommendation(s) combined
            </p>
            """, unsafe_allow_html=True)

        with result_col2:
            # Waterfall chart for on-time rate
            waterfall_data = combined['waterfall_data']

            if len(waterfall_data) > 1:
                baseline = current_metrics.get('on_time_rate', 70)
                improvements = []

                for i in range(1, len(waterfall_data) - 1):
                    prev_val = waterfall_data[i-1].get('on_time_rate', baseline)
                    curr_val = waterfall_data[i].get('on_time_rate', prev_val)
                    improvements.append({
                        'name': waterfall_data[i]['stage'],
                        'impact': curr_val - prev_val
                    })

                fig = scenario_waterfall_chart(
                    baseline=baseline,
                    improvements=improvements,
                    title="Cumulative Impact on On-Time Rate",
                    metric_name="On-Time Rate (%)",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select one or more recommendations above to see combined impact.")


# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def _calculate_outlier_free_pct(stats: Dict) -> float:
    """Calculate percentage of data that is outlier-free."""
    outliers = stats.get('outliers', {})
    total_rows = stats.get('total_rows', 1)

    if not outliers or total_rows == 0:
        return 100.0

    total_outliers = sum(
        o.get('count', 0) for o in outliers.values()
        if isinstance(o, dict)
    )

    outlier_pct = (total_outliers / total_rows) * 100
    return max(0, 100 - outlier_pct)


def _build_column_health_stats(df: pd.DataFrame, stats: Dict) -> Dict:
    """Build column health statistics for visualization."""
    column_stats = {}
    total_rows = len(df)

    missing_by_col = stats.get('missing_by_column', {})
    outliers = stats.get('outliers', {})

    for col in df.columns[:10]:  # Limit to first 10 columns
        missing_count = missing_by_col.get(col, 0)
        missing_pct = (missing_count / total_rows * 100) if total_rows > 0 else 0

        # Get outlier info if numeric
        outlier_info = outliers.get(col, {})
        outlier_count = outlier_info.get('count', 0) if isinstance(outlier_info, dict) else 0
        outlier_pct = (outlier_count / total_rows * 100) if total_rows > 0 else 0

        complete_pct = 100 - missing_pct - outlier_pct

        column_stats[col] = {
            'complete_pct': max(0, complete_pct),
            'missing_pct': missing_pct,
            'outlier_pct': outlier_pct
        }

    return column_stats


def _render_confidence_badge(score: float, context: str = 'quality') -> None:
    """Render a confidence badge based on score."""
    if score >= 80:
        confidence = 'HIGH'
        color = COLORS['success']
    elif score >= 60:
        confidence = 'MEDIUM'
        color = COLORS['warning']
    else:
        confidence = 'LOW'
        color = COLORS['danger']

    st.markdown(f"""
    <div style="text-align: center;">
        <span style="
            background: {color}20;
            color: {color};
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: bold;
        ">Confidence: {confidence}</span>
    </div>
    """, unsafe_allow_html=True)


def _render_metric_subtitle(text: str) -> None:
    """Render a subtitle text below a metric."""
    st.markdown(f"""
    <p style="
        text-align: center;
        color: {COLORS['text_muted']};
        font-size: 0.75rem;
        margin: 0;
    ">{text}</p>
    """, unsafe_allow_html=True)


def _render_gap_indicator(gap: float, unit: str, higher_is_better: bool = True) -> None:
    """Render a gap indicator showing distance from target."""
    is_good = (gap >= 0 and higher_is_better) or (gap <= 0 and not higher_is_better)
    color = COLORS['success'] if is_good else COLORS['danger']
    sign = '+' if gap > 0 else ''

    st.markdown(f"""
    <div style="text-align: center;">
        <span style="
            color: {color};
            font-size: 0.85rem;
            font-weight: bold;
        ">{sign}{gap:.1f}{unit}</span>
    </div>
    """, unsafe_allow_html=True)
