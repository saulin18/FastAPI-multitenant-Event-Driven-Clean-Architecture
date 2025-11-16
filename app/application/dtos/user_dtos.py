from uuid import UUID
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.domain.entities.user import User

class CreateUserRequest(BaseModel):
    email: str
    username: str
    password: str
    full_name: Optional[str] = None


class UpdateUserRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None
    
    def from_entity(self, user: User) -> "UserResponse":
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat() if user.updated_at else None
        )
    
    def to_entity(self) -> User:
        return User(
            id=self.id,
            email=self.email,
            username=self.username,
            full_name=self.full_name,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=datetime.fromisoformat(self.updated_at) if self.updated_at else None
        )
        
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    
class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
        