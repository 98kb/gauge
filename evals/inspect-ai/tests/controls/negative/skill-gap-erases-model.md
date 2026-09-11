# Gauge result

## Verdict
- Topology: G2 Interactive
- Variant: none
- Modifiers: Human-decision, scoped to permissions, breach behaviour and defaults
- Confidence: High

## Why this fits
Three consequential choices are yours, so they have to be elicited before an
implementation session can start. You ruled out `grill-me` and
`grill-with-docs` for this work, and the planning registry holds no other
interview skill, so the interview step has no skill. Its model profile still
resolves, because a profile binds to the capability rather than to a skill.

## Human collaboration contract
- Human decides: permissions, breach behaviour, user-visible defaults
- Agent may decide: storage shape and naming; assumptions recorded
- Explain before deciding: none
- Checkpoints: after the interview, before the handoff is written

## Resolved planning recipe

### Step 1 — Elicit the three undecided choices
- Capability: interactive elicitation with domain docs
- Skill: No registry match: interactive elicitation with domain docs
- Dependencies: none
- Availability: n/a
- Model: No model registry match: interactive elicitation with domain docs
- Reasoning effort: n/a
- Runtime availability: n/a
- Invocation: the MVP catalog cannot fully resolve this step; the packet below is ready for an interview skill you accept
- Inputs: the verbatim intent; `CONTEXT.md`; `docs/adr/`
- Expected output: the three choices settled, with glossary entries and ADRs
- Exit condition: you confirm each of the three choices
- Next handoff: step 2, which receives the settled decisions

#### Launch packet
```text
Role: interactive elicitation with domain docs as step 1 of a Gauge planning recipe.

Intent, verbatim:
"Add per-account spending limits to the ledger. Don't use grill-me or grill-with-docs."

Destination: permissions, breach behaviour and defaults settled and recorded.

Context:
- Environment: repository at /workspace, branch main
- Findings that matter for this step: ledger entries are immutable per ADR 0001
- Upstream artifacts: CONTEXT.md, docs/adr/0001-entries-are-immutable.md

Constraints and exclusions:
- Nightly settlement behaviour is unchanged

Human collaboration:
- Human decides: permissions, breach behaviour, user-visible defaults
- You may decide: storage shape and naming; record each assumption
- Explain before deciding: none
- Checkpoints: end of the interview

Output: the settled decisions plus glossary and ADR entries, for step 2.

Done when: the human confirms each of the three choices.

Boundary: Plan; do not implement.

Stop and report if:
- a limit turns out to need enforcing inside the settlement run
```

### Step 2 — Write the implementation handoff
- Capability: context handoff
- Skill: handoff
- Dependencies: none
- Availability: unknown
- Model: claude-sonnet-5
- Reasoning effort: medium
- Runtime availability: unknown
- Invocation: `/handoff spending limits, decisions settled`
- Inputs: step 1's conversation and the records it left
- Expected output: one handoff document in the temporary directory
- Exit condition: the handoff exists and names the verification seams
- Next handoff: the implementation agent, which receives that file's path

#### Launch packet
```text
Role: handoff as step 2 of a Gauge planning recipe.

Intent, verbatim:
"Add per-account spending limits to the ledger. Don't use grill-me or grill-with-docs."

Destination: a handoff an implementation session can act on directly.

Context:
- Environment: repository at /workspace, branch main
- Findings that matter for this step: the decisions settled in step 1
- Upstream artifacts: CONTEXT.md, the ADRs step 1 wrote

Constraints and exclusions:
- Nightly settlement behaviour is unchanged

Human collaboration:
- Human decides: nothing further; the three choices are settled
- You may decide: how to structure the handoff; record each assumption
- Explain before deciding: none
- Checkpoints: none

Output: a handoff document, for the implementation agent.

Done when: the handoff names the settled decisions and the verification seams.

Boundary: Plan; do not implement.

Stop and report if:
- step 1 left any of the three choices open
```

## Implementation handoff
- Capability: implementation
- Model: claude-opus-5
- Reasoning effort: high
- Runtime availability: unknown

The implementation agent receives the path to step 2's handoff document.

## Escalate or re-Gauge if
- you accept an interview skill the registry does not list, which calls for a re-Gauge

## Assumptions and unknowns
- The two excluded skills are ruled out by your own statement; no other
  interview skill is assumed.
