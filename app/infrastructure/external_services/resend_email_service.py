from typing import List, Optional
from app.domain.interfaces.mail_service import IMailService
import resend
from app.shared.config import Settings

class ResendEmailService(IMailService):
    
    def __init__(self, settings: Settings):
        self.settings = settings
        resend.api_key = self.settings.resend_api_key
    
    async def send_email(self, to: str, subject: str, html: Optional[str] = None, **kwargs) -> None:
        """Send an email to a single recipient."""
        try:
            params: resend.Emails.SendParams = {
                "from": self.settings.resend_from_email,
                "to": [to],
                "subject": subject,
                "html": html,
                **kwargs
            }
            email: resend.Email = resend.Emails.send(params)
            print(f" Email sent to {to}: {email.id}")
        except Exception as e:
            print(f"Error sending email to {to}: {e}")
            raise e
    
    async def send_bulk_email(self, recipients: List[str], subject: str, html: Optional[str] = None, **kwargs) -> None:
        """Send email to multiple recipients."""
        try:
            params: resend.Emails.SendParams = {
                "from": self.settings.resend_from_email,
                "to": recipients,
                "subject": subject,
                "html": html,
                **kwargs
            }
            email: resend.Email = resend.Emails.send(params)
            print(f" Bulk email sent to {len(recipients)} recipients: {email.id}")
        except Exception as e:
            print(f" Error sending bulk email: {e}")
            raise e