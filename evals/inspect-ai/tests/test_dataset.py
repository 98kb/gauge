"""The case file's own contract.

These run without a model or a sandbox, so a malformed case is caught before
anybody pays for a trajectory.
"""

from __future__ import annotations

import pytest

from skill_evals.gauge.dataset import CATEGORIES, all_cases, gauge_dataset, validate_case
from skill_evals.gauge.expectations import ExpectationError, validate_expectations
from skill_evals.shared.dataset import CaseError


def test_suite_size_is_a_regression_suite_not_a_corpus() -> None:
    assert 10 <= len(all_cases()) <= 15


def test_every_taxonomy_bucket_is_populated() -> None:
    """`regression` is deliberately allowed to be empty until a real bug lands."""
    present = {case["category"] for case in all_cases()}
    assert present == set(CATEGORIES) - {"regression"}


def test_every_case_validates() -> None:
    for case in all_cases():
        validate_case(case)


def test_smoke_subset_is_small_and_covers_both_routing_directions() -> None:
    smoke = [case for case in all_cases() if case.get("smoke")]
    assert 2 <= len(smoke) <= 4
    invoked = {case["expect"].get("gauge_invoked", True) for case in smoke}
    assert invoked == {True, False}


def test_dataset_builds_samples_with_their_fixtures() -> None:
    dataset = gauge_dataset()
    by_id = {sample.id: sample for sample in dataset}
    with_repo = by_id["gauge-canonical-001-bounded-rename"]
    assert with_repo.files
    assert all(path.startswith("/workspace/") for path in with_repo.files)

    without_repo = by_id["gauge-boundary-003-no-repository"]
    assert without_repo.files == {}


def test_category_filter_narrows_the_dataset() -> None:
    routing = gauge_dataset(categories=["routing"])
    assert {sample.metadata["category"] for sample in routing if sample.metadata} == {
        "routing"
    }


def test_a_filter_matching_nothing_is_an_error_not_an_empty_run() -> None:
    with pytest.raises(CaseError):
        gauge_dataset(categories=["regression"])


# --- the expect-block contract ------------------------------------------------


def test_an_unknown_expectation_key_is_rejected() -> None:
    with pytest.raises(ExpectationError, match="unknown expectation"):
        validate_expectations({"toplogy": "G1"})


def test_a_key_the_harness_cannot_observe_is_not_in_the_catalogue() -> None:
    """`asks_no_questions` was in the catalogue and read tool calls to
    `ask_user`. The solver never grants that tool, so the check could not fail —
    the exact silent no-op this file exists to keep out. It was removed rather
    than left reading as an assertion; the judge carries it instead."""
    with pytest.raises(ExpectationError, match="unknown expectation"):
        validate_expectations({"asks_no_questions": True})


def test_an_empty_expect_block_is_rejected() -> None:
    with pytest.raises(ExpectationError, match="asserts nothing"):
        validate_expectations({})


@pytest.mark.parametrize(
    "expect",
    [
        {"binds": []},
        {"forbids": []},
        {"modifiers_include": []},
        {"installation_section": False},
        {"no_registry_match": False},
    ],
)
def test_a_value_whose_only_branch_is_trivially_true_is_rejected(
    expect: dict[str, object],
) -> None:
    """The exact shape this repository's harness README calls a silent no-op:
    a key that reads as an assertion while grading nothing."""
    with pytest.raises(ExpectationError):
        validate_expectations(expect)


def test_binding_a_skill_the_registry_does_not_list_is_rejected() -> None:
    with pytest.raises(ExpectationError, match="planning registry"):
        validate_expectations({"binds": ["context-packer"]})


def test_gauge_invoked_false_may_not_carry_recipe_expectations() -> None:
    """No Gauge run means no recipe, so a topology expectation beside it would
    grade the empty string."""
    with pytest.raises(CaseError, match="no recipe"):
        validate_case(
            {
                "id": "x",
                "category": "routing",
                "difficulty": "easy",
                "input": "...",
                "expect": {"gauge_invoked": False, "topology": "G1"},
            }
        )
