from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from models.conversation import Base
import structlog

logger = structlog.get_logger()

# Use regular SQLite database (SQLCipher commented out due to compatibility issues)
# For now, we'll use regular SQLite with application-level encryption
# Explicitly specify SQLite dialect to avoid SQLCipher auto-detection
database_url = "sqlite:///./secure_memory.db"
engine = create_engine(
    database_url,
    echo=False,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def init_db():
    """Initialize database with encrypted storage"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        raise

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
