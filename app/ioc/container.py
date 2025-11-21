
from dependency_injector import containers, providers
from fastapi_events.handlers.local import local_handler

from app.application.use_cases.user_use_cases import CreateUserUseCase, GetUserUseCase, LoginUseCase, UpdateUserUseCase, RefreshTokenUseCase
from app.application.use_cases.tenant_use_cases import (
    CreateTenantUseCase,
    GetTenantUseCase,
    UpdateTenantUseCase,
    ListTenantsUseCase,
    DeleteTenantUseCase
)
from app.application.handlers.user_event_handlers import (
    UserCreatedEventHandler,
    UserUpdatedEventHandler,
    UserLoggedInEventHandler,
)
from app.infrastructure.authentication.token_service import TokenService
from app.infrastructure.database.connection import get_db_session
from app.infrastructure.database.repositories.user_repository import UserRepositoryImpl
from app.infrastructure.database.repositories.tenant_repository import TenantRepository
from app.infrastructure.database.repositories.refresh_token_repository import RefreshTokenRepositoryImpl
from app.infrastructure.events.event_dispatcher import EventDispatcher
from app.infrastructure.external_services.resend_email_service import ResendEmailService
from app.infrastructure.external_services.rabbitmq_service import RabbitMQService
from app.application.extensions.pagination import CursorPaginationHelper
from app.shared.config import get_settings
from sqlalchemy.ext.asyncio import AsyncSession


class Container(containers.DeclarativeContainer):
   

    config = providers.Configuration()
    

    settings = providers.Singleton(get_settings)
    
    db_session = providers.Resource(get_db_session)
    
   
    user_repository = providers.Factory(
        UserRepositoryImpl,
        session=db_session,
    )
    
    refresh_token_repository = providers.Factory(
        RefreshTokenRepositoryImpl,
        session=db_session,
    )
    
    token_service = providers.Singleton(TokenService, settings=settings)

    
    login_use_case = providers.Factory(
        LoginUseCase, 
        user_repository=user_repository, 
        token_service=token_service,
        refresh_token_repository=refresh_token_repository
    )
    
    refresh_token_use_case = providers.Factory(
        RefreshTokenUseCase,
        user_repository=user_repository,
        token_service=token_service,
        refresh_token_repository=refresh_token_repository
    )
    
    
    cursor_pagination_helper = providers.Singleton(CursorPaginationHelper)
    
    tenant_repository = providers.Factory(
        TenantRepository,
        session=db_session,
        pagination_helper=cursor_pagination_helper,
    )
    
    
    event_dispatcher = providers.Singleton(EventDispatcher)
    
    email_service = providers.Singleton(
        ResendEmailService,
        settings=settings,
    )
    
    rabbitmq_service = providers.Singleton(
        RabbitMQService,
        settings=settings,
    )
    
    # Event Handlers
    user_created_event_handler = providers.Factory(
        UserCreatedEventHandler,
        email_service=email_service,
        message_queue_service=rabbitmq_service,
    )
    
    user_updated_event_handler = providers.Factory(
        UserUpdatedEventHandler,
        email_service=email_service,
        message_queue_service=rabbitmq_service,
    )
    
    user_logged_in_event_handler = providers.Factory(
        UserLoggedInEventHandler,
        message_queue_service=rabbitmq_service,
        email_service=email_service,
    )
    
    # Use Cases
    create_user_use_case = providers.Factory(
        CreateUserUseCase,
        user_repository=user_repository,
        event_dispatcher=event_dispatcher,
    )
    
    get_user_use_case = providers.Factory(
        GetUserUseCase,
        user_repository=user_repository,
    )
    
    update_user_use_case = providers.Factory(
        UpdateUserUseCase,
        user_repository=user_repository,
        event_dispatcher=event_dispatcher,
    )
    
    # Tenant Use Cases
    create_tenant_use_case = providers.Factory(
        CreateTenantUseCase,
        tenant_repository=tenant_repository,
    )
    
    get_tenant_use_case = providers.Factory(
        GetTenantUseCase,
        tenant_repository=tenant_repository,
    )
    
    update_tenant_use_case = providers.Factory(
        UpdateTenantUseCase,
        tenant_repository=tenant_repository,
    )
    
    list_tenants_use_case = providers.Factory(
        ListTenantsUseCase,
        tenant_repository=tenant_repository,
    )
    
    delete_tenant_use_case = providers.Factory(
        DeleteTenantUseCase,
        tenant_repository=tenant_repository,
    )


# Helper functions to create repositories with custom session
def create_user_repository_with_session(session: AsyncSession) -> UserRepositoryImpl:
    """Create user repository with a specific session."""
    return UserRepositoryImpl(session=session)


