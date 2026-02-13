"""
PDF report generation for PizzaOps Intelligence.
Creates professional PDF reports using FPDF2.
"""

import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
from io import BytesIO
import tempfile
import os

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


class PizzaOpsPDF:
    """Custom PDF class for PizzaOps reports."""

    def __init__(self):
        """Initialize the PDF."""
        if not FPDF_AVAILABLE:
            raise ImportError("fpdf2 not installed. Run: pip install fpdf2")

        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)

        # Colors (RGB)
        self.primary = (255, 107, 53)  # Orange
        self.success = (16, 185, 129)
        self.warning = (245, 158, 11)
        self.danger = (239, 68, 68)
        self.dark = (14, 17, 23)
        self.gray = (148, 163, 184)

    def wrap_long_words(self, text: str, max_length: int = 50) -> str:
        """
        Breaks excessively long words in a string by inserting hyphens.
        Useful for preventing fpdf2 from failing on long, unbroken strings (like URLs)
        that exceed the cell width.
        """
        words = []
        for word in text.split(' '):
            if len(word) > max_length and not ' ' in word: # Check if it's genuinely a long word without spaces
                # Insert hyphens
                wrapped_word = '-'.join([word[i:i+max_length] for i in range(0, len(word), max_length)])
                words.append(wrapped_word)
            else:
                words.append(word)
        return ' '.join(words)

    def add_cover_page(
        self,
        title: str = "PizzaOps Performance Report",
        subtitle: str = "",
        date_range: str = ""
    ):
        """Add a cover page to the report."""
        self.pdf.add_page()

        # Title
        self.pdf.set_font('Helvetica', 'B', 32)
        self.pdf.set_text_color(*self.primary)
        self.pdf.cell(0, 40, '', ln=True)  # Spacing
        self.pdf.cell(0, 20, title, ln=True, align='C')

        # Subtitle
        if subtitle:
            self.pdf.set_font('Helvetica', '', 16)
            self.pdf.set_text_color(*self.gray)
            self.pdf.cell(0, 10, subtitle, ln=True, align='C')

        # Date range
        if date_range:
            self.pdf.set_font('Helvetica', '', 12)
            self.pdf.cell(0, 10, f"Report Period: {date_range}", ln=True, align='C')

        # Generated date
        self.pdf.cell(0, 30, '', ln=True)  # Spacing
        self.pdf.set_font('Helvetica', '', 10)
        self.pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%d %B %Y at %H:%M')}", ln=True, align='C')

        # Footer branding
        self.pdf.cell(0, 40, '', ln=True)  # Spacing
        self.pdf.set_font('Helvetica', 'B', 14)
        self.pdf.set_text_color(*self.primary)
        self.pdf.cell(0, 10, "PizzaOps Intelligence", ln=True, align='C')
        self.pdf.set_font('Helvetica', '', 10)
        self.pdf.set_text_color(*self.gray)
        self.pdf.cell(0, 6, "by JLWanalytics - Africa's Premier Data Refinery", ln=True, align='C')

    def add_section_header(self, title: str):
        """Add a section header."""
        self.pdf.set_font('Helvetica', 'B', 18)
        self.pdf.set_text_color(*self.dark)
        self.pdf.cell(0, 15, title, ln=True)
        self.pdf.ln(5)

    def add_subsection_header(self, title: str):
        """Add a subsection header."""
        self.pdf.set_font('Helvetica', 'B', 14)
        self.pdf.set_text_color(*self.primary)
        self.pdf.cell(0, 10, title, ln=True)
        self.pdf.ln(3)

    def add_paragraph(self, text: str):
        """Add a paragraph of text."""
        self.pdf.set_font('Helvetica', '', 11)
        self.pdf.set_text_color(*self.dark)
        self.pdf.multi_cell(0, 6, text)
        self.pdf.ln(3)

    def add_kpi_row(self, kpis: List[Dict]):
        """
        Add a row of KPI boxes.

        Args:
            kpis: List of dicts with 'label', 'value', 'status' keys
        """
        box_width = 45
        box_height = 25
        start_x = self.pdf.l_margin  # Use left margin instead of hardcoded value
        start_y = self.pdf.get_y()   # Store starting y position ONCE

        for i, kpi in enumerate(kpis[:4]):  # Max 4 KPIs per row
            x = start_x + (i * (box_width + 5))

            # Determine color based on status
            status = kpi.get('status', 'neutral')
            if status == 'good':
                color = self.success
            elif status == 'warning':
                color = self.warning
            elif status == 'danger':
                color = self.danger
            else:
                color = self.gray

            # Draw box at consistent y position
            self.pdf.set_fill_color(240, 240, 240)
            self.pdf.set_draw_color(*color)
            self.pdf.rect(x, start_y, box_width, box_height, 'DF')

            # Label - use stored start_y
            self.pdf.set_xy(x + 2, start_y + 3)
            self.pdf.set_font('Helvetica', '', 8)
            self.pdf.set_text_color(*self.gray)
            self.pdf.cell(box_width - 4, 5, kpi.get('label', ''), ln=False)

            # Value - use stored start_y
            self.pdf.set_xy(x + 2, start_y + 12)
            self.pdf.set_font('Helvetica', 'B', 14)
            self.pdf.set_text_color(*color)
            self.pdf.cell(box_width - 4, 10, str(kpi.get('value', '')), ln=False)

        # Reset position: x to left margin, y below the boxes
        self.pdf.set_xy(self.pdf.l_margin, start_y + box_height + 5)

    def add_table(self, data: pd.DataFrame, title: str = ""):
        """
        Add a data table with defensive column handling, robust sizing, and text wrapping.
        Truncates tables that are too wide and adds a warning to the PDF.
        """
        if title:
            self.add_subsection_header(title)

        effective_page_width = self.pdf.w - self.pdf.l_margin - self.pdf.r_margin
        original_num_columns = len(data.columns)

        if original_num_columns == 0:
            return

        # --- Defensive Column Handling ---
        MIN_COL_WIDTH = 15  # Minimum width in mm for a column to be readable
        max_cols_that_can_fit = int(effective_page_width / MIN_COL_WIDTH)
        
        df_display = data
        # If we have more columns than we can reasonably fit, truncate them
        if original_num_columns > max_cols_that_can_fit:
            display_cols_count = max_cols_that_can_fit
            df_display = data.iloc[:, :display_cols_count]
            
            # Add a warning message directly into the PDF
            self.pdf.set_font('Helvetica', 'I', 9)
            self.pdf.set_text_color(220, 53, 69)  # A noticeable red color
            warning_text = (
                f"Note: This table has been truncated to display the first {display_cols_count} of "
                f"{original_num_columns} total columns to fit the page width."
            )
            self.pdf.multi_cell(0, 5, warning_text, align='L')
            self.pdf.set_text_color(*self.dark)  # Reset to default text color
            self.pdf.ln(2)
        
        num_columns = len(df_display.columns)
        col_width = effective_page_width / num_columns
        row_height = 8  # Base height for a single line

        # --- Header ---
        self.pdf.set_font('Helvetica', 'B', 9)
        self.pdf.set_fill_color(240, 240, 240)
        self.pdf.set_text_color(*self.dark)

        y_before_header = self.pdf.get_y()
        x_start = self.pdf.get_x()
        header_max_y = y_before_header

        for i, col in enumerate(df_display.columns):
            self.pdf.set_xy(x_start + i * col_width, y_before_header)
            self.pdf.multi_cell(col_width, row_height, str(col), border=1, fill=True, align='C')
            header_max_y = max(header_max_y, self.pdf.get_y())

        self.pdf.set_y(header_max_y)

        # --- Data Rows ---
        self.pdf.set_font('Helvetica', '', 9)
        self.pdf.set_fill_color(255, 255, 255)
        self.pdf.set_text_color(*self.dark)

        for _, row in df_display.head(20).iterrows():  # Limit to 20 rows
            y_before_row = self.pdf.get_y()
            row_max_y = y_before_row

            for i, col in enumerate(df_display.columns):
                value = row[col]
                if isinstance(value, float):
                    value = f"{value:.2f}"

                self.pdf.set_xy(x_start + i * col_width, y_before_row)
                self.pdf.multi_cell(col_width, row_height, str(value), border=1, fill=True, align='L')
                row_max_y = max(row_max_y, self.pdf.get_y())
            
            self.pdf.set_y(row_max_y)

        self.pdf.ln(5)

    def add_bullet_list(self, items: List[str], title: str = ""):
        """Add a bulleted list."""
        if title:
            self.add_subsection_header(title)

        self.pdf.set_font('Helvetica', '', 11)
        self.pdf.set_text_color(*self.dark)

        for item in items:
            self.pdf.cell(5, 6, chr(149), ln=False)  # Bullet character
            self.pdf.multi_cell(0, 6, f" {item}")

        self.pdf.ln(3)

    def add_page_break(self):
        """Add a new page."""
        self.pdf.add_page()

    def get_output(self) -> bytes:
        """Get the PDF as bytes."""
        return self.pdf.output()


