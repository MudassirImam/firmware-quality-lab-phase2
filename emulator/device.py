"""Hybrid firmware-controller and DSP-pipeline emulator."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any
import logging
import time

from dsp.reference import moving_average
from dsp.specifications import validate_samples, validate_window_size
from emulator.fault_injection import FaultInjector, FaultType
from emulator.protocols import DeviceError, DeviceTimeoutError, InvalidResponseError
from emulator.state import DeviceState

logger = logging.getLogger('firmware_quality_lab.emulator')


class FirmwareDevice:
    """In-memory device emulator with deterministic behavior and fault injection."""

    DEFAULT_WINDOW_SIZE = 3
    FIRMWARE_VERSION = "1.0.0"
    API_VERSION = "1"

    def __init__(self, fault_injector: FaultInjector | None = None) -> None:
        self._faults = fault_injector or FaultInjector()
        self._state = DeviceState.READY
        self._window_size = self.DEFAULT_WINDOW_SIZE
        self._processed_batches = 0
        self._last_error: str | None = None
        self._injected_faults = 0
        self._failed_commands = 0
        self._total_processing_ms = 0.0

    def _apply_next_fault(self, command: str) -> None:
        fault = self._faults.consume()
        if fault is None:
            return
        self._injected_faults += 1
        self._failed_commands += 1
        logger.warning("injected fault", extra={"event": "fault_injected", "command": command, "error_type": fault.value, "state": self._state.value})
        if fault is FaultType.TIMEOUT:
            self._last_error = f"timeout during {command}"
            raise DeviceTimeoutError(self._last_error)
        if fault is FaultType.DEVICE_ERROR:
            self._state = DeviceState.ERROR
            self._last_error = f"injected device error during {command}"
            raise DeviceError(self._last_error)
        if fault is FaultType.INVALID_RESPONSE:
            self._last_error = f"invalid response during {command}"
            raise InvalidResponseError(self._last_error)

    def get_status(self) -> dict[str, Any]:
        self._apply_next_fault("get_status")
        return {
            "state": self._state.value,
            "firmware_version": self.FIRMWARE_VERSION,
            "api_version": self.API_VERSION,
            "window_size": self._window_size,
            "processed_batches": self._processed_batches,
            "last_error": self._last_error,
            "injected_faults": self._injected_faults,
            "failed_commands": self._failed_commands,
            "total_processing_ms": round(self._total_processing_ms, 3),
        }

    def configure(self, *, window_size: int) -> dict[str, Any]:
        self._apply_next_fault("configure")
        if self._state is DeviceState.ERROR:
            raise DeviceError("device is in error state; call reset() before configuring")
        validate_window_size(window_size)
        self._window_size = window_size
        self._last_error = None
        return {"ok": True, "window_size": self._window_size}

    def process_signal(self, samples: Sequence[float]) -> dict[str, Any]:
        self._apply_next_fault("process_signal")
        if self._state is DeviceState.ERROR:
            raise DeviceError("device is in error state; call reset() before processing")

        normalized = validate_samples(samples)
        self._state = DeviceState.PROCESSING
        started = time.perf_counter()
        try:
            output = moving_average(normalized, self._window_size)
            self._processed_batches += 1
            self._last_error = None
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            self._total_processing_ms += elapsed_ms
            logger.info("signal processed", extra={"event": "signal_processed", "command": "process_signal", "state": self._state.value, "duration_ms": round(elapsed_ms, 3), "batch_count": self._processed_batches})
            return {
                "ok": True,
                "algorithm": "causal_moving_average",
                "window_size": self._window_size,
                "input_count": len(normalized),
                "output": output,
            }
        finally:
            # Processing is synchronous in this phase. Return to READY even if
            # validation or the reference algorithm raises unexpectedly.
            if self._state is DeviceState.PROCESSING:
                self._state = DeviceState.READY

    def reset(self) -> dict[str, Any]:
        """Restore defaults and clear any armed fault; reset is recovery-safe."""
        self._faults.clear()
        self._state = DeviceState.READY
        self._window_size = self.DEFAULT_WINDOW_SIZE
        self._processed_batches = 0
        self._last_error = None
        self._injected_faults = 0
        self._failed_commands = 0
        self._total_processing_ms = 0.0
        logger.info("device reset", extra={"event": "device_reset", "command": "reset", "state": self._state.value})
        return {"ok": True, "state": self._state.value}
