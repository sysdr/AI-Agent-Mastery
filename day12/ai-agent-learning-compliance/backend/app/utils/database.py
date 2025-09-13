from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://user:password@localhost:5432/ai_agent_learning')

# Initialize engine lazily to avoid import-time connection issues
_engine = None
_AsyncSessionLocal = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(DATABASE_URL, echo=False)
    return _engine

def get_session_maker():
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        engine = get_engine()
        _AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return _AsyncSessionLocal

async def get_db_session():
    session_maker = get_session_maker()
    async with session_maker() as session:
        yield session
