"""Utilities for safe stock-model dataset splitting."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class SplitResult:
    """Holds train/validation slices while preserving temporal order."""

    train: list[T]
    validation: list[T]


def time_series_train_validation_split(
    rows: Sequence[T],
    validation_ratio: float = 0.2,
) -> SplitResult:
    """Split rows into train/validation without shuffling future data into training.

    Bug fix: for stock prediction, data must remain ordered by time. A common bug is
    to use random splits, which leaks future observations into the train set.
    """

    if not 0 < validation_ratio < 1:
        raise ValueError("validation_ratio must be between 0 and 1")

    total_rows = len(rows)
    if total_rows < 2:
        raise ValueError("rows must contain at least two records")

    validation_size = max(1, int(total_rows * validation_ratio))
    train_end = total_rows - validation_size

    if train_end <= 0:
        raise ValueError("validation_ratio leaves no training data")

    return SplitResult(train=list(rows[:train_end]), validation=list(rows[train_end:]))
