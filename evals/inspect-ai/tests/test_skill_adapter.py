"""The adapter that lets Inspect read this repository's real SKILL.md files.

Inspect validates skill frontmatter against the agentskills.io schema with
`additionalProperties: false`. Every skill in this repo carries
`disable-model-invocation: true`, a vendor extension the schema rejects, so
`read_skills()` fails outright on the production source. The adapter normalises
the frontmatter and nothing else; these tests pin "and nothing else".
"""

from __future__ import annotations

import shutil

import pytest
from inspect_ai.tool import read_skills

from skill_evals.shared.paths import GAUGE_SKILL
from skill_evals.shared.skills import UnknownFrontmatterKey, load_repo_skill


def test_inspect_cannot_read_the_production_skill_unaided() -> None:
    """The reason this adapter exists. If this ever passes, delete the adapter."""
    with pytest.raises(Exception) as excinfo:
        read_skills([GAUGE_SKILL])
    assert "disable-model-invocation" in str(excinfo.value)


def test_loads_gauge_from_the_real_source() -> None:
    skill = load_repo_skill(GAUGE_SKILL)
    assert skill.name == "gauge"
    assert skill.description.startswith("Assess an intent before planning")


def test_instructions_are_the_real_body_verbatim() -> None:
    skill = load_repo_skill(GAUGE_SKILL)
    body = (GAUGE_SKILL / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[2]
    assert skill.instructions == body.lstrip("\n")


def test_references_point_at_the_production_files_not_copies() -> None:
    skill = load_repo_skill(GAUGE_SKILL)
    assert set(skill.references) == {
        "routing-model.md",
        "planning-registry.md",
        "recipe-contract.md",
        "evaluation-scenarios.md",
        "model-registry.md",
    }
    for path in skill.references.values():
        assert GAUGE_SKILL in path.parents  # type: ignore[union-attr]


def test_vendor_frontmatter_is_preserved_rather_than_dropped() -> None:
    """`disable-model-invocation` is load-bearing (ADR 0002 keys composition on
    it). It survives into `metadata`, which round-trips into the sandbox
    SKILL.md, so the evaluated agent still sees that Gauge is user-invoked."""
    skill = load_repo_skill(GAUGE_SKILL)
    assert skill.metadata == {"disable-model-invocation": True}
    assert "disable-model-invocation" in skill.skill_md()



def test_an_unrecognised_frontmatter_key_is_an_error() -> None:
    """Silently dropping a key we have not thought about is how the evaluated
    skill drifts from the shipped one without anybody noticing."""
    with pytest.raises(UnknownFrontmatterKey, match="tentacles"):
        load_repo_skill(GAUGE_SKILL, _extra_frontmatter={"tentacles": 7})


def test_adapter_output_matches_inspects_own_reader(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """Anti-drift pin: the adapter enumerates scripts/references/assets itself.
    Materialise a schema-clean copy, let Inspect read *that*, and require the
    two to agree — so an upstream change to Inspect's enumeration rules is a
    test failure rather than a silent divergence."""
    adapted = load_repo_skill(GAUGE_SKILL)

    clean = tmp_path / "gauge"
    shutil.copytree(GAUGE_SKILL, clean)
    (clean / "SKILL.md").write_text(adapted.skill_md(), encoding="utf-8")
    native = read_skills([clean])[0]

    assert native.name == adapted.name
    assert native.description == adapted.description
    assert native.instructions == adapted.instructions
    assert set(native.references) == set(adapted.references)
    assert set(native.scripts) == set(adapted.scripts)
    assert set(native.assets) == set(adapted.assets)
