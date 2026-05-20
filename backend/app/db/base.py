import sqlite3
from contextlib import contextmanager
from typing import Iterator

from ..core.config import DATABASE_PATH
from ..utils.file_utils import ensure_parent_dir


def ensure_database_dir():
    ensure_parent_dir(DATABASE_PATH)


def get_connection() -> sqlite3.Connection:
    ensure_database_dir()
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def transaction() -> Iterator[sqlite3.Connection]:
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
