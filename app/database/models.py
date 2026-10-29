from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, Float, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


class FileEvent(Base):
    __tablename__ = "file_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(32), index=True)
    path: Mapped[str] = mapped_column(Text)
    old_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    extension: Mapped[str] = mapped_column(String(32), default="")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    entropy: Mapped[float | None] = mapped_column(Float, nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    extension_changed: Mapped[bool] = mapped_column(Boolean, default=False)


class ProcessSnapshot(Base):
    __tablename__ = "process_snapshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pid: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    cpu_percent: Mapped[float] = mapped_column(Float, default=0)
    memory_percent: Mapped[float] = mapped_column(Float, default=0)
    write_bytes: Mapped[int] = mapped_column(Integer, default=0)
    executable: Mapped[str] = mapped_column(Text, default="")
    parent_pid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    level: Mapped[str] = mapped_column(String(16), index=True)
    score: Mapped[int] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(Text)
    signals_json: Mapped[str] = mapped_column(Text, default="[]")


class Incident(Base):
    __tablename__ = "incidents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    level: Mapped[str] = mapped_column(String(16), index=True)
    score: Mapped[int] = mapped_column(Integer)
    summary: Mapped[str] = mapped_column(Text)
    affected_files_json: Mapped[str] = mapped_column(Text, default="[]")
    signals_json: Mapped[str] = mapped_column(Text, default="[]")
    suspect_process_json: Mapped[str] = mapped_column(Text, default="{}")
    quarantine_dir: Mapped[str | None] = mapped_column(Text, nullable=True)
