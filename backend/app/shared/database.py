from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# 1. Create the Async Engine
# echo=True prints SQL queries to the console in development mode
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=(settings.ENVIRONMENT == "development"),
    future=True,
    pool_size=5,
    max_overflow=10,
)

# 2. Create the Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 3. Base class for all SQLAlchemy Models
Base = declarative_base()


# 4. Dependency Injection function for FastAPI routes
async def get_db_session():
    """
    Yields a database session to a FastAPI route, and safely closes it
    after the request finishes, even if an exception occurs.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
