# Set Up Inspect AI Evals for the `/gauge` Skill

## Objective

Set up a reliable, repeatable evaluation harness for this monorepo using **Inspect AI**, starting with the `/gauge` skill.

The repository contains multiple installable agent skills in a monorepo structure. Skills may be installed/consumed using the repository's existing npm-based skills workflow. Do **not** redesign the skill packaging system. Add evaluation infrastructure alongside it.

The first target is `/gauge`, but the eval architecture must make it straightforward to add evals for other skills later without duplicating infrastructure.

Treat this document as an implementation task. Inspect the repository first, adapt paths/names to the actual repo, implement the setup, add a small but meaningful Gauge eval suite, and document how to run it.

> Naming note: this task assumes the skill is named **Gauge** and is invoked/referenced as `/gauge`. If the actual directory/package is named `kage`, preserve the repository's real naming instead of renaming it.

---

## Desired Outcome

After implementation, a developer should be able to run something conceptually equivalent to:

```bash
# from repo root
npm run eval:gauge
```

or, if the repo uses another package manager:

```bash
pnpm eval:gauge
# or
yarn eval:gauge
```

The command should:

1. create/use an isolated Python environment for Inspect AI;
2. execute the Gauge skill against a deterministic eval dataset;
3. save Inspect `.eval` logs in a predictable repo-local location;
4. report per-sample results and aggregate metrics;
5. return a non-zero exit status when required quality gates fail, if practical with the repo's CI conventions;
6. make it easy to inspect failures using `inspect view`.

The setup must be suitable for local development and CI.

---

# 1. First Inspect the Repository

Before changing files, determine:

- package manager (`npm`, `pnpm`, `yarn`, etc.);
- workspace/monorepo configuration;
- where skills live;
- the exact path of the Gauge skill;
- how `npm skills` or the existing skill installation mechanism works;
- whether skills use a standard `SKILL.md`-style directory format;
- how an agent currently discovers/invokes `/gauge`;
- whether the Gauge skill requires shell access, files, network access, or other tools;
- existing test/eval conventions;
- existing Python tooling, if any;
- CI provider and current test commands.

Do not introduce a second competing monorepo/package convention.

If Gauge can be evaluated directly from its source skill directory, prefer that over publishing/installing a package during every eval run. The eval must test the same skill content that users/agents receive.

---

# 2. Architectural Principle

Keep the production skill implementation independent from the evaluation harness.

Use this separation:

```text
repository
│
├── skills/
│   ├── gauge/                 # real production skill
│   ├── another-skill/
│   └── ...
│
├── evals/
│   ├── pyproject.toml
│   ├── gauge/
│   │   ├── task.py
│   │   ├── dataset/
│   │   ├── scorers.py
│   │   └── README.md
│   └── shared/
│       ├── ...
│
└── package.json
```

Adapt names to the actual repo. A structure such as `packages/skills/gauge`, `.evals/`, or `tests/evals/` is also acceptable if it better matches existing conventions.

**Do not copy Gauge into the eval directory.** Reference the real skill source.

---

# 3. Use Inspect AI as the Eval Harness

Use current **Inspect AI** (`inspect-ai`) rather than writing a custom eval runner.

Create a small Python eval project, preferably under `evals/`, with a `pyproject.toml`.

A minimal dependency declaration should be along these lines:

```toml
[project]
name = "repo-skill-evals"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "inspect-ai",
]
```

Pin versions according to the repository's dependency policy. If reproducibility is important, commit the appropriate Python lock file.

Do not globally install Inspect as part of normal repo usage.

Useful upstream commands:

```bash
pip install inspect-ai
inspect eval ...
inspect view
```

Inspect writes an eval log for each task. Keep these under a repo-local ignored directory such as:

```text
evals/logs/
```

Do not commit generated `.eval` logs by default.

---

# 4. Evaluate Gauge as a Real Skill

Prefer Inspect's native skill support where compatible with the Gauge skill format.

Current Inspect provides:

```python
from inspect_ai.tool import skill
```

with a skill tool that can make one or more skill directories available to the evaluated agent.

