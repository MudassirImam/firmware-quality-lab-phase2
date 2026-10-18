"""Simple DSP implementation used as the emulator's reference algorithm."""

from __future__ import annotations

from collections.abc import Sequence

from dsp.specifications import validate_samples, validate_window_size


def moving_average(samples: Sequence[float], window_size: int) -> list[float]:
    """Return a causal moving average with a shortened window at the start.

    Each output uses the current sample and up to ``window_size - 1`` previous
    samples. Output length always equals input length. This definition makes
    edge behavior explicit and easy to verify independently in tests.
    """
    validate_window_size(window_size)
    normalized = validate_samples(list(samples) if not isinstance(samples, (list, tuple)) else samples)

    output: list[float] = []
    running_sum = 0.0
    history: list[float] = []
    for sample in normalized:
        history.append(sample)
        running_sum += sample
        if len(history) > window_size:
            running_sum -= history.pop(0)
        output.append(running_sum / len(history))
    return output
