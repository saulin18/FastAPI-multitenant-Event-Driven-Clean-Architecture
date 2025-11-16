from abc import ABC, abstractmethod


from app.domain.events.user_events import UserCreatedEvent, UserUpdatedEvent
from app.domain.events.tenant_events import TenantCreatedEvent, TenantUpdatedEvent, TenantDeletedEvent


class EventDispatcher(ABC):
    
    @abstractmethod
    def dispatch_user_created(self, UserCreatedEvent: UserCreatedEvent) -> None:
        pass
    
    @abstractmethod
    def dispatch_user_updated(self, UserUpdatedEvent: UserUpdatedEvent) -> None:
        pass
    
    @abstractmethod
    def dispatch_tenant_created(self, TenantCreatedEvent: TenantCreatedEvent) -> None:
        pass
    
    @abstractmethod
    def dispatch_tenant_updated(self, TenantUpdatedEvent: TenantUpdatedEvent) -> None:
        pass
    
    @abstractmethod
    def dispatch_tenant_deleted(self, TenantDeletedEvent: TenantDeletedEvent) -> None:
        pass