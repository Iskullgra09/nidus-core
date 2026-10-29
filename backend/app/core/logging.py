"""Structured JSON logging for Nidus Core (stdlib only — no extra deps)."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Optional

from app.core.config import settings
from app.core.request_context import RequestContext


class JsonFormatter(logging.Formatter):
    """Emits one JSON object per log line for log aggregators."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "environment": settings.ENVIRONMENT,
        }

        request_id = RequestContext.get_request_id()
        if request_id:
            payload["request_id"] = request_id

        client_ip = RequestContext.get_client_ip()
        if client_ip:
            payload["client_ip"] = client_ip

        actor = RequestContext.get_actor()
        if actor:
            payload["user_id"] = str(actor)

        org_id = RequestContext.get_organization()
        if org_id:
            payload["organization_id"] = str(org_id)

        for key in ("method", "path", "status_code", "latency_ms"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def configure_logging(level: Optional[str] = None) -> None:
    """Idempotent root logger setup. Safe to call from app startup and tests."""
    root = logging.getLogger()
    if getattr(root, "_nidus_configured", False):
        return

    log_level = getattr(logging, (level or "INFO").upper(), logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)
    setattr(root, "_nidus_configured", True)

    # Quiet noisy libs; keep app loggers at configured level.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING if settings.ENVIRONMENT != "development" else logging.INFO)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
