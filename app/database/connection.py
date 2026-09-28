"""
SQLite Connection Manager.
Manages database connection lifecycle, context managers, and foreign key enforcement.
"""

import sqlite3
from pathlib import Path
from typing import Optional, Generator
from contextlib import contextmanager
from app.config.settings import DATABASE_PATH, ensure_directories
from app.utils.logger import logger


class DatabaseConnection:
    """Provides SQLite database connection management."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DATABASE_PATH

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager yielding an active SQLite connection."""
        ensure_directories()
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            # Enforce Foreign Keys
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error on connection: {e}")
            raise e
        finally:
            conn.close()
