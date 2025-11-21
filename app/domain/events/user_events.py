from typing import Optional
from uuid import UUID
from app.shared.events import DomainEvent

class UserCreatedEvent(DomainEvent):
    __event_name__ = "user.created"
    
    def __init__(self, user_id: UUID, email: str, username: str, tenant_id: UUID,
                 full_name: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.email = email
        self.username = username
        self.tenant_id = tenant_id  
        self.full_name = full_name
        self.event_type = "user.created"

class UserUpdatedEvent(DomainEvent):
    __event_name__ = "user.updated"
    
    def __init__(self, user_id: UUID, tenant_id: UUID, email: Optional[str] = None, 
                 username: Optional[str] = None, full_name: Optional[str] = None, 
                 is_active: Optional[bool] = None, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.tenant_id = tenant_id  
        self.email = email
        self.username = username
        self.full_name = full_name
        self.is_active = is_active
        self.event_type = "user.updated"

class UserLoggedInEvent(DomainEvent):
    __event_name__ = "user.logged_in"
    
    def __init__(self, user_id: UUID, email: str, username: str, tenant_id: Optional[UUID] = None,
                 access_token: str = None, refresh_token: str = None, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.email = email
        self.username = username
        self.tenant_id = tenant_id
        self.access_token = access_token 
        self.refresh_token = refresh_token
        self.event_type = "user.logged_in"