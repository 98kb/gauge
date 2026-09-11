# Model registry

The authoritative, human-edited source of Gauge's model profiles and the capabilities they bind to. It is separate from the planning registry: a boundary's skill and its model profile resolve independently, and neither outcome changes the other. Human edits to this file are authoritative. Gauge never refreshes it, never queries a provider API to extend it, and never infers a binding from a provider's suitability guidance.

**Scope.** One provider, deliberately: Anthropic. A second provider is a separate decision, not a new row.

**Verified** 2026-09-11 against Anthropic's live documentation, linked from each row. The model IDs are pinned; the documentation is not, so every maintenance pass re-verifies each ID, its effort values, and its lifecycle.

## Profiles

A profile is one canonical pinned model ID plus one reasoning-effort value that model supports. Reasoning effort is Anthropic's `output_config.effort` model control, a control on how much the model reasons. It is never an estimate of implementation time, cost, size, or complexity. A model without effort support cannot form a profile, which is why Claude Haiku 4.5 (`claude-haiku-4-5-20251001`) has none. Convenience aliases such as `opus`, `fable`, or `best` are never profile IDs.

| Profile | Provider | Model ID | Reasoning effort | Supported effort values | Lifecycle | Harness caveats | Verified | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `fable-5-1-low` | Anthropic | `claude-fable-5-1` | `low` | `low`, `medium`, `high`, `xhigh`, `max` | Active; retirement not sooner than 2027-09-01 | Claude Code 2.1.257 or later; on the Anthropic API only when the server reports it available to the organization; in Claude apps gateway sessions the `fable` and `best` aliases resolve to Fable 5 | 2026-09-11 | [models], [effort], [lifecycle], [Claude Code models] |
| `fable-5-1-medium` | Anthropic | `claude-fable-5-1` | `medium` | `low`, `medium`, `high`, `xhigh`, `max` | Active; retirement not sooner than 2027-09-01 | Claude Code 2.1.257 or later; on the Anthropic API only when the server reports it available to the organization; in Claude apps gateway sessions the `fable` and `best` aliases resolve to Fable 5 | 2026-09-11 | [models], [effort], [lifecycle], [Claude Code models] |
| `fable-5-1-high` | Anthropic | `claude-fable-5-1` | `high` | `low`, `medium`, `high`, `xhigh`, `max` | Active; retirement not sooner than 2027-09-01 | Claude Code 2.1.257 or later; on the Anthropic API only when the server reports it available to the organization; in Claude apps gateway sessions the `fable` and `best` aliases resolve to Fable 5 | 2026-09-11 | [models], [effort], [lifecycle], [Claude Code models] |
| `fable-5-1-xhigh` | Anthropic | `claude-fable-5-1` | `xhigh` | `low`, `medium`, `high`, `xhigh`, `max` | Active; retirement not sooner than 2027-09-01 | Claude Code 2.1.257 or later; on the Anthropic API only when the server reports it available to the organization; in Claude apps gateway sessions the `fable` and `best` aliases resolve to Fable 5 | 2026-09-11 | [models], [effort], [lifecycle], [Claude Code models] |
| `fable-5-1-max` | Anthropic | `claude-fable-5-1` | `max` | `low`, `medium`, `high`, `xhigh`, `max` | Active; retirement not sooner than 2027-09-01 | Claude Code 2.1.257 or later; on the Anthropic API only when the server reports it available to the organization; in Claude apps gateway sessions the `fable` and `best` aliases resolve to Fable 5; `max` is accepted for a session or in skill frontmatter, not in the persistent `effortLevel` or `modelSettings` keys | 2026-09-11 | [models], [effort], [lifecycle], [Claude Code models] |
| `opus-5-low` | Anthropic | `claude-opus-5` | `low` | `low`, `medium`, `high`, `xhigh`, `max` | Active; retirement not sooner than 2027-07-24 | none | 2026-09-11 | [models], [effort], [lifecycle] |
| `opus-5-medium` | Anthropic | `claude-opus-5` | `medium` | `low`, `medium`, `high`, `xhigh`, `max` | Active; retirement not sooner than 2027-07-24 | none | 2026-09-11 | [models], [effort], [lifecycle] |
| `opus-5-high` | Anthropic | `claude-opus-5` | `high` | `low`, `medium`, `high`, `xhigh`, `max` | Active; retirement not sooner than 2027-07-24 | none | 2026-09-11 | [models], [effort], [lifecycle] |
| `opus-5-xhigh` | Anthropic | `claude-opus-5` | `xhigh` | `low`, `medium`, `high`, `xhigh`, `max` | Active; retirement not sooner than 2027-07-24 | disabling thinking at this reasoning effort is an API error | 2026-09-11 | [models], [effort], [lifecycle] |
| `opus-5-max` | Anthropic | `claude-opus-5` | `max` | `low`, `medium`, `high`, `xhigh`, `max` | Active; retirement not sooner than 2027-07-24 | disabling thinking at this reasoning effort is an API error; `max` is accepted for a session or in skill frontmatter, not in the persistent `effortLevel` or `modelSettings` keys | 2026-09-11 | [models], [effort], [lifecycle], [Claude Code models] |
| `sonnet-5-low` | Anthropic | `claude-sonnet-5` | `low` | `low`, `medium`, `high`, `xhigh`, `max` | Active; retirement not sooner than 2027-06-30 | none | 2026-09-11 | [models], [effort], [lifecycle] |
| `sonnet-5-medium` | Anthropic | `claude-sonnet-5` | `medium` | `low`, `medium`, `high`, `xhigh`, `max` | Active; retirement not sooner than 2027-06-30 | none | 2026-09-11 | [models], [effort], [lifecycle] |
| `sonnet-5-high` | Anthropic | `claude-sonnet-5` | `high` | `low`, `medium`, `high`, `xhigh`, `max` | Active; retirement not sooner than 2027-06-30 | none | 2026-09-11 | [models], [effort], [lifecycle] |
| `sonnet-5-xhigh` | Anthropic | `claude-sonnet-5` | `xhigh` | `low`, `medium`, `high`, `xhigh`, `max` | Active; retirement not sooner than 2027-06-30 | none | 2026-09-11 | [models], [effort], [lifecycle] |
| `sonnet-5-max` | Anthropic | `claude-sonnet-5` | `max` | `low`, `medium`, `high`, `xhigh`, `max` | Active; retirement not sooner than 2027-06-30 | `max` is accepted for a session or in skill frontmatter, not in the persistent `effortLevel` or `modelSettings` keys | 2026-09-11 | [models], [effort], [lifecycle], [Claude Code models] |

