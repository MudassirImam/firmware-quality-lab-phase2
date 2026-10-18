"""State definitions for the emulated firmware controller."""

from enum import Enum


class DeviceState(str, Enum):
    READY = "ready"
    PROCESSING = "processing"
    ERROR = "error"