Conceptually:

```python
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.solver import react
from inspect_ai.tool import bash, skill

REPO_ROOT = Path(__file__).resolve().parents[2]
GAUGE_SKILL = REPO_ROOT / "skills" / "gauge"

@task
def gauge():
    gauge_skill = skill([GAUGE_SKILL])

    return Task(
        dataset=...,
        solver=react(
            tools=[
                gauge_skill,
                # only tools Gauge genuinely requires
            ]
        ),
        scorer=[...],
        sandbox=...,
    )
```

Adapt the path and solver to the real repository.

### Important

Inspect's `skill()` tool publishes skills into a filesystem available to the agent, so the task needs a sandbox.

Use the smallest sandbox that faithfully represents Gauge's runtime. Prefer Docker for CI reproducibility if Gauge needs a real filesystem or shell environment.

Do not grant tools merely to make cases pass. The evaluated agent should receive the same practical capabilities expected when using Gauge normally.

If Gauge's existing skill format is not compatible with Inspect's native `skill()` facility, create a thin adapter. Do not rewrite Gauge solely for Inspect.

---

# 5. Sandbox

If Gauge needs filesystem/shell behavior, add an Inspect sandbox.

Example direction:

```python
return Task(
    ...,
    sandbox=("docker", "compose.yaml"),
)
```

Keep the sandbox intentionally constrained.

The sandbox should contain only what the eval needs. Mount or copy fixtures deliberately rather than exposing the full developer machine.

For each sample, aim for a clean state so one run cannot pollute another.

If Gauge operates on repository files, construct a small fixture workspace for each case instead of letting the model mutate the actual checkout.

Example:

```text
evals/gauge/fixtures/
├── simple-project/
├── malformed-project/
└── multi-package-project/
```

The scorer should inspect the fixture's resulting state when Gauge is expected to make changes.

---

# 6. Gauge Eval Dataset

Create an initial dataset with **at least 10-15 cases**, not hundreds.

The goal of v1 is a trustworthy regression suite.

Every sample should have:

- stable ID;
- user request;
- fixture/environment where needed;
- category;
- difficulty;
- explicit requirements;
- forbidden outcomes where relevant;
- machine-checkable expectations where possible;
- optional semantic grading rubric.

Example conceptual record:

```json
{
  "id": "gauge-basic-001",
  "input": "Use /gauge to ...",
  "metadata": {
    "category": "basic",
    "difficulty": "easy",
    "requirements": [
      "Gauge skill must be used",
      "Result must contain X"
    ],
    "forbidden": [
      "Do not invent Y"
    ]
  }
}
```

Use Inspect `Sample` objects or a JSON/JSONL dataset loaded into `Sample` objects.

---

# 7. Initial Case Taxonomy

Create Gauge cases that cover the behavior Gauge is actually designed to provide.

After reading the skill, derive its contract and build cases in these buckets:

### A. Canonical success

Straightforward requests where Gauge should clearly be used and should succeed.

Include 3-4 cases.

### B. Boundary / ambiguity

Requests that are close to Gauge's scope or omit some information.

Evaluate whether the skill:

- handles reasonable ambiguity;
- avoids fabricating missing data;
- asks for clarification only when necessary;
- follows its documented behavior.

Include 2-3 cases.

### C. Negative routing

Requests where `/gauge` should **not** be used, if skill-selection behavior is part of what is being evaluated.

Include 1-2 cases.

If the eval intentionally forces Gauge to be installed/available and does not test routing, omit this category rather than pretending to measure routing.

### D. Error handling

Create controlled failures relevant to Gauge:

- missing file;
- malformed input;
- unavailable dependency;
- empty result;
- tool command failure;
- invalid state.

Gauge should fail safely and communicate the problem rather than hallucinating success.

Include 2-3 cases.

### E. Adversarial / instruction conflict

Only add cases that are realistic for the skill. For example:

- user request conflicts with the skill's declared constraints;
- fixture content contains irrelevant instructions;
- a requested result would require unsupported evidence.

Include 1-2 cases.

