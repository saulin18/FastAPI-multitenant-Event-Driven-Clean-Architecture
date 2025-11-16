from uuid import UUID

from app.shared.events import DomainEvent


class TenantCreatedEvent(DomainEvent):
    __event_name__ = "tenant.created"
    
    def __init__(self, tenant_id: UUID, name: str, domain: str, **kwargs):
        super().__init__(**kwargs)
        self.tenant_id = tenant_id
        self.name = name
        self.domain = domain
        self.event_type = "tenant.created"

class TenantDeletedEvent(DomainEvent):
    __event_name__ = "tenant.deleted"
    
    def __init__(self, tenant_id: UUID, **kwargs):
        super().__init__(**kwargs)
        self.tenant_id = tenant_id
        self.event_type = "tenant.deleted"

class TenantUpdatedEvent(DomainEvent):
    __event_name__ = "tenant.updated"
    
    def __init__(self, tenant_id: UUID, name: str, domain: str, **kwargs):
        super().__init__(**kwargs)
        self.tenant_id = tenant_id
        self.name = name
        self.domain = domain
        self.event_type = "tenant.updated"