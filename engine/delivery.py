import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import logging
import time

logger = logging.getLogger(__name__)

class DeliveryChannel:
    """Email delivery system with SMTP support."""
    
    def __init__(self, smtp_config: Dict):
        self.smtp_config = smtp_config
        self.dry_run = smtp_config["username"] is None
        if self.dry_run:
            logger.info("Delivery channel initialized in DRY RUN mode (no actual emails will be sent)")
        else:
            logger.info("Delivery channel initialized in LIVE mode")

    def send_email(self, to: str, subject: str, body: str, attachments: List[str] = None) -> bool:
        """Send an email with optional attachments."""
        msg = MIMEMultipart()
        msg['From'] = self.smtp_config.get("username", "orchestrator@example.com")
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        if attachments:
            for filepath in attachments:
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(filepath)}"')
                    msg.attach(part)
                    logger.info(f"Attached file: {filepath}")
                else:
                    logger.warning(f"Attachment file not found: {filepath}")

        if self.dry_run:
            logger.info(f"[DRY RUN] Email to {to} with subject '{subject}'")
            logger.debug(f"Email body:\n{body}")
            return True

        try:
            server = smtplib.SMTP(self.smtp_config["host"], self.smtp_config["port"])
            if self.smtp_config.get("use_tls", True):
                server.starttls()
            if self.smtp_config["username"]:
                server.login(self.smtp_config["username"], self.smtp_config["password"])
            server.send_message(msg)
            server.quit()
            logger.info(f"Email sent to {to}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            return False
