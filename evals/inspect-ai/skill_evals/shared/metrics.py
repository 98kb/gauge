"""Metrics the standard set does not provide."""

from __future__ import annotations

import math

from inspect_ai.scorer import Metric, SampleScore, metric, value_to_float


@metric
def graded_mean() -> Metric:
    """Mean over only the samples a scorer actually graded.

    A scorer that does not apply to a sample has to return *something*, and a
    0.0 placeholder swept into a plain `mean()` reads as a bad score for
    correct behaviour — the mirror image of hiding a catastrophic failure in an
    average, and just as misleading. Samples whose score carries
    `metadata["graded"] is False` are excluded; if none were graded the metric
    is `nan` rather than a confident zero.
    """

    to_float = value_to_float()

    def compute(scores: list[SampleScore]) -> float:
        graded = [
            score
            for score in scores
            if (score.score.metadata or {}).get("graded", True) is not False
        ]
        if not graded:
            return float("nan")
        return sum(to_float(score.score.value) for score in graded) / len(graded)

    return compute


@metric
def graded_stderr() -> Metric:
    """Standard error over the same subset `graded_mean` averages.

    Pairing `graded_mean` with the stock `stderr` would report a spread
    computed over placeholder zeros the mean deliberately excluded — two
    numbers describing different populations, side by side.
    """

    to_float = value_to_float()

    def compute(scores: list[SampleScore]) -> float:
        values = [
            to_float(score.score.value)
            for score in scores
            if (score.score.metadata or {}).get("graded", True) is not False
        ]
        if len(values) < 2:
            return float("nan")
        average = sum(values) / len(values)
        variance = sum((value - average) ** 2 for value in values) / (len(values) - 1)
        return math.sqrt(variance / len(values))

    return compute


@metric
def total() -> Metric:
    """Sum rather than average.

    `evals/README.md` in this repository and section 10 of the eval spec both
    insist a catastrophic failure must not be averaged away. A count answers
    "how many samples did the forbidden thing", which a rate cannot.
    """

    to_float = value_to_float()

    def compute(scores: list[SampleScore]) -> float:
        return float(sum(to_float(score.score.value) for score in scores))

    return compute
