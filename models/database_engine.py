from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import inspect
from models.github_model import (
    PullRequest,
)
DATABASE_URL = ("postgresql://postgres@0.0.0.0/f_db")
engine = create_engine(DATABASE_URL)

SessionLocal = lambda: Session(engine)


def check_table_exists(table_name: str) -> bool:
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def init_db():
    if not check_table_exists("pullrequest"):
        print("Table 'pullrequest' does not exist. Creating the table...")
        SQLModel.metadata.create_all(
            bind=engine, tables=[PullRequest.__table__]
        )
    else:
        print("Table 'pullrequest' already exists.")


init_db()
# from sqlmodel import SQLModel, create_engine, Session
# from sqlalchemy import inspect
# from models.github_model import PullRequest
# from dotenv import load_dotenv
# import os

# load_dotenv()
#
# DB_USERNAME = os.getenv("DB_USERNAME")
# DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_HOST = os.getenv("DB_HOST")
# DB_NAME = os.getenv("DB_NAME")
#
# if not all([DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME]):
#     raise ValueError("Database configuration is incomplete. Check your .env file.")
#
# DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
#
# engine = create_engine(DATABASE_URL)
#
# SessionLocal = lambda: Session(engine)
#
#
# def check_table_exists(table_name: str) -> bool:
#     inspector = inspect(engine)
#     return table_name in inspector.get_table_names()
#
#
# def init_db():
#     if not check_table_exists("pullrequest"):
#         SQLModel.metadata.create_all(bind=engine, tables=[PullRequest.__table__])
#
#
# init_db()
