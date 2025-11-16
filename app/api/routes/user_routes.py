from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.application.dtos.user_dtos import (
    CreateUserRequest,
    UpdateUserRequest,
    UserResponse,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
)
from app.infrastructure.database.dependencies import get_tenant_db, _get_container
from app.application.exceptions.user_exceptions import (
    UserNotFoundError,
    InvalidUserDataError,
    UserAlreadyExistsError,
)
from app.infrastructure.authentication.token_service import TokenService
from app.ioc.container import (
    get_create_user_use_case_with_session,
    get_get_user_use_case_with_session,
    get_update_user_use_case_with_session,
    get_login_use_case_with_session,
    get_refresh_token_use_case_with_session,
)

router = APIRouter(prefix="/users", tags=["users"])

# Helper function to get token service
def _get_token_service() -> TokenService:
    container = _get_container()
    return container.token_service()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_tenant_db),
    token_service: TokenService = Depends(_get_token_service),
):
    # Create use case with the session from FastAPI Depends
    container = _get_container()
    create_user_use_case = get_create_user_use_case_with_session(container, db)
    tenant_id = None
    x_tenant_id = request_obj.headers.get("X-Tenant-ID")
    if x_tenant_id:
        try:
            tenant_id = UUID(x_tenant_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid tenant ID format",
            )

    hashed_password = token_service.get_password_hash(request.password)
    try:
        user = await create_user_use_case.execute(
            email=request.email,
            username=request.username,
            tenant_id=tenant_id,
            full_name=request.full_name,
            password=hashed_password,
        )
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat() if user.updated_at else None,
        )
    except (ValueError, UserAlreadyExistsError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_tenant_db),
):
    try:
        container = _get_container()
        get_user_use_case = get_get_user_use_case_with_session(container, db)
        user = await get_user_use_case.execute(user_id)
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat() if user.updated_at else None,
        )
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    request: UpdateUserRequest,
    db: AsyncSession = Depends(get_tenant_db),
):
    try:
        container = _get_container()
        update_user_use_case = get_update_user_use_case_with_session(container, db)
        user = await update_user_use_case.execute(user_id, request)
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat() if user.updated_at else None,
        )
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_tenant_db),
):
    container = _get_container()
    login_use_case = get_login_use_case_with_session(container, db)
    try:
        tokens = await login_use_case.execute(request)
        return tokens
    except (UserNotFoundError, InvalidUserDataError) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_tenant_db),
):
    container = _get_container()
    refresh_token_use_case = get_refresh_token_use_case_with_session(container, db)
    try:
        tokens = await refresh_token_use_case.execute(request)
        return tokens
    except (UserNotFoundError, InvalidUserDataError) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
