"""
Plotly chart factory functions for PizzaOps Intelligence.
All functions return themed Plotly figures.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional, List

from ui.theme import COLORS, PLOTLY_TEMPLATE, apply_plotly_theme


def line_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    target_line: Optional[float] = None,
    color: Optional[str] = None,
    color_column: Optional[str] = None,
    height: int = 400
) -> go.Figure:
    """Create a line chart with optional target line."""
    if color_column:
        fig = px.line(df, x=x, y=y, color=color_column, title=title)
    else:
        fig = px.line(df, x=x, y=y, title=title)
        if color:
            fig.update_traces(line_color=color)
        else:
            fig.update_traces(line_color=COLORS["primary"])

    # Add target line
    if target_line is not None:
        fig.add_hline(
            y=target_line,
            line_dash="dash",
            line_color=COLORS["danger"],
            annotation_text=f"Target: {target_line}",
            annotation_position="right"
        )

    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height)
    return fig


def bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    color_column: Optional[str] = None,
    orientation: str = "v",
    show_values: bool = False,
    height: int = 400
) -> go.Figure:
    """Create a bar chart."""
    if color_column:
        fig = px.bar(df, x=x, y=y, color=color_column, title=title, orientation=orientation)
    else:
        fig = px.bar(df, x=x, y=y, title=title, orientation=orientation)
        bar_color = color or COLORS["primary"]
        fig.update_traces(marker_color=bar_color)

    if show_values:
        fig.update_traces(texttemplate='%{y:.1f}', textposition='outside')

    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height)
    return fig


def horizontal_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    height: int = 400
) -> go.Figure:
    """Create a horizontal bar chart."""
    fig = px.bar(df, x=x, y=y, title=title, orientation='h')
    fig.update_traces(marker_color=color or COLORS["primary"])
    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height, yaxis={'categoryorder': 'total ascending'})
    return fig


def box_plot(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    color_column: Optional[str] = None,
    height: int = 400
) -> go.Figure:
    """Create a box plot."""
    if color_column:
        fig = px.box(df, x=x, y=y, color=color_column, title=title)
    else:
        fig = px.box(df, x=x, y=y, title=title)

    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height)
    return fig


def heatmap(
    df: pd.DataFrame,
    x: str,
    y: str,
    z: str,
    title: str,
    colorscale: str = "RdYlGn_r",
    height: int = 400
) -> go.Figure:
    """Create a heatmap from aggregated data."""
    # Pivot the data
    pivot_df = df.pivot_table(values=z, index=y, columns=x, aggfunc='mean')

    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns.tolist(),
        y=pivot_df.index.tolist(),
        colorscale=colorscale,
        hoverongaps=False
    ))

    fig.update_layout(title=title)
    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height)
    return fig


def donut_chart(
    df: pd.DataFrame,
    names: str,
    values: str,
    title: str,
    hole: float = 0.45,
    height: int = 400
) -> go.Figure:
    """Create a donut/pie chart."""
    fig = px.pie(df, names=names, values=values, title=title, hole=hole)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height)
    return fig


def scatter_plot(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    color_column: Optional[str] = None,
    size: Optional[str] = None,
    trendline: Optional[str] = None,
    height: int = 400
) -> go.Figure:
    """Create a scatter plot with optional trendline."""
    fig = px.scatter(
        df, x=x, y=y, title=title,
        color=color_column,
        size=size,
        trendline=trendline
    )

    if color and not color_column:
        fig.update_traces(marker_color=color)

    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height)
    return fig


def stacked_bar_chart(
    df: pd.DataFrame,
    x: str,
    y_cols: List[str],
    title: str,
    colors: Optional[dict] = None,
    height: int = 400
) -> go.Figure:
    """Create a stacked bar chart."""
    fig = go.Figure()

    for i, col in enumerate(y_cols):
        color = colors.get(col, COLORS["chart_palette"][i % len(COLORS["chart_palette"])]) if colors else COLORS["chart_palette"][i % len(COLORS["chart_palette"])]
        fig.add_trace(go.Bar(
            name=col.replace("_", " ").title(),
            x=df[x],
            y=df[col],
            marker_color=color
        ))

    fig.update_layout(barmode='stack', title=title)
    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height)
    return fig


def area_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    fill: bool = True,
    height: int = 400
) -> go.Figure:
    """Create an area chart."""
    fig = px.area(df, x=x, y=y, title=title)
    fig.update_traces(line_color=color or COLORS["primary"])
    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height)
    return fig


def gauge_chart(
    value: float,
    title: str,
    min_val: float = 0,
    max_val: float = 100,
    thresholds: Optional[dict] = None,
    height: int = 250
) -> go.Figure:
    """Create a gauge chart."""
    # Default thresholds
    if thresholds is None:
        thresholds = {
            "good": (0, 40),
            "warning": (40, 70),
            "danger": (70, 100)
        }

    # Build steps for colored ranges
    steps = []
    for level, (low, high) in thresholds.items():
        color = COLORS.get(level, COLORS["text_muted"])
        steps.append({"range": [low, high], "color": color})

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"color": COLORS["text_primary"]}},
        gauge={
            "axis": {"range": [min_val, max_val], "tickcolor": COLORS["text_secondary"]},
            "bar": {"color": COLORS["primary"]},
            "bgcolor": COLORS["bg_card"],
            "steps": steps,
            "threshold": {
                "line": {"color": COLORS["text_primary"], "width": 4},
                "thickness": 0.75,
                "value": value
            }
        }
    ))

    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height)
    return fig


def time_series_with_forecast(
    actual_df: pd.DataFrame,
    forecast_df: pd.DataFrame,
    x: str,
    y_actual: str,
    y_forecast: str,
    y_lower: Optional[str] = None,
    y_upper: Optional[str] = None,
    title: str = "Forecast",
    height: int = 400
) -> go.Figure:
    """Create a time series chart with forecast and confidence interval."""
    fig = go.Figure()

    # Add actual values
    fig.add_trace(go.Scatter(
        x=actual_df[x],
        y=actual_df[y_actual],
        mode='lines',
        name='Actual',
        line=dict(color=COLORS["primary"], width=2)
    ))

    # Add forecast
    fig.add_trace(go.Scatter(
        x=forecast_df[x],
        y=forecast_df[y_forecast],
        mode='lines',
        name='Forecast',
        line=dict(color=COLORS["info"], width=2, dash='dash')
    ))

    # Add confidence interval
    if y_lower and y_upper:
        fig.add_trace(go.Scatter(
            x=forecast_df[x].tolist() + forecast_df[x].tolist()[::-1],
            y=forecast_df[y_upper].tolist() + forecast_df[y_lower].tolist()[::-1],
            fill='toself',
            fillcolor=f'rgba(59, 130, 246, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='95% CI',
            showlegend=True
        ))

    fig.update_layout(title=title)
    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height)
    return fig


def comparison_bar_chart(
    df: pd.DataFrame,
    category: str,
    values: List[str],
    title: str,
    value_labels: Optional[List[str]] = None,
    height: int = 400
) -> go.Figure:
    """Create a grouped bar chart for comparison."""
    fig = go.Figure()

    labels = value_labels or values
    for i, (val, label) in enumerate(zip(values, labels)):
        fig.add_trace(go.Bar(
            name=label,
            x=df[category],
            y=df[val],
            marker_color=COLORS["chart_palette"][i % len(COLORS["chart_palette"])]
        ))

    fig.update_layout(barmode='group', title=title)
    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# EDA CHART FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def histogram_chart(
    df: pd.DataFrame,
    column: str,
    title: str,
    show_mean: bool = True,
    show_median: bool = True,
    bins: int = 30,
    height: int = 300
) -> go.Figure:
    """Create histogram with optional mean/median lines."""
    fig = px.histogram(df, x=column, nbins=bins, title=title)
    fig.update_traces(marker_color=COLORS["primary"], opacity=0.7)

    if show_mean and column in df.columns:
        mean_val = df[column].mean()
        fig.add_vline(
            x=mean_val,
            line_dash="dash",
            line_color=COLORS["success"],
            annotation_text=f"Mean: {mean_val:.1f}",
            annotation_position="top right"
        )

    if show_median and column in df.columns:
        median_val = df[column].median()
        fig.add_vline(
            x=median_val,
            line_dash="dot",
            line_color=COLORS["warning"],
            annotation_text=f"Median: {median_val:.1f}",
            annotation_position="top left"
        )

    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height, bargap=0.05)
    return fig


def correlation_heatmap(
    corr_matrix: pd.DataFrame,
    title: str = "Correlation Matrix",
    height: int = 400
) -> go.Figure:
    """Create annotated correlation heatmap."""
    if corr_matrix.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Not enough numeric columns for correlation",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=14, color=COLORS["text_muted"])
        )
        fig = apply_plotly_theme(fig)
        fig.update_layout(height=height)
        return fig

    # Create heatmap with annotations
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns.tolist(),
        y=corr_matrix.index.tolist(),
        colorscale="RdBu_r",
        zmid=0,
        zmin=-1,
        zmax=1,
        text=corr_matrix.values.round(2),
        texttemplate="%{text}",
        textfont={"size": 10, "color": "white"},
        hoverongaps=False,
        colorbar=dict(
            title="Correlation",
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=["-1", "-0.5", "0", "0.5", "1"]
        )
    ))

    fig.update_layout(title=title)
    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height)
    return fig


def missing_values_chart(
    missing_data: dict,
    title: str = "Missing Values by Column",
    height: int = 300
) -> go.Figure:
    """Create horizontal bar chart for missing value percentages."""
    # Filter to only columns with missing values
    filtered_data = {k: v for k, v in missing_data.items() if v > 0}

    if not filtered_data:
        # Return figure with success message
        fig = go.Figure()
        fig.add_annotation(
            text="No missing values found!",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color=COLORS["success"])
        )
        fig = apply_plotly_theme(fig)
        fig.update_layout(height=height)
        return fig

    # Create dataframe and sort
    chart_df = pd.DataFrame({
        "column": list(filtered_data.keys()),
        "pct": list(filtered_data.values())
    }).sort_values("pct", ascending=True)

    fig = px.bar(
        chart_df,
        x="pct",
        y="column",
        orientation="h",
        title=title
    )
    fig.update_traces(marker_color=COLORS["warning"])
    fig = apply_plotly_theme(fig)
    fig.update_layout(
        height=height,
        xaxis_title="Missing %",
        yaxis_title=""
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# AI DASHBOARD CHART FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def impact_simulation_chart(
    before_values: dict,
    after_values: dict,
    title: str = "Before vs After Impact",
    height: int = 350
) -> go.Figure:
    """
    Create a before/after impact simulation bar chart.
    Shows current state vs projected state side-by-side.

    Args:
        before_values: Dict with metric names as keys, values before change
        after_values: Dict with metric names as keys, values after change
        title: Chart title
        height: Chart height in pixels

    Returns:
        Plotly figure
    """
    metrics = list(before_values.keys())
    before = list(before_values.values())
    after = list(after_values.values())

    # Format metric names
    metric_labels = [m.replace('_', ' ').title() for m in metrics]

    fig = go.Figure()

    # Before bars (muted color)
    fig.add_trace(go.Bar(
        name='Current',
        x=metric_labels,
        y=before,
        marker_color=COLORS["text_muted"],
        text=[f'{v:.1f}' for v in before],
        textposition='outside'
    ))

    # After bars (primary color)
    fig.add_trace(go.Bar(
        name='Projected',
        x=metric_labels,
        y=after,
        marker_color=COLORS["primary"],
        text=[f'{v:.1f}' for v in after],
        textposition='outside'
    ))

    fig.update_layout(
        title=title,
        barmode='group',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height)
    return fig


def priority_matrix_chart(
    data: pd.DataFrame,
    x_col: str = 'effort_score',
    y_col: str = 'impact_score',
    label_col: str = 'issue_name',
    quadrant_col: str = 'priority_quadrant',
    title: str = "Priority Matrix: Effort vs Impact",
    height: int = 400
) -> go.Figure:
    """
    Create a quadrant scatter plot for ROI/effort prioritization.
    Quadrants: Quick Wins (high impact, low effort), Strategic (high/high), etc.

    Args:
        data: DataFrame with effort/impact scores
        x_col: Column name for X axis (effort)
        y_col: Column name for Y axis (impact)
        label_col: Column for point labels
        quadrant_col: Column for quadrant assignment
        title: Chart title
        height: Chart height

    Returns:
        Plotly figure
    """
    if data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No issues to display",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=14, color=COLORS["text_muted"])
        )
        fig = apply_plotly_theme(fig)
        fig.update_layout(height=height)
        return fig

    # Color mapping for quadrants
    quadrant_colors = {
        'quick_win': COLORS["success"],
        'strategic': COLORS["primary"],
        'fill_in': COLORS["warning"],
        'avoid': COLORS["danger"]
    }

    fig = go.Figure()

    # Add quadrant background shapes
    fig.add_shape(type="rect", x0=0, y0=5, x1=5, y1=10,
                  fillcolor=f"{COLORS['success']}15", line_width=0)  # Quick wins
    fig.add_shape(type="rect", x0=5, y0=5, x1=10, y1=10,
                  fillcolor=f"{COLORS['primary']}15", line_width=0)  # Strategic
    fig.add_shape(type="rect", x0=0, y0=0, x1=5, y1=5,
                  fillcolor=f"{COLORS['warning']}15", line_width=0)  # Fill-in
    fig.add_shape(type="rect", x0=5, y0=0, x1=10, y1=5,
                  fillcolor=f"{COLORS['danger']}15", line_width=0)  # Avoid

    # Add quadrant lines
    fig.add_hline(y=5, line_dash="dash", line_color=COLORS["border"], opacity=0.5)
    fig.add_vline(x=5, line_dash="dash", line_color=COLORS["border"], opacity=0.5)

    # Add quadrant labels
    annotations = [
        dict(x=2.5, y=9.5, text="QUICK WINS", showarrow=False,
             font=dict(size=10, color=COLORS["success"])),
        dict(x=7.5, y=9.5, text="STRATEGIC", showarrow=False,
             font=dict(size=10, color=COLORS["primary"])),
        dict(x=2.5, y=0.5, text="FILL-IN", showarrow=False,
             font=dict(size=10, color=COLORS["warning"])),
        dict(x=7.5, y=0.5, text="AVOID", showarrow=False,
             font=dict(size=10, color=COLORS["danger"]))
    ]

    # Plot points
    for _, row in data.iterrows():
        quadrant = row.get(quadrant_col, 'fill_in')
        color = quadrant_colors.get(quadrant, COLORS["text_muted"])

        fig.add_trace(go.Scatter(
            x=[row[x_col]],
            y=[row[y_col]],
            mode='markers+text',
            marker=dict(size=15, color=color, line=dict(width=2, color='white')),
            text=[row[label_col][:15] + '...' if len(str(row[label_col])) > 15 else row[label_col]],
            textposition='top center',
            textfont=dict(size=9, color=COLORS["text_secondary"]),
            name=row[label_col],
            hovertemplate=f"<b>{row[label_col]}</b><br>Effort: {row[x_col]:.1f}<br>Impact: {row[y_col]:.1f}<extra></extra>"
        ))

    fig.update_layout(
        title=title,
        xaxis=dict(title="Effort (1-10)", range=[0, 10.5]),
        yaxis=dict(title="Impact (1-10)", range=[0, 10.5]),
        annotations=annotations,
        showlegend=False
    )
    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height)
    return fig


def issue_severity_donut(
    issues: List[dict],
    title: str = "Issue Severity Breakdown",
    height: int = 280
) -> go.Figure:
    """
    Create a donut chart showing issue distribution by severity.
    Colors: critical=danger, high=warning, medium=info, low=success

    Args:
        issues: List of issue dicts with 'severity' key
        title: Chart title
        height: Chart height

    Returns:
        Plotly figure
    """
    if not issues:
        fig = go.Figure()
        fig.add_annotation(
            text="No issues found!",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=14, color=COLORS["success"])
        )
        fig = apply_plotly_theme(fig)
        fig.update_layout(height=height)
        return fig

    # Count by severity
    severity_counts = {}
    for issue in issues:
        sev = issue.get('severity', 'medium')
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    # Order and colors
    severity_order = ['critical', 'high', 'medium', 'low']
    severity_colors = {
        'critical': COLORS["danger"],
        'high': COLORS["warning"],
        'medium': COLORS["info"],
        'low': COLORS["success"]
    }

    labels = []
    values = []
    colors = []

    for sev in severity_order:
        if sev in severity_counts:
            labels.append(sev.title())
            values.append(severity_counts[sev])
            colors.append(severity_colors.get(sev, COLORS["text_muted"]))

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker=dict(colors=colors),
        textinfo='label+value',
        textposition='inside',
        textfont=dict(size=11, color='white'),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>"
    )])

    # Add center text
    total = sum(values)
    fig.add_annotation(
        text=f"<b>{total}</b><br>Issues",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=14, color=COLORS["text_primary"])
    )

    fig.update_layout(title=title, showlegend=True,
                      legend=dict(orientation='h', yanchor='bottom', y=-0.2))
    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height)
    return fig


def column_health_bar_chart(
    column_stats: dict,
    title: str = "Column Health Overview",
    height: int = 300
) -> go.Figure:
    """
    Create a stacked horizontal bar chart showing column health.
    Each column shows: complete %, missing %, outlier %

    Args:
        column_stats: Dict mapping column names to stats with 'complete_pct', 'missing_pct', 'outlier_pct'
        title: Chart title
        height: Chart height

    Returns:
        Plotly figure
    """
    if not column_stats:
        fig = go.Figure()
        fig.add_annotation(
            text="No column data available",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=14, color=COLORS["text_muted"])
        )
        fig = apply_plotly_theme(fig)
        fig.update_layout(height=height)
        return fig

    columns = list(column_stats.keys())
    complete = [column_stats[c].get('complete_pct', 100) for c in columns]
    missing = [column_stats[c].get('missing_pct', 0) for c in columns]
    outliers = [column_stats[c].get('outlier_pct', 0) for c in columns]

    fig = go.Figure()

    # Complete (green)
    fig.add_trace(go.Bar(
        name='Complete',
        y=columns,
        x=complete,
        orientation='h',
        marker_color=COLORS["success"],
        text=[f'{v:.0f}%' for v in complete],
        textposition='inside',
        insidetextanchor='middle'
    ))

    # Missing (orange)
    fig.add_trace(go.Bar(
        name='Missing',
        y=columns,
        x=missing,
        orientation='h',
        marker_color=COLORS["warning"],
        text=[f'{v:.1f}%' if v > 2 else '' for v in missing],
        textposition='inside'
    ))

    # Outliers (red)
    fig.add_trace(go.Bar(
        name='Outliers',
        y=columns,
        x=outliers,
        orientation='h',
        marker_color=COLORS["danger"],
        text=[f'{v:.1f}%' if v > 2 else '' for v in outliers],
        textposition='inside'
    ))

    fig.update_layout(
        title=title,
        barmode='stack',
        xaxis=dict(title='Percentage', range=[0, 105]),
        yaxis=dict(title=''),
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height)
    return fig


def scenario_waterfall_chart(
    baseline: float,
    improvements: List[dict],
    title: str = "Cumulative Impact of Improvements",
    metric_name: str = "On-Time Rate",
    height: int = 350
) -> go.Figure:
    """
    Create a waterfall chart showing cumulative impact of multiple fixes.
    Each bar shows incremental improvement from applying each fix.

    Args:
        baseline: Starting value
        improvements: List of dicts with 'name' and 'impact' keys
        title: Chart title
        metric_name: Name of metric being improved
        height: Chart height

    Returns:
        Plotly figure
    """
    if not improvements:
        fig = go.Figure()
        fig.add_annotation(
            text="Select improvements to simulate",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=14, color=COLORS["text_muted"])
        )
        fig = apply_plotly_theme(fig)
        fig.update_layout(height=height)
        return fig

    # Build waterfall data
    names = ['Baseline'] + [imp.get('name', f'Step {i+1}')[:15] for i, imp in enumerate(improvements)] + ['Final']
    values = [baseline]

    # Calculate cumulative
    running = baseline
    measures = ['absolute']

    for imp in improvements:
        impact = imp.get('impact', 0)
        values.append(impact)
        measures.append('relative')
        running += impact

    values.append(running)
    measures.append('total')

    # Determine colors
    text_values = [f'{baseline:.1f}']
    for imp in improvements:
        impact = imp.get('impact', 0)
        sign = '+' if impact >= 0 else ''
        text_values.append(f'{sign}{impact:.1f}')
    text_values.append(f'{running:.1f}')

    fig = go.Figure(go.Waterfall(
        name=metric_name,
        orientation="v",
        measure=measures,
        x=names,
        y=values,
        text=text_values,
        textposition="outside",
        connector={"line": {"color": COLORS["border"]}},
        increasing={"marker": {"color": COLORS["success"]}},
        decreasing={"marker": {"color": COLORS["danger"]}},
        totals={"marker": {"color": COLORS["primary"]}}
    ))

    fig.update_layout(
        title=title,
        yaxis_title=metric_name,
        showlegend=False
    )
    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height)
    return fig


def bottleneck_severity_chart(
    bottlenecks: List[dict],
    title: str = "Bottleneck Analysis",
    height: int = 300
) -> go.Figure:
    """
    Create a horizontal bar chart showing bottleneck severity.

    Args:
        bottlenecks: List of bottleneck dicts with 'area'/'column', 'severity', 'current_value', 'benchmark_value'
        title: Chart title
        height: Chart height

    Returns:
        Plotly figure
    """
    if not bottlenecks:
        fig = go.Figure()
        fig.add_annotation(
            text="No bottlenecks detected!",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=14, color=COLORS["success"])
        )
        fig = apply_plotly_theme(fig)
        fig.update_layout(height=height)
        return fig

    # Severity colors
    severity_colors = {
        'critical': COLORS["danger"],
        'high': COLORS["warning"],
        'medium': COLORS["info"],
        'low': COLORS["success"]
    }

    # Extract data
    areas = [b.get('column', b.get('area', 'Unknown'))[:25] for b in bottlenecks]
    current_values = [b.get('current_value', 0) for b in bottlenecks]
    benchmark_values = [b.get('benchmark_value', 0) for b in bottlenecks]
    severities = [b.get('severity', 'medium') for b in bottlenecks]
    colors = [severity_colors.get(s, COLORS["text_muted"]) for s in severities]

    # Calculate variance from benchmark
    variances = [
        ((c - b) / b * 100) if b > 0 else 0
        for c, b in zip(current_values, benchmark_values)
    ]

    fig = go.Figure()

    # Current values bar
    fig.add_trace(go.Bar(
        name='Current Value',
        y=areas,
        x=current_values,
        orientation='h',
        marker_color=colors,
        text=[f'{v:.1f}' for v in current_values],
        textposition='inside',
        hovertemplate="<b>%{y}</b><br>Current: %{x:.1f}<extra></extra>"
    ))

    # Add benchmark markers
    for i, (area, benchmark, severity) in enumerate(zip(areas, benchmark_values, severities)):
        fig.add_shape(
            type="line",
            x0=benchmark, x1=benchmark,
            y0=i - 0.3, y1=i + 0.3,
            line=dict(color="white", width=3, dash="dash")
        )
        # Add benchmark annotation
        fig.add_annotation(
            x=benchmark, y=i,
            text=f"Target: {benchmark:.0f}",
            showarrow=False,
            xshift=30,
            font=dict(size=9, color=COLORS["text_muted"])
        )

    fig.update_layout(
        title=title,
        xaxis_title="Value",
        yaxis=dict(title='', categoryorder='total ascending'),
        showlegend=False
    )
    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height)
    return fig


def kpi_gauge_with_target(
    value: float,
    target: float,
    title: str,
    is_lower_better: bool = False,
    unit: str = "%",
    height: int = 200
) -> go.Figure:
    """
    Create a gauge chart with target indicator.

    Args:
        value: Current value
        target: Target value
        title: Gauge title
        is_lower_better: If True, lower values are better (e.g., complaint rate)
        unit: Unit suffix for display
        height: Chart height

    Returns:
        Plotly figure
    """
    # Determine min/max based on context
    if is_lower_better:
        max_val = max(target * 2, value * 1.5, 20)
        min_val = 0
        # Green zone is below target
        thresholds = {
            "good": (0, target),
            "warning": (target, target * 1.5),
            "danger": (target * 1.5, max_val)
        }
    else:
        max_val = 100 if unit == "%" else max(target * 1.5, value * 1.2)
        min_val = 0
        # Green zone is above target
        thresholds = {
            "danger": (0, target * 0.7),
            "warning": (target * 0.7, target),
            "good": (target, max_val)
        }

    # Build steps for colored ranges
    steps = []
    for level in ["danger", "warning", "good"]:
        if level in thresholds:
            low, high = thresholds[level]
            color = COLORS.get(level, COLORS["text_muted"])
            steps.append({"range": [low, high], "color": f"{color}40"})

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        number={"suffix": unit, "font": {"size": 24, "color": COLORS["text_primary"]}},
        delta={
            "reference": target,
            "relative": False,
            "valueformat": ".1f",
            "increasing": {"color": COLORS["success"] if not is_lower_better else COLORS["danger"]},
            "decreasing": {"color": COLORS["danger"] if not is_lower_better else COLORS["success"]}
        },
        title={"text": title, "font": {"color": COLORS["text_secondary"], "size": 12}},
        gauge={
            "axis": {"range": [min_val, max_val], "tickcolor": COLORS["text_muted"]},
            "bar": {"color": COLORS["primary"]},
            "bgcolor": COLORS["bg_card"],
            "steps": steps,
            "threshold": {
                "line": {"color": "white", "width": 3},
                "thickness": 0.8,
                "value": target
            }
        }
    ))

    fig = apply_plotly_theme(fig)
    fig.update_layout(height=height)
    return fig
