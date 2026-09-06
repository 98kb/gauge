"""Per-case expectations, and the contract they themselves must honour.

This repository has already paid for the lesson that an expectation which
registers no check is worse than no expectation at all — it reads as an
assertion in review while grading nothing, which is how a refusal scenario once
scored 11 of 12 against an empty transcript. So the rule from
`evals/README.md` is enforced here too:

- an expectation **omitted** is not asserted;
- an expectation **present** must register at least one check;
- a key no check reads is a hard error, and so is a value whose only branch is
  trivially true.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from skill_evals.gauge.contract import Check, Recipe
from skill_evals.gauge.registry import REGISTRY_SKILLS
from skill_evals.shared.trajectory import Trajectory

TOPOLOGIES = ("G0", "G1", "G2", "G3")
VARIANTS = ("G3-A", "G3-B", "none")
CONFIDENCE_ORDER = ("Low", "Medium", "High")


class ExpectationError(ValueError):
    """An `expect` block the harness will not grade."""


@dataclass(frozen=True)
class Outcome:
    """Everything a per-case check may read."""

    recipe: Recipe
    trajectory: Trajectory


ExpectationCheck = Callable[[Any, Outcome], list[Check]]

# Deliberately absent: an `asks_no_questions` key. The solver is a single-turn
# react loop with `skill` and `bash` only — the agent has no channel to the
# human at all, so no run can put a question to one and the check could never
# fail. "Asking the human any question" stays in the affected cases' `forbidden`
# list, where the semantic grader can actually see it in the emitted result.
#
# Also absent: `mentions` / `omits` free-text keys. They were written before the
# cases were, no case reached for them, and a substring match over a result
# whose wording is explicitly allowed to vary is a false-fail waiting to happen.
# Add them back the day a case genuinely needs one.


def check_expectations(expect: dict[str, Any], outcome: Outcome) -> list[Check]:
    """Grade one case's `expect` block. Raises rather than silently skipping."""
    validate_expectations(expect)
    checks: list[Check] = []
    for key, value in expect.items():
        registered = CATALOGUE[key](value, outcome)
        if not registered:
            raise ExpectationError(
                f'"{key}": {value!r} registered no check — it grades nothing while '
                "reading as an assertion."
            )
        checks.extend(registered)
    return checks


def validate_expectations(expect: dict[str, Any]) -> None:
    """Reject an `expect` block before any model is called."""
    if not expect:
        raise ExpectationError("empty expect block: the case asserts nothing")
    for key, value in expect.items():
        if key not in CATALOGUE:
            raise ExpectationError(
                f'unknown expectation "{key}". Known keys: {sorted(CATALOGUE)}'
            )
        VALIDATORS[key](key, value)


# --- value validators ---------------------------------------------------------


def _one_of(allowed: tuple[str, ...]) -> Callable[[str, Any], None]:
    def validate(key: str, value: Any) -> None:
        if value not in allowed:
            raise ExpectationError(f'"{key}": {value!r} is not one of {allowed}')

    return validate


def _nonempty_skills(key: str, value: Any) -> None:
    if not isinstance(value, list) or not value:
        raise ExpectationError(f'"{key}" must be a non-empty list of skill names')
    unknown = sorted(set(value) - REGISTRY_SKILLS)
    if unknown:
        raise ExpectationError(
            f'"{key}" names {unknown}, which the planning registry does not list'
        )


def _nonempty_strings(key: str, value: Any) -> None:
    if not isinstance(value, list) or not value or not all(isinstance(v, str) for v in value):
        raise ExpectationError(f'"{key}" must be a non-empty list of strings')


def _true_only(key: str, value: Any) -> None:
    if value is not True:
        raise ExpectationError(
            f'"{key}": {value!r} asserts nothing — omit the key to say "not asserted"'
        )


def _boolean(key: str, value: Any) -> None:
    if not isinstance(value, bool):
        raise ExpectationError(f'"{key}" must be true or false')


# --- checks -------------------------------------------------------------------


def _topology(value: Any, outcome: Outcome) -> list[Check]:
    found = outcome.recipe.topologies
    return [
        Check(
            f"case/topology:{value}",
            found == [value],
            f"expected {value}, recipe names {found or 'nothing'}",
        )
    ]


def _variant(value: Any, outcome: Outcome) -> list[Check]:
    stated = (outcome.recipe.variant or "").strip()
    matched = value.lower() in stated.lower() if stated else False
    return [Check(f"case/variant:{value}", matched, f"variant reads {stated!r}")]


