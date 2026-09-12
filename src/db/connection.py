import logging
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import DATABASE_URI, SQLITE_DATABASE_URI, POSTGRES_DATABASE_URI

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

Base = declarative_base()

def get_engine(db_uri=None):
    """
    Creates and returns a SQLAlchemy engine.
    Attempts the configured URI (PostgreSQL or SQLite), with graceful fallback to SQLite.
    """
    target_uri = db_uri or DATABASE_URI
    try:
        engine = create_engine(target_uri, echo=False, pool_pre_ping=True)
        # Test connection
        with engine.connect() as conn:
            pass
        logger.info(f"Connected to database: {engine.url.render_as_string(hide_password=True)}")
        return engine
    except Exception as e:
        logger.warning(f"Could not connect to {target_uri} ({e}). Falling back to SQLite database.")
        engine = create_engine(SQLITE_DATABASE_URI, echo=False)
        return engine

@contextmanager
def get_session(engine=None):
    """Context manager for transactional database sessions."""
    eng = engine or get_engine()
    Session = sessionmaker(bind=eng)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Transaction rolled back due to error: {e}")
        raise
    finally:
        session.close()
