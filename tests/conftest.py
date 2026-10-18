"""Reusable fixtures shared by all test layers."""
from __future__ import annotations
import json
import logging
import os
from pathlib import Path
import pytest
from emulator import FaultInjector, FirmwareDevice
from observability.logging_config import JsonFormatter

@pytest.fixture(scope="session")
def diagnostics_dir():
    """Directory for test-run diagnostics; overridable with FQL_ARTIFACTS_DIR."""
    path = Path(os.getenv("FQL_ARTIFACTS_DIR", "artifacts/phase2"))
    path.mkdir(parents=True, exist_ok=True)
    return path

@pytest.fixture(scope="session", autouse=True)
def json_test_logging(diagnostics_dir):
    """Write structured emulator logs to an artifact file for each test run."""
    logger = logging.getLogger("firmware_quality_lab")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    log_path = diagnostics_dir / "emulator.jsonl"
    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    yield
    logger.removeHandler(handler)
    handler.close()

@pytest.fixture
def fault_injector():
    """A fresh fault injector per test to prevent cross-test contamination."""
    return FaultInjector()

@pytest.fixture
def def_fault_injector(fault_injector):
    """Backward-compatible fixture name retained from Phase 1 tests."""
    return fault_injector

@pytest.fixture
def device(fault_injector):
    """A fresh emulator per test; tests should not share mutable device state."""
    return FirmwareDevice(fault_injector=fault_injector)

@pytest.fixture
def device_scenario(request, fault_injector):
    """Indirect parametrization: scenario config is passed via request.param."""
    scenario = request.param
    device = FirmwareDevice(fault_injector=fault_injector)
    device.configure(window_size=scenario["window_size"])
    return device, scenario["window_size"], scenario["samples"]

@pytest.fixture
def failure_diagnostics(request, diagnostics_dir):
    """Utility fixture for writing a small JSON diagnostic record."""
    def write_diagnostic(payload):
        safe_name = request.node.name.replace("/", "_").replace("[", "_").replace("]", "_")
        path = diagnostics_dir / f"{safe_name}.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return path
    return write_diagnostic