def _binds(value: Any, outcome: Outcome) -> list[Check]:
    bound = {step.skill for step in outcome.recipe.steps if step.skill}
    return [
        Check(f"case/binds:{skill}", skill in bound, f"bound skills: {sorted(bound)}")
        for skill in value
    ]


def _forbids(value: Any, outcome: Outcome) -> list[Check]:
    bound = {step.skill for step in outcome.recipe.steps if step.skill}
    return [
        Check(
            f"case/forbids:{skill}",
            skill not in bound,
            f"bound skills: {sorted(bound)}",
        )
        for skill in value
    ]


def _binds_no_planning_skill(value: Any, outcome: Outcome) -> list[Check]:
    steps = outcome.recipe.steps
    return [
        Check(
            "case/binds-no-planning-skill",
            bool(steps) and all(step.binds_no_planning_skill for step in steps),
            f"step skills: {[step.fields.get('skill') for step in steps]}",
        )
    ]


def _no_registry_match(value: Any, outcome: Outcome) -> list[Check]:
    steps = [step for step in outcome.recipe.steps if step.is_no_registry_match]
    return [
        Check(
            "case/no-registry-match",
            bool(steps),
            f"{len(steps)} step(s) resolve to `No registry match`",
        )
    ]


def _modifiers_include(value: Any, outcome: Outcome) -> list[Check]:
    stated = " ".join(outcome.recipe.modifiers).lower()
    return [
        Check(
            f"case/modifier:{modifier}",
            modifier.lower() in stated,
            f"modifiers: {outcome.recipe.modifiers}",
        )
        for modifier in value
    ]


def _availability(value: Any, outcome: Outcome) -> list[Check]:
    bound = [step for step in outcome.recipe.steps if step.skill]
    return [
        Check(
            f"case/availability:{value}",
            bool(bound) and all(step.availability == value for step in bound),
            f"labels: {[step.availability for step in bound]}",
        )
    ]


def _installation_section(value: Any, outcome: Outcome) -> list[Check]:
    present = re.search(
        r"^#+\s*installation required\b", outcome.recipe.text, re.I | re.MULTILINE
    )
    return [
        Check(
            "case/installation-section",
            present is not None,
            "an `Installation required` section is present"
            if present
            else "no `Installation required` section, though a bound skill needs installing",
        )
    ]


def _gauge_invoked(value: Any, outcome: Outcome) -> list[Check]:
    invoked = outcome.trajectory.invoked("gauge")
    return [
        Check(
            "case/gauge-invoked" if value else "case/gauge-not-invoked",
            invoked is value,
            f"skill invocations: {list(outcome.trajectory.skill_invocations)}",
        )
    ]


def _confidence_at_most(value: Any, outcome: Outcome) -> list[Check]:
    stated = (outcome.recipe.confidence or "").strip().capitalize()
    ceiling = CONFIDENCE_ORDER.index(value)
    within = stated in CONFIDENCE_ORDER and CONFIDENCE_ORDER.index(stated) <= ceiling
    return [
        Check(
            f"case/confidence-at-most:{value}",
            within,
            f"confidence reads {stated or 'nothing'}",
        )
    ]


CATALOGUE: dict[str, ExpectationCheck] = {
    "topology": _topology,
    "variant": _variant,
    "binds": _binds,
    "forbids": _forbids,
    "binds_no_planning_skill": _binds_no_planning_skill,
    "no_registry_match": _no_registry_match,
    "modifiers_include": _modifiers_include,
    "availability": _availability,
    "installation_section": _installation_section,
    "gauge_invoked": _gauge_invoked,
    "confidence_at_most": _confidence_at_most,
}

VALIDATORS: dict[str, Callable[[str, Any], None]] = {
    "topology": _one_of(TOPOLOGIES),
    "variant": _one_of(VARIANTS),
    "binds": _nonempty_skills,
    "forbids": _nonempty_skills,
    "binds_no_planning_skill": _true_only,
    "no_registry_match": _true_only,
    "modifiers_include": _nonempty_strings,
    "availability": _one_of(("installed", "not detected", "unknown", "n/a")),
    "installation_section": _true_only,
    # Both branches assert: `false` is negative routing, not a no-op.
    "gauge_invoked": _boolean,
    "confidence_at_most": _one_of(CONFIDENCE_ORDER),
}
