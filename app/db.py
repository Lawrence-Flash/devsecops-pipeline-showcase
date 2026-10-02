"""SQLite access. Queries are parameterized; nothing here builds SQL from user input."""

import os
import sqlite3
from collections.abc import Iterator
from datetime import UTC, datetime

from app.models import Ticket

_SCHEMA = """
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


def connect(path: str) -> sqlite3.Connection:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    connection = sqlite3.connect(path, timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def init_db(path: str) -> None:
    connection = connect(path)
    try:
        connection.execute(_SCHEMA)
        connection.commit()
    finally:
        connection.close()


def insert_ticket(connection: sqlite3.Connection, title: str, body: str) -> Ticket:
    created_at = datetime.now(UTC).isoformat()
    cursor = connection.execute(
        "INSERT INTO tickets (title, body, created_at) VALUES (?, ?, ?)",
        (title, body, created_at),
    )
    connection.commit()
    return Ticket(id=int(cursor.lastrowid), title=title, body=body, created_at=created_at)


def list_tickets(connection: sqlite3.Connection) -> list[Ticket]:
    rows = connection.execute(
        "SELECT id, title, body, created_at FROM tickets ORDER BY id"
    ).fetchall()
    return [_row_to_ticket(row) for row in rows]


def get_ticket(connection: sqlite3.Connection, ticket_id: int) -> Ticket | None:
    row = connection.execute(
        "SELECT id, title, body, created_at FROM tickets WHERE id = ?",
        (ticket_id,),
    ).fetchone()
    if row is None:
        return None
    return _row_to_ticket(row)


def _row_to_ticket(row: sqlite3.Row) -> Ticket:
    return Ticket(
        id=row["id"],
        title=row["title"],
        body=row["body"],
        created_at=row["created_at"],
    )


def connection_scope(path: str) -> Iterator[sqlite3.Connection]:
    connection = connect(path)
    try:
        yield connection
    finally:
        connection.close()
