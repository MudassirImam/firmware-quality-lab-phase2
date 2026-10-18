# Firmware Emulation & Quality Engineering Lab — Phase 1

A deterministic, in-memory emulator for a hybrid firmware controller and DSP pipeline. It does not require a physical FPGA or a running service.

## Phase 1 scope

- Device status, configuration, signal processing, and reset commands
- Explicit device states and version fields
- One-shot deterministic timeout, device-error, and invalid-response faults
- Causal moving-average DSP reference algorithm
- Pytest coverage for valid/invalid inputs, recovery, determinism, and algorithm behavior

## Requirements

- Python 3.10+
- Pytest 8+

The core implementation uses only the Python standard library. NumPy/SciPy are not needed yet; they can be introduced later for richer DSP experiments.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate       # macOS/Linux
# .venv\\Scripts\\activate    # Windows PowerShell
python -m pip install --upgrade pip
pip install -e '.[test]'
```

## Run tests

```bash
pytest -v
pytest tests/unit -v
pytest -n auto -v                 # optional parallel run; requires pytest-xdist
pytest --junitxml=artifacts/junit.xml
```

Create the artifact directory before the JUnit command:

```bash
mkdir -p artifacts
```

## Quick manual smoke test

```bash
python - <<'PY'
from emulator import FirmwareDevice

device = FirmwareDevice()
print(device.get_status())
print(device.configure(window_size=3))
print(device.process_signal([3, 6, 9, 12, 15]))
print(device.reset())
PY
```

Expected DSP output for the example input: `[3.0, 4.5, 6.0, 9.0, 12.0]`.

## API behavior

- `get_status()` returns state, firmware/API versions, configured window size, processed batch count, and last error.
- `configure(window_size=...)` accepts integer window sizes from 1 through 31.
- `process_signal(samples)` accepts a non-empty list or tuple of finite numbers and returns one output per input.
- `reset()` restores defaults and clears an armed fault.
- `FaultInjector.arm(FaultType.TIMEOUT | DEVICE_ERROR | INVALID_RESPONSE)` arms a one-shot fault consumed by the next eligible command. Reset intentionally bypasses faults so recovery is possible.

The moving average is causal: each output averages the current sample and up to `window_size - 1` previous samples. At the beginning of a signal, it uses the available samples only.

## Known scope limits

This is a software emulator, not a real FPGA/firmware integration. Timing is synchronous and faults are simulated. The next phases can add richer protocol contracts, a FastAPI adapter, Docker, GitLab CI/CD, Allure reports, and performance measurements.
# firmware-quality-lab-phase2
