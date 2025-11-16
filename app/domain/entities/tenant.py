
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

class Tenant:
    
    def __init__(self, name: str, domain: str, is_active: bool = True, 
                 tenant_id: UUID = None, created_at: datetime = None, 
                 updated_at: datetime = None):
        self.tenant_id = tenant_id or uuid4()
        self.name = name
        self.domain = domain
        self.is_active = is_active
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
    
    def activate(self) -> None:
        self.is_active = True
        self.updated_at = datetime.now(timezone.utc)
    
    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)
    
    def update_info(self, name: Optional[str] = None, domain: Optional[str] = None) -> None:
        if name is not None:
            self.name = name
        if domain is not None:
            self.domain = domain
        self.updated_at = datetime.now(timezone.utc)
    
    def __repr__(self) -> str:
        return f"Tenant(id={self.tenant_id}, name={self.name}, domain={self.domain})"
