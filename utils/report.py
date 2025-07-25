from fpdf import FPDF
from datetime import datetime
from typing import Optional
from context import UserSessionContext

class PDFReport(FPDF):
    """Custom PDF layout for generating Health & Wellness Reports."""

    def header(self):
        self.set_font('Arial', 'B', 13)
        self.cell(0, 10, 'Health & Wellness Report', border=0, ln=1, align='C')
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 0, 'C')

def generate_pdf_report(context: UserSessionContext) -> bytes:
    """
    Creates a personalized PDF report for the user's health journey.

    Args:
        context: UserSessionContext containing user data, goals, plans, and logs.

    Returns:
        bytes: The PDF binary (latin-1 encoded). Save to file, serve, or stream.
    """
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # User Info Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "User Information:", ln=1)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"Name: {context.name}", ln=1)
    goal_str = getattr(context, "goal", None) or getattr(context, "goal_type", None)
    if goal_str:
        goal_disp = str(goal_str).replace("_", " ").title()
        pdf.cell(0, 8, f"Goal: {goal_disp}", ln=1)
    if getattr(context, "age", None):
        pdf.cell(0, 8, f"Age: {context.age}", ln=1)
    if getattr(context, "weight", None):
        pdf.cell(0, 8, f"Weight: {context.weight} kg", ln=1)
    if getattr(context, "height", None):
        pdf.cell(0, 8, f"Height: {context.height} cm", ln=1)
    if hasattr(context, "calculate_bmi"):
        bmi = context.calculate_bmi()
        if bmi:
            pdf.cell(0, 8, f"BMI: {bmi:.2f}", ln=1)
    activity = getattr(context, "activity_level", None)
    if activity:
        pdf.cell(0, 8, f"Activity Level: {str(activity).replace('_', ' ').title()}", ln=1)
    dietary = getattr(context, "dietary_preference", None)
    if dietary:
        pdf.cell(0, 8, f"Dietary Preference: {getattr(dietary, 'value', str(dietary)).replace('_',' ').title()}", ln=1)
    pdf.ln(6)

    # Meal Plan Section
    meal_plan = getattr(context, "meal_plan", None)
    if meal_plan and any(meal_plan):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Recommended Meal Plan", ln=1)
        pdf.set_font("Arial", size=11)
        if isinstance(meal_plan, dict):
            for day, meals in meal_plan.items():
                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 9, f"{day}:", ln=1)
                pdf.set_font("Arial", size=11)
                if isinstance(meals, dict):
                    for meal_type, items in meals.items():
                        if items:
                            meal_line = f"  {meal_type.capitalize()}: {items}"
                            pdf.multi_cell(0, 8, meal_line)
                pdf.ln(2)
        else:
            for meal in meal_plan:
                pdf.multi_cell(0, 8, str(meal))
                pdf.ln(1)
        pdf.ln(6)

    # Progress Section
    if getattr(context, "progress_logs", None):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Recent Progress Log", ln=1)
        pdf.set_font("Arial", size=10)
        for log in context.progress_logs[-10:]:
            date = log.get("date") or log.get("timestamp", "Unknown Date")
            notes = log.get("notes") or log.get("interaction", "No detail")
            metric = log.get("metric", "")
            value = log.get("value", "")
            unit = log.get("unit", "")
            desc = f"{date}: {metric} {value}{unit} - {notes}"
            pdf.multi_cell(0, 7, desc)
            pdf.ln(1)
        pdf.ln(4)

    # Optional: Latest Metrics table (if available)
    latest = getattr(context, 'latest_metrics', None)
    if latest:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Latest Metrics", ln=1)
        pdf.set_font("Arial", size=10)
        for metric, data in latest.items():
            metric_line = (
                f"{metric.title()}: {data.get('value', '')}{data.get('unit', '')} | "
                f"({data.get('timestamp', '')[:10]}) {data.get('notes', '') or ''}"
            )
            pdf.multi_cell(0, 8, metric_line)
        pdf.ln(3)

    # Footer Disclaimer
    pdf.set_y(-35)
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 7, "This report was automatically generated by your Health & Wellness AI agent (Gemini-based). For medical decisions, always consult with a healthcare professional.\n© 2025 Health Agents")

    # Output to binary for streaming/download
    try:
        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        print(f"[PDF Generation Error] {e}")
        return b""

# ---- Optional utility to save PDF to file (if needed) ----
def save_pdf_report(pdf_bytes: bytes, output_path: str) -> None:
    with open(output_path, "wb") as f:
        f.write(pdf_bytes)
