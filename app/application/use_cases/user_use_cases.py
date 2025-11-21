from typing import Optional
from uuid import UUID

from app.domain.entities.user import User
from app.domain.events.user_events import (
    UserCreatedEvent,
    UserLoggedInEvent,
    UserUpdatedEvent,
)
from app.domain.interfaces.user_repository import UserRepository
from app.domain.interfaces.event_dispatcher import EventDispatcher as IEventDispatcher
from app.domain.interfaces.refresh_token_repository import RefreshTokenRepository
from app.application.exceptions.user_exceptions import (
    InvalidUserDataError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.application.dtos.user_dtos import (
    LoginRequest,
    TokenResponse,
    UpdateUserRequest,
    RefreshTokenRequest,
)
from app.domain.interfaces.token_service import ITokenService


class CreateUserUseCase:
    def __init__(
        self, user_repository: UserRepository, event_dispatcher: IEventDispatcher
    ):
        self.user_repository = user_repository
        self.event_dispatcher = event_dispatcher

    async def execute(
        self,
        email: str,
        username: str,
        tenant_id: Optional[UUID] = None,
        full_name: Optional[str] = None,
        password: str = None,
    ) -> User:
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError(f"User with email {email} already exists")

        existing_user = await self.user_repository.get_by_username(username)
        if existing_user:
            raise UserAlreadyExistsError(
                f"User with username {username} already exists"
            )

        user = User(
            email=email,
            username=username,
            password=password,
            tenant_id=tenant_id,
            full_name=full_name,
        )

        created_user = await self.user_repository.create(user)

        event = UserCreatedEvent(
            user_id=created_user.id,
            email=created_user.email,
            username=created_user.username,
            tenant_id=created_user.tenant_id,
            full_name=created_user.full_name,
        )
        self.event_dispatcher.dispatch_user_created(event)

        return created_user


class GetUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: UUID) -> Optional[User]:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return user


class UpdateUserUseCase:
    def __init__(
        self, user_repository: UserRepository, event_dispatcher: IEventDispatcher
    ):
        self.user_repository = user_repository
        self.event_dispatcher = event_dispatcher

    async def execute(self, user_id: UUID, request: UpdateUserRequest) -> User:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        user.update_profile(
            email=request.email, username=request.username, full_name=request.full_name
        )
        updated_user = await self.user_repository.update(user)
        if not updated_user:
            raise UserNotFoundError(f"User with id {user_id} not found")

        event = UserUpdatedEvent(
            user_id=updated_user.id,
            tenant_id=updated_user.tenant_id,
            email=updated_user.email,
            username=updated_user.username,
            full_name=updated_user.full_name,
            is_active=updated_user.is_active,
        )

        self.event_dispatcher.dispatch_user_updated(event)

        return updated_user


class LoginUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        token_service: ITokenService,
        event_dispatcher: IEventDispatcher,
        refresh_token_repository: RefreshTokenRepository,
    ):
        self.user_repository = user_repository
        self.token_service = token_service
        self.event_dispatcher = event_dispatcher
        self.refresh_token_repository = refresh_token_repository

    async def execute(self, request: LoginRequest) -> TokenResponse:
        user = await self.user_repository.get_by_email(request.email)
        if not user:
            raise UserNotFoundError("User not found")
        if not user.password:
            raise InvalidUserDataError("User has no password set")
        if not self.token_service.verify_password(request.password, user.password):
            raise InvalidUserDataError("Invalid password")

        # Generate tokens
        access_token = self.token_service.generate_token(user)
        refresh_token = self.token_service.generate_refresh_token(user)

        # Store refresh token in database
        expires_at = self.token_service.get_refresh_token_expires_at()
        await self.refresh_token_repository.create(user.id, refresh_token, expires_at)

        event = UserLoggedInEvent(
            user_id=user.id,
            email=user.email,
            username=user.username,
            tenant_id=user.tenant_id,
            access_token=access_token,
            refresh_token=refresh_token,
        )

        self.event_dispatcher.dispatch_user_logged_in(event)

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)


class RefreshTokenUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        token_service: ITokenService,
        refresh_token_repository: RefreshTokenRepository,
    ):
        self.user_repository = user_repository
        self.token_service = token_service
        self.refresh_token_repository = refresh_token_repository

    async def execute(self, request: RefreshTokenRequest) -> TokenResponse:
        if not await self.refresh_token_repository.is_token_valid(
            request.refresh_token
        ):
            raise InvalidUserDataError("Invalid or expired refresh token")

        try:
            payload = self.token_service.decode_token(request.refresh_token)
        except ValueError as e:
            raise InvalidUserDataError(f"Invalid refresh token: {str(e)}")

        if payload.get("type") != "refresh":
            raise InvalidUserDataError("Token is not a refresh token")

        user_id = UUID(payload["sub"])
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")

        await self.refresh_token_repository.revoke_token(request.refresh_token)

        access_token = self.token_service.generate_token(user)
        new_refresh_token = self.token_service.generate_refresh_token(user)

        expires_at = self.token_service.get_refresh_token_expires_at()
        await self.refresh_token_repository.create(
            user.id, new_refresh_token, expires_at
        )

        return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)
