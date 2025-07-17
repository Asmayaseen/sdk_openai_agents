import smtplib
from email.mime.text import MIMEText
from typing import Optional
from ..context import UserSessionContext
import logging

class SpecialistConnector:
    """Handles connections to human specialists"""

    def __init__(self, smtp_server: str = "localhost", smtp_port: int = 25):
        self.specialists = {
            "nutritionist": "nutrition@example.com",
            "trainer": "training@example.com",
            "doctor": "medical@example.com"
        }
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def request_human_specialist(
        self,
        specialist_type: str,
        context: Optional[UserSessionContext],
        user_notes: Optional[str] = None
    ) -> bool:
        """
        Initiate connection to human specialist
        
        Args:
            specialist_type: Type of specialist needed
            context: User session context
            user_notes: Additional user comments
            
        Returns:
            bool: True if request succeeded
        """
        if specialist_type not in self.specialists:
            logging.warning(f"Unknown specialist type requested: {specialist_type}")
            return False

        if context is None:
            logging.error("User context is missing.")
            return False

        email_content = f"""
        👤 User Name: {context.name}
        🎯 Goal: {context.goal or 'N/A'}
        📝 Notes: {user_notes or 'No additional notes'}
        """

        try:
            msg = MIMEText(email_content)
            msg['Subject'] = f"🔔 Specialist Request - {specialist_type.capitalize()}"
            msg['From'] = "bot@wellness.ai"
            msg['To'] = self.specialists[specialist_type]

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.send_message(msg)
            
            logging.info(f"Specialist request sent to {specialist_type}")
            return True
        
        except Exception as e:
            logging.error(f"Failed to send specialist request: {e}")
            return False
