# Planning registry (MVP)

The authoritative binding source for Gauge: which skill delivers each capability the routing model names, what each skill needs, what it accepts and produces, and how to install it when absent. Human edits to this file are authoritative. The MVP does not refresh the registry, crawl marketplaces, or update installed skills.

**Scope.** One ecosystem, deliberately: the planning-relevant skills of [Matt Pocock's skills repository](https://github.com/mattpocock/skills). The capability names in `routing-model.md` carry no author or ecosystem name, so a second registry can be added later without changing the routing model.

**Verified** 2026-09-04 against upstream commit [`3cca18b368ae95cdbdebbff572ccafa662551015`](https://github.com/mattpocock/skills/tree/3cca18b368ae95cdbdebbff572ccafa662551015). Each entry links the live file on `main` and the commit-pinned copy it was verified from; when the two diverge, the pinned copy is what this registry describes and the entry is due a maintenance pass.

## Recipe bindings

| Capability (routing model) | Skill | Required dependencies | Prerequisite |
| --- | --- | --- | --- |
| `tracker setup` | `setup-matt-pocock-skills` | none | a repository checkout |
| `context handoff` | `handoff` | none | settled context in the conversation |
| `interactive elicitation` | `grill-me` | `grilling` | none |
| `interactive elicitation with domain docs` | `grill-with-docs` | `grilling`, `domain-modeling` | a repository checkout |
| `durable specification` | `to-spec` | none | `tracker setup` done once in the repository |
| `ticket decomposition` | `to-tickets` | none | `tracker setup` done once in the repository |
| `navigated decision map` | `wayfinder` | `grilling`, `domain-modeling`; `research` and `prototype` as ticket types require | `tracker setup` done once in the repository |
| `external research` | `research` | none | none |
| `design prototype` | `prototype` | none | a runnable project, for UI variants |
| `implementation` | no planning skill | none | none |

A dependency is expanded every time its entry point is bound: a recipe that names `grill-me` lists `grilling`; one that names `grill-with-docs` lists `grilling` and `domain-modeling`. When `to-spec`, `to-tickets`, or `wayfinder` is bound and the repository shows no tracker configuration (no `docs/agents/issue-tracker.md` or equivalent written by the setup skill), the recipe gains a `tracker setup` step before them. Setup is a prerequisite, never a planning step.

## Availability

Label every bound skill with exactly one of:

- `installed`: the current environment explicitly exposes the skill.
- `not detected`: the environment exposes an inventory and the skill is absent from it.
- `unknown`: the runtime provides no inventory to read.

`unknown` stays `unknown`; it is never rewritten as `not installed`. For a skill that is `not detected` or `unknown`, the recipe's **Installation required** section carries the exact installation route and the skill's dependencies.

**Evidence that counts as an inventory:**

- Claude Code: the session's list of available skills. The managed plugin exposes each skill under the namespace `mattpocock-skills:<name>`; an editable copy exposes it as `<name>`. On disk: `.claude/skills/<name>/SKILL.md` in the project, or `~/.claude/skills/<name>/SKILL.md` for the user.
- Codex: `.codex/skills/<name>/SKILL.md` in the project, or `~/.codex/skills/<name>/SKILL.md` for the user.
- Any agent set up through the `skills` CLI: `.agents/skills/<name>/SKILL.md`, and `skills-lock.json` at the repository root naming the skill.

A directory or inventory that can be read and lacks the name is `not detected`. A runtime where none of these can be read is `unknown`.

## No registry match

`No registry match` is a resolution outcome, not an availability state. Use it when no entry below provides the capability the selected topology requires. The recipe step names the missing capability precisely and states that the MVP catalog cannot fully resolve the recipe. The closest entry is not force-fitted, and no third-party or invented skill is proposed in its place.

## Installation

The documented routes, from the [official installation instructions](https://github.com/mattpocock/skills#installation-30-second-setup):

- **Claude Code, managed plugin:** `claude plugins install mattpocock-skills`, or `/plugin install mattpocock-skills` inside a session. Read-only bundle, updates when upstream ships.
- **Codex and other compatible agents, editable copies:** `npx skills@latest add mattpocock/skills`. The installer lets the user pick skills; `setup-matt-pocock-skills` must be among them.
- **Selective install:** `npx skills@latest add mattpocock/skills --skill <name>`, repeated for every dependency the binding table lists for that skill.
- **Repository preparation:** run `/setup-matt-pocock-skills` once per repository before `to-spec`, `to-tickets`, or `wayfinder`.

Pick one route per environment. Installing the managed plugin and the editable copies side by side leaves every skill present twice.

## Entries

Each entry records: canonical name; ecosystem and source; capability tags; invocation status; prerequisites; dependencies; suitable scenarios; unsuitable scenarios; accepted context; expected output; continuation; invocation examples; annotation. Invocation examples cover Claude Code (`/name`, or `/mattpocock-skills:name` under the managed plugin) and Codex (`$name`); a model-invoked skill is additionally reachable by a composing skill through the harness's Skill tool.

### `setup-matt-pocock-skills`

- **Ecosystem and source:** mattpocock/skills, [live](https://github.com/mattpocock/skills/blob/main/skills/engineering/setup-matt-pocock-skills/SKILL.md) · [pinned](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/setup-matt-pocock-skills/SKILL.md)
- **Capability tags:** `tracker setup`
- **Invocation status:** user-invoked (`disable-model-invocation: true`)
- **Prerequisites:** a repository checkout
- **Dependencies:** none
- **Suitable:** once per repository, before the first `to-spec`, `to-tickets`, or `wayfinder`, when the tracker and domain-doc configuration is absent
- **Unsuitable:** as a planning step; on a repository that already carries `docs/agents/` from a previous run
- **Accepted context:** the repository: `git remote`, `CLAUDE.md` or `AGENTS.md`, `CONTEXT.md`, `docs/adr/`, monorepo signals
- **Expected output:** `docs/agents/issue-tracker.md`, `docs/agents/domain.md`, optionally `docs/agents/triage-labels.md`, and an `## Agent skills` block in `CLAUDE.md` or `AGENTS.md`, each confirmed with the user before writing
- **Continuation:** `to-spec`, `to-tickets`, `wayfinder`
- **Invocation:** Claude Code `/setup-matt-pocock-skills`; Codex `$setup-matt-pocock-skills`
- **Annotation:** allowed, prerequisite only

### `handoff`

- **Ecosystem and source:** mattpocock/skills, [live](https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md) · [pinned](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/productivity/handoff/SKILL.md)
- **Capability tags:** `context handoff`
- **Invocation status:** user-invoked (`disable-model-invocation: true`); accepts an argument describing what the next session is for
- **Prerequisites:** a conversation whose material decisions are settled
- **Dependencies:** none
- **Suitable:** G1; the boundary after a G2 interview when a fresh session implements; any phase or session boundary
- **Unsuitable:** as a substitute for unresolved planning; when the current conversation is already a sufficient direct launch packet
- **Accepted context:** the current conversation; existing artifacts (specs, plans, ADRs, issues, commits, diffs), which it references by path or URL rather than duplicating; the optional focus argument
- **Expected output:** one handoff document saved to the operating system's temporary directory, not the workspace, with a "suggested skills" section and secrets redacted. The recipe's implementation step must pass that file's path to the next session.
- **Continuation:** the implementation agent, or the next planning step
- **Invocation:** Claude Code `/handoff <what the next session is for>`; Codex `$handoff <what the next session is for>`
- **Annotation:** preferred for `context handoff`

### `grill-me`

- **Ecosystem and source:** mattpocock/skills, [live](https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md) · [pinned](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/productivity/grill-me/SKILL.md); user documentation [live](https://github.com/mattpocock/skills/blob/main/docs/productivity/grill-me.md) · [pinned](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/docs/productivity/grill-me.md)
- **Capability tags:** `interactive elicitation`, entry point
- **Invocation status:** user-invoked (`disable-model-invocation: true`)
- **Prerequisites:** none
- **Dependencies:** **`grilling`**, required; its whole body is a call to that primitive
- **Suitable:** G2 with no repository or a non-code intent; a loose idea that must be sharpened until the human can commit to it
- **Unsuitable:** a repository-backed change that should leave a glossary and decision trail (`grill-with-docs`); an effort too big for one session (`wayfinder`); a question that needs an artifact to react to (`prototype`)
- **Accepted context:** a fresh conversation holding the idea; plan mode off
- **Expected output:** no files. A shared understanding reached in rounds, ended when the design tree's frontier is empty and the human confirms it; nothing is acted on before that confirmation
- **Continuation:** `to-spec` in the same conversation when the result is software that spans sessions; `handoff` when a fresh session implements
- **Invocation:** Claude Code `/grill-me` in a fresh conversation; Codex `$grill-me`
- **Annotation:** preferred for non-repository `interactive elicitation`; never installed alone

### `grilling`

- **Ecosystem and source:** mattpocock/skills, [live](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md) · [pinned](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/productivity/grilling/SKILL.md)
- **Capability tags:** interview primitive under `interactive elicitation`, `interactive elicitation with domain docs`, and the grilling tickets of `navigated decision map`
- **Invocation status:** model-invoked; reachable through the Skill tool and by name
- **Prerequisites:** none
- **Dependencies:** none
- **Suitable:** as the dependency of `grill-me`, `grill-with-docs`, and `wayfinder`
- **Unsuitable:** as a recipe step of its own; the recipe binds the entry point and lists this as its dependency
- **Accepted context:** a plan, decision, or idea in the conversation
- **Expected output:** numbered question rounds over a design tree, each question carrying a recommended answer; facts fetched by sub-agent rather than asked; done when the frontier is empty and the human confirms shared understanding
- **Continuation:** the skill that composed it
- **Invocation:** Skill tool `grilling`; Claude Code `/grilling`; Codex `$grilling`
- **Annotation:** allowed, dependency

### `grill-with-docs`

- **Ecosystem and source:** mattpocock/skills, [live](https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md) · [pinned](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/grill-with-docs/SKILL.md)
- **Capability tags:** `interactive elicitation with domain docs`, entry point
- **Invocation status:** user-invoked (`disable-model-invocation: true`)
- **Prerequisites:** a repository checkout
- **Dependencies:** **`grilling` and `domain-modeling`**, both required; its whole body is two Skill-tool calls. When a session degrades into an undifferentiated question dump with no glossary or decision records appearing, check that the runtime loaded both dependencies.
- **Suitable:** G2 for a repository-backed software change whose terminology and hard decisions should land in `CONTEXT.md` and `docs/adr/`; one planning session
- **Unsuitable:** a non-code intent (`grill-me`); an effort whose decisions span sessions (`wayfinder`); decisions already settled (`to-spec`)
- **Accepted context:** the repository and the conversation; existing `CONTEXT.md`, `CONTEXT-MAP.md`, and `docs/adr/`
- **Expected output:** the same shared understanding as `grill-me`, plus glossary entries and ADRs created lazily as terms and decisions crystallize
- **Continuation:** `to-spec` when the build spans sessions; `handoff` when a fresh session implements in one run
- **Invocation:** Claude Code `/grill-with-docs`; Codex `$grill-with-docs`
- **Annotation:** preferred for repository-backed `interactive elicitation with domain docs`

### `domain-modeling`

- **Ecosystem and source:** mattpocock/skills, [live](https://github.com/mattpocock/skills/blob/main/skills/engineering/domain-modeling/SKILL.md) · [pinned](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/domain-modeling/SKILL.md)
- **Capability tags:** glossary and decision-record primitive under `interactive elicitation with domain docs` and `navigated decision map`
- **Invocation status:** model-invoked; reachable through the Skill tool and by name
- **Prerequisites:** a repository checkout
- **Dependencies:** none
- **Suitable:** as the dependency of `grill-with-docs` and `wayfinder`
- **Unsuitable:** as a recipe step of its own
- **Accepted context:** the repository; `CONTEXT.md` or `CONTEXT-MAP.md` and `docs/adr/` when present
- **Expected output:** `CONTEXT.md` entries and ADRs, created lazily the moment a term or decision crystallizes; challenges to terms that conflict with the glossary or the code
- **Continuation:** the skill that composed it
- **Invocation:** Skill tool `domain-modeling`; Claude Code `/domain-modeling`; Codex `$domain-modeling`
- **Annotation:** allowed, dependency

### `to-spec`

- **Ecosystem and source:** mattpocock/skills, [live](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-spec/SKILL.md) · [pinned](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/to-spec/SKILL.md)
- **Capability tags:** `durable specification`
- **Invocation status:** user-invoked (`disable-model-invocation: true`)
- **Prerequisites:** `tracker setup` completed in the repository; decisions already made in the conversation
- **Dependencies:** none
- **Suitable:** the first step of G3-A; the step after a cleared `wayfinder` map in G3-B; whenever decisions must survive a multi-session build
- **Unsuitable:** as the interview (it synthesizes and does not ask); to make a G1 recipe feel formal; on unresolved decisions
- **Accepted context:** the current conversation and codebase understanding; the project glossary and ADRs
- **Expected output:** a spec with Problem Statement, Solution, User Stories, Implementation Decisions, Testing Decisions, Out of Scope, and Further Notes, published to the configured tracker with the `ready-for-agent` label. It confirms the test seams with the user once before writing; that confirmation is the only interaction.
- **Continuation:** `to-tickets`; implementation sessions
- **Invocation:** Claude Code `/to-spec`; Codex `$to-spec`
- **Annotation:** preferred for `durable specification`

### `to-tickets`

- **Ecosystem and source:** mattpocock/skills, [live](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-tickets/SKILL.md) · [pinned](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/to-tickets/SKILL.md)
- **Capability tags:** `ticket decomposition`
- **Invocation status:** user-invoked (`disable-model-invocation: true`); accepts a spec path, issue number, or URL as argument
- **Prerequisites:** `tracker setup` completed in the repository; a settled plan, spec, or conversation
- **Dependencies:** none
- **Suitable:** after `to-spec` for a multi-session implementation; a wide mechanical refactor, which it sequences as expand-contract instead of vertical slices
- **Unsuitable:** as a substitute for unresolved decisions; work that fits one implementation run
- **Accepted context:** the conversation; the referenced spec or issue with its comments; the codebase
- **Expected output:** tracer-bullet tickets, each sized to one fresh context window and declaring its blocking edges, published in dependency order with `ready-for-agent`: one issue per ticket on a real tracker, one file per ticket under `.scratch/<feature>/issues/` locally. The breakdown is shown to the user and iterated until approved before publishing.
- **Continuation:** implementation sessions working the frontier of unblocked tickets
- **Invocation:** Claude Code `/to-tickets <spec reference>`; Codex `$to-tickets <spec reference>`
- **Annotation:** preferred for `ticket decomposition`

### `wayfinder`

- **Ecosystem and source:** mattpocock/skills, [live](https://github.com/mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md) · [pinned](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/wayfinder/SKILL.md)
- **Capability tags:** `navigated decision map`
- **Invocation status:** user-invoked (`disable-model-invocation: true`); charts on a loose idea, works on a map URL or number
- **Prerequisites:** `tracker setup` completed in the repository
- **Dependencies:** **`grilling` and `domain-modeling`** for the destination-naming session and every grilling ticket; `research` for research tickets and `prototype` for prototype tickets
- **Suitable:** G3-B only: a nameable destination whose route holds interdependent decisions or investigations too extensive for one session, with decisions that must persist on the tracker
- **Unsuitable:** a well-scoped single-session feature; a large effort whose decisions are already settled (G3-A); an intent with no nameable destination (Interactive first). Charting that surfaces no fog is the skill's own signal that no map is needed; it stops and asks, which is a re-Gauge trigger.
- **Accepted context:** a loose idea, or an existing map; the tracker configuration's wayfinding operations
- **Expected output:** one map issue labelled `wayfinder:map` (Destination, Notes, Decisions so far, Not yet specified, Out of scope) with child decision tickets labelled `wayfinder:research`, `wayfinder:prototype`, `wayfinder:grilling`, or `wayfinder:task`. Charting is one session; each later session resolves one ticket. Done when no tickets remain and the way is clear.
- **Continuation:** `to-spec`, then `to-tickets`, then implementation sessions
- **Invocation:** Claude Code `/wayfinder <loose idea>` to chart, `/wayfinder <map reference>` to work a ticket; Codex `$wayfinder` with the same arguments
- **Annotation:** allowed for G3-B; discouraged everywhere else

### `research`

- **Ecosystem and source:** mattpocock/skills, [live](https://github.com/mattpocock/skills/blob/main/skills/engineering/research/SKILL.md) · [pinned](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/research/SKILL.md)
- **Capability tags:** `external research`, Discovery-first
- **Invocation status:** model-invoked; reachable through the Skill tool and by name
- **Prerequisites:** none
- **Dependencies:** none
- **Suitable:** a decision blocked on a trustworthy external fact: third-party behaviour, an API contract, a specification
- **Unsuitable:** making the blocked decision; a fact the repository itself holds, which the planning agent reads directly
- **Accepted context:** the question, and where the repository keeps research notes
- **Expected output:** one Markdown file of findings from primary sources, every claim cited, written by a background agent to the repository's existing notes location
- **Continuation:** the step whose decision was blocked, or a re-Gauge when the finding moves the topology
- **Invocation:** Skill tool `research`; Claude Code `/research <question>`; Codex `$research <question>`
- **Annotation:** allowed

### `prototype`

- **Ecosystem and source:** mattpocock/skills, [live](https://github.com/mattpocock/skills/blob/main/skills/engineering/prototype/SKILL.md) · [pinned](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/prototype/SKILL.md)
- **Capability tags:** `design prototype`, Discovery-first
- **Invocation status:** model-invoked; reachable through the Skill tool and by name
- **Prerequisites:** a runnable project for UI variants; none for a logic demo
- **Dependencies:** none
- **Suitable:** a question that needs an artifact to react to: whether a state model or logic feels right, or what a UI should look like
- **Unsuitable:** production implementation; a question that talking can settle
- **Accepted context:** the design question; the surrounding code
- **Expected output:** throwaway code, clearly marked: a single HTML file that drives a state machine through hard cases, or several radically different UI variants on one route. Committed to a throwaway branch with the question and verdict captured on the issue; only the validated decision reaches `main`.
- **Continuation:** the elicitation step it served; the validated decision folds into the spec
- **Invocation:** Skill tool `prototype`; Claude Code `/prototype <question>`; Codex `$prototype <question>`
- **Annotation:** allowed

## Exclusions

- `ask-matt`: **prohibited**. It is a router, and Gauge already owns routing; binding it adds indirection beneath Gauge.
- `implement`, `tdd`, `code-review`: **prohibited as planning steps**. They may appear only as the downstream implementation boundary in the recipe's **Implementation handoff** section.
- `teach`: **discouraged**. Educational is an interaction style inside a planning step. `teach` is a multi-session teaching workspace, bound only when learning is itself the durable mission.
- Third-party ecosystems: **not in the MVP**. A capability none of the entries above provides resolves to `No registry match`.
