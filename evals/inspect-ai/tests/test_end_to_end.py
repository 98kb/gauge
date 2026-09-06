"""End-to-end: a whole sample through the real sandbox, with a scripted model.

Model access is the one thing this environment cannot supply, so the agent is
replaced by a deterministic script while everything else stays real — the
Docker sandbox, the fixture copy, the adapted production skill installed by
Inspect's own `skill()` tool, the workspace snapshots, and all five scorers.
What this proves is that the harness works; what it cannot prove is how a real
model behaves, which is the baseline the README says is still owed.

Marked `docker` and skipped by default. Run it with:

    pytest -m docker
"""

from __future__ import annotations

from pathlib import Path

import pytest
from inspect_ai import eval as inspect_eval
from inspect_ai.model import (
    ChatMessage,
    ChatMessageAssistant,
    ChatMessageUser,
    ModelOutput,
    get_model,
)

from skill_evals.gauge.task import gauge

pytestmark = pytest.mark.docker

CONTROLS = Path(__file__).parent / "controls"
CASE_ID = "gauge-canonical-002-auth-boundary"

#: A correct G1 recipe for the sample under test — the same fixture the offline
#: contract controls use, so the two layers cannot disagree about what "correct"
#: means.
RECIPE = (CONTROLS / "positive" / "canonical-g1.md").read_text(encoding="utf-8")

GRADER_REPLY = "GRADE: 3\nREASON: scripted grader for the harness test."


def _scripted(messages: list[ChatMessage], *_: object) -> ModelOutput:
    """Drive one Gauge-shaped trajectory, then answer grading calls."""
    text = "\n".join(
        m.text for m in messages if isinstance(m, ChatMessageUser) and m.text
    )
    if "You are grading the output" in text:
        return ModelOutput.from_content(model="mockllm", content=GRADER_REPLY)

    turn = sum(1 for m in messages if isinstance(m, ChatMessageAssistant))
    if turn == 0:
        return ModelOutput.for_tool_call("mockllm", "skill", {"command": "gauge"})
    if turn == 1:
        return ModelOutput.for_tool_call(
            "mockllm",
            "bash",
            {"command": "ls -a /workspace && ls -a /workspace/.agents/skills || true"},
        )
    return ModelOutput.for_tool_call("mockllm", "submit", {"answer": RECIPE})


@pytest.fixture(scope="module")
def sample():  # type: ignore[no-untyped-def]
    scripted = get_model("mockllm/model", custom_outputs=_scripted)
    logs = inspect_eval(
        gauge(),
        model=scripted,
        # Also the proof that the grader is a separately addressable role: the
        # semantic scorer reaches this model only because the role points here.
        model_roles={"grader": scripted},
        sample_id=CASE_ID,
        log_dir=None,
        display="none",
    )
    assert logs[0].status == "success", logs[0].error
    assert logs[0].samples
    return logs[0].samples[0]


def _score(sample, name: str):  # type: ignore[no-untyped-def]
    assert name in sample.scores, sorted(sample.scores)
    return sample.scores[name]


def test_the_production_skill_reached_the_sandbox(sample) -> None:  # type: ignore[no-untyped-def]
    """The skill tool installed the real Gauge instructions, references and all."""
    skill_results = [
        message.text
        for message in sample.messages
        if message.role == "tool" and "The \"gauge\" skill is running" in (message.text or "")
    ]
    assert skill_results, "the skill tool never returned Gauge's instructions"
    served = skill_results[0]
    assert "references/planning-registry.md" in served
    assert "G3 | Navigated" in served


def test_task_success_is_green_for_a_correct_recipe(sample) -> None:  # type: ignore[no-untyped-def]
    score = _score(sample, "gauge_task_success")
    assert score.value == "C", score.explanation
    assert score.metadata["registered"] >= 12


def test_skill_use_is_scored_apart_from_success(sample) -> None:  # type: ignore[no-untyped-def]
    score = _score(sample, "gauge_skill_use")
    assert score.value == "C"
    assert score.metadata["skill_invoked"] is True
    assert score.metadata["skill_invocation_count"] == 1


def test_the_read_only_floor_recorded_real_evidence(sample) -> None:  # type: ignore[no-untyped-def]
    """Not merely 0.0 — the snapshots must actually exist, or a run that
    recorded nothing would read as a clean run."""
    assert _score(sample, "gauge_constraints").value == 0.0
    assert sample.store["workspace_before"]
    assert sample.store["workspace_before"] == sample.store["workspace_after"]
    assert any("SKILL.md" in name for name in sample.store["skills_after"])


def test_semantic_grade_comes_from_the_grader_role(sample) -> None:  # type: ignore[no-untyped-def]
    score = _score(sample, "gauge_semantic_quality")
    assert score.value == 3.0
    assert score.metadata["parsed"] is True


def test_tool_errors_are_measured(sample) -> None:  # type: ignore[no-untyped-def]
    assert _score(sample, "gauge_tool_errors").value == 0.0


def test_a_side_effect_would_have_been_caught(sample) -> None:  # type: ignore[no-untyped-def]
    """The negative half of the floor. Re-grades the recorded run with a
    doctored after-snapshot, so the check is proven able to fail on real log
    data rather than only on a hand-made fixture."""
    from inspect_ai.solver import TaskState

    from skill_evals.gauge.scorers import _side_effect_checks
    from skill_evals.shared.trajectory import analyse

    state = TaskState(
        model="mockllm/model",  # type: ignore[arg-type]
        sample_id=CASE_ID,
        epoch=1,
        input=sample.input,
        messages=list(sample.messages),
    )
    for key, value in sample.store.items():
        state.store.set(key, value)
    doctored = dict(state.store.get("workspace_after"))
    doctored["docs/product/spec.md"] = "0" * 64
    state.store.set("workspace_after", doctored)

    failures = [c for c in _side_effect_checks(state, analyse(state.messages)) if not c.passed]
    assert [c.id for c in failures] == ["floor/workspace-unchanged"]
    assert "docs/product/spec.md" in failures[0].detail
