from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class FileEventData:
    event_type: str
    path: str
    timestamp: datetime = field(default_factory=utcnow)
    extension: str = ""
    old_path: str | None = None
    entropy: float | None = None
    size_bytes: int | None = None

    @property
    def extension_changed(self) -> bool:
        if not self.old_path:
            return False
        return Path(self.old_path).suffix.lower() != Path(self.path).suffix.lower()
