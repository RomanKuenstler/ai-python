from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

LOGGER = logging.getLogger(__name__)


def retry(operation: Callable[[], T], attempts: int = 10, delay_seconds: float = 1.0) -> T:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            LOGGER.warning("Retryable operation failed", extra={"attempt": attempt, "error": str(exc)})
            if attempt < attempts:
                time.sleep(delay_seconds * attempt)
    assert last_error is not None
    raise last_error
