"""Read this repository's real SKILL.md files as Inspect `Skill` objects.

Inspect validates skill frontmatter against the agentskills.io schema with
`additionalProperties: false`. Every skill here carries the vendor extension
`disable-model-invocation: true`, so `inspect_ai.tool.read_skills()` raises on
the production source. Rewriting the skills to suit Inspect would change what
users receive, so the adaptation happens on this side of the boundary.

The adapter does exactly two things: it moves vendor-only frontmatter keys into
the spec's own `metadata` field (which round-trips into the SKILL.md written
into the sandbox, so nothing is lost), and it refuses to guess about a key it
has never seen.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from inspect_ai.tool import Skill

#: Keys the agentskills.io schema defines. Passed through untouched.
SPEC_KEYS = frozenset(
    {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
)

#: Vendor extensions this repository uses. Relocated into `metadata`.
VENDOR_KEYS = frozenset({"disable-model-invocation"})


class UnknownFrontmatterKey(ValueError):
    """A SKILL.md frontmatter key the adapter has no policy for.

    Deliberately fatal. A dropped key is a silent difference between the skill
    under evaluation and the skill users install.
    """


def load_repo_skill(
    skill_dir: str | Path,
    *,
    _extra_frontmatter: dict[str, Any] | None = None,
) -> Skill:
    """Load `<skill_dir>/SKILL.md` and its supporting files as an Inspect `Skill`.

    Args:
        skill_dir: Directory of a production skill. Read, never written.
        _extra_frontmatter: Test seam — merged over the parsed frontmatter to
            exercise the unknown-key path without editing a real skill.

    Raises:
        FileNotFoundError: No SKILL.md in `skill_dir`.
        UnknownFrontmatterKey: Frontmatter carries a key with no policy.
    """
    root = Path(skill_dir).resolve()
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        raise FileNotFoundError(f"No SKILL.md in {root}")

    frontmatter, instructions = _split_frontmatter(skill_md.read_text(encoding="utf-8"))
    frontmatter.update(_extra_frontmatter or {})

    unknown = sorted(set(frontmatter) - SPEC_KEYS - VENDOR_KEYS)
    if unknown:
        raise UnknownFrontmatterKey(
            f"{skill_md}: no adapter policy for frontmatter key(s) {unknown}. "
            f"Add each to SPEC_KEYS or VENDOR_KEYS in {__name__} once you have "
            f"decided what it means for an evaluated skill."
        )

    metadata: dict[str, Any] = dict(frontmatter.get("metadata") or {})
    metadata.update(
        {key: frontmatter[key] for key in sorted(VENDOR_KEYS & set(frontmatter))}
    )

    return Skill(
        name=frontmatter["name"],
        description=frontmatter["description"],
        instructions=instructions,
        scripts=_enumerate(root / "scripts"),
        references=_enumerate(root / "references"),
        assets=_enumerate(root / "assets"),
        license=frontmatter.get("license"),
        compatibility=frontmatter.get("compatibility"),
        metadata=metadata or None,
        **{"allowed-tools": frontmatter.get("allowed-tools")},
    )


def _split_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    parsed = yaml.safe_load(parts[1].strip())
    return (parsed if isinstance(parsed, dict) else {}), parts[2].lstrip("\n")


def _enumerate(directory: Path) -> dict[str, str | bytes | Path]:
    """Map relative path -> absolute path for every file under `directory`.

    Mirrors Inspect's own rule: recursive, files only, skipping any path
    component starting with `.` or `_`. The adapter/native comparison test is
    what keeps the two in step.
    """
    if not directory.is_dir():
        return {}
    found: dict[str, str | bytes | Path] = {}
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(directory)
        if any(part.startswith((".", "_")) for part in relative.parts):
            continue
        found[str(relative)] = path.absolute()
    return found
