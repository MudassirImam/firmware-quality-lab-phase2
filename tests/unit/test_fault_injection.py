"""Fault injector unit tests."""
import pytest
from emulator import FaultInjector, FaultType, FirmwareDevice
from emulator.protocols import DeviceError, DeviceTimeoutError, InvalidResponseError

@pytest.mark.parametrize(
    "fault,exception",
    [
        (FaultType.TIMEOUT, DeviceTimeoutError),
        (FaultType.INVALID_RESPONSE, InvalidResponseError),
        (FaultType.DEVICE_ERROR, DeviceError),
    ],
)
def test_each_fault_is_consumed_once(fault, exception):
    injector = FaultInjector()
    device = FirmwareDevice(fault_injector=injector)
    injector.arm(fault)
    with pytest.raises(exception):
        device.get_status()
    # Device errors affect state; reset before checking recovery for that fault type.
    if fault is FaultType.DEVICE_ERROR:
        device.reset()
    assert device.get_status()["state"] == "ready"

pytestmark = pytest.mark.unit
