"""Unit tests for the hybrid firmware/DSP emulator."""

import math

import pytest

from emulator.device import FirmwareDevice
from emulator.fault_injection import FaultType
from emulator.protocols import DeviceError, DeviceTimeoutError, InvalidResponseError
from emulator.state import DeviceState


def test_device_starts_ready_with_documented_defaults(device):
    status = device.get_status()
    assert status["state"] == DeviceState.READY.value
    assert status["window_size"] == FirmwareDevice.DEFAULT_WINDOW_SIZE
    assert status["processed_batches"] == 0
    assert status["firmware_version"] == "1.0.0"
    assert status["api_version"] == "1"


@pytest.mark.parametrize("window_size", [1, 2, 3, 7, 31])
def test_configure_accepts_supported_window_sizes(device, window_size):
    result = device.configure(window_size=window_size)
    assert result == {"ok": True, "window_size": window_size}
    assert device.get_status()["window_size"] == window_size


@pytest.mark.parametrize("window_size", [0, -1, 32, 100])
def test_configure_rejects_out_of_range_window_sizes(device, window_size):
    with pytest.raises(ValueError, match="window_size must be between"):
        device.configure(window_size=window_size)


@pytest.mark.parametrize("window_size", [True, 2.5, "3", None])
def test_configure_rejects_non_integer_window_sizes(device, window_size):
    with pytest.raises(ValueError, match="window_size must be an integer"):
        device.configure(window_size=window_size)


def test_process_signal_uses_causal_moving_average(device):
    device.configure(window_size=3)
    result = device.process_signal([3, 6, 9, 12, 15])
    assert result["ok"] is True
    assert result["algorithm"] == "causal_moving_average"
    assert result["input_count"] == 5
    assert result["output"] == [3.0, 4.5, 6.0, 9.0, 12.0]
    assert device.get_status()["processed_batches"] == 1
    assert device.get_status()["state"] == DeviceState.READY.value


def test_window_size_one_passes_samples_through_unchanged(device):
    device.configure(window_size=1)
    assert device.process_signal([-2, 0, 2.5])["output"] == [-2.0, 0.0, 2.5]


@pytest.mark.parametrize(
    "samples",
    [[], "123", b"123", [1, "bad"], [True, 1], [float("nan")], [float("inf")], [float("-inf")]],
)
def test_process_signal_rejects_invalid_samples(device, samples):
    with pytest.raises(ValueError):
        device.process_signal(samples)


def test_timeout_fault_is_one_shot_and_does_not_corrupt_device(device, def_fault_injector):
    def_fault_injector.arm(FaultType.TIMEOUT)
    with pytest.raises(DeviceTimeoutError, match="timeout during get_status"):
        device.get_status()
    assert device.get_status()["state"] == DeviceState.READY.value


def test_device_error_requires_reset_before_processing(device, def_fault_injector):
    def_fault_injector.arm(FaultType.DEVICE_ERROR)
    with pytest.raises(DeviceError, match="injected device error"):
        device.process_signal([1, 2, 3])
    assert device.get_status()["state"] == DeviceState.ERROR.value
    with pytest.raises(DeviceError, match="call reset"):
        device.process_signal([1, 2, 3])
    assert device.reset() == {"ok": True, "state": "ready"}
    assert device.process_signal([1, 2])["output"] == [1.0, 1.5]


def test_invalid_response_fault_is_explicit_and_one_shot(device, def_fault_injector):
    def_fault_injector.arm(FaultType.INVALID_RESPONSE)
    with pytest.raises(InvalidResponseError, match="invalid response"):
        device.get_status()
    assert device.get_status()["state"] == DeviceState.READY.value


def test_reset_restores_defaults_and_counters(device):
    device.configure(window_size=5)
    device.process_signal([1, 2, 3, 4])
    result = device.reset()
    assert result == {"ok": True, "state": "ready"}
    status = device.get_status()
    assert status["window_size"] == FirmwareDevice.DEFAULT_WINDOW_SIZE
    assert status["processed_batches"] == 0
    assert status["last_error"] is None


def test_repeated_runs_are_deterministic(device):
    samples = [0, 1, 0, -1, 0]
    first = device.process_signal(samples)["output"]
    second = device.process_signal(samples)["output"]
    assert first == second


def test_numeric_outputs_are_finite(device):
    output = device.process_signal([1, 2, 3, 4])["output"]
    assert all(math.isfinite(value) for value in output)
