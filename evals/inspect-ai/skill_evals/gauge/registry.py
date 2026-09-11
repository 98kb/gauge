"""The planning registry, read from Gauge's own reference file.

`references/planning-registry.md` is described in the skill as "the
authoritative, human-edited binding source". Hard-coding a copy of it here
would give the eval a second opinion about which skills exist, and the two
would drift the first time a maintainer edits the real one. So the checks parse
it instead: adding a registry entry changes what the eval accepts, with no edit
to this harness.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from skill_evals.shared.paths import GAUGE_SKILL

REGISTRY_FILE = GAUGE_SKILL / "references" / "planning-registry.md"

_BACKTICKED = re.compile(r"`([a-z0-9][a-z0-9-]*)`")
_ENTRY_HEADING = re.compile(r"^###\s+`([a-z0-9][a-z0-9-]*)`\s*$", re.MULTILINE)


def _registry_text() -> str:
    return REGISTRY_FILE.read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _parse() -> tuple[frozenset[str], dict[str, frozenset[str]], frozenset[str]]:
    text = _registry_text()

    names: set[str] = set(_ENTRY_HEADING.findall(text))
    dependencies: dict[str, frozenset[str]] = {}

    for row in _binding_rows(text):
        _capability, skill_cell, deps_cell = row[0], row[1], row[2]
        skills = _BACKTICKED.findall(skill_cell)
        if not skills:
            # "no planning skill" — a binding outcome, not a skill name.
            continue
        skill = skills[0]
        names.add(skill)
        dependencies[skill] = _required_dependencies(deps_cell)

    return frozenset(names), dependencies, _prohibited(text)


def _binding_rows(text: str) -> list[list[str]]:
    """Rows of the `## Recipe bindings` table, as trimmed cell lists."""
    section = _section(text, "Recipe bindings")
    rows: list[list[str]] = []
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 3 or set("".join(cells)) <= set("- :"):
            continue  # header separator
        if cells[0].lower().startswith("capability"):
            continue  # header
        rows.append(cells)
    return rows


def _required_dependencies(cell: str) -> frozenset[str]:
    """Dependencies a recipe must expand whenever the entry point is bound.

    Only the part before the first `;` counts. `wayfinder`'s cell reads
    "`grilling`, `domain-modeling`; `research` and `prototype` as ticket types
    require" — the clause after the semicolon is conditional on what the map
    turns up, so it is not something every binding owes.
    """
    head = cell.split(";", 1)[0]
    if "none" in head.lower() and not _BACKTICKED.search(head):
        return frozenset()
    return frozenset(_BACKTICKED.findall(head))


def _prohibited(text: str) -> frozenset[str]:
    """Skills the `## Exclusions` section bars from appearing as a recipe step."""
    section = _section(text, "Exclusions")
    barred: set[str] = set()
    for line in section.splitlines():
        if not line.strip().startswith("-"):
            continue
        if "prohibited" not in line:
            continue
        barred.update(_BACKTICKED.findall(line.split(":", 1)[0]))
    return frozenset(barred)


def _section(text: str, heading: str, source: Path = REGISTRY_FILE) -> str:
    match = re.search(
        rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise ValueError(f"{source} has no '## {heading}' section")
    return match.group(1)


def _skills() -> frozenset[str]:
    return _parse()[0]


def _skill_capabilities() -> dict[str, str]:
    """Entry-point skill -> the capability the binding table binds it to."""
    mapping: dict[str, str] = {}
    for row in _binding_rows(_registry_text()):
        capabilities = _CODE_SPAN.findall(row[0])
        skills = _BACKTICKED.findall(row[1])
        if capabilities and skills:
            mapping[str(skills[0])] = str(capabilities[0])
    return mapping


def _planning_capabilities() -> frozenset[str]:
    return frozenset(
        match
        for row in _binding_rows(_registry_text())
        for match in _CODE_SPAN.findall(row[0])[:1]
    )


# --- model registry -----------------------------------------------------------
#
# `references/model-registry.md` is the second human-edited authority (ADR 0017):
# model profiles and the capability bindings that select them. It is parsed for
# the same reason the planning registry is — a Python copy would be a second
# opinion that drifts the first time a maintainer edits the real file.

MODEL_REGISTRY_FILE = GAUGE_SKILL / "references" / "model-registry.md"

_CODE_SPAN = re.compile(r"`([^`]+)`")
_UNBOUND = "unbound"


@dataclass(frozen=True)
class ModelProfile:
    """One canonical pinned model ID plus one reasoning effort it supports."""

    key: str
    model: str
    effort: str
    supported: frozenset[str]


@dataclass(frozen=True)
class ModelRegistry:
    profiles: dict[str, ModelProfile]
    #: (capability, high_assurance) -> profile key, or None for `unbound`.
    bindings: dict[tuple[str, bool], str | None]

    def binding(self, capability: str, *, high_assurance: bool) -> ModelProfile | None:
        """The profile a boundary must recommend, or None for a model registry gap.

        A High-assurance boundary reads only its own row: an unbound one is a
        gap even when a base binding exists (ADR 0017 forbids the fallback).
        """
        key = self.bindings.get((capability, high_assurance))
        return self.profiles[key] if key is not None else None


def parse_model_registry(text: str, source: Path = MODEL_REGISTRY_FILE) -> ModelRegistry:
    """Parse the Profiles and Bindings tables, rejecting anything malformed.

    Validation is strict on purpose: a typo in a binding cell must not read as
    an intentional `unbound` gap, and a profile must never pair a model with an
    effort that model does not support.
    """
    profiles: dict[str, ModelProfile] = {}
    for row in _table(_section(text, "Profiles", source)):
        key = _code(row, "profile", source)
        supported = frozenset(_CODE_SPAN.findall(row.get("supported effort values", "")))
        profile = ModelProfile(
            key=key,
            model=_code(row, "model id", source),
            effort=_code(row, "reasoning effort", source),
            supported=supported,
        )
        if profile.effort not in supported:
            raise ValueError(
                f"{source}: profile {key!r} pairs {profile.model} with effort "
                f"{profile.effort!r}, which it does not support ({sorted(supported)})"
            )
        profiles[key] = profile

    bindings: dict[tuple[str, bool], str | None] = {}
    for row in _table(_section(text, "Bindings", source)):
        cells = list(row.values())
        capability = _CODE_SPAN.findall(cells[0])
        if not capability:
            raise ValueError(f"{source}: binding row {cells[0]!r} names no capability")
        for column, high_assurance in (("base", False), ("high-assurance", True)):
            bindings[(capability[0], high_assurance)] = _binding_cell(
                row.get(column, ""), profiles, source
            )

    return ModelRegistry(profiles=profiles, bindings=bindings)


def _binding_cell(cell: str, profiles: dict[str, ModelProfile], source: Path) -> str | None:
    if cell.strip().lower() == _UNBOUND:
        return None
    keys = _CODE_SPAN.findall(cell)
    if len(keys) != 1:
        raise ValueError(
            f"{source}: binding cell {cell!r} is neither a profile nor `{_UNBOUND}`"
        )
    key = str(keys[0])
    if key not in profiles:
        raise ValueError(f"{source}: binding names unknown profile {key!r}")
    return key


def _table(section: str) -> list[dict[str, str]]:
    """The first Markdown table in `section`, as rows keyed by plain header."""
    header: list[str] | None = None
    rows: list[dict[str, str]] = []
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            if header is not None and rows:
                break
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if set("".join(cells)) <= set("- :"):
            continue  # header separator
        if header is None:
            header = [cell.replace("`", "").strip().lower() for cell in cells]
            continue
        rows.append(dict(zip(header, cells, strict=False)))
    return rows


def _code(row: dict[str, str], column: str, source: Path) -> str:
    found = _CODE_SPAN.findall(row.get(column, ""))
    if len(found) != 1:
        raise ValueError(f"{source}: column {column!r} must hold one code span, got {row!r}")
    return str(found[0])


REGISTRY_SKILLS: frozenset[str] = _skills()
"""Every canonical skill name the registry knows, bindable or dependency."""

REQUIRED_DEPENDENCIES: dict[str, frozenset[str]] = _parse()[1]
"""Entry point -> the dependencies a recipe must list whenever it binds it."""

PROHIBITED_AS_STEP: frozenset[str] = _parse()[2]
"""Skills the registry bars from appearing as a recipe step."""

PLANNING_CAPABILITIES: frozenset[str] = _planning_capabilities()
"""Every capability the planning registry's binding table names."""

SKILL_CAPABILITIES: dict[str, str] = _skill_capabilities()
"""Entry-point skill -> the capability the planning registry binds it to."""

MODEL_REGISTRY: ModelRegistry = parse_model_registry(
    MODEL_REGISTRY_FILE.read_text(encoding="utf-8")
)
"""Model profiles and their capability bindings, from the production reference."""


def registry_path() -> Path:
    return REGISTRY_FILE
