"""Controls for the deterministic Gauge checks.

This repository's eval README is emphatic that a suite whose checks cannot fail
is not a suite that passed. So every check here is exercised from both sides: a
hand-written correct recipe must pass all of them, and each negative control is
a copy of that recipe with exactly one defect introduced, named together with
the check it must trip.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from skill_evals.gauge.contract import Evidence, check_recipe, parse_recipe
from skill_evals.gauge.registry import (
    PROHIBITED_AS_STEP,
    REGISTRY_SKILLS,
    REQUIRED_DEPENDENCIES,
)

CONTROLS = Path(__file__).parent / "controls"

#: Each negative control names the check ids it must break. A control that
#: names a check the recipe never registers proves nothing, so the runner
#: treats an unregistered id as a failure too.
NEGATIVE_CONTROLS: dict[str, list[str]] = {
    "estimates.md": ["contract/no-estimates"],
    "two-topologies.md": ["contract/single-topology"],
    "unknown-topology.md": ["contract/single-topology"],
    "binds-ask-matt.md": ["contract/ask-matt-not-bound"],
    "unexpanded-dependencies.md": ["contract/dependency-expansion"],
    "invented-skill.md": ["contract/registry-membership"],
    "bad-availability-label.md": ["contract/availability-vocabulary"],
    "installed-without-evidence.md": ["contract/availability-evidence"],
    "missing-step-fields.md": ["contract/step-fields"],
    "missing-launch-packet.md": ["contract/launch-packet"],
    "unnamed-registry-gap.md": ["contract/no-registry-match-names-capability"],
    "g0-still-binds-a-skill.md": ["contract/g0-no-planning-skill"],
    "cost-estimate.md": ["contract/no-estimates"],
}

#: No inventory was read, so nothing may be labelled `installed`.
NO_INVENTORY = Evidence(inventory=None)

#: A run that did read an inventory and found everything. Positive controls are
#: graded against this because one of them legitimately labels its steps
#: `installed`; the negative control for that label supplies NO_INVENTORY
#: explicitly, which is the whole difference between them.
FULL_INVENTORY = Evidence(inventory=REGISTRY_SKILLS)


def _read(relative: str) -> str:
    return (CONTROLS / relative).read_text(encoding="utf-8")


# --- registry, parsed from the skill's own reference -------------------------


def test_registry_is_read_from_the_production_reference() -> None:
    assert "handoff" in REGISTRY_SKILLS
    assert "wayfinder" in REGISTRY_SKILLS
    assert "grilling" in REGISTRY_SKILLS
    assert "context-packer" not in REGISTRY_SKILLS


def test_required_dependencies_match_the_binding_table() -> None:
    assert REQUIRED_DEPENDENCIES["grill-me"] == frozenset({"grilling"})
    assert REQUIRED_DEPENDENCIES["grill-with-docs"] == frozenset(
        {"grilling", "domain-modeling"}
    )
    assert REQUIRED_DEPENDENCIES["wayfinder"] >= frozenset(
        {"grilling", "domain-modeling"}
    )
    assert REQUIRED_DEPENDENCIES["handoff"] == frozenset()


def test_exclusions_are_read_from_the_production_reference() -> None:
    assert "ask-matt" in PROHIBITED_AS_STEP
    assert {"implement", "tdd", "code-review"} <= PROHIBITED_AS_STEP


# --- parsing ------------------------------------------------------------------


def test_parses_the_verdict_and_steps() -> None:
    recipe = parse_recipe(_read("positive/canonical-g1.md"))
    assert recipe.topologies == ["G1"]
    assert recipe.modifiers == ["High-assurance"]
    assert recipe.confidence == "High"
    assert [step.skill for step in recipe.steps] == ["handoff"]
    assert recipe.steps[0].availability == "not detected"
    assert recipe.steps[0].launch_packet is not None


def test_g0_step_binds_no_planning_skill() -> None:
    recipe = parse_recipe(_read("positive/canonical-g0.md"))
    assert recipe.topologies == ["G0"]
    assert recipe.steps[0].binds_no_planning_skill
    assert recipe.steps[0].skill is None


# --- positive controls: would a correct recipe pass? --------------------------


@pytest.mark.parametrize("control", sorted(p.name for p in (CONTROLS / "positive").iterdir()))
def test_positive_control_passes_every_registered_check(control: str) -> None:
    recipe = parse_recipe(_read(f"positive/{control}"))
    results = check_recipe(recipe, FULL_INVENTORY)
    assert results, f"{control} registered no checks at all"
    failed = [r for r in results if not r.passed]
    assert not failed, "\n".join(f"{r.id}: {r.detail}" for r in failed)


# --- negative controls: would a broken recipe fail? ---------------------------


@pytest.mark.parametrize("control,must_fail", sorted(NEGATIVE_CONTROLS.items()))
def test_negative_control_trips_the_checks_it_names(
    control: str, must_fail: list[str]
) -> None:
    recipe = parse_recipe(_read(f"negative/{control}"))
    results = check_recipe(recipe, NO_INVENTORY)
    registered = {r.id: r for r in results}

    for check_id in must_fail:
        assert check_id in registered, (
            f"{control} names {check_id}, which this recipe never registers — "
            "an unregistered check cannot fail, so the control proves nothing"
        )
        assert not registered[check_id].passed, (
            f"{control} was built to break {check_id} and it passed"
        )


def test_installed_is_accepted_when_the_inventory_shows_it() -> None:
    """The mirror of `installed-without-evidence`: the check must not simply
    reject the label outright, or it would be unfailable in the other
    direction."""
    recipe = parse_recipe(_read("negative/installed-without-evidence.md"))
    results = {r.id: r for r in check_recipe(recipe, Evidence(inventory=frozenset({"handoff"})))}
    assert results["contract/availability-evidence"].passed


def test_unknown_is_never_rewritten_as_not_installed() -> None:
    """`not installed` is not a label in the registry's vocabulary; `unknown`
    stays `unknown`."""
    recipe = parse_recipe(_read("negative/bad-availability-label.md"))
    results = {r.id: r for r in check_recipe(recipe, NO_INVENTORY)}
    assert "not installed" in results["contract/availability-vocabulary"].detail


# --- the estimate scan, from both sides --------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "Invocation: `bash scripts/seed.sh $1`",   # shell positional, not a cost
        "Charting is one session; each session resolves one ticket.",
        "The same 30-day window as the existing option.",
        "Retries three times, doubling from one second.",
    ],
)
def test_ordinary_recipe_prose_is_not_an_estimate(text: str) -> None:
    """The cry-wolf half. Launch packets are mandatory fenced shell, so a
    pattern that reads `$1` as a cost estimate fails every correct recipe."""
    checks = {c.id: c for c in check_recipe(parse_recipe(f"- Topology: G1\n\n{text}\n"), NO_INVENTORY)}
    assert checks["contract/no-estimates"].passed, checks["contract/no-estimates"].detail


@pytest.mark.parametrize(
    "text",
    [
        "Estimated effort: 3 story points.",
        "Roughly 2 weeks of work.",
        "~3 days once the interview is done.",
        "Budget $4,000 for this.",
        "Size: XL",
        "8 hours of effort",
        "complexity score: 7",
    ],
)
def test_an_actual_estimate_is_caught(text: str) -> None:
    checks = {c.id: c for c in check_recipe(parse_recipe(f"- Topology: G1\n\n{text}\n"), NO_INVENTORY)}
    assert not checks["contract/no-estimates"].passed


def test_quoting_the_humans_own_estimate_is_not_making_one() -> None:
    """The recipe contract *requires* the intent to be quoted verbatim in every
    packet. Failing Gauge because the human said "about 5 minutes" would be
    grading the human's wording, not the skill's."""
    request = "Drop the table. It's about 5 minutes of work, so let's not make a meal of it."
    recipe = parse_recipe(f'- Topology: G1\n\nIntent, verbatim:\n"{request}"\n')
    checks = {c.id: c for c in check_recipe(recipe, Evidence(human_request=request))}
    assert checks["contract/no-estimates"].passed, checks["contract/no-estimates"].detail

    # ...but the same words with no such request behind them still fail.
    bare = {c.id: c for c in check_recipe(recipe, NO_INVENTORY)}
    assert not bare["contract/no-estimates"].passed


def test_a_packet_restating_the_verdict_is_not_a_second_topology() -> None:
    """Launch packets quote the verdict back to the receiving skill. Counting
    that as a second topology false-fails a correct two-step recipe."""
    recipe = parse_recipe(
        "- Topology: G1 Handoff\n\n### Step 1\n- Skill: handoff\n\n"
        "```text\nContext: this recipe is Topology: G1 Handoff.\n```\n"
    )
    assert recipe.topologies == ["G1"]
