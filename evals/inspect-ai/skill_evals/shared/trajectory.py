"""What the agent actually did, read from the recorded messages.

Nothing here asks a judge to guess at behaviour that the log already states
exactly. Every function is a pure read over `TaskState.messages`, so these
scorers survive `inspect score` on a committed `.eval` log.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from inspect_ai.model import ChatMessage, ChatMessageAssistant, ChatMessageTool

#: Where an agent can read a skill inventory, per the planning registry's
#: "Evidence that counts as an inventory".
INVENTORY_LOCATIONS = (
    ".claude/skills",
    ".codex/skills",
    ".agents/skills",
    "skills-lock.json",
)

#: Commands that install something. Gauge "installs nothing".
_INSTALL_COMMAND = re.compile(
    r"\b(npx\s+skills|claude\s+plugins?\s+install|/plugin\s+install|npm\s+(i|install)\b|pnpm\s+add\b|yarn\s+add\b|pip\s+install\b|uv\s+pip\s+install\b)",
    re.I,
)

#: Commands that write to a tracker. Gauge "opens no tracker issue".
_TRACKER_COMMAND = re.compile(r"\bgh\s+(issue|pr)\s+(create|edit|comment|close)\b", re.I)


@dataclass(frozen=True)
class ToolUse:
    name: str
    arguments: dict[str, object]
    error: str | None


@dataclass(frozen=True)
class Trajectory:
    """The trajectory facts the scorers grade, extracted once."""

    tool_uses: tuple[ToolUse, ...]
    skill_invocations: tuple[str, ...]
    read_inventory: bool
    install_commands: tuple[str, ...]
    tracker_commands: tuple[str, ...]

    @property
    def tool_errors(self) -> tuple[ToolUse, ...]:
        return tuple(use for use in self.tool_uses if use.error)

    @property
    def redundant_tool_calls(self) -> int:
        """Calls repeating an earlier one with byte-identical arguments.

        Objectively wasted work. Whether a *distinct* call was necessary is a
        judgement, so it is left to the rubric rather than asserted here.
        """
        seen: set[tuple[str, str]] = set()
        repeats = 0
        for use in self.tool_uses:
            key = (use.name, repr(sorted(use.arguments.items())))
            if key in seen:
                repeats += 1
            seen.add(key)
        return repeats

    def invoked(self, skill: str) -> bool:
        return skill in self.skill_invocations


def analyse(messages: list[ChatMessage]) -> Trajectory:
    """Extract the trajectory facts from a sample's message history."""
    errors = {
        message.tool_call_id: _tool_error(message)
        for message in messages
        if isinstance(message, ChatMessageTool) and message.tool_call_id
    }

    uses: list[ToolUse] = []
    for message in messages:
        if not isinstance(message, ChatMessageAssistant) or not message.tool_calls:
            continue
        for call in message.tool_calls:
            uses.append(
                ToolUse(
                    name=call.function,
                    arguments=dict(call.arguments or {}),
                    error=errors.get(call.id),
                )
            )

    skills = tuple(
        str(use.arguments.get("command", "")).strip()
        for use in uses
        if use.name == "skill" and not use.error
    )

    # A call that errored established nothing. A failed `ls .agents/skills` is
    # not evidence that an inventory was read, and treating it as such would
    # promote the registry's `unknown` into a declared inventory.
    succeeded = [use for use in uses if not use.error]

    # Only the arguments that are actually a command. Including `pattern`/`path`
    # meant `grep -rn "pip install" .` read as having run an install.
    haystack = "\n".join(
        text for text in (_command_text(use) for use in succeeded) if text
    )
    paths = [text for text in (_referenced_paths(use) for use in succeeded) if text]

    return Trajectory(
        tool_uses=tuple(uses),
        skill_invocations=tuple(s for s in skills if s),
        read_inventory=any(
            location in text
            for text in [*paths, haystack]
            for location in INVENTORY_LOCATIONS
        ),
        install_commands=tuple(_matching(_INSTALL_COMMAND, haystack)),
        tracker_commands=tuple(_matching(_TRACKER_COMMAND, haystack)),
    )


def _matching(pattern: re.Pattern[str], text: str) -> list[str]:
    return [match.group(0) for match in pattern.finditer(text)]


#: Arguments that carry something the sandbox will execute.
_COMMAND_ARGS = ("cmd", "command", "code", "input")

#: Arguments that merely name a location the agent looked at.
_PATH_ARGS = ("path", "file", "dir", "directory")


def _command_text(use: ToolUse) -> str | None:
    """The part of a tool call that will actually be run."""
    parts = [str(value) for key, value in use.arguments.items() if key in _COMMAND_ARGS]
    return " ".join(parts) if parts else None


def _referenced_paths(use: ToolUse) -> str | None:
    """The locations a tool call named, without anything it executes."""
    parts = [str(value) for key, value in use.arguments.items() if key in _PATH_ARGS]
    return " ".join(parts) if parts else None


def _tool_error(message: ChatMessageTool) -> str | None:
    if message.error is not None:
        return message.error.message or message.error.type
    return None
