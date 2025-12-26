"""Shared context and state management for pipelines."""

from typing import Dict, Any, Optional
from threading import Lock


class PipelineContext:
    """Shared context for processors in a pipeline"""

    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._lock = Lock()

    def set(self, key: str, value: Any):
        """Set a context value"""
        with self._lock:
            self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a context value"""
        with self._lock:
            return self._data.get(key, default)

    def has(self, key: str) -> bool:
        """Check if key exists"""
        with self._lock:
            return key in self._data

    def delete(self, key: str):
        """Delete a key"""
        with self._lock:
            if key in self._data:
                del self._data[key]

    def clear(self):
        """Clear all context"""
        with self._lock:
            self._data.clear()
