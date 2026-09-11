# Anthropic model-registry research

**Verified:** 2026-09-11 (first written 2026-09-10)  
**Purpose:** factual input to `grill-with-docs` for a maintainer-approved Gauge brief  
**Boundary:** research only; no registry schema, step binding, fallback policy, or tracker change is chosen here

## Result

The requested control still exists. Anthropic documents `output_config.effort`
as a response-level behavioral control, and the current Claude Code harness can
select both a model and an effort level. The stop conditions did not fire:
primary documentation was available, harness support was evidenced, and the
requested effort control remains supported.

The current general-purpose Anthropic lineup yields three straightforward
effort-capable registry candidates and one explicit incompatibility:

| Model | Canonical pinned Claude API ID | Supported effort values | Default | Lifecycle on 2026-09-11 | Anthropic-stated suitability | Registry-relevant caveat |
| --- | --- | --- | --- | --- | --- | --- |
| Claude Fable 5.1 | `claude-fable-5-1` | `low`, `medium`, `high`, `xhigh`, `max` | `high` | Active; retirement not sooner than 2027-09-01 | Demanding reasoning and long-horizon agentic work; use when higher-effort Opus 5 still falls short | Claude Code requires v2.1.257+; on the Anthropic API it is usable only when the server reports it available for the organization; in Claude apps gateway sessions the `fable` and `best` aliases still resolve to Fable 5 |
| Claude Opus 5 | `claude-opus-5` | `low`, `medium`, `high`, `xhigh`, `max` | `high` | Active; retirement not sooner than 2027-07-24 | Anthropic's starting point for most workloads; complex agentic coding and enterprise work | At `xhigh` or `max`, disabling thinking is an API error |
| Claude Sonnet 5 | `claude-sonnet-5` | `low`, `medium`, `high`, `xhigh`, `max` | `high` | Active; retirement not sooner than 2027-06-30 | Everyday coding and agent workloads needing a strong speed/capability balance | A lower-capability starting point is a product choice, not established by these facts |
| Claude Haiku 4.5 | `claude-haiku-4-5-20251001` | none | n/a | Active; retirement not sooner than 2026-10-15 | Lowest latency; high-volume, straightforward, cost-sensitive, and subagent tasks | Cannot satisfy a requirement that every selected model carry an executable effort value |

Sources: Anthropic's [models overview], [model-selection guide], [effort guide],
and [model lifecycle table]. The lifecycle dates apply to Anthropic-operated
platforms; partner-operated Bedrock and Google Cloud schedules can differ.

These are candidate records, not a decided registry. The table intentionally
uses Anthropic's current comparison lineup rather than treating every still-active
older or specialized model as equally recommendable. That catalog policy remains
for the maintainer.

## Changes since 2026-09-10

- **Models and lifecycle: none.** No model was launched, deprecated, or retired
  between 2026-09-10 and 2026-09-11. Anthropic's newest [release notes] entry
  (2026-09-10) covers only Managed Agents and the `ant` CLI. The most recent
  model launch remains Fable 5.1 and Mythos 5.1 on 2026-09-01. The four IDs,
  effort sets, defaults, and retirement dates in the table above re-verified
  unchanged. Haiku 4.5's "not sooner than" date (2026-10-15) is now about five
  weeks away, but no deprecation notice has been published.
- **Claude Code harness: changed.** The local version is now `2.1.268` (it was
  `2.1.266`). Per the [Claude Code changelog], v2.1.267 (2026-09-09):
  - fixed `effort:` frontmatter being ignored on models whose default effort
    is still held (Opus 4.7, Opus 4.8, Fable 5);
  - added a `maxEffortLevel` setting that caps effort;
  - kept `fable`/`best` resolving to Fable 5 in Claude apps gateway sessions.

  The harness caveats below were updated to match.
- **Wording refinements, not changes in fact:** the Fable 5.1 org-access
  caveat, the Models API "organization" wording, the Opus 4.5 effort gap, and
  the Gauge-spec citation are now stated more precisely. A further possible
  conflict with the Gauge spec was added as discrepancy 8.

## Canonical IDs and verification

- Anthropic states that every model ID identifies a fixed model version. For
  Claude 4.6 and later, a dateless ID such as `claude-opus-5` is the canonical
  pinned snapshot, not an evergreen alias. Models before 4.6 use a dated ID;
  therefore `claude-haiku-4-5-20251001` is the pinned Haiku spelling. Earlier
  short forms such as `claude-haiku-4-5` are convenience aliases and are not
  suitable for a registry that promises pinning. See [model IDs and versioning].
- The authenticated [Models API] is the authoritative account-level inventory.
  Anthropic says `GET /v1/models` "can be used to determine which models are
  available for use in the API". It is called with the caller's API key and an
  optional `anthropic-workspace-id` header. The docs do not say "organization";
  scoping it to the caller's account/workspace is an inference. For every model
  it returns a `capabilities.effort` object: a `supported` flag plus per-level
  flags for `low`, `medium`, `high`, and `max`, with `xhigh` nullable.
  Public documentation establishes the catalog facts above; an implementation
  can only claim runtime availability after checking the target account/provider.
