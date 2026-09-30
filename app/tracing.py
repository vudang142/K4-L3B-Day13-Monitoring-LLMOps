from __future__ import annotations

import os
from contextlib import contextmanager as _contextmanager
from typing import TYPE_CHECKING, Any, Iterator

try:
    from langfuse import Langfuse as _LangfuseClient, get_client, observe, propagate_attributes

    LANGFUSE_SDK_AVAILABLE = True
except ImportError:  # pragma: no cover - chỉ dùng khi chưa cài requirements
    LANGFUSE_SDK_AVAILABLE = False

    class _DummyLangfuseClient:
        """Dummy client used when Langfuse SDK is not available."""

        def update_current_span(self, **kwargs: Any) -> None:
            return None

        def update_current_generation(self, **kwargs: Any) -> None:
            return None

        def start_span(self, **kwargs: Any) -> _DummySpan:
            return _DummySpan()

    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func

        return decorator

    class _DummySpan:
        """Dummy span that does nothing."""

        def end(self, **kwargs: Any) -> None:
            pass

    _LangfuseClient = _DummyLangfuseClient  # type: ignore

    def get_client():
        return _DummyLangfuseClient()

    @_contextmanager
    def propagate_attributes(**kwargs: Any):
        yield


if TYPE_CHECKING:
    LangfuseClient = _LangfuseClient


def get_langfuse_client():
    return get_client()


def tracing_enabled() -> bool:
    return LANGFUSE_SDK_AVAILABLE and bool(
        os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")
    )
