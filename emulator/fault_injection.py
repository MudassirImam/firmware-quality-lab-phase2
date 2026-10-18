"""Deterministic, one-shot fault injection for emulator tests."""

from __future__ import annotations

from enum import Enum


class FaultType(str, Enum):
    TIMEOUT = "timeout"
    DEVICE_ERROR = "device_error"
    INVALID_RESPONSE = "invalid_response"


class FaultInjector:
    """Arms one fault that is consumed by the next eligible command.

    Faults are one-shot by design: a test can reproduce a failure without
    introducing randomness or contaminating later tests.
    """

    def __init__(self) -> None:
        self._next_fault: FaultType | None = None

    def arm(self, fault: FaultType) -> None:
        self._next_fault = FaultType(fault)

    def consume(self) -> FaultType | None:
        fault = self._next_fault
        self._next_fault = None
        return fault

    def clear(self) -> None:
        self._next_fault = None
