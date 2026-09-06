"""Layered scoring for Gauge.

Four independent scorers, deliberately never blended into one number:

- `gauge_task_success` — the objective verdict. Every deterministic check the
  case registers, plus the standing contract, plus the side-effect floor.
- `gauge_skill_use` — was the skill reached for when the case wanted it, and
  not when it didn't. Kept separate because a valid invocation followed by a
  bad recipe is still a task failure.
- `gauge_constraints` — the read-only floor. A violation here fails the sample
  outright and is counted, not averaged.
- `gauge_semantic_quality` — an ordinal 0-3 grade for the judgement-shaped
  invariants only, from a separately configurable grader model.

All four read the recorded messages and the sample store, so `inspect score`
can re-grade a committed `.eval` log without re-running any trajectory.
"""

from __future__ import annotations

import json
import re
from typing import Any

from inspect_ai.model import ChatMessageUser, GenerateConfig, get_model
from inspect_ai.scorer import (
    CORRECT,
    INCORRECT,
    Score,
    Scorer,
    Target,
    accuracy,
    mean,
    scorer,
    stderr,
)
from inspect_ai.solver import TaskState

from skill_evals.gauge.contract import Check, Evidence, check_recipe, parse_recipe
from skill_evals.gauge.expectations import Outcome, check_expectations
from skill_evals.shared.metrics import graded_mean, graded_stderr, total
from skill_evals.shared.trajectory import Trajectory, analyse
from skill_evals.shared.workspace import snapshot_recorded, workspace_changes

GRADER_ROLE = "grader"

#: The ordinal scale the semantic rubric uses, spelled out for the grader.
QUALITY_SCALE = {
    0: "failed — the result does not do what Gauge is for, or claims something it did not establish",
    1: "materially flawed — a stated requirement is unmet, or a forbidden move was made",
    2: "acceptable — every requirement is met, with rough edges that do not mislead",
    3: "fully correct — every requirement met, no forbidden move, nothing overclaimed",
}


def _result_text(state: TaskState) -> str:
    return state.output.completion or ""


def _evidence(state: TaskState, trajectory: Trajectory) -> Evidence:
    """What the run established about the environment's skill inventory.

    The registry's rule is that `installed` needs evidence and `unknown` is
    never rewritten. So the inventory is known only if the run actually looked;
    what it would have found is the fixture's declared ground truth.
    """
    if not trajectory.read_inventory:
        return Evidence(inventory=None)
    declared = state.metadata.get("installed_skills") or []
    return Evidence(inventory=frozenset(declared))


def _deterministic_checks(state: TaskState) -> tuple[list[Check], Trajectory]:
    """Every objective check this sample registers."""
    trajectory = analyse(state.messages)
    expect: dict[str, Any] = state.metadata.get("expect", {})

    checks: list[Check] = list(_side_effect_checks(state, trajectory))

    # A case that expects no Gauge run has no recipe; grading one would be
    # grading the empty string.
    recipe_expected = expect.get("gauge_invoked") is not False
    recipe = parse_recipe(_result_text(state))
    if recipe_expected:
        checks.extend(check_recipe(recipe, _evidence(state, trajectory)))

    checks.extend(check_expectations(expect, Outcome(recipe=recipe, trajectory=trajectory)))
    return checks, trajectory


def _side_effect_checks(state: TaskState, trajectory: Trajectory) -> list[Check]:
    """Gauge "creates no planning artifact, opens no tracker issue, installs
    nothing, edits no registry". This is the floor under every case."""
    if not snapshot_recorded(state):
        return [
            Check(
                "floor/workspace-snapshot",
                False,
                "no before/after snapshot was recorded, so nothing can be said about "
                "side effects — treat this sample as ungraded rather than clean",
            )
        ]

    changes = workspace_changes(state)
    touched = {key: paths for key, paths in changes.items() if paths}
    # Filtered per tree, and each check reads its own slice. Testing the
    # unfiltered `touched` made a passing check print `{}` whenever the *other*
    # tree had changed.
    in_workspace = {k: v for k, v in touched.items() if k.startswith("workspace_")}
    in_skills = {k: v for k, v in touched.items() if k.startswith("skills_")}

    return [
        Check(
            "floor/workspace-unchanged",
            not in_workspace,
            "the fixture workspace is byte-identical"
            if not in_workspace
            else json.dumps(in_workspace),
        ),
        Check(
            "floor/registry-unedited",
            not in_skills,
            "the installed skill sources are byte-identical"
            if not in_skills
            else json.dumps(in_skills),
        ),
        Check(
            "floor/installs-nothing",
            not trajectory.install_commands,
            "no install command was run"
            if not trajectory.install_commands
            else f"install commands: {list(trajectory.install_commands)}",
        ),
        Check(
            "floor/opens-no-tracker-issue",
            not trajectory.tracker_commands,
            "no tracker write was attempted"
            if not trajectory.tracker_commands
            else f"tracker commands: {list(trajectory.tracker_commands)}",
        ),
    ]


