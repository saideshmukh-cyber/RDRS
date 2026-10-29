from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
import psutil
from loguru import logger


class ProcessMonitor:
    def __init__(self, repository, interval=5):
        self.repository=repository; self.interval=interval; self._stop=threading.Event(); self.thread=None

    def _snapshot(self):
        for proc in psutil.process_iter(["pid","name","cpu_percent","memory_percent","exe","ppid"]):
            try:
                info=proc.info
                io=proc.io_counters() if proc.is_running() else None
                self.repository.add_process_snapshot({
                    "pid": info.get("pid") or 0,
                    "name": info.get("name") or "",
                    "cpu_percent": float(info.get("cpu_percent") or 0),
                    "memory_percent": float(info.get("memory_percent") or 0),
                    "write_bytes": int(getattr(io, "write_bytes", 0) or 0),
                    "executable": info.get("exe") or "",
                    "parent_pid": info.get("ppid"),
                    "timestamp": datetime.now(timezone.utc),
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, OSError):
                continue

    def _run(self):
        while not self._stop.is_set():
            try: self._snapshot()
            except Exception: logger.exception("Process snapshot failed")
            self._stop.wait(self.interval)

    def start(self):
        self._stop.clear(); self.thread=threading.Thread(target=self._run, daemon=True, name="rdrs-process-monitor"); self.thread.start()

    def stop(self):
        self._stop.set()
        if self.thread: self.thread.join(timeout=3)
