import os

# Disable testcontainers reaper to avoid port conflicts - must be set before importing testcontainers
os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"

from collections.abc import AsyncGenerator, Generator
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi import Request
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from app.infrastructure.database.dependencies import get_tenant_db
from app.infrastructure.database.models import Tenant, User
from app.main import create_app
from factory.alchemy import SQLAlchemyModelFactory
from sqlmodel import SQLModel
from app.infrastructure.database.connection import get_db_session


@pytest.fixture(scope="session")
def anyio_backend() -> Literal["asyncio"]:
    """Configure anyio backend for async tests."""
    return "asyncio"


@pytest.fixture(scope="session")
def postgres_container(
    anyio_backend: Literal["asyncio"],
) -> Generator[PostgresContainer, None, None]:
    """PostgreSQL container for testing using the same image as docker-compose."""
    with PostgresContainer("postgres:17", driver="asyncpg") as postgres:
        yield postgres


@pytest_asyncio.fixture(scope="function")
async def db_session(
    postgres_container: PostgresContainer,
) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session with fresh tables for each test."""
    db_url = postgres_container.get_connection_url()
    async_engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
    )

    async with async_engine.begin() as conn:
        try:
            await conn.run_sync(SQLModel.metadata.drop_all, checkfirst=True)
        except Exception:
            pass  # Tables might not exist, that's okay
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = async_sessionmaker(
        bind=async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    async with async_session() as session:
        yield session

    await async_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database override."""
    app = create_app()

    async def override_db(request: Request):
        """Override to use test database session."""
        yield db_session

    app.dependency_overrides[get_tenant_db] = override_db
    app.dependency_overrides[get_db_session] = override_db
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=True
    ) as client:
        yield client

    app.dependency_overrides.clear()


class AsyncBaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "flush"

    @classmethod
    async def create_async(cls, **kwargs):
        if cls._meta.sqlalchemy_session is None:
            raise ValueError(
                "sqlalchemy_session must be set before calling create_async()"
            )

        obj = cls(**kwargs)
        await cls._meta.sqlalchemy_session.commit()
        await cls._meta.sqlalchemy_session.refresh(obj)
        return obj


class UserFactory(AsyncBaseFactory):
    class Meta:
        model = User


class TenantFactory(AsyncBaseFactory):
    class Meta:
        model = Tenant


@pytest_asyncio.fixture
async def create_user(db_session: AsyncSession):
    """Create a test user using the factory."""
    import json

    UserFactory._meta.sqlalchemy_session = db_session
    user = await UserFactory.create_async(
        email="test@test.com",
        username="test",
        password="test",
        tenant_id=uuid4(),
        full_name="test",
        role="user",
        permissions=json.dumps(["read", "write"]),  # Convert list to JSON string
        is_active=True,
        id=uuid4(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    yield user


@pytest_asyncio.fixture
async def create_tenant(db_session: AsyncSession):
    """Create a test tenant using the factory."""
    TenantFactory._meta.sqlalchemy_session = db_session
    tenant = await TenantFactory.create_async(
        id=uuid4(),
        name="test",
        domain="test.com",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    yield tenant
