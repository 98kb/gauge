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
    MODEL_REGISTRY,
    PLANNING_CAPABILITIES,
    PROHIBITED_AS_STEP,
    REGISTRY_SKILLS,
    REQUIRED_DEPENDENCIES,
    ModelProfile,
    parse_model_registry,
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
    # --- model profiles (ADR 0017) ---
    "missing-model-fields.md": ["contract/model-fields"],
    "handoff-missing-profile.md": ["contract/implementation-profile"],
    "g0-step-not-implementation.md": ["contract/implementation-profile"],
    "fallback-model-list.md": ["contract/single-profile"],
    "unsupported-effort.md": ["contract/model-profile-registered"],
    "substituted-model.md": ["contract/model-binding"],
    "lowered-effort.md": ["contract/model-binding"],
    "high-assurance-falls-back-to-base.md": ["contract/model-binding"],
    "ha-gap-names-base-key.md": ["contract/model-binding"],
    "skill-gap-erases-model.md": ["contract/model-binding"],
    "reports-available.md": ["contract/runtime-availability"],
    "unevidenced-unavailable.md": ["contract/runtime-evidence"],
    "gap-carries-reasoning-effort.md": ["contract/model-binding"],
    "relabelled-capability.md": ["contract/capability-matches-skill"],
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


# --- model registry, parsed from the skill's own reference -------------------


EFFORTS = frozenset({"low", "medium", "high", "xhigh", "max"})


def test_model_profiles_are_read_from_the_production_reference() -> None:
    assert MODEL_REGISTRY.profiles["opus-5-high"] == ModelProfile(
        key="opus-5-high", model="claude-opus-5", effort="high", supported=EFFORTS
    )
    assert MODEL_REGISTRY.profiles["fable-5-1-max"].model == "claude-fable-5-1"
    # Haiku 4.5 has no effort support, so it cannot form a profile.
    assert not any("haiku" in p.model for p in MODEL_REGISTRY.profiles.values())


def test_high_assurance_binds_its_own_row_and_never_the_base_one() -> None:
    assert MODEL_REGISTRY.binding("implementation", high_assurance=False) == (
        MODEL_REGISTRY.profiles["opus-5-high"]
    )
    assert MODEL_REGISTRY.binding("implementation", high_assurance=True) == (
        MODEL_REGISTRY.profiles["fable-5-1-xhigh"]
    )
    # `unbound` is an intentional gap, even though a base binding exists.
    assert MODEL_REGISTRY.binding("context handoff", high_assurance=False) is not None
    assert MODEL_REGISTRY.binding("context handoff", high_assurance=True) is None
    assert MODEL_REGISTRY.binding("threat modelling", high_assurance=False) is None


def test_model_bindings_cover_exactly_the_planning_registry_capabilities() -> None:
    """The two registries bind the same capability vocabulary; the planning
    registry's old `implementation launch packet` key is now `implementation`."""
    assert "implementation" in PLANNING_CAPABILITIES
    assert "implementation launch packet" not in PLANNING_CAPABILITIES
    assert {capability for capability, _ in MODEL_REGISTRY.bindings} == PLANNING_CAPABILITIES


_MINI_REGISTRY = """\
## Profiles

| Profile | Provider | Model ID | Reasoning effort | Supported effort values |
| --- | --- | --- | --- | --- |
| `a-high` | Anthropic | `claude-a` | `{effort}` | `low`, `high` |

## Bindings

| Capability (routing model) | Base | `High-assurance` |
| --- | --- | --- |
| `implementation` | {base} | unbound |
"""


def test_a_well_formed_model_registry_parses() -> None:
    registry = parse_model_registry(_MINI_REGISTRY.format(effort="high", base="`a-high`"))
    assert registry.binding("implementation", high_assurance=False) == ModelProfile(
        "a-high", "claude-a", "high", frozenset({"low", "high"})
    )
    assert registry.binding("implementation", high_assurance=True) is None


