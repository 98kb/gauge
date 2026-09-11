# Gauge result

## Verdict
- Topology: G1 Handoff
- Variant: none
- Modifiers: High-assurance
- Confidence: High

## Why this fits
The route is known and no product decision is outstanding, so no interview is
needed. The change lands on an authentication boundary, which is what attaches
High-assurance rather than the topology.

## Human collaboration contract
- Human decides: token lifetime policy
- Agent may decide: standard implementation choices; assumptions recorded
- Explain before deciding: none
- Checkpoints: end of step only

## Resolved planning recipe

### Step 1 — Bounded context handoff
- Capability: context handoff
- Skill: handoff
- Dependencies: none
- Availability: not detected
- Model: claude-sonnet-5
- Reasoning effort: medium
- Runtime availability: unknown
- Invocation: `/handoff token expiry change at the auth boundary`
- Inputs: the verbatim intent and the auth module paths found in reconnaissance
- Expected output: one handoff document in the temporary directory
- Exit condition: the handoff file exists and names the verification seams
- Next handoff: the implementation agent, which receives that file's path

#### Launch packet
```text
Role: handoff as step 1 of a Gauge planning recipe.

Intent, verbatim:
"Change how token expiry is handled at our authentication boundary."

Destination: a written handoff an implementation session can act on directly.

Context:
- Environment: repository at /workspace, branch main
- Findings that matter for this step: auth boundary in src/auth/, existing tests
- Upstream artifacts: none

Constraints and exclusions:
- No change to the public token format

Human collaboration:
- Human decides: token lifetime policy
- You may decide: standard implementation choices; record each assumption
- Explain before deciding: none
- Checkpoints: none

Output: a handoff document, for the implementation agent.

Done when: the handoff names failure analysis, verification seams and rollback.

Boundary: Plan; do not implement.

Stop and report if:
- the token format turns out to be consumed outside this repository
```

## Installation required
`handoff` is not detected in this environment. Install it with
`npx skills@latest add mattpocock/skills --skill handoff`. It has no
dependencies.

## Implementation handoff
- Capability: implementation
- Model: claude-fable-5-1
- Reasoning effort: xhigh
- Runtime availability: unknown

The implementation agent receives the path to step 1's handoff document. The
model recommendation is advice for launching that session.

## Escalate or re-Gauge if
- reconnaissance during planning finds a second consumer of the token format

## Assumptions and unknowns
- Assumed the existing test suite covers the auth boundary; not verified.
