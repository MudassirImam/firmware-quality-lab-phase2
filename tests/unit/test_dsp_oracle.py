"""Independent DSP oracle: intentionally does not call dsp.reference."""
import math
import pytest
from emulator import FirmwareDevice

def straightforward_oracle(samples, window_size):
    """Simple slice-and-sum definition, deliberately unlike the running-sum implementation."""
    expected = []
    for index in range(len(samples)):
        start = max(0, index - window_size + 1)
        window = samples[start:index + 1]
        expected.append(sum(window) / len(window))
    return expected

@pytest.mark.parametrize(
    "samples,window",
    [
        ([1.0, 2.0, 3.0, 4.0], 1),
        ([1.0, 2.0, 3.0, 4.0], 3),
        ([0.0, -1.0, 1.0, 0.0], 2),
        ([10.0], 3),
        ([1.25, 2.5, -3.75, 4.0, 0.0], 4),
    ],
)
def test_device_dsp_matches_independent_oracle(device, samples, window):
    device.configure(window_size=window)
    actual = device.process_signal(samples)["output"]
    expected = straightforward_oracle(samples, window)
    assert len(actual) == len(expected)
    assert all(math.isclose(a, e, rel_tol=1e-12, abs_tol=1e-12) for a, e in zip(actual, expected))

pytestmark = pytest.mark.unit
