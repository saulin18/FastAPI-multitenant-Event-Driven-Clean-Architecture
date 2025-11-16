
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel

from app.shared.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_tenant_db_session(
    tenant_schema: str
) -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            # Apply schema translation at the connection level
            await session.connection(
                execution_options={
                    "schema_translate_map": {"public": tenant_schema},
                }
            )
            yield session
        finally:
            await session.close()


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db_connections():
    await engine.dispose()

