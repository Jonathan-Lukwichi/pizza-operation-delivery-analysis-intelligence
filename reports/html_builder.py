"""
This module acts as a small "agent" to generate an HTML representation
of a report from raw data, which can then be converted to other formats like PDF.
"""
import pandas as pd
from typing import Dict, List

def generate_report_html(
    kpis: List[Dict],
    area_metrics: pd.DataFrame,
    bottlenecks: List[Dict],
    recommendations: List[str],
    date_range: str = ""
) -> str:
    """
    Generates a standalone HTML report from various data components.

    Args:
        kpis: A list of dictionaries, each with 'label' and 'value'.
        area_metrics: DataFrame with performance metrics by area.
        bottlenecks: List of bottleneck information.
        recommendations: A list of recommendation strings.
        date_range: The reporting period as a string.

    Returns:
        A string containing the complete HTML report.
    """
    # --- HTML & CSS Boilerplate ---
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Helvetica, sans-serif;
                font-size: 12px;
                color: #333;
            }}
            h1 {{
                color: #FF6B35; /* PizzaOps Orange */
                font-size: 24px;
                text-align: center;
            }}
            h2 {{
                font-size: 18px;
                color: #333;
                border-bottom: 2px solid #FF6B35;
                padding-bottom: 5px;
                margin-top: 20px;
            }}
            p {{
                line-height: 1.4;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin-top: 15px;
                font-size: 11px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            ul {{
                padding-left: 20px;
            }}
            li {{
                margin-bottom: 8px;
            }}
            .report-header {{
                text-align: center;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="report-header">
            <h1>PizzaOps Performance Report</h1>
            <p><b>Report Period:</b> {date_range}</p>
        </div>

        <h2>Executive Summary</h2>
    """

    # --- KPIs Section ---
    if kpis:
        html += "<h3>Key Performance Indicators</h3>"
        kpi_table = "<table><thead><tr>"
        for kpi in kpis:
            kpi_table += f"<th>{kpi.get('label', '')}</th>"
        kpi_table += "</tr></thead><tbody><tr>"
        for kpi in kpis:
            kpi_table += f"<td>{kpi.get('value', '')}</td>"
        kpi_table += "</tr></tbody></table>"
        html += kpi_table

    # --- Area Performance Table ---
    if not area_metrics.empty:
        html += "<h2>Delivery Performance by Area</h2>"
        html += area_metrics.to_html(index=False, border=0)

    # --- Recommendations ---
    if recommendations:
        html += "<h2>Actionable Recommendations</h2><ul>"
        for rec in recommendations:
            html += f"<li>{rec}</li>"
        html += "</ul>"
    
    # --- Bottlenecks ---
    if bottlenecks:
        html += "<h2>Operational Bottlenecks</h2><p>The following stages are causing delays:</p><ul>"
        for bn in bottlenecks:
            html += f"<li><b>{bn['stage'].replace('_', ' ').title()}:</b> Currently at {bn['actual_p95']:.1f} mins (Target: {bn['benchmark_p95']:.1f} mins)</li>"
        html += "</ul>"


    html += "</body></html>"
    return html
