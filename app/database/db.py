from __future__ import annotations

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

class Base(DeclarativeBase):
    pass



def make_database(url: str):
    if url.startswith("sqlite:///"):
        raw = url.replace("sqlite:///", "", 1)
        if raw != ":memory:":
            Path(raw).parent.mkdir(parents=True, exist_ok=True)

    # Share one connection for in-memory SQLite databases.
    # This keeps test tables visible across repository sessions.
    if url in ("sqlite://", "sqlite:///:memory:"):
        engine = create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(
            url,
            connect_args={"check_same_thread": False} if url.startswith("sqlite") else {},
        )

    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    return engine, SessionLocal