def create_refresh_token_repository_with_session(session: AsyncSession) -> RefreshTokenRepositoryImpl:
    """Create refresh token repository with a specific session."""
    return RefreshTokenRepositoryImpl(session=session)


def create_tenant_repository_with_session(container: Container, session: AsyncSession) -> TenantRepository:
    """Create tenant repository with a specific session."""
    pagination_helper = container.cursor_pagination_helper()
    return TenantRepository(
        session=session,
        pagination_helper=pagination_helper
    )


# Helper functions to create user use cases with custom session
def get_create_user_use_case_with_session(container: Container, session: AsyncSession) -> CreateUserUseCase:
    """Get create user use case with a specific session."""
    user_repo = create_user_repository_with_session(session)
    event_dispatcher = container.event_dispatcher()
    return CreateUserUseCase(user_repository=user_repo, event_dispatcher=event_dispatcher)


def get_get_user_use_case_with_session(container: Container, session: AsyncSession) -> GetUserUseCase:
    """Get get user use case with a specific session."""
    user_repo = create_user_repository_with_session(session)
    return GetUserUseCase(user_repository=user_repo)


def get_update_user_use_case_with_session(container: Container, session: AsyncSession) -> UpdateUserUseCase:
    """Get update user use case with a specific session."""
    user_repo = create_user_repository_with_session(session)
    event_dispatcher = container.event_dispatcher()
    return UpdateUserUseCase(user_repository=user_repo, event_dispatcher=event_dispatcher)


def get_login_use_case_with_session(container: Container, session: AsyncSession) -> LoginUseCase:
    """Get login use case with a specific session."""
    user_repo = create_user_repository_with_session(session)
    refresh_token_repo = create_refresh_token_repository_with_session(session)
    token_service = container.token_service()
    event_dispatcher = container.event_dispatcher()
    return LoginUseCase(
        user_repository=user_repo,
        token_service=token_service,
        refresh_token_repository=refresh_token_repo,
        event_dispatcher=event_dispatcher
    )


def get_refresh_token_use_case_with_session(container: Container, session: AsyncSession) -> RefreshTokenUseCase:
    """Get refresh token use case with a specific session."""
    user_repo = create_user_repository_with_session(session)
    refresh_token_repo = create_refresh_token_repository_with_session(session)
    token_service = container.token_service()
    return RefreshTokenUseCase(
        user_repository=user_repo,
        token_service=token_service,
        refresh_token_repository=refresh_token_repo
    )


# Helper functions to create tenant use cases with custom session
def get_create_tenant_use_case_with_session(container: Container, session: AsyncSession) -> CreateTenantUseCase:
    """Get create tenant use case with a specific session."""
    tenant_repo = create_tenant_repository_with_session(container, session)
    return CreateTenantUseCase(tenant_repository=tenant_repo)


def get_get_tenant_use_case_with_session(container: Container, session: AsyncSession) -> GetTenantUseCase:
    """Get get tenant use case with a specific session."""
    tenant_repo = create_tenant_repository_with_session(container, session)
    return GetTenantUseCase(tenant_repository=tenant_repo)


def get_update_tenant_use_case_with_session(container: Container, session: AsyncSession) -> UpdateTenantUseCase:
    """Get update tenant use case with a specific session."""
    tenant_repo = create_tenant_repository_with_session(container, session)
    return UpdateTenantUseCase(tenant_repository=tenant_repo)


def get_list_tenants_use_case_with_session(container: Container, session: AsyncSession) -> ListTenantsUseCase:
    """Get list tenants use case with a specific session."""
    tenant_repo = create_tenant_repository_with_session(container, session)
    return ListTenantsUseCase(tenant_repository=tenant_repo)


def get_delete_tenant_use_case_with_session(container: Container, session: AsyncSession) -> DeleteTenantUseCase:
    """Get delete tenant use case with a specific session."""
    tenant_repo = create_tenant_repository_with_session(container, session)
    return DeleteTenantUseCase(tenant_repository=tenant_repo)


def register_event_handlers(container: Container):
    
    @local_handler.register(event_name="user.created")
    async def handle_user_created(event):
        handler = container.user_created_event_handler()
        await handler.handle(event)
    
    @local_handler.register(event_name="user.updated")
    async def handle_user_updated(event):
        handler = container.user_updated_event_handler()
        await handler.handle(event)
    
    @local_handler.register(event_name="user.logged_in")
    async def handle_user_logged_in(event):
        handler = container.user_logged_in_event_handler()
        await handler.handle(event)
    
    @local_handler.register(event_name="*")
    async def handle_all_events(event) -> None:
        event_name, payload = event
        print(f"Event received: {event_name} - {payload}")
