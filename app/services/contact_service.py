import os
import sqlite3
from datetime import datetime

from flask import current_app


def get_database_path():
    """
    Returns the SQLite database path from Flask configuration.
    """
    database_path = current_app.config["DATABASE_PATH"]

    directory = os.path.dirname(database_path)

    if directory:
        os.makedirs(directory, exist_ok=True)

    return database_path


def get_connection():
    """
    Creates a connection to the SQLite database.
    """
    connection = sqlite3.connect(get_database_path())

    connection.row_factory = sqlite3.Row

    return connection


def init_database():
    """
    Creates the contacts table if it does not exist.
    """
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                message TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

        connection.commit()

    finally:
        connection.close()


def save_contact(
    name: str,
    email: str,
    phone: str = "",
    message: str = ""
):
    """
    Saves a customer contact into the database.
    """

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO contacts (
                name,
                email,
                phone,
                message,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name.strip(),
                email.strip(),
                phone.strip(),
                message.strip(),
                datetime.utcnow().isoformat(),
            ),
        )

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()