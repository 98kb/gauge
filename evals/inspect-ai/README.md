# Inspect AI skill evals

Agent evals for this repository's skills, built on
[Inspect AI](https://inspect.aisi.org.uk/). The first suite is
[`gauge`](skill_evals/gauge/README.md), whose contract, cases and scoring are
documented there; this file is setup, worked examples, and how to extend the
harness.

This sits **beside** [`../harness/`](../README.md), not on top of it. That one
drives a scripted founder through a multi-turn interview and grades the artifact
the session leaves behind; it is the right instrument for `to-vision` and
`to-pitch`. This one runs a single agent turn in a sandbox with the skill
published as a tool, and grades the answer, the trajectory and the filesystem.
Gauge produces no artifact and takes no turns with a persona, so it needs the
second shape. Neither replaces the other, and they share no code.

**Contents** — [Setup](#setup) · [Commands](#commands) ·
[Worked examples](#worked-examples) · [Extending](#extending) ·
[Layout](#layout)

## Setup

Needs [`uv`](https://docs.astral.sh/uv/) and a working Docker daemon. Once:

```bash
cd evals/inspect-ai
./run.sh setup
```

That creates `.venv/` with Python 3.12 and installs `inspect-ai` plus the dev
tools. Nothing is installed globally. Exact versions come from the committed
`uv.lock`, in the same spirit as the repo's `skills-lock.json`: pinned, and
changed deliberately rather than drifting.

## Commands

```bash
./run.sh check                    # offline: types, contracts, controls. No model, no cost.
./run.sh check:docker             # one whole sample through the sandbox, scripted model
./run.sh smoke --model <m>        # 3 cases
./run.sh gauge --model <m>        # the full 15-case suite
./run.sh view                     # Inspect's log viewer
./run.sh gate [log]               # apply gates.json
./run.sh score <log> <scorer>     # re-grade a recorded log
```

Anything after the subcommand is passed through to `inspect`, so every flag in
[its CLI](https://inspect.aisi.org.uk/options.html) is available.

---

## Worked examples

### 1. Before anything costs money

```bash
$ ./run.sh check
Success: no issues found in 36 source files
........................................................................ [ 75%]
........................                                                 [100%]
96 passed, 7 deselected in 2.05s
```

This is the command to run on every change to a case, a pattern, or a scorer.
It checks the skill adapter against the real `SKILL.md`, the case file's own
contract, and both control bars — *would this suite notice a regression*, and
*would it cry wolf at a correct run*. No model, no sandbox, no cost.

The 7 deselected tests need Docker; run them with `./run.sh check:docker`.

### 2. A smoke run, and reading the summary

Any Inspect provider works. `mockllm/model` needs no credentials and is useful
for checking the plumbing:

```bash
$ ./run.sh smoke --model mockllm/model --display plain
gauge_task…         gauge_skil…         gauge_cons…         gauge_tool_e…
accuracy     0.333  accuracy     0.667  mean         0.000  mean           0.000
stderr       0.333  stderr       0.333  total        0.000  stderr         0.000
gauge_semantic_quality
graded_mean             3.000  graded_stderr  0.000
```

Read it as five separate answers, never one score:

| Metric | Question |
| --- | --- |
| `gauge_task_success/accuracy` | did every objective check pass? |
| `gauge_skill_use/accuracy` | was the skill reached for exactly when wanted? |
| `gauge_constraints/mean` | how often was the read-only floor broken? |
| `gauge_constraints/total` | **how many samples did something prohibited?** must be 0 |
| `gauge_tool_errors/mean` | what fraction of tool calls errored? |
| `gauge_semantic_quality/graded_mean` | 0–3, over the samples a rubric applies to |

`total` is a count, not a rate, on purpose: one sample that wrote a file must
not disappear into a mean.

Real models need credentials in the environment, the ordinary Inspect way:

```bash
export ANTHROPIC_API_KEY=...
./run.sh smoke --model anthropic/claude-sonnet-5
```

### 3. Reading a failure

Every failing check names itself and quotes what it saw, so diagnosis is
reading, not bisecting:

```
=== gauge-canonical-001-bounded-rename: I
✗ case/topology:G0: expected G0, recipe names ['G1']
✗ case/binds-no-planning-skill: step skills: ['handoff']
✗ case/forbids:handoff: bound skills: ['handoff']

=== gauge-canonical-002-auth-boundary: C
21 checks, all passed

=== gauge-routing-001-method-already-chosen: I
✗ case/gauge-not-invoked: skill invocations: ['gauge']
```

Three things worth noticing:

- A **passing** sample reports how many checks it registered (`21 checks`). A
  sample that registered none is a failure, not a pass — nothing graded is not
  the same as nothing wrong.
- `contract/*` ids are the skill's standing invariants; `case/*` ids are this
  case's own expectations; `floor/*` ids are the read-only floor.
- The last one is the negative-routing case: Gauge was invoked when it should
  not have been. That is a real routing failure, not a scoring artifact.

### 4. Narrowing a run

```bash
./run.sh gauge --model <m> -T categories=routing,error   # by category
./run.sh gauge --model <m> --sample-id gauge-error-002-no-registry-match
./run.sh gauge --model <m> --limit 3                     # first N samples
```

### 5. Looking at a trajectory

```bash
./run.sh view
```

Per sample: the input, every model message, each skill and tool call with its
arguments, tool errors, the final answer, and each scorer's result with its full
check list. Logs land in `logs/`, which is gitignored; set `INSPECT_LOG_DIR` to
put them elsewhere.

### 6. A separate grader

The semantic scorer resolves an Inspect **model role**, so the judge changes
independently of the model under test:

```bash
./run.sh gauge --model anthropic/claude-sonnet-5 \
                --model-role grader=anthropic/claude-opus-5
```

With no role bound it falls back to the model under evaluation — fine for a
smoke run, not for a number you intend to quote.

### 7. Repeated runs

Agent evals are stochastic, so one green run is not a reliable skill.

```bash
./run.sh gauge --model <m> --epochs 3
```

Report the average *and* the spread; every scorer emits a `stderr` beside its
average for exactly this. The smoke run stays single-epoch — it exists to be
fast.

### 8. Re-grading an old run after a rubric change

Every scorer reads the recorded messages and the sample store, never a live
sandbox, so improving a rubric costs nothing to re-apply:

```bash
./run.sh score logs/2026-09-04T19-14-17_gauge_RdHpRG.eval gauge_task_success \
               --output-file /tmp/rescored.eval
```

No trajectory is re-run and no model is called for the deterministic scorers.
This is why the workspace before/after hashes are written into the store by a
solver step rather than computed by a scorer — a scorer that reached for the
sandbox could not do this.

### 9. Quality gates

```bash
$ ./run.sh gate
quality gates — 2026-09-04T19-20-07_gauge_miy9aG.eval
  ? task_success_rate: measured 1.000, but no threshold is set. Record this as
    the baseline and set it in gates.json — an unset gate passes everything, so
    it is not treated as a pass.
  ? constraint_violation_rate: measured 0.000, but no threshold is set. ...
  ✓ catastrophic_failures: 0.000 (<= 0)

  No gate was breached, but a baseline is still owed. Exit 3.
```

[`gates.json`](gates.json) is the one place thresholds live. Two are `null`
because no baseline has been recorded against a real model yet;
`catastrophic_failures` is already `0`, because zero needs no baseline.

Exit codes follow the same convention as `evals/harness/check.mjs`:

| | |
| --- | --- |
| `0` | every gate passed |
| `1` | a gate with a threshold was breached |
| `2` | the log or the gate file is unusable |
| `3` | a gate has no threshold yet — a baseline is owed |

An unset threshold never reports success. It exits 3 rather than 1 so CI can
raise it as an annotation while still failing the build on a real regression.

---

## Extending

Four things you might add, smallest first. Each ends with `./run.sh check`,
which is free and is what tells you whether the thing you added can actually
fail.

### A. Add a case

The common one: a Gauge bug was found and fixed, and it should never come back.
Append a line to
[`skill_evals/gauge/dataset/cases.jsonl`](skill_evals/gauge/dataset/cases.jsonl):

```json
{"id": "gauge-regression-001-g0-on-a-migration", "category": "regression",
 "difficulty": "medium", "fixture": "repo-with-tests", "installed_skills": [],
 "input": "/gauge Drop the legacy sessions column. It's one line of SQL.",
 "expect": {"gauge_invoked": true, "topology": "G1",
            "modifiers_include": ["High-assurance"]},
 "requirements": ["Irreversibility is named as the reason this is not G0"],
 "forbidden": ["Routing to G0 because the change is one line"],
 "notes": "Regression for #NNN: routed G0 on an irreversible migration."}
```

| Field | |
| --- | --- |
| `id` | stable and unique; it is how the case is addressed and diffed |
| `category` | one of canonical, boundary, routing, error, adversarial, regression |
| `fixture` | a directory under `gauge/fixtures/`, or `null` for no checkout |
| `installed_skills` | ground truth for what the fixture's inventory exposes |
| `expect` | the mechanical assertions — see the catalogue below |
| `requirements` / `forbidden` | natural language, read **only** by the semantic grader |
| `notes` | prose. Anything nothing grades belongs here, not in a key shaped like an assertion |

Expectation keys: `topology`, `variant`, `binds`, `forbids`,
`binds_no_planning_skill`, `no_registry_match`, `modifiers_include`,
`availability`, `installation_section`, `gauge_invoked`, `confidence_at_most`,
`runtime_unavailable`.

**An expectation omitted is not asserted; an expectation present must assert.**
`./run.sh check` enforces that before any model is called, and the errors say
what to do:

```
unknown expectation "toplogy". Known keys: ['availability', 'binds', ...]
"binds" names ['context-packer'], which the planning registry does not list
"forbids" must be a non-empty list of skill names
"topology": 'G4' is not one of ('G0', 'G1', 'G2', 'G3')
gauge-regression-001: category 'regresion' is not one of ('canonical', ...)
```

A case expecting `"gauge_invoked": false` may carry no other key: there is no
recipe, so a topology expectation beside it would grade the empty string.

Add `"smoke": true` only for something cheap that catches a whole class of
breakage — the smoke set is meant to stay at three or four.

### B. Add a fixture

A directory under [`skill_evals/gauge/fixtures/`](skill_evals/gauge/fixtures).
Every file in it is copied to `/workspace` in the sandbox; the real checkout is
never exposed. Keep them small and make the one thing under test obvious. Git
does not track empty directories, so an *intentionally* empty inventory needs a
`.keep` explaining itself — `repo-no-skills` is the worked example, and without
it that case would silently become `unknown` and grade something else.

### C. Add a deterministic check, or an expectation key

A **standing invariant** — true of every recipe — goes in
[`gauge/contract.py`](skill_evals/gauge/contract.py): write `_check_thing()`
returning a `Check`, and register it in `check_recipe()` *only when the recipe
gives it something to grade*. A check that cannot fail is noise in a report
rather than reassurance.

A **per-case** expectation goes in
[`gauge/expectations.py`](skill_evals/gauge/expectations.py): add the check to
`CATALOGUE` and a value validator to `VALIDATORS`.

Either way, both controls are required in the same change:

- a **negative** control — copy `tests/controls/positive/canonical-g1.md`,
  introduce exactly one defect, and name the check id it must trip in
  `NEGATIVE_CONTROLS`. A control naming a check the recipe never registers fails
  too: an unregistered check cannot fail, so it would prove nothing.
- a **positive** control — the three recipes in `tests/controls/positive/` must
  all still pass every registered check. One is deliberately reworded, because
  the skill's own rule is that two results with different wording and the same
  decisions both pass.

For an expectation key, `tests/test_gauge_expectations.py` holds a `CONTROLS`
map of key → (value, an outcome it must pass, an outcome it must fail), and
`test_every_catalogue_key_has_a_control` fails if you add a key without one.

Two mistakes this harness has already made, worth not repeating:

- **Do not check something the harness cannot observe.** An
  `asks_no_questions` key read `ask_user` tool calls; the solver never grants
  that tool, so it could never fail. It was removed, and the judge carries it.
- **Scan the recipe, not the human.** The contract makes Gauge quote the intent
  verbatim, so a pattern matching the human's own words fails Gauge for their
  wording. `Evidence.human_request` exists so a check can tell the two apart.

### D. Add a suite for another skill

The shared pieces know nothing about Gauge, so a second skill reuses them:

| | |
| --- | --- |
| `shared/paths.py` | where the repo, the skills and the logs are |
| `shared/skills.py` | real `SKILL.md` → Inspect `Skill` (the frontmatter adapter) |
| `shared/dataset.py` | JSONL cases → `Sample`s, with the case-file contract |
| `shared/workspace.py` | fixture → sandbox, and the before/after snapshots |
| `shared/trajectory.py` | skill calls, tool errors, installs, tracker writes |
| `shared/metrics.py` | `total`, `graded_mean`, `graded_stderr` |

A new suite is a sibling of `gauge/`:

```
skill_evals/<skill>/
├── README.md            # the skill's contract — write this first
├── task.py              # dataset + solver + scorers + sandbox
├── dataset.py           # its own case-file contract
├── scorers.py           # what is objective for this skill
├── contract.py          # its standing invariants, if it has any
├── dataset/cases.jsonl
└── fixtures/
```

Roughly:

```python
# skill_evals/<skill>/task.py
@task
def my_skill(smoke: bool = False) -> Task:
    skill_spec = load_repo_skill(skill_dir("engineering", "my-skill"))
    return Task(
        dataset=my_skill_dataset(smoke=smoke),
        setup=record_workspace_before([skill_spec]),
        solver=snapshotting(as_solver(react(
            prompt=AgentPrompt(instructions=INSTRUCTIONS),
            tools=[skill([skill_spec], dir=SKILLS_DIR), bash(timeout=60)],
        ))),
        scorer=[...],
        sandbox=("docker", str(COMPOSE_FILE)),
    )
```

Order that actually works:

1. **Write `README.md` first** — the skill's contract, read off its `SKILL.md`.
   The rubric may not be broader than the documented contract, and writing it
   down is how you find where that edge is.
2. Get **one** case running end to end before writing more. `docs/INSPECT_AI_GAUGE_EVAL_SETUP.md`
   is emphatic about this and it was right: the first case is what surfaces the
   harness problems.
3. Add deterministic scoring, then the controls that prove it can fail.
4. Only then the remaining cases, and a semantic grader for what is genuinely
   left over.

Two things to resist. Do not extract into `shared/` before there is a second
caller — the Gauge recipe parser looks generic and is not. And do not grant the
agent a tool merely to make a case pass; it should get the capabilities it would
have in real use, and misbehaviour should be *caught*, not made impossible.

If the skill runs a multi-turn interview and leaves an artifact behind, this is
probably the wrong harness — use [`../harness/`](../README.md) instead.

---

## Layout

```
evals/inspect-ai/
├── README.md            # this file
├── run.sh               # every entry point
├── pyproject.toml       # deps; exact versions in uv.lock
├── uv.lock              # committed, like skills-lock.json
├── compose.yaml         # the sandbox: debian slim, no network
├── gates.json           # the one place thresholds live
├── logs/                # generated, gitignored
├── skill_evals/
│   ├── gate.py          # gates.json -> exit code
│   ├── shared/          # skill-agnostic
│   └── gauge/           # the first suite
└── tests/               # offline checks and both control bars
    └── controls/
        ├── positive/    # correct recipes: must pass every check
        └── negative/    # one defect each, naming the check it must trip
```

## CI

[`.github/workflows/skill-evals.yml`](../../.github/workflows/skill-evals.yml):

- **every pull request** runs `./run.sh check` and `./run.sh check:docker` —
  offline, free, no secrets, and what catches a broken adapter, a malformed case
  or a scorer that stopped being able to fail;
- **pushes to `main`, and a nightly schedule**, additionally run the smoke suite
  and then the full suite with epochs, gated on an `ANTHROPIC_API_KEY` secret.

Model-backed jobs are skipped, loudly, when the secret is absent, and never run
for pull requests from forks. The scripts are CI-ready either way; nothing about
the eval is weakened to make a credential-less run go green.
