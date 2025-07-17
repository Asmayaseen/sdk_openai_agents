# utils/report.py

from fpdf import FPDF
from datetime import datetime

from context import UserSessionContext

from typing import Optional


class PDFReport(FPDF):
    """Custom PDF layout for generating Health & Wellness Reports."""

    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Health & Wellness Report', border=0, ln=1, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d")}', 0, 0, 'C')


def generate_pdf_report(context: UserSessionContext) -> bytes:
    """
    Generates a personalized PDF report for a user's health & wellness journey.

    Args:
        context (UserSessionContext): Object containing user name, goal, meal plan, and progress logs.

    Returns:
        bytes: Binary content of the generated PDF (latin-1 encoded).
    """
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # User Info
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "User Information", ln=1)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 10, f"Name: {context.name}", ln=1)
    pdf.cell(0, 10, f"Goal: {context.goal}", ln=1)
    pdf.ln(10)

    # Meal Plan
    if context.meal_plan and any(context.meal_plan):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Recommended Meal Plan", ln=1)
        pdf.set_font("Arial", size=11)

        if isinstance(context.meal_plan, dict):
            for day, meals in context.meal_plan.items():
                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 10, f"{day}:", ln=1)
                pdf.set_font("Arial", size=10)
                for meal_type, items in meals.items():
                    pdf.multi_cell(0, 8, f"  {meal_type.capitalize()}: {items}")
                pdf.ln(4)
        else:
            for meal in context.meal_plan:
                pdf.multi_cell(0, 8, str(meal))
                pdf.ln(2)

    # Progress Logs
    if context.progress_logs:
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Progress History", ln=1)
        pdf.set_font("Arial", size=10)

        for log in context.progress_logs[-10:]:
            date = log.get("date") or log.get("timestamp", "Unknown Date")
            notes = log.get("notes") or log.get("interaction", "No notes provided")
            pdf.multi_cell(0, 7, f"{date}: {notes}")
            pdf.ln(2)

    # Output PDF
    try:
        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        print(f"[PDF Generation Error] {e}")
        return b""
