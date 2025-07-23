# utils/report_generator.py

import os
from datetime import datetime
from typing import Optional
import tempfile
import logging

from context import UserSessionContext
from config import config

logger = logging.getLogger(__name__)

def generate_pdf_report(context: UserSessionContext) -> str:
    """
    Generates a personalized PDF report for a user's health & wellness journey.

    Args:
        context (UserSessionContext): Object containing user name, goal, meal plan, and progress logs.

    Returns:
        str: Path to the generated PDF file.
    """
    try:
        # Try to use WeasyPrint for better HTML to PDF conversion
        try:
            from weasyprint import HTML, CSS
            return _generate_with_weasyprint(context)
        except ImportError:
            logger.info("WeasyPrint not available, falling back to FPDF")
            return _generate_with_fpdf(context)
            
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        return ""

def _generate_with_weasyprint(context: UserSessionContext) -> str:
    """Generate PDF using WeasyPrint (HTML to PDF)."""
    from weasyprint import HTML
    from jinja2 import Template
    
    # Create reports directory
    reports_dir = config.REPORTS_DIR
    os.makedirs(reports_dir, exist_ok=True)
    
    # HTML template
    template = Template('''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Health & Wellness Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                line-height: 1.6;
            }
            .header {
                background-color: #00C851;
                color: white;
                padding: 20px;
                text-align: center;
                margin-bottom: 30px;
            }
            .section {
                margin-bottom: 30px;
                padding: 20px;
                border-left: 4px solid #00C851;
                background-color: #f9f9f9;
            }
            .metric {
                background-color: white;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
            .goal-progress {
                background-color: #e8f5e8;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
                border: 1px solid #00C851;
            }
            ul {
                list-style-type: none;
                padding-left: 0;
            }
            li {
                margin: 10px 0;
                padding: 10px;
                background-color: white;
                border-radius: 5px;
                border: 1px solid #eee;
            }
            .date {
                color: #666;
                font-size: 0.9em;
            }
            h1, h2 {
                color: #333;
            }
            .footer {
                margin-top: 40px;
                text-align: center;
                color: #666;
                border-top: 1px solid #ddd;
                padding-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Health & Wellness Report</h1>
            <p>For {{ name }}</p>
            <p class="date">Generated on {{ generation_date }}</p>
        </div>
        
        <div class="section">
            <h2>Personal Information</h2>
            <div class="metric">
                <strong>Name:</strong> {{ name }}<br>
                <strong>Goal:</strong> {{ goal_type }} 
                {% if goal_target %}(Target: {{ goal_target }}{{ goal_unit }}){% endif %}<br>
                {% if age %}<strong>Age:</strong> {{ age }}<br>{% endif %}
                {% if weight %}<strong>Current Weight:</strong> {{ weight }} kg<br>{% endif %}
                {% if height %}<strong>Height:</strong> {{ height }} cm<br>{% endif %}
                {% if bmi %}<strong>BMI:</strong> {{ bmi }}<br>{% endif %}
                <strong>Activity Level:</strong> {{ activity_level }}<br>
                <strong>Dietary Preference:</strong> {{ dietary_preference }}
            </div>
        </div>
        
        {% if latest_metrics %}
        <div class="section">
            <h2>Current Metrics</h2>
            {% for metric, data in latest_metrics.items() %}
            <div class="metric">
                <strong>{{ metric.title() }}:</strong> {{ data.value }}{{ data.unit }}
                <span class="date">({{ data.timestamp[:10] }})</span>
                {% if data.notes %}<br><em>{{ data.notes }}</em>{% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if meal_plan %}
        <div class="section">
            <h2>Current Meal Plan</h2>
            {% for day, plan in meal_plan.items() %}
            <div class="metric">
                <h3>{{ day }}</h3>
                {% if plan.breakfast %}
                <strong>Breakfast:</strong> {{ plan.breakfast.name }}<br>
                {% endif %}
                {% if plan.lunch %}
                <strong>Lunch:</strong> {{ plan.lunch.name }}<br>
                {% endif %}
                {% if plan.dinner %}
                <strong>Dinner:</strong> {{ plan.dinner.name }}<br>
                {% endif %}
                {% if plan.total_calories %}
                <strong>Total Calories:</strong> {{ plan.total_calories }}
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if workout_plan %}
        <div class="section">
            <h2>Current Workout Plan</h2>
            {% for day, plan in workout_plan.items() %}
            <div class="metric">
                <h3>{{ day }}</h3>
                <strong>Focus:</strong> {{ plan.focus }}<br>
                <strong>Duration:</strong> {{ plan.duration }}<br>
                <strong>Intensity:</strong> {{ plan.intensity }}<br>
                <strong>Exercises:</strong>
                <ul>
                {% for exercise in plan.exercises %}
                    <li>{{ exercise.name }} - {{ exercise.description }}</li>
                {% endfor %}
                </ul>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if progress_history %}
        <div class="section">
            <h2>Progress History</h2>
            {% for entry in progress_history[-10:] %}
            <div class="metric">
                <strong>{{ entry.metric.title() }}:</strong> {{ entry.value }}{{ entry.unit }}
                <span class="date">({{ entry.date[:10] }})</span>
                {% if entry.notes %}<br><em>{{ entry.notes }}</em>{% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <div class="footer">
            <p>This report was generated automatically based on your health and wellness data.</p>
            <p>Please consult with healthcare professionals for personalized medical advice.</p>
        </div>
    </body>
    </html>
    ''')
    
    # Prepare template data
    template_data = {
        'name': context.name,
        'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'goal_type': context.goal_type.value.replace('_', ' ').title() if context.goal_type else 'General Wellness',
        'goal_target': context.goal_target,
        'goal_unit': context.goal_unit.value if context.goal_unit else '',
        'age': context.age,
        'weight': context.weight,
        'height': context.height,
        'bmi': context.calculate_bmi(),
        'activity_level': context.activity_level.replace('_', ' ').title(),
        'dietary_preference': context.dietary_preference.value.replace('_', ' ').title(),
        'latest_metrics': context.latest_metrics,
        'meal_plan': context.meal_plan,
        'workout_plan': context.workout_plan,
        'progress_history': [entry.model_dump() for entry in context.progress_history]
    }
    
    # Render HTML
    html_content = template.render(**template_data)
    
    # Generate PDF
    filename = f"wellness_report_{context.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    output_path = os.path.join(reports_dir, filename)
    
    HTML(string=html_content).write_pdf(output_path)
    
    return output_path

