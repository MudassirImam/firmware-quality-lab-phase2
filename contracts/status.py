"""Status response contract and backward-compatibility checks."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

REQUIRED_STATUS_FIELDS = {
    "state", "firmware_version", "api_version",
    "window_size", "processed_batches", "last_error",
}
SUPPORTED_API_MAJOR = "1"

@dataclass(frozen=True)
class StatusContract:
    state: str
    firmware_version: str
    api_version: str
    window_size: int
    processed_batches: int
    last_error: str | None

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "StatusContract":
        missing = REQUIRED_STATUS_FIELDS - payload.keys()
        if missing:
            raise ValueError(f"status response missing fields: {sorted(missing)}")
        if not isinstance(payload["state"], str):
            raise ValueError("state must be a string")
        if not isinstance(payload["firmware_version"], str):
            raise ValueError("firmware_version must be a string")
        if not isinstance(payload["api_version"], str):
            raise ValueError("api_version must be a string")
        if not isinstance(payload["window_size"], int) or isinstance(payload["window_size"], bool):
            raise ValueError("window_size must be an integer")
        if not isinstance(payload["processed_batches"], int) or isinstance(payload["processed_batches"], bool):
            raise ValueError("processed_batches must be an integer")
        if payload["last_error"] is not None and not isinstance(payload["last_error"], str):
            raise ValueError("last_error must be a string or null")
        return cls(**{key: payload[key] for key in REQUIRED_STATUS_FIELDS})

def validate_api_compatibility(payload: dict[str, Any]) -> StatusContract:
    """Validate shape and reject unsupported API major versions."""
    contract = StatusContract.from_mapping(payload)
    major = contract.api_version.split(".", 1)[0]
    if major != SUPPORTED_API_MAJOR:
        raise ValueError(
            f"unsupported API major version {major!r}; supported major is {SUPPORTED_API_MAJOR!r}"
        )
    return contract
