"""Contract tests for the public status mapping."""
import copy
import pytest
from contracts.status import validate_api_compatibility

def test_device_status_satisfies_contract(device):
    contract = validate_api_compatibility(device.get_status())
    assert contract.api_version == "1"
    assert contract.firmware_version == "1.0.0"
    assert contract.window_size == 3
    assert contract.processed_batches == 0

def test_contract_rejects_missing_field(device):
    payload = copy.deepcopy(device.get_status())
    payload.pop("window_size")
    with pytest.raises(ValueError, match="missing fields"):
        validate_api_compatibility(payload)

def test_contract_rejects_wrong_field_type(device):
    payload = copy.deepcopy(device.get_status())
    payload["processed_batches"] = "zero"
    with pytest.raises(ValueError, match="processed_batches"):
        validate_api_compatibility(payload)

@pytest.mark.parametrize("api_version", ["2", "3.0"])
def test_contract_rejects_unsupported_api_major(device, api_version):
    payload = copy.deepcopy(device.get_status())
    payload["api_version"] = api_version
    with pytest.raises(ValueError, match="unsupported API major"):
        validate_api_compatibility(payload)

pytestmark = pytest.mark.contract
