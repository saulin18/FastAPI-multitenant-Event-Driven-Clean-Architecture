
from typing import AsyncGenerator
from fastapi import Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.infrastructure.database.connection import (
    get_db_session,
    get_tenant_db_session
)
from app.infrastructure.database.repositories.tenant_repository import TenantRepository
from app.ioc.container import Container

# Lazy container initialization to avoid import-time errors
_container = None

def _get_container():
    global _container
    if _container is None:
        _container = Container()
    return _container


async def get_tenant_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    
    try:
      
        x_tenant_id = request.headers.get("X-Tenant-ID")
        
        # Allow optional tenant_id - if not provided, use public schema
        if not x_tenant_id:
            async for session in get_db_session():
                yield session
            return
    except Exception as e:
        raise
    
    try:
        tenant_uuid = UUID(x_tenant_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tenant ID format"
        )
    
    async for public_session in get_db_session():
        try:
            container = _get_container()
            pagination_helper = container.cursor_pagination_helper()
            tenant_repo = TenantRepository(public_session, pagination_helper)
            tenant = await tenant_repo.get_by_id(tenant_uuid)
            
            if not tenant or not tenant.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Tenant not found or inactive"
                )
            
            tenant_schema = f"tenant_{tenant.tenant_id.hex[:16]}"
            
            async for session in get_tenant_session_with_translation(tenant_schema):
                yield session
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )
        finally:
            await public_session.close()


async def get_tenant_session_with_translation(
    tenant_schema: str
) -> AsyncGenerator[AsyncSession, None]:

    async for session in get_tenant_db_session(tenant_schema):
        yield session

