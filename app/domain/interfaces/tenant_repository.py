from abc import ABC, abstractmethod
from typing import List, Optional, Any
from uuid import UUID
from app.domain.entities.tenant import Tenant

class TenantRepository(ABC):
    
    @abstractmethod
    async def create(self, tenant: Tenant) -> Tenant:
        pass
    
    @abstractmethod
    async def get_by_id(self, tenant_id: UUID) -> Optional[Tenant]:
        pass
    
    @abstractmethod
    async def get_by_domain(self, domain: str) -> Optional[Tenant]:
        pass
    
    @abstractmethod
    async def update(self, tenant: Tenant) -> Optional[Tenant]:
        pass
    
    @abstractmethod
    async def delete(self, tenant_id: UUID) -> bool:
        pass
    
    @abstractmethod
    async def list_all_with_cursor(self, cursor: str = None, limit: int = 100, **kwargs: Any) -> List[Optional[Any]]:
        pass
    
    @abstractmethod
    async def list_all_with_pagination(self, page: int = 1, page_size: int = 10) -> Any:
        pass