- Lifecycle status is a separate fact. The Models API documents availability and
  capabilities, while Anthropic's lifecycle page supplies `Active`, `Legacy`,
  `Deprecated`, and `Retired` status and retirement dates. A future registry
  refresh therefore needs both sources if it claims both availability and
  lifecycle.
- Anthropic's documentation is live rather than commit-pinned. The model IDs are
  pinned; this research snapshot is not. Re-verify the overview, effort, and
  lifecycle pages on every registry maintenance pass.

## What “reasoning effort” means

The API field is `output_config.effort`. Anthropic documents five possible
values: `low`, `medium`, `high`, `xhigh`, and `max`, with model-dependent
support. `high` is equivalent to omitting the parameter on the API. Effort
influences all generated tokens, including text, tool calls, and thinking; it is
a behavioral signal, not a strict token budget. `adaptive` is a thinking mode,
not an effort value. On Fable 5.1, Mythos 5.1, and Opus 5, a beta per-message
effort change (`mid-conversation-output-config-2026-07-01`) can alter effort
mid-conversation while keeping the prompt cache. On other models, a new
top-level value restarts the cache. See the [effort guide].

This is distinct from the implementation estimates Gauge forbids. Gauge's
[implementation specification](../gauge-implementation-spec.md#19-deferred-extensions)
lists "numerical effort, cost, or time estimation" among the extensions not to
implement in the MVP. §4 also rules out time, cost, story-point, or person-day
estimates as Gauge's primary result, and §6.1 forbids a numerical complexity
score. A value such as
`Reasoning effort: high` configures model behavior; it does not predict duration,
cost, story points, complexity, or human work.

Anthropic also says effort should be tuned against workload-specific evaluations.
Its published suitability guidance is enough to seed a maintainer discussion,
not enough to prove a per-Gauge-step mapping without Gauge-specific evals.

## Harness support

### Claude Code: evidenced, with limits

Claude Code's [skill frontmatter reference] supports both fields directly:

- `model` overrides the session model for the rest of the turn in which the
  skill is active, then the session model resumes;
- with `context: fork`, `model` sets the forked subagent's model instead;
- `effort` overrides session effort while the skill is active;
- either can also be selected at session launch with `--model` and `--effort`.

The local check on 2026-09-11 found Claude Code `2.1.268` (it was `2.1.266` on
2026-09-10); its help lists both flags. That version exceeds the documented
minimums: v2.1.257 for Fable 5.1, v2.1.218 for `background: false` on forked
skills, and v2.1.267 for the fix that makes frontmatter effort apply during the
default-effort hold.

The override is not absolute:

- an organization `availableModels` policy can reject a skill's model override,
  in which case Claude Code retains the current session model. For a
  `context: fork` skill, an excluded model instead follows the subagent rule,
  and Claude Code runs it on a fallback model. In auto mode, a model that auto
  mode doesn't support is likewise not used;
- `CLAUDE_CODE_EFFORT_LEVEL` takes precedence over skill frontmatter, and a
  `maxEffortLevel` setting or organization effort cap still limits the level a
  skill runs at (`maxEffortLevel` was added in v2.1.267);
- on Fable 5, Opus 4.8, and Opus 4.7, Claude Code holds the model's default
  effort across sessions. Before v2.1.267 the hold took precedence and
  frontmatter effort was ignored; from v2.1.267, frontmatter effort applies
  during the hold. Opus 5 and Fable 5.1 have no hold;
- if a model does not support the requested effort, Claude Code falls back to
  the highest supported level at or below it rather than preserving the exact
  recommendation;
- `max` is accepted for the session and in skill frontmatter, but not in the
  persistent `effortLevel` or `modelSettings` keys;
- model and effort are Claude Code extensions, not portable Agent Skills fields.
  Claude.ai uploads and the Skills API accept only the standard six-field
  frontmatter subset and reject extra keys. See [Claude Code model configuration]
  and [skill frontmatter portability].

Therefore Claude Code can honor a per-skill model/effort profile, but a Gauge
recipe cannot truthfully claim that every harness will enforce it. Whether the
recipe is advisory or availability-gated is a maintainer decision.

### Current Gauge and Inspect AI harness: separate concern

Gauge currently resolves only skills. The production
[planning registry](../../references/planning-registry.md) has no model entries,
and the [recipe contract](../../references/recipe-contract.md#result-schema)
requires eight step fields without `Model` or `Reasoning effort`. The installed
Matt Pocock skill bundle (plugin cache version `1.2.3`, 35 `SKILL.md` files),
re-inspected on 2026-09-11, also had no `model:` or `effort:` frontmatter
entries. Model recommendations are therefore a new Gauge
layer, not metadata already inherited from the selected skills.

Inspect AI's `--model` option is unrelated to recipe-step execution. This
repository's [Inspect entry point](../../evals/inspect-ai/run.sh) explicitly uses
`--model` or `INSPECT_EVAL_MODEL` for “the model under evaluation,” and its
[task module](../../evals/inspect-ai/skill_evals/gauge/task.py) deliberately does
not hard-code one. That flag can evaluate a future Gauge change against a model;
it does not select or enforce the model recommended inside a generated recipe.

## Explicit discrepancies and constraints

1. **Current does not mean effort-capable.** Haiku 4.5 is active and in the
   current comparison lineup, but the overview marks effort unsupported.
2. **Active does not mean preferred.** The lifecycle table contains older active
   models not present in Anthropic's four-model comparison lineup. Inclusion as
   fallbacks is catalog policy, not a lifecycle fact.
3. **API and Claude Code support are not identical inventories.** The API effort
   guide includes Opus 4.5 among supported models, while Claude Code's effort
   table begins at Opus 4.6. The public effort page lists
   `claude-opus-4-5-20251101` as supported but leaves Opus 4.5 out of both the
   `max` and `xhigh` availability lists. It never states Opus 4.5's accepted
   set; inferring `low`/`medium`/`high` from that omission is not documented.
   Do not create a pinned Opus 4.5 execution profile
   without querying the target Models API and verifying the target harness.
4. **`xhigh` is not universally below `max` in availability.** Opus 4.6 and
   Sonnet 4.6 support `max` but not `xhigh`; Claude Code maps a requested `xhigh`
   on Opus 4.6 down to `high`. Validate values per model, not against one global
   enum alone.
5. **Model IDs and aliases differ by generation.** Dateless 4.6+ IDs are pinned;
   dateless pre-4.6 names can be moving aliases.
6. **A documented recommendation can be overridden at runtime.** Organization
   allowlists, account access, environment settings, and provider-specific IDs
   can prevent the exact model/effort pair from running.
7. **Per-step recommendation is not yet portable.** Claude Code can apply it to
   skill turns, but the cross-tool Agent Skills standard does not carry these
   fields and Inspect's evaluation-model setting serves another purpose.
8. **Possible conflict with a deferred extension.** Gauge's
   [implementation specification](../gauge-implementation-spec.md#19-deferred-extensions)
   defers "multiple provider registries" from the MVP. The spec does not say
   whether a separate Anthropic model registry counts as a second provider
   registry or as a different kind of registry. That call is the maintainer's.

## Facts to carry into `grill-with-docs`

The research does not answer these product questions:

1. Whether model/effort applies to planning-skill steps only, or also G0,
   downstream implementation, and tracker-setup prerequisites.
2. Whether a step names one profile or an ordered fallback list.
3. Whether recommendations are advisory across harnesses or emitted only when
   the current harness proves it can honor them.
4. Whether the binding key is recipe capability, selected skill, modifiers such
   as High-assurance, or some combination.
5. Whether an unsupported pair is retained with availability evidence, rendered
   as `n/a`, or becomes a model-registry gap.
6. Whether to create a separate model registry now, as requested, or use the
   smaller interim shape of execution profiles inside the existing planning
   registry until a second provider exists.

Any maintained entry should minimally preserve: canonical ID, provider,
supported effort values, lifecycle/status, verification date and sources,
suitability, and harness/account availability. The evidence above supports those
fields but does not decide their schema or bindings.

## Primary sources

- [Models overview] — current comparison lineup, IDs, default effort, and broad suitability
- [Model-selection guide] — selection criteria and official starting-point guidance
- [Effort guide] — API field, semantics, values, compatibility, defaults, and model-specific guidance
- [Model IDs and versioning] — pinned IDs versus convenience aliases
- [Model lifecycle table] — lifecycle definitions, current status, and retirement dates
- [Models API] — account inventory and machine-readable per-level effort capabilities
- [Claude Code model configuration] — model and effort compatibility, precedence, fallback, and CLI controls
- [Skill frontmatter reference] — per-skill `model` and `effort` overrides
- [Skill frontmatter portability] — Claude Code extensions versus the Agent Skills subset
- [Release notes] — model launches and API changes, used to confirm nothing changed after 2026-09-10
- [Claude Code changelog] — v2.1.266–v2.1.268 harness changes

The `slash-commands` URL serves the same "Extend Claude with skills" page as
`https://code.claude.com/docs/en/skills`, with the `Frontmatter reference` and
`Using skill frontmatter outside Claude Code` headings. Both anchors below
resolved on 2026-09-11.

[models overview]: https://platform.claude.com/docs/en/models/overview
[model-selection guide]: https://platform.claude.com/docs/en/about-claude/models/choosing-a-model
[effort guide]: https://platform.claude.com/docs/en/build-with-claude/effort
[model IDs and versioning]: https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions
[model lifecycle table]: https://platform.claude.com/docs/en/about-claude/model-deprecations
[Models API]: https://platform.claude.com/docs/en/api/models/list
[Claude Code model configuration]: https://code.claude.com/docs/en/model-config
[skill frontmatter reference]: https://code.claude.com/docs/en/slash-commands#frontmatter-reference
[skill frontmatter portability]: https://code.claude.com/docs/en/slash-commands#using-skill-frontmatter-outside-claude-code
[release notes]: https://platform.claude.com/docs/en/release-notes/overview
[Claude Code changelog]: https://code.claude.com/docs/en/changelog