## Bindings

A binding is keyed by the capability names in `routing-model.md`, never by the selected skill. Only `High-assurance` changes a binding: when the verdict carries `High-assurance`, every execution boundary reads the `High-assurance` column and never falls back to Base. No other modifier plays any part. `unbound` is an intentional gap.

| Capability (routing model) | Base | `High-assurance` |
| --- | --- | --- |
| `tracker setup` | `sonnet-5-low` | unbound |
| `context handoff` | `sonnet-5-medium` | unbound |
| `interactive elicitation` | `opus-5-high` | `fable-5-1-high` |
| `interactive elicitation with domain docs` | `opus-5-high` | `fable-5-1-high` |
| `durable specification` | `fable-5-1-high` | `fable-5-1-xhigh` |
| `ticket decomposition` | `opus-5-high` | `fable-5-1-xhigh` |
| `navigated decision map` | `fable-5-1-high` | `fable-5-1-max` |
| `external research` | `sonnet-5-high` | `opus-5-xhigh` |
| `design prototype` | `sonnet-5-high` | unbound |
| `implementation` | `opus-5-high` | `fable-5-1-xhigh` |

## No model registry match

`No model registry match: <binding key>` is a resolution outcome, not a runtime state. It applies when the table above has no profile for the boundary's binding key: the capability for a base boundary, or `<capability> + High-assurance` for a High-assurance one. A capability absent from the table, such as one the planning registry also cannot supply, is a gap as well. The boundary keeps its `Capability`, and both `Reasoning effort` and `Runtime availability` read `n/a`. The closest profile, the Base column, a different model, and a lower reasoning effort are all ruled out as substitutes. The outcome is distinct from the planning registry's `No registry match`: either can occur without the other.

## Runtime availability

Beside every resolved profile, label what local, read-only evidence proves about selecting that exact model and reasoning effort:

- `unavailable: <evidence>`, when local evidence proves the exact pair cannot be selected. Name the evidence:
  - an `availableModels` list that excludes the model ID, read from managed settings, or from non-managed settings when every non-managed scope is readable and none lists the model (non-managed lists merge);
  - a `maxEffortLevel` or `modelSettings.<model ID>.maxEffortLevel` cap below the profile's effort, read from the highest-precedence scope that sets one, with every scope above it readable (managed settings, then local project `.claude/settings.local.json`, then shared project `.claude/settings.json`, then user `~/.claude/settings.json`);
  - a harness version below the model's stated minimum in **Harness caveats**, such as `claude --version` reporting below 2.1.257 for `claude-fable-5-1`.
- `unknown`, in every other case, including when no settings or version can be read.

Gauge never reports `available`. Organization and account access is enforced server-side, and the recipe usually runs in another session than the one that emitted it. No network or provider-API call is made to settle a label, and lifecycle or catalog status is not account evidence.

The label never changes the recommendation. An `unavailable` boundary keeps its exact model and reasoning effort; Gauge never substitutes a model, lowers the reasoning effort, or turns the mismatch into a model registry gap or `n/a`. Skill availability (`installed`, `not detected`, `unknown`, `n/a`) is a separate field with separate evidence.

[models]: https://platform.claude.com/docs/en/models/overview
[effort]: https://platform.claude.com/docs/en/build-with-claude/effort
[lifecycle]: https://platform.claude.com/docs/en/about-claude/model-deprecations
[Claude Code models]: https://code.claude.com/docs/en/model-config
