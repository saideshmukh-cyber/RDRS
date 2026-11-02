
from __future__ import annotations

from app.core.config import load_settings
from app.core.logging import configure_logging
from app.database.db import Base, make_database
from app.database.repository import Repository
from app.detectors.responder import IncidentResponder
from app.detectors.engine import DetectionEngine
from app.detectors.file_monitor import FileMonitor
from app.detectors.process_monitor import ProcessMonitor
from app.reports.service import ReportService


class Runtime:
    def __init__(self):
        self.settings = load_settings()

        # Never allow production to start with a temporary SQLite database.
        if self.settings.env.lower() == "production":
            allowed_prefixes = (
                "postgresql://",
                "postgresql+psycopg://",
                "postgres://",
            )

            if not self.settings.database_url.startswith(allowed_prefixes):
                raise RuntimeError(
                    "Production requires PostgreSQL. "
                    "Configure RDRS_DATABASE_URL with the Neon connection URL."
                )

        configure_logging(self.settings)

        self.engine_db, self.SessionLocal = make_database(
            self.settings.database_url
        )

        # Create missing tables without deleting existing records.
        Base.metadata.create_all(self.engine_db)

        self.repo = Repository(self.SessionLocal)

        self.responder = IncidentResponder(
            self.settings,
            self.repo,
        )

        self.detector = DetectionEngine(
            self.settings,
            self.repo,
            self.responder,
        )

        self.file_monitor = FileMonitor(
            self.settings.watch_paths,
            self.detector.handle_event,
            self.settings.entropy_sample_bytes,
        )

        self.process_monitor = ProcessMonitor(
            self.repo,
            self.settings.process_snapshot_interval,
        )

        self.reports = ReportService(
            self.settings,
            self.repo,
        )

        self.started = False

    def start(self):
        if self.started:
            return

        self.file_monitor.start()
        self.process_monitor.start()
        self.started = True

    def stop(self):
        if not self.started:
            return

        self.file_monitor.stop()
        self.process_monitor.stop()
        self.started = False


_runtime = None


def get_runtime():
    global _runtime

    if _runtime is None:
        _runtime = Runtime()

    return _runtime
