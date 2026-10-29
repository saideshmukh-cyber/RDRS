from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta, timezone
from statistics import mean
from threading import Lock
from loguru import logger
from app.detectors.scoring import ScoringEngine


class DetectionEngine:
    def __init__(self, settings, repository, responder):
        self.settings=settings; self.repository=repository; self.responder=responder
        self.scorer=ScoringEngine(settings.scoring, settings.thresholds)
        self.window=deque(); self.lock=Lock(); self.last_score=None; self.last_level="Normal"; self.last_incident_id=None
        self.recent_events=deque(maxlen=5000)

    def handle_event(self, event):
        self.repository.add_event(event)
        with self.lock:
            self.window.append(event); self.recent_events.append(event); self._prune()
            result=self._evaluate()
            self.last_score=result.score; self.last_level=result.level
            if result.level in {"Warning","Critical"}:
                self.repository.add_alert(result.level, result.score,
                    f"Ransomware-like activity detected: {', '.join(result.signals)}", result.signals)
            if result.level == "Critical" and result.signals:
                self._create_incident(result)

    def _prune(self):
        cutoff=datetime.now(timezone.utc)-timedelta(seconds=self.settings.event_window_seconds)
        while self.window and self.window[0].timestamp < cutoff: self.window.popleft()

    def _evaluate(self):
        events=list(self.window)
        modified=sum(e.event_type in {"modified","created"} for e in events)
        renames=sum(e.event_type=="renamed" for e in events)
        ext=sum(e.extension_changed for e in events)
        ent=[e.entropy for e in events if e.entropy is not None and e.event_type in {"modified","created"}]
        avg=mean(ent) if ent else 0.0
        cpu_spike=False
        latest=self.repository.latest_processes(25)
        if latest:
            cpu_spike=max(p.cpu_percent for p in latest) >= self.settings.thresholds["cpu_percent"]
        return self.scorer.calculate(modified_count=modified, rename_count=renames,
            extension_change_count=ext, avg_entropy=avg, cpu_spike=cpu_spike, unknown_program=False)

    def _create_incident(self, result):
        # Debounce identical critical bursts: create only if no critical incident was made recently.
        if self.last_incident_id is not None:
            recent=list(self.repository.recent_incidents(1))
            if recent and recent[0].score >= 70:
                return
        affected=list(dict.fromkeys([e.path for e in self.window if e.event_type in {"modified","created","renamed"}]))
        process={}
        procs=self.repository.latest_processes(1)
        if procs:
            p=procs[0]; process={"pid":p.pid,"name":p.name,"cpu_percent":p.cpu_percent,"executable":p.executable}
        incident=self.responder.respond(result, affected, process)
        self.last_incident_id=incident.id

    def status(self):
        with self.lock:
            return {"score": self.last_score or 0, "level": self.last_level, "window_events": len(self.window),
                    "watch_paths": [str(p) for p in self.settings.watch_paths], "simulation_mode": self.settings.simulation_mode}