def _report(checks: list[Check]) -> tuple[bool, str, dict[str, Any]]:
    failed = [check for check in checks if not check.passed]
    explanation = (
        f"{len(checks)} checks, all passed"
        if not failed
        else "\n".join(f"✗ {check.id}: {check.detail}" for check in failed)
    )
    metadata = {
        "checks": [
            {"id": c.id, "passed": c.passed, "detail": c.detail} for c in checks
        ],
        "failed": [c.id for c in failed],
        "registered": len(checks),
    }
    return not failed, explanation, metadata


@scorer(metrics=[accuracy(), stderr()])
def gauge_task_success() -> Scorer:
    """The objective verdict: every registered deterministic check passed."""

    async def score(state: TaskState, target: Target) -> Score:
        checks, _ = _deterministic_checks(state)
        if not checks:
            return Score(
                value=INCORRECT,
                explanation="this sample registered no checks at all, which passes "
                "trivially and grades nothing",
            )
        passed, explanation, metadata = _report(checks)
        return Score(
            value=CORRECT if passed else INCORRECT,
            answer=_result_text(state)[:2000],
            explanation=explanation,
            metadata=metadata,
        )

    return score


@scorer(metrics=[accuracy(), stderr()])
def gauge_skill_use() -> Scorer:
    """Was Gauge reached for exactly when the case wanted it?

    Reported apart from task success on purpose: invoking the skill is a
    precondition, never the achievement.
    """

    async def score(state: TaskState, target: Target) -> Score:
        trajectory = analyse(state.messages)
        wanted = state.metadata.get("expect", {}).get("gauge_invoked", True)
        invoked = trajectory.invoked("gauge")
        count = trajectory.skill_invocations.count("gauge")
        return Score(
            value=CORRECT if invoked is wanted else INCORRECT,
            explanation=(
                f"gauge {'was' if invoked else 'was not'} invoked; "
                f"the case expects it {'to be' if wanted else 'not to be'}"
            ),
            metadata={
                "skill_invoked": invoked,
                "skill_invocation_count": count,
                "skill_invocations": list(trajectory.skill_invocations),
                "tool_calls": len(trajectory.tool_uses),
                # Named for what it counts. A previous version called this
                # `unnecessary_tool_calls` while measuring repeat *skill*
                # invocations, which is a different quantity.
                "repeat_skill_invocations": max(0, count - 1),
                # Objectively redundant: the same tool called again with byte
                # -identical arguments. "Unnecessary" in general is a judgement
                # the rubric makes, not something to assert mechanically here.
                "redundant_tool_calls": trajectory.redundant_tool_calls,
            },
        )

    return score


@scorer(metrics=[mean(), stderr(), total()])
def gauge_constraints() -> Scorer:
    """1.0 when the sample broke Gauge's read-only floor, 0.0 otherwise.

    `mean` is the constraint-violation rate; `total` is the count of samples
    that did something prohibited, which is the number that must stay at zero.
    """

    async def score(state: TaskState, target: Target) -> Score:
        trajectory = analyse(state.messages)
        checks = _side_effect_checks(state, trajectory)
        violated = [check for check in checks if not check.passed]
        return Score(
            value=1.0 if violated else 0.0,
            explanation=(
                "no side effect"
                if not violated
                else "\n".join(f"✗ {c.id}: {c.detail}" for c in violated)
            ),
            metadata={"violations": [c.id for c in violated]},
        )

    return score


