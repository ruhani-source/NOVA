"""
Persistence for information users add to NOVA at runtime.

data/processed_insights.json stays the original NOVA knowledge base.
This module only stores the *new* information submitted through the API.

Storage:
- Primary: Supabase/PostgreSQL, configured through DATABASE_URL.
- Fallback: data/new_information_fallback.json, used when DATABASE_URL is
  not set or the database is unreachable. Nothing submitted is dropped.

get_information() returns database records AND fallback records together,
oldest first, so information saved during an outage is never hidden.
"""

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    MetaData,
    Table,
    Text,
    create_engine,
    func,
    insert,
    make_url,
    select,
    text,
)


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FALLBACK_FILE = BASE_DIR / "data" / "new_information_fallback.json"

metadata = MetaData()

information_table = Table(
    "nova_information",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("information", Text, nullable=False),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
)

_engine = None
_initialized = False
_warned_missing_url = False
_fallback_lock = threading.Lock()


def get_database_url() -> str | None:
    """
    Read DATABASE_URL and point it at the installed psycopg2 driver.
    SQLAlchemy 2.1 maps a bare postgresql:// to psycopg 3, which
    is not a project dependency.
    """

    url = (os.getenv("DATABASE_URL") or "").strip()

    if not url:
        return None

    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            url = "postgresql+psycopg2://" + url[len(prefix):]

    return url


def _get_engine():
    global _engine

    if _engine is None:
        url = get_database_url()

        if not url:
            return None

        connect_args = {}

        if url.startswith("postgresql"):
            connect_args["connect_timeout"] = 5

            # Never fall back to an unencrypted connection to Supabase.
            host = make_url(url).host or ""
            is_local = host in ("", "localhost", "127.0.0.1", "::1")

            if "sslmode=" not in url and not is_local:
                connect_args["sslmode"] = "require"

        _engine = create_engine(
            url,
            pool_pre_ping=True,
            connect_args=connect_args,
        )

    return _engine


def init_database() -> bool:
    """
    Create the nova_information table if needed.
    Returns True when the database is ready, False otherwise.
    """

    global _initialized, _warned_missing_url

    if _initialized:
        return True

    if get_database_url() is None:
        if not _warned_missing_url:
            print("⚠️ NOVA storage: DATABASE_URL not set, using local fallback file")
            _warned_missing_url = True
        return False

    try:
        engine = _get_engine()
        metadata.create_all(engine)

        # Block Supabase's public Data API; our direct connection
        # is the table owner and is not affected by RLS.
        if engine.dialect.name == "postgresql":
            with engine.begin() as connection:
                connection.execute(text(
                    "ALTER TABLE nova_information "
                    "ENABLE ROW LEVEL SECURITY"
                ))

        _initialized = True
        return True

    except Exception as error:
        _warn("could not initialize database", error)
        return False


def is_database_available() -> bool:
    return init_database()


def save_information(information: str) -> dict:
    """
    Persist one piece of new information.

    Returns the saved record:
    {"id", "information", "created_at", "storage"}
    where storage is "database" or "local".
    """

    if not isinstance(information, str) or not information.strip():
        raise ValueError("Information cannot be empty.")

    information = information.strip()

    if init_database():
        try:
            with _get_engine().begin() as connection:
                row = connection.execute(
                    insert(information_table)
                    .values(information=information)
                    .returning(
                        information_table.c.id,
                        information_table.c.created_at,
                    )
                ).one()

            return {
                "id": row.id,
                "information": information,
                "created_at": _to_iso(row.created_at),
                "storage": "database",
            }

        except Exception as error:
            _warn("database save failed, using local fallback", error)

    return _save_to_fallback(information)


def get_information_records() -> list[dict]:
    """All saved information with timestamps, oldest first."""

    records = []

    if init_database():
        try:
            with _get_engine().connect() as connection:
                rows = connection.execute(
                    select(information_table).order_by(
                        information_table.c.created_at,
                        information_table.c.id,
                    )
                ).all()

            records.extend(
                {
                    "id": row.id,
                    "information": row.information,
                    "created_at": _to_iso(row.created_at),
                    "storage": "database",
                }
                for row in rows
            )

        except Exception as error:
            _warn("database read failed, using local fallback only", error)

    records.extend(_load_fallback())
    records.sort(key=lambda record: record["created_at"])

    return records


def get_information() -> list[str]:
    """All saved information as plain strings, oldest first."""

    return [record["information"] for record in get_information_records()]


def _save_to_fallback(information: str) -> dict:
    with _fallback_lock:
        # Refuse to overwrite a file we cannot read: that would lose data.
        records = _load_fallback(strict=True)

        record = {
            "id": f"local-{len(records) + 1}",
            "information": information,
            "created_at": _to_iso(datetime.now(timezone.utc)),
            "storage": "local",
        }

        records.append(record)

        FALLBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
        temp_file = FALLBACK_FILE.with_suffix(".json.tmp")
        temp_file.write_text(
            json.dumps(records, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        temp_file.replace(FALLBACK_FILE)

    return record


def _load_fallback(strict: bool = False) -> list[dict]:
    if not FALLBACK_FILE.exists():
        return []

    try:
        records = json.loads(FALLBACK_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        if strict:
            raise RuntimeError(
                f"Local fallback file is unreadable: {FALLBACK_FILE}"
            ) from error
        _warn("could not read local fallback file", error)
        return []

    return records if isinstance(records, list) else []


def _to_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc).isoformat()


def _warn(message: str, error: Exception) -> None:
    # Only the error type is printed: driver messages can include
    # connection details that should not end up in logs.
    print(f"⚠️ NOVA storage: {message} ({type(error).__name__})")