def generate_executive_report(
    kpis: Dict,
    area_metrics: pd.DataFrame,
    bottlenecks: List[Dict],
    recommendations: List[str],
    date_range: str = ""
) -> bytes:
    """
    Generates an executive summary report by converting a generated HTML report to PDF.
    This function acts as a consumer for the 'html_builder' agent and includes a
    workaround for a potential bug in fpdf2's memory buffer output.
    """
    if not FPDF_AVAILABLE:
        raise ImportError("fpdf2 not installed. Run: pip install fpdf2")

    try:
        from .html_builder import generate_report_html
    except ImportError:
        # If run as a script, the relative import might fail.
        from html_builder import generate_report_html


    pdf = FPDF()
    pdf.add_page()

    # The HTML agent expects a list of dicts for KPIs.
    kpi_list = [
        {
            'label': 'Total Orders',
            'value': f"{kpis.get('total_orders', 0):,}"
        },
        {
            'label': 'On-Time %',
            'value': f"{kpis.get('on_time_pct', 0):.1f}%"
        },
        {
            'label': 'Complaint Rate',
            'value': f"{kpis.get('complaint_rate', 0):.1f}%"
        },
        {
            'label': 'Avg Delivery',
            'value': f"{kpis.get('avg_delivery_time', 0):.1f} min"
        }
    ]

    # Call the agent to get the HTML content
    html_content = generate_report_html(
        kpis=kpi_list,
        area_metrics=area_metrics,
        bottlenecks=bottlenecks,
        recommendations=recommendations,
        date_range=date_range
    )

    # Render the HTML to PDF
    pdf.write_html(html_content)

    # --- Workaround for fpdf2 bug ---
    # Instead of returning pdf.output() directly to a memory buffer,
    # we write to a temporary file and read the bytes back. This avoids
    # an internal issue in some fpdf2 versions related to data compression.
    temp_pdf_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            temp_pdf_path = tmp.name
        
        pdf.output(temp_pdf_path)

        with open(temp_pdf_path, "rb") as f:
            pdf_bytes = f.read()
    finally:
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path) # Clean up the temporary file

    return pdf_bytes


