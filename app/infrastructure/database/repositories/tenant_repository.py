from app.domain.interfaces.tenant_repository import TenantRepository
from app.infrastructure.database.models import Tenant
from app.domain.entities.tenant import Tenant as TenantEntity
from app.shared.pagination import CursorPagedResult, PaginationDirection, ICursorPaginationHelper
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional, Any


class TenantRepository(TenantRepository):
    def __init__(self, session: AsyncSession, pagination_helper: ICursorPaginationHelper):
        self.db = session
        self.pagination_helper = pagination_helper
        
    async def create(self, tenant: TenantEntity) -> TenantEntity:
        
        db_tenant = Tenant(
            id=tenant.tenant_id, 
            name=tenant.name,
            domain=tenant.domain,
            is_active=tenant.is_active,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at
        )
        self.db.add(db_tenant)
        await self.db.commit()
        await self.db.refresh(db_tenant)
        
    
        return TenantEntity(
            tenant_id=db_tenant.id, 
            name=db_tenant.name,
            domain=db_tenant.domain,
            is_active=db_tenant.is_active,
            created_at=db_tenant.created_at,
            updated_at=db_tenant.updated_at
        )
    
    async def get_by_id(self, tenant_id: UUID) -> Optional[TenantEntity]:
        
        tenant = await self.db.get(Tenant, tenant_id)
        if not tenant:
            return None
        
    
        return TenantEntity(
            tenant_id=tenant.id,
            name=tenant.name,
            domain=tenant.domain,
            is_active=tenant.is_active,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at
        )
    
    async def get_by_domain(self, domain: str) -> Optional[TenantEntity]:
    
        result = await self.db.execute(select(Tenant).where(Tenant.domain == domain))
        db_tenant = result.scalar_one_or_none()
        if not db_tenant:
            return None
        
      
        return TenantEntity(
            tenant_id=db_tenant.id,
            name=db_tenant.name,
            domain=db_tenant.domain,
            is_active=db_tenant.is_active,
            created_at=db_tenant.created_at,
            updated_at=db_tenant.updated_at
        )
    
    async def update(self, tenant: TenantEntity) -> Optional[TenantEntity]:
        
        existing_tenant = await self.db.get(Tenant, tenant.tenant_id)
        
        if not existing_tenant:
            return None

    
        existing_tenant.name = tenant.name
        existing_tenant.domain = tenant.domain
        existing_tenant.is_active = tenant.is_active
        existing_tenant.updated_at = tenant.updated_at
        
        await self.db.commit()
        await self.db.refresh(existing_tenant)
        
        return TenantEntity(
            tenant_id=existing_tenant.id,
            name=existing_tenant.name,
            domain=existing_tenant.domain,
            is_active=existing_tenant.is_active,
            created_at=existing_tenant.created_at,
            updated_at=existing_tenant.updated_at
        )
    
    async def delete(self, tenant_id: UUID) -> bool:
       
        tenant = await self.db.get(Tenant, tenant_id)
        if not tenant:
            return None
        self.db.delete(tenant)
        await self.db.commit()
        return True
    
    async def list_all_with_cursor(self, cursor: str = None, limit: int = 100, direction: PaginationDirection = PaginationDirection.FORWARD) -> CursorPagedResult[Any]:
        query = select(Tenant)
        
        if cursor:
          
            query = self.pagination_helper.build_cursor_query(query, Tenant, "id", cursor, limit, direction)
        else:
           
            if direction == PaginationDirection.FORWARD:
                query = query.order_by(Tenant.id)
            else:
                query = query.order_by(Tenant.id.desc())
            query = query.limit(limit + 1)
            
        result = await self.db.execute(query)
        tenants = result.scalars().all()
        
        paginated_result = self.pagination_helper.apply_cursor_pagination_to_query_result(
            tenants, "id", cursor, limit, direction
        )
        
        domain_tenants = []
        for tenant in paginated_result.items:
            domain_tenant = TenantEntity(
                name=tenant.name,
                domain=tenant.domain,
                is_active=tenant.is_active,
                tenant_id=tenant.id,
                created_at=tenant.created_at,
                updated_at=tenant.updated_at
            )
            domain_tenants.append(domain_tenant)
        
        return CursorPagedResult[Any](
            items=domain_tenants,
            next_cursor=paginated_result.next_cursor,
            previous_cursor=paginated_result.previous_cursor,
            has_next_page=paginated_result.has_next_page,
            has_previous_page=paginated_result.has_previous_page,
            page_size=paginated_result.page_size
        )
        
    async def list_all_with_pagination(self, page: int = 1, page_size: int = 10) -> Any:
        query = select(Tenant).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        tenants = result.scalars().all()
        return tenants