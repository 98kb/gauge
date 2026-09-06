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


def _section(text: str, heading: str) -> str:
    match = re.search(
        rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise ValueError(f"{REGISTRY_FILE} has no '## {heading}' section")
    return match.group(1)


def _skills() -> frozenset[str]:
    return _parse()[0]


REGISTRY_SKILLS: frozenset[str] = _skills()
"""Every canonical skill name the registry knows, bindable or dependency."""

REQUIRED_DEPENDENCIES: dict[str, frozenset[str]] = _parse()[1]
"""Entry point -> the dependencies a recipe must list whenever it binds it."""

PROHIBITED_AS_STEP: frozenset[str] = _parse()[2]
"""Skills the registry bars from appearing as a recipe step."""


def registry_path() -> Path:
    return REGISTRY_FILE
