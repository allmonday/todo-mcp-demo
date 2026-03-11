"""Database configuration for the todo application."""

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

# Create async engine with SQLite
engine = create_async_engine("sqlite+aiosqlite:///todo.db", echo=False)

# Create async session factory
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    """Get an async database session."""
    async with async_session() as session:
        yield session


async def init_db() -> None:
    """Initialize database tables."""
    from sqlmodel import SQLModel

    from todo.models import BaseEntity

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