### F. Regression cases

Reserve a category for real bugs discovered later.

Every meaningful Gauge bug fixed after this setup should produce a regression sample.

---

# 8. Define the Gauge Skill Contract Before Scoring

Read the actual Gauge skill and write a concise contract in:

```text
evals/gauge/README.md
```

The contract should answer:

```text
What is Gauge for?
When should it be used?
What inputs does it need?
What actions may it take?
What output/result should it produce?
What must it never claim or do?
What counts as successful completion?
```

Do not make the eval rubric broader than the skill's documented contract.

This contract is the basis for the dataset and scorers.

---

# 9. Scoring Strategy

Do not use one opaque LLM judge as the only scorer.

Use layered scoring.

## 9.1 Deterministic outcome scorer

Wherever possible, directly verify the resulting state.

Examples:

- expected file exists;
- expected file content/schema is valid;
- command completed successfully;
- expected structured fields are present;
- expected artifact/result was produced;
- forbidden mutation did not occur;
- result matches known values;
- required constraint was obeyed.

This should carry the most weight for cases where Gauge has an objective output.

---

## 9.2 Skill-use / trajectory scorer

Verify that Gauge was actually made available/used when the case requires it.

Use Inspect's recorded messages/tool calls rather than asking a judge to guess.

Measure separately:

```text
skill_invoked
skill_invocation_count
unnecessary_tool_calls
tool_errors
```

Do not make "skill was called" equivalent to "task succeeded."

A bad Gauge result after a valid invocation is still a task failure.

---

## 9.3 Semantic quality scorer

Use an LLM grader only for criteria that cannot be reliably determined in code, such as:

- whether the answer accurately explains a failure;
- whether the response fulfills a nuanced natural-language requirement;
- whether unsupported claims were made;
- whether the result is appropriately complete.

Use a tightly specified rubric with explicit score meanings.

Prefer a small ordinal scale such as:

```text
0 = failed
1 = materially flawed
2 = acceptable
3 = fully correct
```

Configure the grader model as an Inspect model role (e.g. `grader`) where practical so it can be changed independently of the model under evaluation.

---

# 10. Required Metrics

At minimum surface:

```text
task_success_rate
skill_use_rate
constraint_violation_rate
tool_error_rate
semantic_quality
```

Add Gauge-specific metrics if the contract suggests them.

Keep **task success** separate from supporting metrics.

Do not hide catastrophic failures inside an average.

If a case performs an unsafe, destructive, fabricated, or otherwise prohibited action, record that separately and fail the sample even if other rubric dimensions are good.

---

# 11. Suggested Inspect Task Shape

Implement idiomatic current Inspect code rather than copying this blindly, but the final structure should resemble:

```python
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.solver import react
from inspect_ai.tool import bash, skill

from .dataset import gauge_dataset
from .scorers import (
    gauge_task_success,
    gauge_skill_usage,
    gauge_constraints,
)

ROOT = Path(__file__).resolve().parents[2]
GAUGE = ROOT / "skills" / "gauge"

@task
def gauge_skill_eval():
    return Task(
        dataset=gauge_dataset(),
        solver=react(
            tools=[
                skill([GAUGE]),
                # bash() only if Gauge requires shell operations
            ]
        ),
        scorer=[
            gauge_task_success(),
            gauge_skill_usage(),
            gauge_constraints(),
        ],
        sandbox=("docker", "compose.yaml"),
    )
```

Use imports/module layout that work cleanly from the repo root.

If evaluating an already-built external agent rather than Inspect's built-in agent loop, use an Inspect custom Agent/Solver or Agent Bridge rather than reimplementing the agent inside the dataset.

---

# 12. Model Configuration

Do not hard-code a proprietary model into the task.

The model under evaluation should be selectable at runtime, for example:

```bash
inspect eval evals/gauge/task.py \
  --model <provider/model>
```

For semantic grading, support a separate grader model where practical:

```bash
inspect eval ... \
  --model <model-under-test> \
  --model-role grader=<grader-model>
```

Store secrets only in normal environment configuration. Never put API keys in the repo.