def generate_detailed_report(
    df: pd.DataFrame,
    kpis: Dict,
    area_metrics: pd.DataFrame,
    stage_metrics: pd.DataFrame,
    bottlenecks: List[Dict],
    complaint_analysis: Dict,
    recommendations: List[str],
    date_range: str = ""
) -> bytes:
    """
    Generate a detailed analysis report.

    Args:
        df: Full DataFrame
        kpis: Overview KPIs
        area_metrics: Area performance
        stage_metrics: Pipeline stage metrics
        bottlenecks: Bottleneck details
        complaint_analysis: Complaint analysis results
        recommendations: Recommendation strings
        date_range: Report period

    Returns:
        PDF bytes
    """
    if not FPDF_AVAILABLE:
        raise ImportError("fpdf2 not installed. Run: pip install fpdf2")

    pdf = PizzaOpsPDF()

    # Cover
    pdf.add_cover_page(
        title="PizzaOps Detailed Analysis",
        subtitle="Operations Intelligence Report",
        date_range=date_range
    )

    # Summary
    pdf.add_page_break()
    pdf.add_section_header("1. Executive Summary")

    kpi_list = [
        {'label': 'Total Orders', 'value': f"{kpis.get('total_orders', 0):,}", 'status': 'neutral'},
        {'label': 'On-Time %', 'value': f"{kpis.get('on_time_pct', 0):.1f}%",
         'status': 'good' if kpis.get('on_time_pct', 0) >= 85 else 'warning'},
        {'label': 'Complaint Rate', 'value': f"{kpis.get('complaint_rate', 0):.1f}%",
         'status': 'good' if kpis.get('complaint_rate', 0) <= 5 else 'danger'},
        {'label': 'Avg Delivery', 'value': f"{kpis.get('avg_delivery_time', 0):.1f} min",
         'status': 'good' if kpis.get('avg_delivery_time', 0) <= 25 else 'warning'}
    ]
    pdf.add_kpi_row(kpi_list)

    # Delivery Analysis
    pdf.add_page_break()
    pdf.add_section_header("2. Delivery Performance")

    if len(area_metrics) > 0:
        pdf.add_table(area_metrics, "Performance by Delivery Area")

    # Process Analysis
    pdf.add_page_break()
    pdf.add_section_header("3. Process Analysis")

    if len(stage_metrics) > 0:
        pdf.add_table(stage_metrics, "Pipeline Stage Metrics")

    if bottlenecks:
        pdf.add_subsection_header("Identified Bottlenecks")
        for bn in bottlenecks[:5]:
            pdf.add_paragraph(
                f"• {bn['stage'].replace('_', ' ').title()}: P95 = {bn['actual_p95']} min "
                f"(benchmark: {bn['benchmark_p95']} min) - Severity: {bn['severity'].upper()}"
            )

    # Complaint Analysis
    pdf.add_page_break()
    pdf.add_section_header("4. Complaint Analysis")

    if complaint_analysis:
        on_time_pct = complaint_analysis.get('on_time_complaint_pct', 0)
        pdf.add_paragraph(
            f"Key Finding: {on_time_pct:.1f}% of complaints came from ON-TIME deliveries, "
            f"indicating quality issues beyond delivery speed."
        )

        if complaint_analysis.get('by_reason'):
            reasons = [f"{k}: {v}" for k, v in list(complaint_analysis['by_reason'].items())[:5]]
            pdf.add_bullet_list(reasons, "Top Complaint Reasons")

    # Recommendations
    pdf.add_page_break()
    pdf.add_section_header("5. Recommendations")
    pdf.add_bullet_list(recommendations[:10])

    return pdf.get_output()


