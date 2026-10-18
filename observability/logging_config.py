"""Structured JSON logging helpers (standard library only)."""
from __future__ import annotations
import json
import logging
from datetime import datetime, timezone
from typing import Any

class JsonFormatter(logging.Formatter):
    """Format log records as one JSON object per line."""
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("event", "command", "state", "duration_ms", "batch_count", "error_type"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, sort_keys=True)

def configure_json_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure a dedicated logger without modifying the root logger."""
    logger = logging.getLogger("firmware_quality_lab")
    logger.setLevel(level)
    logger.propagate = False
    if not any(getattr(handler, "_fql_json_handler", False) for handler in logger.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        handler._fql_json_handler = True  # type: ignore[attr-defined]
        logger.addHandler(handler)
    return logger
