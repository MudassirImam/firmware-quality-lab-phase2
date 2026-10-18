"""Shared protocol types and exceptions used by the emulator."""

from __future__ import annotations

from typing import Any, Protocol, Sequence


class DeviceError(RuntimeError):
    """Base class for expected device/emulator failures."""


class DeviceTimeoutError(DeviceError):
    """Raised when a simulated device command times out."""


class InvalidResponseError(DeviceError):
    """Raised when a simulated device response violates its contract."""


class DSPProcessor(Protocol):
    def process(self, samples: Sequence[float], window_size: int) -> list[float]:
        """Process input samples and return one output per input sample."""


class DeviceInterface(Protocol):
    def get_status(self) -> dict[str, Any]: ...

    def configure(self, *, window_size: int) -> dict[str, Any]: ...

    def process_signal(self, samples: Sequence[float]) -> dict[str, Any]: ...

    def reset(self) -> dict[str, Any]: ...
