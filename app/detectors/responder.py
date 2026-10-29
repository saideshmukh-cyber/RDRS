from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path
from loguru import logger


class IncidentResponder:
    def __init__(self, settings, repository):
        self.settings=settings; self.repository=repository

    def respond(self, score_result, affected_files, process):
        quarantine=None
        if self.settings.quarantine_enabled:
            stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            quarantine=Path(self.settings.quarantine_dir)/f"incident_{stamp}"
            quarantine.mkdir(parents=True, exist_ok=True)
            copied=0
            for raw in affected_files[:self.settings.max_quarantine_files]:
                src=Path(raw)
                if not src.is_file(): continue
                try:
                    safe_name=src.name
                    dest=quarantine/safe_name
                    suffix=1
                    while dest.exists():
                        dest=quarantine/f"{src.stem}_{suffix}{src.suffix}"; suffix+=1
                    shutil.copy2(src, dest); copied+=1
                except OSError:
                    logger.exception("Could not copy evidence {}", src)
            logger.bind(channel="audit").warning("Incident response: copied {} evidence files to {}", copied, quarantine)
        else:
            logger.bind(channel="audit").warning("Incident response generated in log-only mode")
        summary=f"Critical score {score_result.score}; signals: {', '.join(score_result.signals)}"
        incident=self.repository.add_incident(score_result.score, score_result.level, summary,
                                              affected_files, score_result.signals, process, quarantine)
        logger.bind(channel="alerts").critical("CRITICAL incident #{}: {}", incident.id, summary)
        return incident
