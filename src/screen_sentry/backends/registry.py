from __future__ import annotations

from screen_sentry.backends.base import Backend
from screen_sentry.backends.custom import CustomBackend
from screen_sentry.backends.openai_compat import OpenAICompatBackend

_REGISTRY: dict[str, type[Backend]] = {
    "openai_compat": OpenAICompatBackend,
    "custom": CustomBackend,
}


def get_backend_class(backend_type: str) -> type[Backend]:
    try:
        return _REGISTRY[backend_type]
    except KeyError:
        known = ", ".join(sorted(_REGISTRY))
        raise ValueError(
            f"unknown provider type '{backend_type}' (expected one of: {known})"
        ) from None
