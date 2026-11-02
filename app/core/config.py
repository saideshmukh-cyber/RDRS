
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class Settings:
    env: str
    host: str
    port: int
    log_level: str
    database_url: str
    config_path: Path
    allow_origins: list[str]
    simulation_mode: bool
    raw: dict[str, Any] = field(repr=False)

    @property
    def watch_paths(self) -> list[Path]:
        return [Path(p) for p in self.raw["monitoring"]["watch_paths"]]

    @property
    def event_window_seconds(self) -> int:
        return int(self.raw["monitoring"]["event_window_seconds"])

    @property
    def entropy_sample_bytes(self) -> int:
        return int(self.raw["monitoring"]["entropy_sample_bytes"])

    @property
    def process_snapshot_interval(self) -> int:
        return int(self.raw["monitoring"]["process_snapshot_interval_seconds"])

    @property
    def thresholds(self) -> dict[str, float]:
        return self.raw["thresholds"]

    @property
    def scoring(self) -> dict[str, float]:
        return self.raw["scoring"]

    @property
    def quarantine_enabled(self) -> bool:
        return _bool_env(
            "RDRS_QUARANTINE_ENABLED",
            bool(self.raw["response"]["quarantine_enabled"]),
        )

    @property
    def quarantine_dir(self) -> Path:
        return Path(self.raw["response"]["quarantine_dir"])

    @property
    def max_quarantine_files(self) -> int:
        return int(self.raw["response"]["max_quarantine_files_per_incident"])

    @property
    def reports_dir(self) -> Path:
        return Path(self.raw["reports"]["directory"])


def load_settings(config_path: str | Path = "config.yaml") -> Settings:
    load_dotenv()
    path = Path(os.getenv("RDRS_CONFIG_PATH", str(config_path)))

    with path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    simulation = _bool_env(
        "RDRS_SIMULATION_MODE",
        bool(raw.get("app", {}).get("simulation_mode", True)),
    )
    raw.setdefault("app", {})["simulation_mode"] = simulation

    return Settings(
        env=os.getenv("RDRS_ENV", "development"),
        host=os.getenv("RDRS_HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", os.getenv("RDRS_PORT", "8000"))),
        log_level=os.getenv("RDRS_LOG_LEVEL", "INFO"),
        database_url=os.getenv("RDRS_DATABASE_URL", "sqlite:///./data/rdrs.db"),
        config_path=path,
        allow_origins=[
            x.strip()
            for x in os.getenv(
                "RDRS_ALLOW_ORIGINS",
                "http://127.0.0.1:8000,http://localhost:8000",
            ).split(",")
            if x.strip()
        ],
        simulation_mode=simulation,
        raw=raw,
    )