def _generate_with_fpdf(context: UserSessionContext) -> str:
    """Generate PDF using FPDF (fallback method)."""
    from fpdf import FPDF
    
    # Create reports directory
    reports_dir = config.REPORTS_DIR
    os.makedirs(reports_dir, exist_ok=True)
    
    class PDFReport(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, 'Health & Wellness Report', 0, 1, 'C')
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 0, 'C')

    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    # User Info
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Personal Information", ln=1)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"Name: {context.name}", ln=1)
    
    if context.goal_type:
        goal_text = f"Goal: {context.goal_type.value.replace('_', ' ').title()}"
        if context.goal_target:
            goal_text += f" (Target: {context.goal_target}{context.goal_unit.value if context.goal_unit else ''})"
        pdf.cell(0, 8, goal_text, ln=1)
    
    if context.age:
        pdf.cell(0, 8, f"Age: {context.age}", ln=1)
    if context.weight:
        pdf.cell(0, 8, f"Weight: {context.weight} kg", ln=1)
    if context.height:
        pdf.cell(0, 8, f"Height: {context.height} cm", ln=1)
    
    bmi = context.calculate_bmi()
    if bmi:
        pdf.cell(0, 8, f"BMI: {bmi}", ln=1)
    
    pdf.cell(0, 8, f"Activity Level: {context.activity_level.replace('_', ' ').title()}", ln=1)
    pdf.cell(0, 8, f"Dietary Preference: {context.dietary_preference.value.replace('_', ' ').title()}", ln=1)
    pdf.ln(10)

    # Latest Metrics
    if context.latest_metrics:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Current Metrics", ln=1)
        pdf.set_font("Arial", size=11)
        
        for metric, data in context.latest_metrics.items():
            metric_text = f"{metric.title()}: {data['value']}{data['unit']}"
            pdf.cell(0, 8, metric_text, ln=1)
        pdf.ln(10)

    # Progress History
    if context.progress_history:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Recent Progress", ln=1)
        pdf.set_font("Arial", size=10)
        
        for entry in context.progress_history[-10:]:  # Last 10 entries
            date_str = entry.date.strftime("%Y-%m-%d") if hasattr(entry.date, 'strftime') else str(entry.date)[:10]
            progress_text = f"{date_str}: {entry.metric.title()} = {entry.value}{entry.unit}"
            pdf.multi_cell(0, 6, progress_text)
        pdf.ln(5)

    # Generate filename and save
    filename = f"wellness_report_{context.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    output_path = os.path.join(reports_dir, filename)
    
    pdf.output(output_path)
    
    return output_path

def get_latest_report_path(user_id: str) -> Optional[str]:
    """Get the path to the most recent report for a user."""
    reports_dir = config.REPORTS_DIR
    if not os.path.exists(reports_dir):
        return None
    
    # Find the most recent report for this user
    user_reports = [
        f for f in os.listdir(reports_dir) 
        if f.startswith(f"wellness_report_{user_id}_") and f.endswith('.pdf')
    ]
    
    if not user_reports:
        return None
    
    # Sort by timestamp in filename
    user_reports.sort(reverse=True)
    return os.path.join(reports_dir, user_reports[0])