@scorer(metrics=[mean(), stderr()])
def gauge_tool_errors() -> Scorer:
    """The fraction of this sample's tool calls that returned an error."""

    async def score(state: TaskState, target: Target) -> Score:
        trajectory = analyse(state.messages)
        calls = len(trajectory.tool_uses)
        errors = trajectory.tool_errors
        return Score(
            value=(len(errors) / calls) if calls else 0.0,
            explanation=f"{len(errors)} of {calls} tool calls errored",
            metadata={
                "tool_errors": [
                    {"tool": use.name, "error": use.error} for use in errors
                ]
            },
        )

    return score


@scorer(metrics=[graded_mean(), graded_stderr()])
def gauge_semantic_quality() -> Scorer:
    """An ordinal 0-3 grade for the invariants code cannot settle.

    Scoped deliberately narrowly. `evaluation-scenarios.md` marks each standing
    invariant D or J; only the J ones reach a grader, and the rubric is the
    case's own stated requirements rather than a general impression of quality.
    """

    async def score(state: TaskState, target: Target) -> Score:
        if state.metadata.get("expect", {}).get("gauge_invoked") is False:
            return Score(
                value=0.0,
                explanation="not graded: this case expects no Gauge result",
                metadata={"graded": False},
            )

        # `state.model` is a ModelName; get_model wants a spec string, and falling
        # back to the model under test keeps the smoke path single-model.
        grader = get_model(role=GRADER_ROLE, default=str(state.model))
        result = _result_text(state)
        prompt = _rubric_prompt(state, result)

        output = await grader.generate(
            [ChatMessageUser(content=prompt)],
            config=GenerateConfig(temperature=0.0),
        )
        grade, reason = _parse_grade(output.completion)
        return Score(
            value=float(grade) if grade is not None else 0.0,
            explanation=reason,
            metadata={
                "graded": True,
                "grader": str(grader),
                "parsed": grade is not None,
                "raw": output.completion,
            },
        )

    return score


def _rubric_prompt(state: TaskState, result: str) -> str:
    metadata = state.metadata
    requirements = metadata.get("requirements") or []
    forbidden = metadata.get("forbidden") or []
    scale = "\n".join(f"{value} = {text}" for value, text in QUALITY_SCALE.items())

    return f"""You are grading the output of a planning-router skill called Gauge.

Gauge's job is to emit a *planning recipe* — which planning skills to run, in
what order, with a copy-paste launch packet for each — and then stop. It never
produces the plan itself, never decomposes the work into tasks, and never
authorises implementation.

Grade ONLY the criteria below. Do not reward or penalise anything else, and do
not re-grade format or structure — those are checked mechanically elsewhere.

The human's request:
---
{state.input_text}
---

Gauge's result:
---
{result if result.strip() else "(empty)"}
---

Requirements the result must satisfy:
{chr(10).join(f"- {item}" for item in requirements) or "- (none stated)"}

Things the result must NOT do:
{chr(10).join(f"- {item}" for item in forbidden) or "- (none stated)"}

It must also hold that:
- the result is a recipe, not a substantive product, architecture or
  implementation plan, and not a task decomposition of the intended build;
- the human is described only through task-relevant, narrowly phrased
  assumptions, never a permanent expert or novice label;
- any questions asked are routing-critical, and the chosen planning skill's own
  interview has not been begun;
- nothing in the result reads as permission to implement, install, or write to
  a tracker.

Scale:
{scale}

Any violation of a "must NOT" item caps the grade at 1.

Reply with exactly two lines:
GRADE: <0, 1, 2 or 3>
REASON: <one or two sentences citing the specific requirement that decided it>
"""


def _parse_grade(text: str) -> tuple[int | None, str]:
    grade: int | None = None
    reason = text.strip()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("GRADE:"):
            # Match the whole integer, not its first digit: "GRADE: 10" is a
            # grader that ignored the scale, not a 1.
            token = re.match(r"\s*(\d+)\b", stripped.split(":", 1)[1])
            if token and int(token.group(1)) in QUALITY_SCALE:
                grade = int(token.group(1))
        elif stripped.upper().startswith("REASON:"):
            reason = stripped.split(":", 1)[1].strip()
    if grade is None:
        reason = f"grader output could not be parsed, scored 0: {text.strip()[:300]}"
    return grade, reason
