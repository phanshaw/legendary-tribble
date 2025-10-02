from typing import Generator, Optional
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Database engine configuration
if settings.TESTING:
    # Use in-memory database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DATABASE_ECHO,
    )
elif settings.DATABASE_URL.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DATABASE_ECHO,
    )
else:
    # PostgreSQL configuration with connection pool
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,  # Number of connections to maintain
        max_overflow=20,  # Maximum overflow connections
        pool_recycle=3600,  # Recycle connections after 1 hour
    )

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
    expire_on_commit=False,
)


def init_db() -> None:
    """Initialize database, create tables if they don't exist"""
    try:
        # Import all models here to ensure they are registered
        from app.models import user, file  # noqa

        SQLModel.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)


class DatabaseManager:
    """Database manager for advanced operations"""

    @staticmethod
    def check_connection() -> bool:
        """Check if database connection is working"""
        try:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False

    @staticmethod
    def get_table_sizes() -> dict:
        """Get size of all tables (PostgreSQL only)"""
        if not settings.DATABASE_URL.startswith("postgresql"):
            return {}

        query = """
            SELECT
                schemaname AS schema,
                tablename AS table,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
            FROM pg_tables
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
        """

        with engine.connect() as conn:
            result = conn.execute(query)
            return {row[1]: row[2] for row in result}

    @staticmethod
    def vacuum_database():
        """Vacuum database (SQLite only)"""
        if settings.DATABASE_URL.startswith("sqlite"):
            with engine.connect() as conn:
                conn.execute("VACUUM")
                logger.info("Database vacuumed successfully")


# Database health check for monitoring
async def check_database_health() -> dict:
    """Check database health status"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")

        return {
            "status": "healthy",
            "database_url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "local",
            "pool_size": engine.pool.size() if hasattr(engine.pool, "size") else "N/A",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }