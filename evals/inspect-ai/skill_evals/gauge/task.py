"""The Gauge Inspect task.

Run it with:

    inspect eval skill_evals/gauge/task.py --model <provider/model>
    inspect eval skill_evals/gauge/task.py -T smoke=true --model <provider/model>

One `@task` in this file, deliberately: `inspect eval <file>` runs every task it
finds, so a separate `gauge_smoke` entry point would run the full suite beside
the smoke subset and quietly ignore `-T`. The subset is a parameter instead.

The model under evaluation is never named here — see the README for the
smoke/full split, the grader role, and epochs.
"""

from __future__ import annotations

from inspect_ai import Task, task
from inspect_ai.agent import AgentPrompt, as_solver, react
from inspect_ai.tool import bash, skill

from skill_evals.gauge.dataset import gauge_dataset
from skill_evals.gauge.scorers import (
    gauge_constraints,
    gauge_semantic_quality,
    gauge_skill_use,
    gauge_task_success,
    gauge_tool_errors,
)
from skill_evals.shared.paths import COMPOSE_FILE, GAUGE_SKILL
from skill_evals.shared.skills import load_repo_skill
from skill_evals.shared.workspace import (
    SKILLS_DIR,
    WORKSPACE,
    record_workspace_before,
    snapshotting,
)

INSTRUCTIONS = f"""You are an engineering agent working with a human on their \
codebase.

The human's repository, if they have given you one, is checked out at \
`{WORKSPACE}`, which is your working directory. It may be empty — some requests \
arrive without a checkout, and that is a fact about the situation rather than a \
problem to route around.

Skills are available to you through the `skill` tool. Consult the skill \
descriptions and use a skill when it genuinely applies to what the human asked \
for. When none applies, answer the human directly.

Your final answer is what the human sees. When a skill defines an output \
format, your final answer is that output in full — do not summarise it or \
promise it separately.
"""


@task
def gauge(
    smoke: bool = False,
    categories: str | None = None,
    message_limit: int = 40,
) -> Task:
    """Evaluate the production Gauge skill against its regression suite.

    Args:
        smoke: Run only the cheap smoke subset.
        categories: Comma-separated category filter, e.g. "canonical,routing".
        message_limit: Cap on messages per sample.
    """
    selected = (
        [name.strip() for name in categories.split(",") if name.strip()]
        if categories
        else None
    )

    # Built once and shared, so the pre-install and the tool publish identical
    # bytes into the sandbox.
    gauge_skill = load_repo_skill(GAUGE_SKILL)

    return Task(
        dataset=gauge_dataset(smoke=smoke, categories=selected),
        setup=record_workspace_before([gauge_skill]),
        # The after-snapshot is taken by a solver rather than a scorer so that
        # the side-effect evidence lands in the log itself. Scorers then read
        # the log, which is what lets `inspect score` re-grade an old run
        # against a sandbox that is long gone.
        solver=snapshotting(
            as_solver(
                react(
                    prompt=AgentPrompt(instructions=INSTRUCTIONS),
                    tools=[
                        # The real skill source, adapted only where Inspect's
                        # frontmatter schema and this repository's vendor keys
                        # disagree. Installed outside the workspace so the
                        # agent's cwd stays a faithful copy of the human's
                        # repository.
                        skill([gauge_skill], dir=SKILLS_DIR),
                        # Gauge's step 2 is bounded reconnaissance of the
                        # repository and of the skill inventory, which is shell
                        # work. `bash` can also write — deliberately. This
                        # repository's eval harness already takes the position
                        # that the point is to catch the reach, not to make it
                        # impossible, and `gauge_constraints` is what catches it.
                        bash(timeout=60),
                    ],
                )
            )
        ),
        scorer=[
            gauge_task_success(),
            gauge_skill_use(),
            gauge_constraints(),
            gauge_tool_errors(),
            gauge_semantic_quality(),
        ],
        sandbox=("docker", str(COMPOSE_FILE)),
        message_limit=message_limit,
        # A sample that errors is a finding, not a reason to lose the run.
        fail_on_error=0.25,
    )
