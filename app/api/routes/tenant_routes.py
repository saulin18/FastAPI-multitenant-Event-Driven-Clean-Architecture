from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.dtos.tenant_dtos import (
    CreateTenantRequest,
    UpdateTenantRequest,
    TenantResponse,
    CursorPagedTenantRequest,
    CursorPagedTenantResponse,
    PaginationDirection
)
from app.infrastructure.database.connection import get_db_session
from app.infrastructure.database.dependencies import _get_container
from app.ioc.container import (
    get_create_tenant_use_case_with_session,
    get_get_tenant_use_case_with_session,
    get_update_tenant_use_case_with_session,
    get_list_tenants_use_case_with_session,
    get_delete_tenant_use_case_with_session,
)

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    request: CreateTenantRequest,
    db: AsyncSession = Depends(get_db_session),
):
  
    container = _get_container()
    create_tenant_use_case = get_create_tenant_use_case_with_session(container, db)
    try:
        tenant = await create_tenant_use_case.execute(request)
        return TenantResponse(
            id=tenant.tenant_id,
            name=tenant.name,
            domain=tenant.domain,
            is_active=tenant.is_active,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
  
    container = _get_container()
    get_tenant_use_case = get_get_tenant_use_case_with_session(container, db)
    try:
        tenant = await get_tenant_use_case.execute(tenant_id)
        return TenantResponse(
            id=tenant.tenant_id,
            name=tenant.name,
            domain=tenant.domain,
            is_active=tenant.is_active,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    request: UpdateTenantRequest,
    db: AsyncSession = Depends(get_db_session),
):
  
    container = _get_container()
    update_tenant_use_case = get_update_tenant_use_case_with_session(container, db)
    try:
        tenant = await update_tenant_use_case.execute(tenant_id, request)
        return TenantResponse(
            id=tenant.tenant_id,
            name=tenant.name,
            domain=tenant.domain,
            is_active=tenant.is_active,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/", response_model=CursorPagedTenantResponse)
async def list_tenants(
    cursor: Optional[str] = Query(None),
    page_size: int = Query(10, ge=1, le=100),
    direction: PaginationDirection = Query(PaginationDirection.FORWARD),
    db: AsyncSession = Depends(get_db_session),
):
 
    container = _get_container()
    list_tenants_use_case = get_list_tenants_use_case_with_session(container, db)
    request = CursorPagedTenantRequest(
        cursor=cursor,
        page_size=page_size,
        direction=direction
    )
    result = await list_tenants_use_case.execute(request)
    
    return CursorPagedTenantResponse(
        items=[TenantResponse(
            id=item.tenant_id,
            name=item.name,
            domain=item.domain,
            is_active=item.is_active,
            created_at=item.created_at,
            updated_at=item.updated_at
        ) for item in result.items],
        next_cursor=result.next_cursor,
        previous_cursor=result.previous_cursor,
        has_next_page=result.has_next_page,
        has_previous_page=result.has_previous_page,
        page_size=result.page_size
    )


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
  
    container = _get_container()
    delete_tenant_use_case = get_delete_tenant_use_case_with_session(container, db)
    try:
        await delete_tenant_use_case.execute(tenant_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

