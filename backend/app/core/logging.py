"""Strukturaviy JSON logging sozlamalari."""

import json
import logging
import sys
from datetime import UTC, datetime


class JsonFormatter(logging.Formatter):
    """Log yozuvlarini JSON ko'rinishida chiqaradi (kuzatuv/monitoring uchun qulay)."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        # Middleware qo'shgan qo'shimcha maydonlar (masalan, request_id)
        for key in ("request_id", "method", "path", "status_code", "duration_ms"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # uvicorn access loglarini o'z formatimizga o'tkazamiz
    for name in ("uvicorn", "uvicorn.error"):
        logging.getLogger(name).handlers = [handler]
    logging.getLogger("uvicorn.access").disabled = True


logger = logging.getLogger("nazartepa")
