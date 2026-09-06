# Planning recipe for the spending-limits work

<!--
The cry-wolf control. Same decisions as a canonical G2 recipe, deliberately
different surface: a reworded top heading, `## Result` for `## Verdict`,
numbered step headings instead of `### Step 1 — ...`, bold field labels, and
tilde fences. `evaluation-scenarios.md` says two results with different wording
and the same decisions both pass, so every check must still pass here. A
phrasing-tuned pattern false-failing a correct run is a different risk from a
check that cannot fail, and it is not covered by the negative controls.
-->

## Result
- **Topology:** G2 Interactive
- **Variant:** none
- **Modifiers:** Human-decision, scoped to permissions, breach behaviour and defaults
- **Confidence:** High

## Why this fits
Three consequential choices sit with you and nowhere else, so the knowledge has
to be elicited before anything can be specified. Once they are settled the build
is one coherent run, which is what keeps this off G3.

## Human collaboration contract
- **Human decides:** permissions, breach behaviour, user-visible defaults
- **Agent may decide:** storage shape and naming; assumptions recorded
- **Explain before deciding:** none
- **Checkpoints:** after the interview, before the handoff is written

## Resolved planning recipe

### 1. Elicit the three undecided choices
- **Skill:** grill-with-docs
- **Dependencies:** grilling, domain-modeling
- **Availability:** installed
- **Invocation:** `/grill-with-docs`
- **Inputs:** the verbatim intent; `CONTEXT.md`; `docs/adr/`
- **Expected output:** shared understanding, plus glossary entries and any ADRs
- **Exit condition:** the frontier is empty and you confirm it
- **Next handoff:** step 2, which receives the settled decisions

#### Launch packet

~~~text
Role: grill-with-docs as step 1 of a Gauge planning recipe.

Intent, verbatim:
"Add per-account spending limits to the ledger."

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

Output: shared understanding plus glossary and ADR entries, for step 2.

Done when: the design tree's frontier is empty and the human confirms it.

Boundary: Plan; do not implement.

Stop and report if:
- a limit turns out to need enforcing inside the settlement run
~~~

### 2. Write the implementation handoff
- **Skill:** handoff
- **Dependencies:** none
- **Availability:** installed
- **Invocation:** `/handoff spending limits, decisions settled`
- **Inputs:** step 1's conversation and the records it left
- **Expected output:** one handoff document in the temporary directory
- **Exit condition:** the handoff exists and names the verification seams
- **Next handoff:** the implementation agent, which receives that file's path

#### Launch packet

~~~text
Role: handoff as step 2 of a Gauge planning recipe.

Intent, verbatim:
"Add per-account spending limits to the ledger."

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
~~~

## Implementation handoff
The implementation agent receives the path to step 2's handoff document.

## Escalate or re-Gauge if
- the interview surfaces a decision that cannot be settled in one session

## Assumptions and unknowns
- Assumed the three named choices are the only human-held ones, from your own
  statement that they are yours to call.
