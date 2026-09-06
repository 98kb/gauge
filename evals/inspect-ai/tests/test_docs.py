"""The README documents lists that live in code. Pin them so they cannot drift.

A README that quietly goes stale is the documentation version of a check that
cannot fail: it reads as authoritative while asserting nothing. The extension
guide tells a reader which expectation keys exist and which categories are
legal, so adding one to the code and not the prose has to be a test failure.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from skill_evals.gauge.dataset import CATEGORIES
from skill_evals.gauge.expectations import CATALOGUE

INSPECT_ROOT = Path(__file__).resolve().parents[1]
README = INSPECT_ROOT / "README.md"
GAUGE_README = INSPECT_ROOT / "skill_evals" / "gauge" / "README.md"


@pytest.fixture(scope="module")
def readme() -> str:
    return README.read_text(encoding="utf-8")


def test_readme_lists_every_expectation_key(readme: str) -> None:
    block = re.search(r"Expectation keys: (.+?)\n\n", readme, re.S)
    assert block, "the extension guide no longer lists the expectation keys"
    documented = set(re.findall(r"`([a-z_]+)`", block.group(1)))
    assert documented == set(CATALOGUE), {
        "undocumented": sorted(set(CATALOGUE) - documented),
        "stale": sorted(documented - set(CATALOGUE)),
    }


def test_readme_lists_every_case_category(readme: str) -> None:
    row = re.search(r"\| `category` \| one of (.+?) \|", readme)
    assert row, "the case-field table no longer lists the categories"
    documented = set(row.group(1).replace(",", " ").split())
    assert documented == set(CATEGORIES)


@pytest.mark.parametrize("doc", [README, GAUGE_README], ids=["readme", "gauge-readme"])
def test_relative_links_resolve(doc: Path) -> None:
    broken = [
        target
        for target in re.findall(r"\]\(([^)#][^)]*)\)", doc.read_text(encoding="utf-8"))
        if not target.startswith("http")
        and not (doc.parent / target.split("#")[0]).exists()
    ]
    assert not broken, broken


def test_documented_run_subcommands_exist(readme: str) -> None:
    """Every `./run.sh <cmd>` the README shows must be a case in run.sh."""
    script = (INSPECT_ROOT / "run.sh").read_text(encoding="utf-8")
    handled = set()
    for line in script.splitlines():
        match = re.match(r"\s{2}([a-z:|]+)\)$", line)
        if match:
            handled.update(match.group(1).split("|"))

    shown = set(re.findall(r"\./run\.sh ([a-z:]+)", readme))
    assert shown <= handled, sorted(shown - handled)
