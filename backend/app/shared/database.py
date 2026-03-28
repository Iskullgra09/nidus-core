from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# 1. Create the Async Engine
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=(settings.ENVIRONMENT == "development"),
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Critical: Validates connection before using it
)

# 2. Create the Session Factory
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# 3. Modern SQLAlchemy 2.0 Declarative Base
class Base(DeclarativeBase):
    pass


# 4. Dependency Injection function for FastAPI
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to provide an AsyncSession to FastAPI routes.
    The 'async with' block handles opening and closing automatically.
    """
    async with async_session_maker() as session:
        yield session
        # No need for explicit close() here; 'async with' handles it
        # even if an exception occurs during the yield.
