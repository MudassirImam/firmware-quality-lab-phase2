"""Integration tests spanning configure -> process -> status -> reset."""
import pytest
def test_configure_process_and_reset_workflow(device):
    configured = device.configure(window_size=2)
    assert configured == {"ok": True, "window_size": 2}

    result = device.process_signal([2.0, 4.0, 8.0])
    assert result["ok"] is True
    assert result["output"] == [2.0, 3.0, 6.0]

    status = device.get_status()
    assert status["processed_batches"] == 1
    assert status["window_size"] == 2

    device.reset()
    reset_status = device.get_status()
    assert reset_status["window_size"] == device.DEFAULT_WINDOW_SIZE
    assert reset_status["processed_batches"] == 0
    assert reset_status["state"] == "ready"

def test_device_error_recovery_workflow(device, fault_injector):
    from emulator import FaultType
    from emulator.protocols import DeviceError
    import pytest

    fault_injector.arm(FaultType.DEVICE_ERROR)
    with pytest.raises(DeviceError):
        device.process_signal([1, 2, 3])
    with pytest.raises(DeviceError, match="reset"):
        device.process_signal([1, 2, 3])
    device.reset()
    assert device.process_signal([1, 2, 3])["ok"] is True

pytestmark = pytest.mark.integration
