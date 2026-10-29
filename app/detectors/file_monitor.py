from __future__ import annotations

import threading
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from loguru import logger
from app.core.models import FileEventData
from app.core.entropy import file_entropy


class RDRSEventHandler(FileSystemEventHandler):
    def __init__(self, callback, sample_bytes):
        self.callback=callback; self.sample_bytes=sample_bytes

    def _emit(self, event_type, path, old_path=None):
        if not path and not old_path: return
        p=Path(path or old_path)
        if p.is_dir(): return
        entropy=None; size=None
        if p.exists() and p.is_file() and event_type != "deleted":
            try: size=p.stat().st_size
            except OSError: size=None
            entropy=file_entropy(p, self.sample_bytes)
        data=FileEventData(event_type=event_type, path=str(p), old_path=old_path,
                           extension=p.suffix.lower(), entropy=entropy, size_bytes=size)
        self.callback(data)

    def on_created(self, event): self._emit("created", event.src_path)
    def on_modified(self, event): self._emit("modified", event.src_path)
    def on_deleted(self, event): self._emit("deleted", event.src_path)
    def on_moved(self, event): self._emit("renamed", event.dest_path, event.src_path)


class FileMonitor:
    def __init__(self, paths, callback, sample_bytes):
        self.paths=[Path(p) for p in paths]; self.callback=callback; self.sample_bytes=sample_bytes
        self.observer=Observer(); self._started=False

    def start(self):
        for path in self.paths:
            path.mkdir(parents=True, exist_ok=True)
            self.observer.schedule(RDRSEventHandler(self.callback, self.sample_bytes), str(path), recursive=True)
        self.observer.start(); self._started=True
        logger.info("File monitor started for {}", [str(p) for p in self.paths])

    def stop(self):
        if self._started:
            self.observer.stop(); self.observer.join(timeout=5); self._started=False