@pytest.mark.parametrize(
    "effort, base, match",
    [
        ("max", "`a-high`", "does not support"),
        ("high", "`a-typo`", "unknown profile"),
        ("high", "tbd", "neither a profile nor `unbound`"),
    ],
)
def test_a_malformed_model_registry_is_rejected(effort: str, base: str, match: str) -> None:
    """A typo must not silently become an intentional gap or an unsupported pair."""
    with pytest.raises(ValueError, match=match):
        parse_model_registry(_MINI_REGISTRY.format(effort=effort, base=base))


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


def test_non_g0_boundaries_are_every_step_plus_the_implementation_handoff() -> None:
    recipe = parse_recipe(_read("positive/canonical-g1.md"))
    step, handoff = recipe.steps[0], recipe.handoff
    assert handoff is not None
    assert recipe.boundaries == [step, handoff]

    assert step.capability == "context handoff"
    assert step.model_gap_key == "context handoff + High-assurance"
    assert (step.effort, step.runtime) == ("n/a", "n/a")

    assert handoff.capability == "implementation"
    assert (handoff.model, handoff.effort, handoff.runtime) == (
        "claude-fable-5-1",
        "xhigh",
        "unknown",
    )
    assert handoff.model_gap_key is None


def test_g0_carries_its_profile_on_its_only_step_and_has_no_handoff_boundary() -> None:
    recipe = parse_recipe(_read("positive/canonical-g0.md"))
    assert recipe.handoff is None
    assert recipe.boundaries == recipe.steps
    step = recipe.steps[0]
    assert (step.capability, step.model, step.effort) == ("implementation", "claude-opus-5", "high")


def test_runtime_evidence_is_parsed_apart_from_its_label() -> None:
    recipe = parse_recipe(_read("positive/reworded-g2.md"))
    assert recipe.handoff is not None
    assert recipe.handoff.runtime == "unavailable"
    assert "maxEffortLevel" in (recipe.handoff.runtime_evidence or "")
    assert recipe.steps[1].runtime == "unknown"
    assert recipe.steps[1].runtime_evidence is None


def test_handoff_fields_do_not_bleed_into_the_last_step() -> None:
    """A step block used to run to the next `###`, so the handoff section's
    bullets would have filled in a step's missing model fields."""
    recipe = parse_recipe(
        "- Topology: G1 Handoff\n\n### Step 1\n- Skill: handoff\n\n"
        "## Implementation handoff\n- Capability: implementation\n- Model: claude-opus-5\n"
    )
    assert "capability" not in recipe.steps[0].fields
    assert recipe.handoff is not None and recipe.handoff.capability == "implementation"


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


def _g0_with(model: str, effort: str) -> dict[str, bool]:
    recipe = parse_recipe(
        "- Topology: G0 Direct\n\n### Step 1\n- Capability: implementation\n"
        "- Skill: No planning skill\n"
        f"- Model: {model}\n- Reasoning effort: {effort}\n- Runtime availability: unknown\n"
    )
    return {c.id: c.passed for c in check_recipe(recipe, NO_INVENTORY)}


@pytest.mark.parametrize(
    "model, effort, check_id, passes",
    [
        # One profile, however it is decorated, is not a fallback list...
        ("`claude-opus-5` (Claude Opus 5)", "high (advisory)", "contract/single-profile", True),
        # ...while any second model or effort is one.
        ("claude-opus-5 or claude-sonnet-5", "high", "contract/single-profile", False),
        ("claude-opus-5", "high, then medium", "contract/single-profile", False),
        # A convenience alias is never a pinned profile ID.
        ("opus", "high", "contract/model-profile-registered", False),
        ("claude-opus-5", "high", "contract/model-profile-registered", True),
    ],
)
def test_single_profile_and_registered_profile_from_both_sides(
    model: str, effort: str, check_id: str, passes: bool
) -> None:
    assert _g0_with(model, effort)[check_id] is passes


def test_a_packet_restating_the_verdict_is_not_a_second_topology() -> None:
    """Launch packets quote the verdict back to the receiving skill. Counting
    that as a second topology false-fails a correct two-step recipe."""
    recipe = parse_recipe(
        "- Topology: G1 Handoff\n\n### Step 1\n- Skill: handoff\n\n"
        "```text\nContext: this recipe is Topology: G1 Handoff.\n```\n"
    )
    assert recipe.topologies == ["G1"]
