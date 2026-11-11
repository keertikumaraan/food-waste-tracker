from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# The database is a single file called waste_tracker.db, created automatically
DATABASE_URL = "sqlite:///./waste_tracker.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Every database table you define will inherit from this
Base = declarative_base()


def get_db():
    """Gives each API request its own database session, then closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()