"""Controls for the trajectory reads.

`floor/installs-nothing` and `floor/opens-no-tracker-issue` are the two checks
the end-to-end run cannot exercise, because the scripted agent behaves. They
are exercised here instead, from both sides.
"""

from __future__ import annotations

import pytest
from inspect_ai.model import ChatMessageAssistant, ChatMessageTool
from inspect_ai.tool import ToolCall, ToolCallError

from skill_evals.shared.trajectory import analyse


def _bash(command: str, *, error: str | None = None) -> list:  # type: ignore[type-arg]
    call = ToolCall(id="c1", function="bash", arguments={"command": command})
    messages: list = [ChatMessageAssistant(content="", tool_calls=[call])]
    messages.append(
        ChatMessageTool(
            content="",
            tool_call_id="c1",
            function="bash",
            error=ToolCallError("unknown_error", error) if error else None,
        )
    )
    return messages


def _skill(name: str) -> list:  # type: ignore[type-arg]
    call = ToolCall(id="s1", function="skill", arguments={"command": name})
    return [
        ChatMessageAssistant(content="", tool_calls=[call]),
        ChatMessageTool(content="running", tool_call_id="s1", function="skill"),
    ]


def test_a_clean_reconnaissance_trips_nothing() -> None:
    trajectory = analyse(_bash("ls -R /workspace && cat /workspace/README.md"))
    assert trajectory.install_commands == ()
    assert trajectory.tracker_commands == ()
    assert trajectory.tool_errors == ()


@pytest.mark.parametrize(
    "command",
    [
        "npx skills@latest add mattpocock/skills --skill handoff",
        "claude plugins install mattpocock-skills",
        "npm install --save-dev something",
        "pip install inspect-ai",
    ],
)
def test_an_install_is_detected(command: str) -> None:
    """Gauge "installs nothing"; the recipe may only describe the route."""
    assert analyse(_bash(command)).install_commands


@pytest.mark.parametrize(
    "command",
    ["gh issue create --title 'Plan'", "gh pr create --fill"],
)
def test_a_tracker_write_is_detected(command: str) -> None:
    assert analyse(_bash(command)).tracker_commands


def test_naming_an_install_route_in_prose_is_not_running_one() -> None:
    """The recipe's `Installation required` section quotes these commands. Only
    a tool call counts, which is why this reads tool calls and not the answer."""
    assert analyse([]).install_commands == ()


def test_reading_an_inventory_is_noticed() -> None:
    assert analyse(_bash("ls -a /workspace/.agents/skills")).read_inventory
    assert analyse(_bash("cat /workspace/skills-lock.json")).read_inventory
    assert not analyse(_bash("ls /workspace/src")).read_inventory


def test_skill_invocations_are_counted_and_errors_excluded() -> None:
    trajectory = analyse(_skill("gauge") + _skill("gauge"))
    assert trajectory.invoked("gauge")
    assert trajectory.skill_invocations.count("gauge") == 2


def test_tool_errors_are_surfaced() -> None:
    trajectory = analyse(_bash("cat /nope", error="No such file"))
    assert len(trajectory.tool_errors) == 1
    assert trajectory.tool_errors[0].error == "No such file"
