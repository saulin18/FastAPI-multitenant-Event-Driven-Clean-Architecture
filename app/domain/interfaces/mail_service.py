from abc import ABC, abstractmethod
from typing import List, Optional

class IMailService(ABC):
  
    
    @abstractmethod
    async def send_email(self, to: str, subject: str, html: Optional[str] = None, **kwargs) -> None:
        """Send an email to a recipient."""
        pass
    
    @abstractmethod
    async def send_bulk_email(self, recipients: List[str], subject: str, html: Optional[str] = None, **kwargs) -> None:
        """Send email to multiple recipients."""
        pass
    
