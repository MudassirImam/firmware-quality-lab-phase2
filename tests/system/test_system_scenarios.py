"""End-to-end system scenarios with parameterized device configurations."""
import pytest

@pytest.mark.parametrize(
    "device_scenario",
    [
        {"window_size": 1, "samples": [4.0, -2.0, 8.0]},
        {"window_size": 3, "samples": [1.0, 2.0, 3.0, 4.0, 5.0]},
        {"window_size": 7, "samples": [0.5, 0.5, -0.5, 2.0]},
    ],
    indirect=True,
    ids=["passthrough", "default-window", "window-larger-than-input"],
)
def test_system_signal_processing_scenario(device_scenario):
    device, window_size, samples = device_scenario
    response = device.process_signal(samples)
    assert response["ok"] is True
    assert response["window_size"] == window_size
    assert response["input_count"] == len(samples)
    assert len(response["output"]) == len(samples)
    assert device.get_status()["processed_batches"] == 1

pytestmark = pytest.mark.system
