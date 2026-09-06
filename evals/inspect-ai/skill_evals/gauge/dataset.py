"""The Gauge dataset, and the contract its own case file must satisfy."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from inspect_ai.dataset import MemoryDataset

from skill_evals.gauge.expectations import validate_expectations
from skill_evals.shared.dataset import CaseError, build_dataset, load_cases

CASES_FILE = Path(__file__).parent / "dataset" / "cases.jsonl"
FIXTURES_DIR = Path(__file__).parent / "fixtures"

CATEGORIES = ("canonical", "boundary", "routing", "error", "adversarial", "regression")


def validate_case(case: dict[str, Any]) -> None:
    """Reject a case the suite cannot honestly grade, before any model is called."""
    if case["category"] not in CATEGORIES:
        raise CaseError(
            f"{case['id']}: category {case['category']!r} is not one of {CATEGORIES}"
        )
    if case["difficulty"] not in ("easy", "medium", "hard"):
        raise CaseError(f"{case['id']}: difficulty must be easy, medium or hard")

    fixture = case.get("fixture")
    if fixture is not None and not (FIXTURES_DIR / fixture).is_dir():
        raise CaseError(f"{case['id']}: no fixture directory {fixture!r}")

    try:
        validate_expectations(case["expect"])
    except ValueError as ex:
        raise CaseError(f"{case['id']}: {ex}") from ex

    # A case whose Gauge run is expected not to happen has no recipe to grade,
    # so a recipe-shaped expectation beside it would grade nothing.
    if case["expect"].get("gauge_invoked") is False:
        recipe_keys = sorted(set(case["expect"]) - {"gauge_invoked"})
        if recipe_keys:
            raise CaseError(
                f"{case['id']}: expects gauge not to be invoked, so there is no recipe "
                f"for {recipe_keys} to assert against"
            )


def gauge_dataset(
    *, smoke: bool = False, categories: Iterable[str] | None = None
) -> MemoryDataset:
    return build_dataset(
        CASES_FILE,
        FIXTURES_DIR,
        smoke=smoke,
        categories=categories,
        validate=validate_case,
    )


def all_cases() -> list[dict[str, Any]]:
    return load_cases(CASES_FILE)
