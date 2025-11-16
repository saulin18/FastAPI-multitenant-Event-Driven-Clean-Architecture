from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
import sqlalchemy as sa

from app.domain.entities.tenant import Tenant as TenantEntity
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}
    
    id: UUID = Field(default=uuid4(), primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    username: str = Field(unique=True, index=True, nullable=False)
    password: Optional[str] = Field(default=None, nullable=True)
    tenant_id: Optional[UUID] = Field(default=None, nullable=True, index=True)
    full_name: Optional[str] = Field(default=None, nullable=True)
    role: Optional[str] = Field(default="user", nullable=False)
    permissions: Optional[str] = Field(default="[]", nullable=True) 
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False)
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True)
    )

class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"
    __table_args__ = {"schema": "public"}
    
    id: UUID = Field(default=uuid4(), primary_key=True)
    user_id: UUID = Field(foreign_key="public.users.id", index=True, nullable=False)
    token: str = Field(unique=True, index=True, nullable=False)
    expires_at: datetime = Field(
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False)
    )
    is_revoked: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False)
    )
    revoked_at: Optional[datetime] = Field(
        default=None,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True)
    )


class Tenant(SQLModel, table=True):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "public"}
    id: UUID = Field(default=uuid4(), primary_key=True)
    name: str = Field(index=True)
    domain: str = Field(unique=True, index=True, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False)
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True)
    )

    def from_entity(self, entity: TenantEntity) -> "Tenant":
        return Tenant(
            id=entity.tenant_id,
            name=entity.name,
            domain=entity.domain,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )