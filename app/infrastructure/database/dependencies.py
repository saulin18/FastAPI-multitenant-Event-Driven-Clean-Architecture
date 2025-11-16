
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
    """
    Dependency for getting a database session with tenant schema switching.
    """
    import logging
    import sys
    logger = logging.getLogger(__name__)
    
    sys.stdout.flush()
    print("🔌 get_tenant_db: Starting...", flush=True)
    logger.info("🔌 get_tenant_db: Starting...")
    
    try:
        # Get tenant_id from header
        x_tenant_id = request.headers.get("X-Tenant-ID")
        print(f"   X-Tenant-ID header: {x_tenant_id}", flush=True)
        
        # Allow optional tenant_id - if not provided, use public schema
        if not x_tenant_id:
            print("   No tenant ID, using public schema", flush=True)
            async for session in get_db_session():
                print("   ✅ Session obtained", flush=True)
                yield session
            return
    except Exception as e:
        print(f"   ❌ Error in get_tenant_db (no tenant): {e}", flush=True)
        import traceback
        print(traceback.format_exc(), flush=True)
        raise
    
    try:
        tenant_uuid = UUID(x_tenant_id)
    except ValueError:
        print(f"   ❌ Invalid tenant ID format: {x_tenant_id}")
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
            
            # Use tenant domain as schema name (you can customize this)
            tenant_schema = f"tenant_{tenant.tenant_id.hex[:16]}"
            
            # Now get the tenant-scoped session with schema translation
            async for session in get_tenant_session_with_translation(tenant_schema):
                yield session
                
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Error in get_tenant_db: {str(e)}")
            import traceback
            print(traceback.format_exc())
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

