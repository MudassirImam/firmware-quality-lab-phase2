"""Tests for the standalone DSP reference algorithm."""

import pytest

from dsp.reference import moving_average


def test_reference_algorithm_has_same_length_as_input():
    samples = [2, 4, 6, 8]
    assert len(moving_average(samples, 3)) == len(samples)


def test_reference_algorithm_uses_shortened_window_at_start():
    assert moving_average([2, 4, 6, 8], 3) == [2.0, 3.0, 4.0, 6.0]


@pytest.mark.parametrize("window_size", [0, 32, True, 1.5])
def test_reference_rejects_invalid_window_size(window_size):
    with pytest.raises(ValueError):
        moving_average([1, 2, 3], window_size)
