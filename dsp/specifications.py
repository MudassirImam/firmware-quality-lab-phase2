"""Executable constraints for the emulated DSP interface."""

MIN_WINDOW_SIZE = 1
MAX_WINDOW_SIZE = 31
MAX_SAMPLE_COUNT = 100_000
ABSOLUTE_TOLERANCE = 1e-12


def validate_window_size(window_size: int) -> None:
    if isinstance(window_size, bool) or not isinstance(window_size, int):
        raise ValueError("window_size must be an integer")
    if not MIN_WINDOW_SIZE <= window_size <= MAX_WINDOW_SIZE:
        raise ValueError(
            f"window_size must be between {MIN_WINDOW_SIZE} and {MAX_WINDOW_SIZE}"
        )


def validate_samples(samples: object) -> list[float]:
    """Validate and normalize a non-empty sequence of finite numeric samples."""
    if isinstance(samples, (str, bytes)) or not isinstance(samples, (list, tuple)):
        raise ValueError("samples must be a list or tuple of numbers")
    if not samples:
        raise ValueError("samples must not be empty")
    if len(samples) > MAX_SAMPLE_COUNT:
        raise ValueError(f"samples cannot exceed {MAX_SAMPLE_COUNT} values")

    normalized: list[float] = []
    for index, value in enumerate(samples):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"samples[{index}] must be numeric")
        converted = float(value)
        if converted != converted or converted in (float("inf"), float("-inf")):
            raise ValueError(f"samples[{index}] must be finite")
        normalized.append(converted)
    return normalized