def generate_recommendations_pdf(
    kpis: Any,
    recommendations: List[Dict[str, str]],
    checklist_items: List[str],
    config: Any,
    date_str: str = ""
) -> bytes:
    """
    Generate a professional PDF report of recommendations.

    Args:
        kpis: KPIs dataclass with on_time_rate, complaint_rate, avg_delivery_time
        recommendations: List of recommendation dicts with priority, title, action, expected_impact, evidence
        checklist_items: List of checklist item strings
        config: Config object with targets (on_time_target_pct, complaint_target_pct, delivery_target_minutes)
        date_str: Optional date string for the report header

    Returns:
        PDF file as bytes
    """
    if not FPDF_AVAILABLE:
        raise ImportError("fpdf2 not installed. Run: pip install fpdf2")

    pdf = PizzaOpsPDF()

    # Cover page
    pdf.add_cover_page(
        title="Actions & Recommendations",
        subtitle="Performance Improvement Report",
        date_range=date_str if date_str else datetime.now().strftime("%Y-%m-%d")
    )

    # KPI Summary section
    pdf.add_page_break()
    pdf.add_section_header("Performance Summary")

    # Determine status colors based on targets
    on_time_status = "good" if kpis.on_time_rate >= config.on_time_target_pct else "danger"
    complaint_status = "good" if kpis.complaint_rate < config.complaint_target_pct else "danger"
    delivery_status = "good" if kpis.avg_delivery_time <= config.delivery_target_minutes else "danger"

    kpi_list = [
        {
            'label': 'On-Time Rate',
            'value': f"{kpis.on_time_rate:.1f}%",
            'status': on_time_status
        },
        {
            'label': 'Complaint Rate',
            'value': f"{kpis.complaint_rate:.1f}%",
            'status': complaint_status
        },
        {
            'label': 'Avg Delivery',
            'value': f"{kpis.avg_delivery_time:.1f} min",
            'status': delivery_status
        }
    ]
    pdf.add_kpi_row(kpi_list)

    # Targets reference
    pdf.add_paragraph(
        f"Targets: On-Time >= {config.on_time_target_pct}% | "
        f"Complaints < {config.complaint_target_pct}% | "
        f"Delivery <= {config.delivery_target_minutes} min"
    )

    # Recommendations section
    pdf.add_section_header("Prioritized Recommendations")

    if recommendations:
        # Group by priority
        priority_order = ["high", "medium", "quick_win"]
        priority_labels = {
            "high": "HIGH PRIORITY",
            "medium": "MEDIUM PRIORITY",
            "quick_win": "QUICK WIN"
        }

        for priority in priority_order:
            priority_recs = [r for r in recommendations if r.get("priority") == priority]
            if priority_recs:
                pdf.add_subsection_header(priority_labels.get(priority, priority.upper()))

                for rec in priority_recs:
                    title = rec.get("title", "Recommendation")
                    action = pdf.wrap_long_words(rec.get("action", "N/A"))
                    impact = pdf.wrap_long_words(rec.get("expected_impact", "N/A"))
                    evidence = pdf.wrap_long_words(rec.get("evidence", "Based on data analysis"))

                    pdf.add_paragraph(f"{title}")
                    pdf.pdf.set_font('Helvetica', '', 10)
                    pdf.pdf.set_text_color(*pdf.gray)
                    pdf.pdf.multi_cell(0, 5, f"Action: {action}")
                    pdf.pdf.multi_cell(0, 5, f"Expected Impact: {impact}")
                    pdf.pdf.multi_cell(0, 5, f"Evidence: {evidence}")
                    pdf.pdf.ln(5)
    else:
        pdf.add_paragraph("No urgent actions required - all metrics within targets!")

    # Checklist section
    pdf.add_page_break()
    pdf.add_section_header("Today's Checklist")

    if checklist_items:
        checklist_formatted = [f"[ ] {item}" for item in checklist_items]
        pdf.add_bullet_list(checklist_formatted)
    else:
        pdf.add_paragraph("No specific checklist items for today.")

    # Footer
    pdf.pdf.ln(20)
    pdf.pdf.set_font('Helvetica', 'I', 9)
    pdf.pdf.set_text_color(*pdf.gray)
    pdf.pdf.cell(0, 6, "Generated by PizzaOps Intelligence - LocalAnalytics Engine", ln=True, align='C')
    pdf.pdf.cell(0, 6, f"Report Date: {datetime.now().strftime('%d %B %Y at %H:%M')}", ln=True, align='C')

    return pdf.get_output()
