from pathlib import Path
from loguru import logger


def configure_logging(settings) -> None:
    log_dir = Path(settings.raw["logging"]["directory"])
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(lambda msg: print(msg, end=""), level=settings.log_level, enqueue=True)
    retention = settings.raw["logging"].get("retention", "14 days")
    rotation = settings.raw["logging"].get("rotation", "10 MB")
    logger.add(log_dir / "system.log", rotation=rotation, retention=retention, level="INFO", enqueue=True)
    logger.add(log_dir / "events.log", rotation=rotation, retention=retention, level="INFO", filter=lambda r: r["extra"].get("channel") == "events", enqueue=True)
    logger.add(log_dir / "alerts.log", rotation=rotation, retention=retention, level="WARNING", filter=lambda r: r["extra"].get("channel") == "alerts", enqueue=True)
    logger.add(log_dir / "audit.log", rotation=rotation, retention=retention, level="INFO", filter=lambda r: r["extra"].get("channel") == "audit", enqueue=True)
    logger.add(log_dir / "errors.log", rotation=rotation, retention=retention, level="ERROR", enqueue=True)
