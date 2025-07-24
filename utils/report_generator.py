import os
from datetime import datetime
from typing import Optional
from context import UserSessionContext
from config import config  # Should contain config.REPORTS_DIR

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf_report(context: UserSessionContext) -> str:
    """
    Generate a personalized PDF report for a user's health & wellness journey.

    Args:
        context (UserSessionContext): The user session with data.

    Returns:
        str: Path to the generated PDF file.
    """
    try:
        reports_dir = config.REPORTS_DIR
        os.makedirs(reports_dir, exist_ok=True)

        filename = f"wellness_report_{context.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(reports_dir, filename)

        # Use the high-level ReportLab Platypus framework:
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph("Health & Wellness Report", styles['Title']))
        story.append(Spacer(1, 18))
        story.append(Paragraph(f"User: <b>{context.name}</b>", styles['Normal']))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 18))

        # Personal Info
        story.append(Paragraph("<b>Personal Information</b>", styles['Heading2']))
        info_lines = []
        info_lines.append(f"<b>Goal:</b> {getattr(context.goal_type, 'value', str(context.goal_type)).replace('_',' ').title()} " +
                          (f"(Target: {context.goal_target}{getattr(context.goal_unit, 'value', '')})" if context.goal_target else ""))
        if context.age:
            info_lines.append(f"<b>Age:</b> {context.age}")
        if context.weight:
            info_lines.append(f"<b>Weight:</b> {context.weight} kg")
        if context.height:
            info_lines.append(f"<b>Height:</b> {context.height} cm")
        if hasattr(context, 'calculate_bmi'):
            bmi = context.calculate_bmi()
            if bmi:
                info_lines.append(f"<b>BMI:</b> {bmi}")
        info_lines.append(f"<b>Activity Level:</b> {getattr(context, 'activity_level', '').replace('_',' ').title()}")
        info_lines.append(f"<b>Dietary Preference:</b> {getattr(context.dietary_preference, 'value', str(context.dietary_preference)).replace('_',' ').title()}")

        for line in info_lines:
            story.append(Paragraph(line, styles['Normal']))
        story.append(Spacer(1, 12))

        # Metrics Table
        if getattr(context, 'latest_metrics', None):
            story.append(Paragraph("<b>Current Metrics</b>", styles['Heading2']))
            metric_data = [['Metric', 'Value', 'Unit', 'Date', 'Notes']]
            for k, v in context.latest_metrics.items():
                metric_data.append([
                    k.title(),
                    v.get('value', ''),
                    v.get('unit', ''),
                    v.get('timestamp', '')[:10],
                    str(v.get('notes', ''))
                ])
            tbl = Table(metric_data)
            tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 12))

        # Meal Plan Table (if available)
        if getattr(context, 'meal_plan', None):
            meal_plan = context.meal_plan
            if isinstance(meal_plan, dict):  # daywise
                story.append(Paragraph("<b>Meal Plan</b>", styles['Heading2']))
                for day, plan in meal_plan.items():
                    story.append(Paragraph(f"<b>{day}</b>", styles['Normal']))
                    for meal_type in ['breakfast', 'lunch', 'dinner']:
                        meal = getattr(plan, meal_type, None)
                        if meal:
                            story.append(Paragraph(f"{meal_type.title()}: {getattr(meal, 'name', meal)}", styles['Normal']))
                    if hasattr(plan, 'total_calories'):
                        story.append(Paragraph(f"Total Calories: {plan.total_calories}", styles['Normal']))
                    story.append(Spacer(1, 6))

        # Progress History Table (10 recent)
        if getattr(context, 'progress_history', None):
            story.append(Paragraph("<b>Progress History</b>", styles['Heading2']))
            progress_data = [['Date', 'Metric', 'Value', 'Unit', 'Notes']]
            for entry in context.progress_history[-10:]:
                date_str = entry.date.strftime('%Y-%m-%d') if hasattr(entry.date, 'strftime') else str(entry.date)[:10]
                progress_data.append([
                    date_str,
                    entry.metric.title(),
                    entry.value,
                    entry.unit,
                    entry.notes or ''
                ])
            tbl = Table(progress_data)
            tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 12))

        # Footer/Disclaimer
        story.append(Spacer(1, 20))
        story.append(Paragraph(
            "This report was auto-generated based on your wellness data. For medical advice, please consult with a healthcare professional.",
            styles['Italic'])
        )

        # Build PDF
        doc.build(story)
        return output_path

    except Exception as e:
        import logging
        logging.error(f"PDF generation failed: {e}")
        return ""

def get_latest_report_path(user_id: str) -> Optional[str]:
    """Get the path to the most recent report for a user."""
    reports_dir = config.REPORTS_DIR
    if not os.path.exists(reports_dir):
        return None
    user_reports = [
        f for f in os.listdir(reports_dir)
        if f.startswith(f"wellness_report_{user_id}_") and f.endswith('.pdf')
    ]
    if not user_reports:
        return None
    user_reports.sort(reverse=True)
    return os.path.join(reports_dir, user_reports[0])


def save_pdf_report(pdf_bytes: bytes, filename: str = "health_report.pdf") -> None:
    """
    Save the PDF byte content to a file on disk.
    """
    with open(filename, "wb") as f:
        f.write(pdf_bytes)
