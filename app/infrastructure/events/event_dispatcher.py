
from fastapi_events.dispatcher import dispatch

from app.domain.events.user_events import UserCreatedEvent, UserUpdatedEvent
from app.domain.interfaces.event_dispatcher import EventDispatcher as IEventDispatcher
from app.domain.events.tenant_events import TenantCreatedEvent, TenantUpdatedEvent, TenantDeletedEvent


class EventDispatcher(IEventDispatcher):
    
    def dispatch_user_created(self, event: UserCreatedEvent) -> None:
        
        dispatch("user.created", payload=event.__dict__)
    
    def dispatch_user_updated(self, event: UserUpdatedEvent) -> None:
    
        dispatch("user.updated", payload=event.__dict__)
        
    def dispatch_tenant_created(self, event: TenantCreatedEvent) -> None:
        dispatch("tenant.created", payload=event.__dict__)
    
    def dispatch_tenant_updated(self, event: TenantUpdatedEvent) -> None:
        dispatch("tenant.updated", payload=event.__dict__)
    
    def dispatch_tenant_deleted(self, event: TenantDeletedEvent) -> None:
        dispatch("tenant.deleted", payload=event.__dict__)