Create/update `.env.example` only if the repository already uses that convention.

---

# 13. Repeat Runs for Reliability

Agent evals are stochastic.

Support Inspect epochs or an equivalent repeated-run command for reliability testing.

Example intended workflow:

```bash
inspect eval evals/gauge/task.py \
  --model <provider/model> \
  --epochs 3
```

Do not require multiple epochs for the fastest local smoke test, but document them for release/CI evaluation.

Report both:

- average performance;
- failures/variance across repeated attempts.

A skill that sometimes succeeds is not equivalent to one that succeeds reliably.

---

# 14. Developer Commands

Add repo-level scripts matching existing package conventions.

For npm, aim for something like:

```json
{
  "scripts": {
    "eval:gauge": "...",
    "eval:gauge:smoke": "...",
    "eval:view": "..."
  }
}
```

Desired semantics:

```bash
npm run eval:gauge:smoke
```

Runs a cheap subset, e.g. 2-3 cases.

```bash
npm run eval:gauge
```

Runs the full Gauge regression suite.

```bash
npm run eval:view
```

Starts Inspect's log viewer against the configured log directory.

If a Makefile/task runner is already standard in the repo, integrate there instead of adding redundant wrappers.

---

# 15. CI

Add CI only after local execution works.

Recommended split:

### Pull requests

Run a small stable Gauge smoke suite.

Target:

- low cost;
- low latency;
- deterministic cases;
- catches obvious regressions.

### Main/release/nightly

Run the full Gauge suite and, if budget permits, multiple epochs.

Do not expose secrets on untrusted fork PRs.

If model/API access is unavailable in normal CI, keep the scripts CI-ready and document the required secret/configuration rather than weakening the eval.

---

# 16. Quality Gates

Do not pick arbitrary impressive-looking thresholds before establishing a baseline.

First implement the suite, run it, and record a baseline.

Then add explicit gates.

Good gate shape:

```text
task_success_rate >= baseline-approved-threshold
constraint_violation_rate <= allowed-threshold
catastrophic_failures == 0
```

Store thresholds in one obvious place.

Do not create a single "Gauge score" that averages away serious failures.

---

# 17. Logging and Failure Analysis

Use Inspect's native eval logs.

Configure log output under something like:

```text
evals/logs/
```

and add it to `.gitignore`.

Document:

```bash
inspect view
```

Developers must be able to inspect:

- sample input;
- model messages;
- skill/tool calls;
- arguments;
- tool errors;
- final answer;
- individual scorer results.

Do not build a custom dashboard in v1.

Inspect logs can be re-scored later, so keep grading logic decoupled from task execution when practical.

---

# 18. Re-Scoring

Design custom scorers so an existing `.eval` log can be re-scored after grading changes where possible.

Useful pattern:

```bash
inspect score path/to/run.eval \
  --scorer path/to/scorers.py@some_scorer
```

This is valuable because we should be able to improve a rubric without paying to rerun every agent trajectory.

Document any scorer that cannot operate during re-scoring because it depends on ephemeral external state.

---

# 19. Shared Infrastructure for Future Skills

Gauge is the first eval, not a special one-off framework.

Place generic utilities in something like:

```text
evals/shared/
├── datasets.py
├── scorers.py
├── fixtures.py
└── paths.py
```

Only extract code when it is truly generic.

A future skill should be addable with a structure roughly like:

```text
evals/
├── shared/
├── gauge/
└── another_skill/
    ├── task.py
    ├── scorers.py
    ├── dataset/
    └── README.md
```

Do not prematurely create a large abstraction layer.

---

# 20. Avoid These Anti-Patterns

Do **not**:

- copy the Gauge skill into the eval suite;
- create a custom eval framework when Inspect already provides the plumbing;
- grade everything with one LLM judge;
- measure only the final prose response when Gauge changes real state;
- equate tool invocation with success;
- let cases mutate the real repository checkout;
- make network-dependent test data silently change between runs;
- hard-code one model/provider;
- commit API credentials;
- introduce hundreds of low-quality generated test prompts;
- optimize Gauge against only trivial happy-path cases;
- average catastrophic failures into a generic score;
- rewrite the monorepo packaging/install system merely to accommodate Inspect.

