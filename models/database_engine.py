from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "postgresql://postgres@localhost/fast_db"
engine = create_engine(DATABASE_URL)

# Define SessionLocal as a callable for session creation
SessionLocal = lambda: Session(engine)


def init_db():
    """Initialize the database and create tables."""
    SQLModel.metadata.create_all(bind=engine)
