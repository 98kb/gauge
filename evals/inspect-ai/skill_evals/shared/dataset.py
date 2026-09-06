"""Load a JSONL case file into Inspect `Sample`s.

Generic: it knows about ids, categories, fixtures and a smoke subset, and
nothing about any particular skill. A second skill's suite reuses this by
pointing it at its own cases file and fixtures directory.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

from inspect_ai.dataset import MemoryDataset, Sample

from skill_evals.shared.workspace import fixture_files

#: Keys a case record may carry. An unrecognised key is a typo or an
#: expectation nothing reads; either way it is an error, never a silent drop.
CASE_KEYS = frozenset(
    {
        "id",
        "category",
        "difficulty",
        "smoke",
        "input",
        "fixture",
        "installed_skills",
        "expect",
        "requirements",
        "forbidden",
        "notes",
    }
)

REQUIRED_KEYS = frozenset({"id", "category", "difficulty", "input", "expect"})


class CaseError(ValueError):
    """A case record the harness will not run."""


def load_cases(path: Path) -> list[dict[str, Any]]:
    """Parse and validate a JSONL case file, in file order."""
    cases: list[dict[str, Any]] = []
    seen: set[str] = set()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        try:
            case = json.loads(stripped)
        except json.JSONDecodeError as ex:
            raise CaseError(f"{path}:{number}: {ex}") from ex

        missing = sorted(REQUIRED_KEYS - set(case))
        if missing:
            raise CaseError(f"{path}:{number}: case is missing {missing}")
        unknown = sorted(set(case) - CASE_KEYS)
        if unknown:
            raise CaseError(
                f"{path}:{number}: unrecognised case key(s) {unknown}; "
                f"known keys are {sorted(CASE_KEYS)}"
            )
        if case["id"] in seen:
            raise CaseError(f"{path}:{number}: duplicate case id {case['id']!r}")
        seen.add(case["id"])
        cases.append(case)

    if not cases:
        raise CaseError(f"{path}: no cases")
    return cases


def build_dataset(
    cases_file: Path,
    fixtures_dir: Path,
    *,
    smoke: bool = False,
    categories: Iterable[str] | None = None,
    validate: Callable[[dict[str, Any]], None] | None = None,
) -> MemoryDataset:
    """Turn a case file into a dataset, optionally narrowed.

    Args:
        cases_file: JSONL of case records.
        fixtures_dir: Root the `fixture` field resolves against.
        smoke: Keep only cases flagged `"smoke": true`.
        categories: Keep only these categories.
        validate: Per-case check run at load time — a suite's own contract, so
            a malformed expectation fails before any model is called.
    """
    cases = load_cases(cases_file)
    if validate is not None:
        for case in cases:
            validate(case)

    wanted = set(categories) if categories is not None else None
    selected = [
        case
        for case in cases
        if (not smoke or case.get("smoke", False))
        and (wanted is None or case["category"] in wanted)
    ]
    if not selected:
        raise CaseError(
            f"{cases_file}: no cases match "
            f"(smoke={smoke}, categories={sorted(wanted) if wanted else 'all'})"
        )

    return MemoryDataset(
        samples=[_sample(case, fixtures_dir) for case in selected],
        name=cases_file.stem,
        location=str(cases_file),
    )


def _sample(case: dict[str, Any], fixtures_dir: Path) -> Sample:
    fixture = case.get("fixture")
    metadata = {key: value for key, value in case.items() if key not in ("id", "input")}
    return Sample(
        id=case["id"],
        input=case["input"],
        files=fixture_files(fixtures_dir / fixture if fixture else None),
        metadata=metadata,
    )
