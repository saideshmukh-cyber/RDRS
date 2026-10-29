from __future__ import annotations

import math
from collections import Counter
from pathlib import Path


def shannon_entropy(data: bytes) -> float:
    """Return Shannon entropy for bytes, in the range 0..8."""
    if not data:
        return 0.0
    counts = Counter(data)
    length = len(data)
    return -sum((n / length) * math.log2(n / length) for n in counts.values())


def file_entropy(path: str | Path, sample_bytes: int = 65536) -> float | None:
    """Calculate entropy from a bounded prefix; return None if unreadable/missing."""
    try:
        with Path(path).open("rb") as fh:
            return shannon_entropy(fh.read(sample_bytes))
    except (OSError, PermissionError):
        return None
