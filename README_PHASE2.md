# Firmware Emulation & Quality Engineering Lab — Phase 2

Phase 2 extends Phase 1 with reusable test fixtures, layered testing, an independent DSP oracle,
versioned status-contract validation, structured JSON logs, and run artifacts.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[test]'
```

## Run all layers

```bash
pytest -v
python scripts/run_validation.py
```

## Run one layer

```bash
pytest tests/unit -v
pytest tests/contract -v
pytest tests/integration -v
pytest tests/system -v
```

## Parallel run

```bash
pytest -n auto -v
```

## Artifacts

The default artifact directory is `artifacts/phase2/`. It contains `emulator.jsonl` (structured
JSON logs) and `junit.xml` when using `scripts/run_validation.py`.

Override the directory with `FQL_ARTIFACTS_DIR=/some/path`.

## Test layers

- `tests/unit`: component behavior, fault injection, independent DSP oracle.
- `tests/contract`: public status shape, field types, supported API major version.
- `tests/integration`: workflows spanning configuration, processing, status and recovery.
- `tests/system`: end-to-end scenarios using indirect parametrization.

## Metrics

The status response includes `processed_batches`, `injected_faults`, `failed_commands`, and
`total_processing_ms`. These are in-memory emulator metrics, not production telemetry.

## Notes

- No real FPGA or firmware is connected.
- Contract checks validate the direct Python status mapping; Phase 3/4 can add HTTP/OpenAPI
  contracts when a service interface exists.
- The DSP oracle intentionally uses direct slices and sums, independently of the running-sum
  implementation in `dsp.reference`.
