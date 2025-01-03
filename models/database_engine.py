import os

import psycopg2
from psycopg2 import sql
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError
from sqlmodel import Session, SQLModel, create_engine

from models.github_model import PullRequest

DB_USERNAME = os.getenv("DB_USERNAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = lambda: Session(engine)


def check_database_exists():
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USERNAME,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cur.fetchone()

        if not exists:
            print(f"Database {DB_NAME} does not exist. Creating it...")
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            print(f"Database {DB_NAME} created.")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error checking/creating database: {e}")
        raise


def check_table_exists():
    try:
        engine_url = (
            f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        engine = create_engine(engine_url)
        inspector = inspect(engine)

        if "pullrequest" not in inspector.get_table_names():
            print("Table 'pullrequest' does not exist. Creating the table...")
            SQLModel.metadata.create_all(bind=engine, tables=[PullRequest.__table__])
            print("Table 'pullrequest' created.")
        else:
            print("Table 'pullrequest' already exists.")
    except OperationalError as e:
        print(f"Error checking/creating table: {e}")
        raise


def init_db():
    check_database_exists()
    check_table_exists()


init_db()
