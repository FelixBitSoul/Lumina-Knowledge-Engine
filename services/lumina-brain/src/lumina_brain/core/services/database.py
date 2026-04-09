import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from lumina_brain.config.settings import settings

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
DATABASE_URL = f"postgresql://{settings.postgres.user}:{settings.postgres.password}@{settings.postgres.host}:{settings.postgres.port}/{settings.postgres.db}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    try:
        # Import all models here to ensure they are registered with Base
        from lumina_brain.core.models import document
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