---

# 21. Initial Deliverables

Implement all applicable items below.

```text
[ ] Inspect eval project/dependencies added
[ ] Gauge source path discovered and referenced directly
[ ] Gauge skill contract documented
[ ] Gauge Inspect Task implemented
[ ] sandbox/fixture setup implemented if required
[ ] 10-15 meaningful v1 cases
[ ] deterministic scorer(s)
[ ] skill/trajectory scorer
[ ] semantic grader only where needed
[ ] aggregate metrics
[ ] predictable .eval log directory
[ ] log directory gitignored
[ ] smoke command
[ ] full Gauge eval command
[ ] inspect-view command/docs
[ ] model configurable from CLI/environment
[ ] separate grader model configurable where applicable
[ ] repeated-run/epochs workflow documented
[ ] README with local setup and examples
[ ] CI integration or CI-ready instructions
```

---

# 22. Acceptance Criteria

The task is complete when all of the following are true:

1. A fresh developer can follow the eval README and run Gauge evals without understanding the internal implementation of Inspect.

2. The evaluated skill is the repository's real Gauge source, not an eval-only copy.

3. At least one case can detect a deliberate regression to Gauge.

4. At least one failure case verifies that Gauge does not falsely claim success.

5. Scoring includes objective checks wherever objective checks are possible.

6. Eval logs expose the trajectory/tool/skill behavior needed to diagnose failures.

7. The model under test can be changed without editing the Gauge task source.

8. The same eval framework can accommodate another repository skill with minimal boilerplate.

9. Generated fixtures/logs do not dirty or mutate production skill sources.

10. The README clearly distinguishes:
   - smoke evals;
   - full evals;
   - grader model;
   - model under evaluation;
   - logs/viewing;
   - adding future regression cases.

---

# 23. Implementation Sequence

Use this order:

```text
1. Inspect repo and Gauge implementation
2. Write Gauge contract
3. Add minimal Inspect dependency/project
4. Make one Gauge case execute end-to-end
5. Add deterministic scoring
6. Verify Inspect log contains useful trajectory data
7. Add remaining core cases
8. Add semantic scorer only where necessary
9. Add npm/package-manager commands
10. Add documentation
11. Add smoke/full split
12. Add CI integration
13. Run the suite and report baseline results
```

Do not begin by generating lots of test cases. First prove one case exercises the real skill correctly.

---

# 24. Final Report Expected From the Implementing Agent

After making changes, report:

```text
Files added/changed:
- ...

Gauge contract:
- ...

How the skill is injected/exercised:
- ...

Cases:
- N total
- categories: ...

Scorers:
- ...

Commands:
- smoke:
- full:
- view:

Model configuration:
- ...

Baseline:
- task success:
- skill usage:
- constraint violations:
- tool errors:
- semantic quality:

Known limitations:
- ...

Recommended next 3 eval cases:
- ...
```

Do not report success unless the Gauge eval command was actually executed, except where execution is blocked by unavailable credentials/provider access. In that case, run every local/non-model validation possible and clearly identify the single blocked step.

---

# References

Use current Inspect AI APIs and documentation rather than relying on old examples:

- Inspect AI: https://inspect.aisi.org.uk/
- Tasks: https://inspect.aisi.org.uk/tasks.html
- Skills / tool API: https://inspect.aisi.org.uk/reference/inspect_ai.tool.html
- Standard tools and `skill()`: https://inspect.aisi.org.uk/tools-standard
- Custom tools: https://inspect.aisi.org.uk/tools-custom.html
- Eval logs: https://inspect.aisi.org.uk/eval-logs.html
- Agent Bridge: https://inspect.aisi.org.uk/agent-bridge.html

The key design goal is **reliable evaluation of the real `/gauge` skill**, with Inspect responsible for execution/logging/eval plumbing and this repository responsible for the Gauge contract, cases, fixtures, and grading criteria.
