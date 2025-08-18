from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings

# Log DB connection URL
# Log original DB connection URL
print(f"📦 Database engine created for: {settings.DATABASE_URL}")

# Normalize URL to ensure asyncpg driver is used
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://") and "+asyncpg" not in db_url:
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
print(f"🔧 Using async DB URL: {db_url}")
# Create async engine with normalized URL
engine = create_async_engine(
    db_url,
    echo=True,
    future=True
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Dependency to get DB session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Initialize database
async def init_db():
    from app.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
