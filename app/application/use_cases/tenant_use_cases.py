from app.domain.interfaces.tenant_repository import TenantRepository
from app.application.dtos.tenant_dtos import CreateTenantRequest, UpdateTenantRequest, CursorPagedTenantRequest
from app.domain.entities.tenant import Tenant
from app.application.exceptions.tenant_exceptions import TenantNotFoundError, TenantAlreadyExistsError
from app.shared.pagination import CursorPagedResult
from typing import Any
from uuid import UUID


class CreateTenantUseCase:
    
    def __init__(self, tenant_repository: TenantRepository):
        self.tenant_repository = tenant_repository
    
    async def execute(self, request: CreateTenantRequest) -> Tenant:
        
        existing_tenant = await self.tenant_repository.get_by_domain(request.domain)
        if existing_tenant:
            raise TenantAlreadyExistsError(f"Tenant with domain {request.domain} already exists")
        
        tenant = Tenant(
            name=request.name,
            domain=request.domain,
            is_active=True
        )
        
        return await self.tenant_repository.create(tenant)


class GetTenantUseCase:
    
    
    def __init__(self, tenant_repository: TenantRepository):
        self.tenant_repository = tenant_repository
    
    async def execute(self, tenant_id: UUID) -> Tenant:
        tenant = await self.tenant_repository.get_by_id(tenant_id)
        if not tenant:
            raise TenantNotFoundError(f"Tenant with id {tenant_id} not found")
        return tenant


class UpdateTenantUseCase:

    
    def __init__(self, tenant_repository: TenantRepository):
        self.tenant_repository = tenant_repository
    
    async def execute(self, tenant_id: UUID, request: UpdateTenantRequest) -> Tenant:

        existing_tenant = await self.tenant_repository.get_by_id(tenant_id)
        if not existing_tenant:
            raise TenantNotFoundError(f"Tenant with id {tenant_id} not found")
    
        existing_tenant.update_info(
            name=request.name,
            domain=request.domain
        )
        
        if request.is_active is not None:
            if request.is_active:
                existing_tenant.activate()
            else: 
                
                existing_tenant.deactivate()
        
        updated_tenant = await self.tenant_repository.update(existing_tenant)
        if not updated_tenant:
            raise TenantNotFoundError(f"Tenant with id {tenant_id} not found")
        
        return updated_tenant


class ListTenantsUseCase:
   
    
    def __init__(self, tenant_repository: TenantRepository):
        self.tenant_repository = tenant_repository
    
    async def execute(self, request: CursorPagedTenantRequest) -> CursorPagedResult[Any]:
       
        return await self.tenant_repository.list_all_with_cursor(
            cursor=request.cursor,
            limit=request.page_size,
            direction=request.direction
        )


class DeleteTenantUseCase:
  
    
    def __init__(self, tenant_repository: TenantRepository):
        self.tenant_repository = tenant_repository
    
    async def execute(self, tenant_id: UUID) -> bool:
        tenant = await self.tenant_repository.get_by_id(tenant_id)
        if not tenant:
            raise TenantNotFoundError(f"Tenant with id {tenant_id} not found")
        
        return await self.tenant_repository.delete(tenant_id)
