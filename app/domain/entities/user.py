from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID, uuid4


class User:
    def __init__(
        self,
        email: str,
        username: str,
        tenant_id: Optional[UUID] = None,
        password: Optional[str] = None,
        full_name: Optional[str] = None,
        is_active: bool = True,
        role: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        user_id: UUID = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = user_id or uuid4()
        self.email = email
        self.username = username
        self.tenant_id = tenant_id
        self.password = password
        self.full_name = full_name
        self.is_active = is_active
        self.role = role or "user"
        self.permissions = permissions or []
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    def activate(self) -> None:
        self.is_active = True
        self.updated_at = datetime.now(timezone.utc)

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)

    def update_profile(
        self,
        email: Optional[str] = None,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
    ) -> None:
        if email is not None:
            self.email = email
        if username is not None:
            self.username = username
        if full_name is not None:
            self.full_name = full_name
        self.updated_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email}, tenant_id={self.tenant_id})"
