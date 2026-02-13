"""
Scenario Simulator Module
=========================

Simulation logic for what-if scenarios in AI dashboards.
Computes projected impacts of applying fixes and recommendations.
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


# Impact templates by recommendation type
IMPACT_TEMPLATES = {
    'oven_optimization': {
        'on_time_rate': +8.0,
        'complaint_rate': -2.0,
        'avg_delivery_time': -3.0,
        'confidence': 'high',
        'timeline': 'this_week'
    },
    'route_optimization': {
        'on_time_rate': +5.0,
        'complaint_rate': -1.0,
        'avg_delivery_time': -4.0,
        'confidence': 'medium',
        'timeline': 'this_week'
    },
    'staff_scheduling': {
        'on_time_rate': +6.0,
        'complaint_rate': -1.5,
        'avg_delivery_time': -2.0,
        'confidence': 'high',
        'timeline': 'today'
    },
    'area_focus': {
        'on_time_rate': +4.0,
        'complaint_rate': -1.0,
        'avg_delivery_time': -2.0,
        'confidence': 'medium',
        'timeline': 'this_week'
    },
    'process_improvement': {
        'on_time_rate': +5.0,
        'complaint_rate': -1.5,
        'avg_delivery_time': -2.5,
        'confidence': 'medium',
        'timeline': 'this_month'
    },
    'quality_control': {
        'on_time_rate': +2.0,
        'complaint_rate': -3.0,
        'avg_delivery_time': 0,
        'confidence': 'high',
        'timeline': 'this_week'
    },
    'default': {
        'on_time_rate': +3.0,
        'complaint_rate': -1.0,
        'avg_delivery_time': -1.5,
        'confidence': 'low',
        'timeline': 'this_month'
    }
}


def simulate_quality_fix_impact(
    current_score: float,
    stats: Dict,
    issues: List[Dict],
    selected_fixes: List[Dict]
) -> Dict:
    """
    Calculate projected quality score after applying selected fixes.

    Args:
        current_score: Current data quality score (0-100)
        stats: Current data statistics (missing_by_column, outliers, duplicates)
        issues: List of identified issues
        selected_fixes: List of fixes user wants to apply

    Returns:
        Dict with projected_score, score_improvement, metrics_before/after, confidence
    """
    if not selected_fixes:
        return {
            'projected_score': current_score,
            'score_improvement': 0,
            'metrics_before': {},
            'metrics_after': {},
            'confidence': 'high',
            'fix_details': []
        }

    projected_score = current_score
    fix_details = []
    total_rows = stats.get('total_rows', 1)

    # Track metrics before and after
    metrics_before = {
        'completeness': 100 - stats.get('missing_pct', 0),
        'uniqueness': 100 - stats.get('duplicate_pct', 0),
        'outlier_free': 100 - _calculate_outlier_pct(stats)
    }

    metrics_after = metrics_before.copy()

    for fix in selected_fixes:
        fix_type = fix.get('type', 'unknown')
        fix_count = fix.get('count', 0)
        fix_column = fix.get('column', 'unknown')
        impact = 0

        if fix_type == 'duplicate':
            # Removing duplicates: impact based on duplicate percentage
            dup_pct = stats.get('duplicate_pct', 0)
            impact = min(dup_pct * 4, 20)  # Max +20 pts
            metrics_after['uniqueness'] = 100

        elif fix_type == 'missing':
            # Filling missing values: impact based on column missing percentage
            col_missing_pct = (fix_count / total_rows) * 100 if total_rows > 0 else 0
            impact = min(col_missing_pct * 2, 15)  # Max +15 pts per column
            # Improve completeness proportionally
            current_missing_pct = stats.get('missing_pct', 0)
            reduction = col_missing_pct * 0.8  # Assume 80% filled
            metrics_after['completeness'] = min(100, metrics_after['completeness'] + reduction)

        elif fix_type == 'outlier':
            # Capping outliers: +3 points per column fixed
            impact = 3
            # Improve outlier-free metric
            metrics_after['outlier_free'] = min(100, metrics_after['outlier_free'] + 2)

        elif fix_type == 'type_error':
            # Type conversion: moderate impact
            impact = 2

        elif fix_type == 'invalid':
            # Invalid value handling
            invalid_pct = (fix_count / total_rows) * 100 if total_rows > 0 else 0
            impact = min(invalid_pct * 1.5, 10)

        projected_score += impact
        fix_details.append({
            'type': fix_type,
            'column': fix_column,
            'impact': round(impact, 1),
            'description': fix.get('description', f"Fix {fix_type} in {fix_column}")
        })

    # Cap at 100
    projected_score = min(100, projected_score)

    # Determine confidence based on number of fixes
    if len(selected_fixes) <= 2:
        confidence = 'high'
    elif len(selected_fixes) <= 4:
        confidence = 'medium'
    else:
        confidence = 'low'

    return {
        'projected_score': round(projected_score, 1),
        'score_improvement': round(projected_score - current_score, 1),
        'metrics_before': {k: round(v, 1) for k, v in metrics_before.items()},
        'metrics_after': {k: round(v, 1) for k, v in metrics_after.items()},
        'confidence': confidence,
        'fix_details': fix_details
    }


def _calculate_outlier_pct(stats: Dict) -> float:
    """Calculate overall outlier percentage from stats."""
    outliers = stats.get('outliers', {})
    total_rows = stats.get('total_rows', 1)

    if not outliers:
        return 0

    total_outliers = sum(
        o.get('count', 0) for o in outliers.values()
        if isinstance(o, dict)
    )

    return (total_outliers / total_rows) * 100 if total_rows > 0 else 0


def classify_recommendation(recommendation: Dict) -> str:
    """
    Classify a recommendation into a template category.
    Uses keyword matching on title and action.
    """
    title = recommendation.get('title', '').lower()
    action = recommendation.get('action', '').lower()
    text = f"{title} {action}"

    # Keyword matching
    if any(w in text for w in ['oven', 'cook', 'bake', 'heat']):
        return 'oven_optimization'
    elif any(w in text for w in ['route', 'area', 'delivery', 'driver', 'traffic']):
        return 'route_optimization'
    elif any(w in text for w in ['staff', 'schedule', 'shift', 'hire', 'team']):
        return 'staff_scheduling'
    elif any(w in text for w in ['focus', 'priority', 'bottleneck', 'target']):
        return 'area_focus'
    elif any(w in text for w in ['process', 'workflow', 'efficiency', 'optimize']):
        return 'process_improvement'
    elif any(w in text for w in ['quality', 'complaint', 'customer', 'satisfaction']):
        return 'quality_control'
    else:
        return 'default'


def simulate_recommendation_impact(
    current_metrics: Dict,
    recommendation: Dict,
    df: Optional[pd.DataFrame] = None
) -> Dict:
    """
    Calculate KPI changes if a recommendation is applied.

    Args:
        current_metrics: Dict with on_time_rate, complaint_rate, avg_delivery_time
        recommendation: Recommendation dict with priority, action, expected_impact
        df: Optional DataFrame for trend-based projections

    Returns:
        Dict with kpi_changes, projected_values, confidence, timeline
    """
    # Classify the recommendation
    rec_type = classify_recommendation(recommendation)
    template = IMPACT_TEMPLATES.get(rec_type, IMPACT_TEMPLATES['default'])

    # Adjust impact based on priority
    priority = recommendation.get('priority', 'medium')
    priority_multiplier = {
        'high': 1.2,
        'medium': 1.0,
        'quick_win': 0.8
    }.get(priority, 1.0)

    # Calculate projected values
    projected = {}
    changes = {}

    for metric in ['on_time_rate', 'complaint_rate', 'avg_delivery_time']:
        current = current_metrics.get(metric, 0)
        base_change = template.get(metric, 0) * priority_multiplier

        # Apply change
        if metric == 'complaint_rate':
            # Complaint rate can't go below 0
            projected[metric] = max(0, current + base_change)
        elif metric == 'on_time_rate':
            # On-time rate can't exceed 100
            projected[metric] = min(100, current + base_change)
        else:
            # Delivery time can't go below 15 minutes
            projected[metric] = max(15, current + base_change)

        changes[metric] = round(base_change, 1)
        projected[metric] = round(projected[metric], 1)

    return {
        'recommendation_type': rec_type,
        'kpi_changes': changes,
        'current_values': {k: round(v, 1) for k, v in current_metrics.items()},
        'projected_values': projected,
        'confidence': template.get('confidence', 'medium'),
        'timeline': template.get('timeline', recommendation.get('timeline', 'this_week'))
    }


def simulate_combined_recommendations(
    current_metrics: Dict,
    recommendations: List[Dict],
    df: Optional[pd.DataFrame] = None
) -> Dict:
    """
    Calculate combined impact of multiple recommendations.
    Uses diminishing returns for stacking multiple fixes.

    Args:
        current_metrics: Current KPI values
        recommendations: List of selected recommendations
        df: Optional DataFrame for analysis

    Returns:
        Dict with cumulative_changes, waterfall_data, projected_final
    """
    if not recommendations:
        return {
            'cumulative_changes': {},
            'waterfall_data': [],
            'projected_final': current_metrics.copy(),
            'confidence': 'high'
        }

    # Track cumulative values
    running = current_metrics.copy()
    waterfall_data = [{'stage': 'Baseline', **running}]

    # Apply each recommendation with diminishing returns
    for i, rec in enumerate(recommendations):
        impact = simulate_recommendation_impact(running, rec, df)

        # Diminishing returns factor (first has 100%, second 80%, etc.)
        diminish_factor = 0.8 ** i

        for metric in ['on_time_rate', 'complaint_rate', 'avg_delivery_time']:
            change = impact['kpi_changes'].get(metric, 0) * diminish_factor

            if metric == 'complaint_rate':
                running[metric] = max(0, running[metric] + change)
            elif metric == 'on_time_rate':
                running[metric] = min(100, running[metric] + change)
            else:
                running[metric] = max(15, running[metric] + change)

            running[metric] = round(running[metric], 1)

        waterfall_data.append({
            'stage': rec.get('title', f'Step {i+1}')[:20],
            **running
        })

    # Calculate total changes
    cumulative_changes = {
        metric: round(running[metric] - current_metrics.get(metric, 0), 1)
        for metric in ['on_time_rate', 'complaint_rate', 'avg_delivery_time']
    }

    # Confidence decreases with more recommendations
    if len(recommendations) <= 2:
        confidence = 'high'
    elif len(recommendations) <= 4:
        confidence = 'medium'
    else:
        confidence = 'low'

    return {
        'cumulative_changes': cumulative_changes,
        'waterfall_data': waterfall_data,
        'projected_final': running,
        'confidence': confidence,
        'recommendation_count': len(recommendations)
    }


def create_scenario_comparison_data(
    scenarios: List[Dict],
    baseline: Dict,
    metrics: List[str] = None
) -> pd.DataFrame:
    """
    Generate DataFrame for comparison bar charts.

    Args:
        scenarios: List of scenario dicts with name, metrics
        baseline: Dict with current/baseline metrics
        metrics: List of metric names to include

    Returns:
        DataFrame suitable for comparison_bar_chart()
    """
    if metrics is None:
        metrics = ['on_time_rate', 'complaint_rate', 'avg_delivery_time']

    # Build data structure
    data = []

    for metric in metrics:
        row = {
            'Metric': metric.replace('_', ' ').title(),
            'Current': baseline.get(metric, 0)
        }

        for i, scenario in enumerate(scenarios):
            col_name = scenario.get('name', f'Scenario {i+1}')
            row[col_name] = scenario.get('metrics', {}).get(metric, 0)

        data.append(row)

    return pd.DataFrame(data)


def calculate_bottleneck_cascading_impact(
    bottleneck: Dict,
    df: pd.DataFrame,
    target_reduction_pct: float = 20.0
) -> Dict:
    """
    Calculate cascading impact of reducing a bottleneck by X%.

    Args:
        bottleneck: Bottleneck dict with area, current_value, benchmark
        df: Full dataset for recalculation
        target_reduction_pct: Target reduction percentage

    Returns:
        Dict with original_metrics, projected_metrics, improvements
    """
    # Get bottleneck details
    area = bottleneck.get('column', bottleneck.get('area', 'unknown'))
    current_value = bottleneck.get('current_value', 0)
    benchmark = bottleneck.get('benchmark_value', current_value)
    severity = bottleneck.get('severity', 'medium')

    # Calculate current metrics
    original_metrics = {}
    if 'delivery_target_met' in df.columns:
        original_metrics['on_time_rate'] = df['delivery_target_met'].mean() * 100
    if 'complaint' in df.columns:
        original_metrics['complaint_rate'] = df['complaint'].mean() * 100
    if 'total_process_time' in df.columns:
        original_metrics['avg_delivery_time'] = df['total_process_time'].mean()

    # Estimate impact based on severity
    severity_impact = {
        'critical': 1.5,
        'high': 1.2,
        'medium': 1.0,
        'low': 0.7
    }.get(severity, 1.0)

    # Project improvements
    base_improvement = target_reduction_pct * 0.5 * severity_impact

    projected_metrics = {
        'on_time_rate': min(100, original_metrics.get('on_time_rate', 70) + base_improvement * 0.8),
        'complaint_rate': max(0, original_metrics.get('complaint_rate', 8) - base_improvement * 0.3),
        'avg_delivery_time': max(15, original_metrics.get('avg_delivery_time', 35) - base_improvement * 0.5)
    }

    # Round values
    original_metrics = {k: round(v, 1) for k, v in original_metrics.items()}
    projected_metrics = {k: round(v, 1) for k, v in projected_metrics.items()}

    # Calculate improvements
    improvements = {
        metric: round(projected_metrics[metric] - original_metrics.get(metric, 0), 1)
        for metric in projected_metrics
    }

    return {
        'bottleneck_area': area,
        'reduction_target': target_reduction_pct,
        'original_metrics': original_metrics,
        'projected_metrics': projected_metrics,
        'kpi_improvements': improvements,
        'confidence': 'medium' if severity in ['critical', 'high'] else 'low'
    }


def calculate_fix_priority_matrix(
    issues: List[Dict],
    stats: Dict
) -> pd.DataFrame:
    """
    Calculate ROI/effort matrix for issue prioritization.

    Args:
        issues: List of issues with severity, count
        stats: Stats dict for context

    Returns:
        DataFrame with impact_score, effort_score, priority_quadrant
    """
    if not issues:
        return pd.DataFrame()

    total_rows = stats.get('total_rows', 1)
    data = []

    for issue in issues:
        issue_type = issue.get('type', 'unknown')
        severity = issue.get('severity', 'medium')
        count = issue.get('count', 0)
        auto_fixable = issue.get('auto_fixable', True)

        # Calculate impact score (1-10)
        severity_score = {'critical': 10, 'high': 8, 'medium': 5, 'low': 3}.get(severity, 5)
        volume_factor = min(count / total_rows * 10, 5) if total_rows > 0 else 0
        impact_score = min(10, severity_score + volume_factor)

        # Calculate effort score (1-10, lower is easier)
        effort_base = {'duplicate': 2, 'missing': 4, 'outlier': 3, 'type_error': 5, 'invalid': 6}.get(issue_type, 5)
        effort_score = effort_base if auto_fixable else effort_base + 3
        effort_score = min(10, effort_score)

        # Determine quadrant
        if impact_score >= 6 and effort_score <= 4:
            quadrant = 'quick_win'
        elif impact_score >= 6 and effort_score > 4:
            quadrant = 'strategic'
        elif impact_score < 6 and effort_score <= 4:
            quadrant = 'fill_in'
        else:
            quadrant = 'avoid'

        data.append({
            'issue_name': f"{issue_type}: {issue.get('column', 'unknown')}"[:30],
            'issue_type': issue_type,
            'severity': severity,
            'impact_score': round(impact_score, 1),
            'effort_score': round(effort_score, 1),
            'priority_quadrant': quadrant,
            'x': round(effort_score, 1),
            'y': round(impact_score, 1)
        })

    return pd.DataFrame(data)
