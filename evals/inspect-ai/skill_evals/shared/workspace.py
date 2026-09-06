"""Fixture workspaces, and proof that a read-only skill left them alone.

Two jobs. Before the run, turn a fixture directory into the `files` mapping a
`Sample` copies into its sandbox — the eval never points an agent at the real
checkout, so no case can mutate the repository it is being run from. After the
run, hash the sandbox trees and record the result **into the sample store**, so
the side-effect scorer reads the log rather than a sandbox that no longer
exists. That is what keeps `inspect score` able to re-grade an old `.eval`.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from inspect_ai.solver import Generate, Solver, TaskState, solver
from inspect_ai.tool import Skill, install_skills
from inspect_ai.util import sandbox

#: Where a fixture is copied to, and the agent's working directory.
WORKSPACE = "/workspace"

#: Where Inspect installs the skills under evaluation. Deliberately outside
#: `WORKSPACE`: installing into the agent's cwd would both pollute the fixture
#: and hand Gauge a `skills/` directory that no real repository has.
SKILLS_DIR = "/opt/skills"

_BEFORE = "workspace_before"
_AFTER = "workspace_after"
_SKILLS_BEFORE = "skills_before"
_SKILLS_AFTER = "skills_after"


def fixture_files(fixture: Path | None) -> dict[str, str]:
    """Map every file under `fixture` to its destination in the sandbox.

    Returns an empty mapping for `None`, which is how a case models "no
    repository is reachable" without any special casing downstream.
    """
    if fixture is None:
        return {}
    if not fixture.is_dir():
        raise FileNotFoundError(f"No such fixture: {fixture}")
    return {
        f"{WORKSPACE}/{path.relative_to(fixture).as_posix()}": str(path.resolve())
        for path in sorted(fixture.rglob("*"))
        if path.is_file()
    }


async def _hash_tree(root: str) -> dict[str, str]:
    """`relative path -> sha256` for every file under `root` in the sandbox."""
    result = await sandbox().exec(
        [
            "sh",
            "-c",
            f"[ -d {root} ] && cd {root} && find . -type f -exec sha256sum {{}} + | sort || true",
        ],
        timeout=120,
    )
    tree: dict[str, str] = {}
    for line in result.stdout.splitlines():
        digest, _, name = line.partition("  ")
        if digest and name:
            tree[name.removeprefix("./")] = digest
    return tree


@solver
def record_workspace_before(skills: Sequence[Skill] = ()) -> Solver:
    """Task `setup` step: hash the trees the agent must not modify.

    The skills are installed here rather than left to the `skill()` tool's own
    lazy install on first call. Otherwise the harness writing the skill into the
    sandbox lands *between* the two snapshots and reads as the agent having
    created those files — which is exactly the finding the floor exists to
    report, arriving on every single sample. Installing the same bytes twice is
    harmless; the tool's later install is a no-op against these hashes.
    """

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        if skills:
            await install_skills(skills, dir=SKILLS_DIR)
        state.store.set(_BEFORE, await _hash_tree(WORKSPACE))
        state.store.set(_SKILLS_BEFORE, await _hash_tree(SKILLS_DIR))
        return state

    return solve


@solver
def snapshotting(inner: Solver) -> Solver:
    """Run `inner`, then hash the trees again — even if `inner` blew a limit.

    This wraps rather than following the agent in a solver chain. A sample that
    exceeds its message or token limit raises, and a chained step after the
    agent simply never runs: the after-snapshot goes missing on exactly the
    samples where a runaway agent is most likely to have written something. The
    `finally` is the whole point, and the sandbox is still alive here because
    teardown happens after scoring.
    """

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        try:
            return await inner(state, generate)
        finally:
            state.store.set(_AFTER, await _hash_tree(WORKSPACE))
            state.store.set(_SKILLS_AFTER, await _hash_tree(SKILLS_DIR))

    return solve


def workspace_changes(state: TaskState) -> dict[str, list[str]]:
    """Files created, deleted or modified across the run.

    Reads only the store, so it works identically live and on re-score. The
    skills tree is reported separately because editing the planning registry is
    a different finding from writing into the project.
    """
    return {
        **_diff("workspace", state.store.get(_BEFORE, {}), state.store.get(_AFTER, {})),
        **_diff(
            "skills",
            state.store.get(_SKILLS_BEFORE, {}),
            state.store.get(_SKILLS_AFTER, {}),
        ),
    }


def _diff(label: str, before: dict[str, str], after: dict[str, str]) -> dict[str, list[str]]:
    return {
        f"{label}_created": sorted(set(after) - set(before)),
        f"{label}_deleted": sorted(set(before) - set(after)),
        f"{label}_modified": sorted(
            name for name in set(before) & set(after) if before[name] != after[name]
        ),
    }


def snapshot_recorded(state: TaskState) -> bool:
    """Whether both snapshots exist.

    Without them the side-effect scorer has nothing to compare and must say so
    rather than reporting a clean run.
    """
    return state.store.get(_BEFORE) is not None and state.store.get(_AFTER) is not None
