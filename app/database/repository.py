from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from sqlalchemy import desc, select
from .models import Alert, FileEvent, Incident, ProcessSnapshot


class Repository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def add_event(self, event):
        with self.session_factory() as s:
            row = FileEvent(event_type=event.event_type, path=event.path, old_path=event.old_path,
                            extension=event.extension, timestamp=event.timestamp, entropy=event.entropy,
                            size_bytes=event.size_bytes, extension_changed=event.extension_changed)
            s.add(row); s.commit(); s.refresh(row)
            return row

    def add_process_snapshot(self, data):
        with self.session_factory() as s:
            row = ProcessSnapshot(**data); s.add(row); s.commit(); return row

    def add_alert(self, level, score, message, signals):
        with self.session_factory() as s:
            row = Alert(timestamp=datetime.now(timezone.utc), level=level, score=score,
                        message=message, signals_json=json.dumps(signals)); s.add(row); s.commit(); s.refresh(row)
            return row

    def add_incident(self, score, level, summary, affected_files, signals, process, quarantine_dir=None):
        with self.session_factory() as s:
            row = Incident(created_at=datetime.now(timezone.utc), level=level, score=score, summary=summary,
                           affected_files_json=json.dumps(affected_files), signals_json=json.dumps(signals),
                           suspect_process_json=json.dumps(process or {}), quarantine_dir=str(quarantine_dir) if quarantine_dir else None)
            s.add(row); s.commit(); s.refresh(row); return row

    def recent_events(self, limit=100):
        with self.session_factory() as s:
            return list(s.scalars(select(FileEvent).order_by(desc(FileEvent.timestamp)).limit(limit)))

    def recent_alerts(self, limit=50):
        with self.session_factory() as s:
            return list(s.scalars(select(Alert).order_by(desc(Alert.timestamp)).limit(limit)))

    def recent_incidents(self, limit=50):
        with self.session_factory() as s:
            return list(s.scalars(select(Incident).order_by(desc(Incident.created_at)).limit(limit)))

    def latest_processes(self, limit=20):
        with self.session_factory() as s:
            return list(s.scalars(select(ProcessSnapshot).order_by(desc(ProcessSnapshot.timestamp)).limit(limit)))

    def events_since(self, seconds: int):
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=seconds)
        with self.session_factory() as s:
            return list(s.scalars(select(FileEvent).where(FileEvent.timestamp >= cutoff).order_by(FileEvent.timestamp)))

    def get_incident(self, incident_id: int):
        with self.session_factory() as s:
            return s.get(Incident, incident_id)
