"""Controls for the per-case expectation layer.

`evals/README.md` asks both bars of *every* scenario-layer check, not just the
standing ones: "every scenario-layer check is a pattern tuned close to a
phrasing, and a phrasing check false-fails the first correct run that words it
differently." So each key in the catalogue is exercised from both sides here,
and a key with no control is itself a failure — otherwise a key could be added
and never proven able to fail.
"""

from __future__ import annotations

from typing import Any

import pytest
from inspect_ai.model import ChatMessageAssistant, ChatMessageTool
from inspect_ai.tool import ToolCall

from skill_evals.gauge.contract import parse_recipe
from skill_evals.gauge.expectations import CATALOGUE, Outcome, check_expectations
from skill_evals.shared.trajectory import Trajectory, analyse


def _trajectory(*skills: str) -> Trajectory:
    messages: list[Any] = []
    for index, name in enumerate(skills):
        call = ToolCall(id=f"s{index}", function="skill", arguments={"command": name})
        messages.append(ChatMessageAssistant(content="", tool_calls=[call]))
        messages.append(
            ChatMessageTool(content="running", tool_call_id=f"s{index}", function="skill")
        )
    return analyse(messages)


GAUGE_RUN = _trajectory("gauge")
NO_RUN = _trajectory()

STEP = """### Step 1 — do the thing
- Skill: {skill}
- Dependencies: {deps}
- Availability: {availability}
- Invocation: `/{skill}`
- Inputs: the intent
- Expected output: an artifact
- Exit condition: it exists
- Next handoff: the next step

#### Launch packet
```text
packet
```
"""


def _recipe(
    *,
    topology: str = "G1 Handoff",
    variant: str = "none",
    modifiers: str = "High-assurance",
    confidence: str = "High",
    skill: str = "handoff",
    deps: str = "none",
    availability: str = "not detected",
    extra: str = "",
) -> str:
    return (
        f"# Gauge result\n\n"
        f"- Topology: {topology}\n- Variant: {variant}\n"
        f"- Modifiers: {modifiers}\n- Confidence: {confidence}\n\n"
        f"## Resolved planning recipe\n\n"
        + STEP.format(skill=skill, deps=deps, availability=availability)
        + extra
    )


HANDOFF = """
## Implementation handoff
- Capability: implementation
- Model: claude-fable-5-1
- Reasoning effort: xhigh
- Runtime availability: {runtime}
"""


def _outcome(text: str, trajectory: Trajectory = GAUGE_RUN) -> Outcome:
    return Outcome(recipe=parse_recipe(text), trajectory=trajectory)


#: key -> (value, an outcome it must pass, an outcome it must fail).
CONTROLS: dict[str, tuple[Any, Outcome, Outcome]] = {
    "topology": ("G1", _outcome(_recipe()), _outcome(_recipe(topology="G2 Interactive"))),
    "variant": (
        "G3-A",
        _outcome(_recipe(topology="G3 Navigated", variant="G3-A route decided")),
        _outcome(_recipe(topology="G3 Navigated", variant="G3-B route foggy")),
    ),
    "binds": (["handoff"], _outcome(_recipe()), _outcome(_recipe(skill="to-spec"))),
    "forbids": (["wayfinder"], _outcome(_recipe()), _outcome(_recipe(skill="wayfinder"))),
    "binds_no_planning_skill": (
        True,
        _outcome(_recipe(topology="G0 Direct", skill="No planning skill", availability="n/a")),
        _outcome(_recipe(topology="G0 Direct")),
    ),
    "no_registry_match": (
        True,
        _outcome(_recipe(skill="No registry match: threat modelling", availability="n/a")),
        _outcome(_recipe()),
    ),
    "modifiers_include": (
        ["High-assurance"],
        _outcome(_recipe()),
        _outcome(_recipe(modifiers="Exception-only")),
    ),
    "availability": (
        "not detected",
        _outcome(_recipe()),
        _outcome(_recipe(availability="unknown")),
    ),
    "installation_section": (
        True,
        _outcome(_recipe(extra="\n## Installation required\nRun the installer.\n")),
        _outcome(_recipe()),
    ),
    "gauge_invoked": (True, _outcome(_recipe()), _outcome(_recipe(), NO_RUN)),
    "confidence_at_most": (
        "Medium",
        _outcome(_recipe(confidence="Medium")),
        _outcome(_recipe(confidence="High")),
    ),
    "runtime_unavailable": (
        ["implementation"],
        _outcome(
            _recipe(
                extra=HANDOFF.format(
                    runtime="unavailable: `maxEffortLevel` is `high` in .claude/settings.json"
                )
            )
        ),
        _outcome(_recipe(extra=HANDOFF.format(runtime="unknown"))),
    ),
}


def test_every_catalogue_key_has_a_control() -> None:
    """A key with no control has never been shown able to fail. Adding one to
    the catalogue means adding it here in the same change."""
    assert set(CONTROLS) == set(CATALOGUE), {
        "uncontrolled": sorted(set(CATALOGUE) - set(CONTROLS)),
        "stale": sorted(set(CONTROLS) - set(CATALOGUE)),
    }


@pytest.mark.parametrize("key", sorted(CONTROLS))
def test_expectation_passes_the_outcome_it_describes(key: str) -> None:
    value, passing, _ = CONTROLS[key]
    checks = check_expectations({key: value}, passing)
    assert checks, f"{key} registered no check"
    failed = [c for c in checks if not c.passed]
    assert not failed, "\n".join(f"{c.id}: {c.detail}" for c in failed)


@pytest.mark.parametrize("key", sorted(CONTROLS))
def test_expectation_fails_the_outcome_it_forbids(key: str) -> None:
    value, _, failing = CONTROLS[key]
    checks = check_expectations({key: value}, failing)
    assert checks, f"{key} registered no check"
    assert any(not c.passed for c in checks), (
        f"{key} passed an outcome built to break it — the check cannot fail"
    )


def test_gauge_invoked_false_asserts_in_its_own_direction() -> None:
    """`false` is negative routing, not the trivially-true branch the other
    boolean keys are rejected for. It has to fail when the skill *was* used."""
    assert all(c.passed for c in check_expectations({"gauge_invoked": False}, _outcome("", NO_RUN)))
    assert not all(
        c.passed for c in check_expectations({"gauge_invoked": False}, _outcome("", GAUGE_RUN))
    )
