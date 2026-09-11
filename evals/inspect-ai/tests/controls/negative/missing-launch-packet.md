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
- Model: No model registry match: context handoff + High-assurance
- Reasoning effort: n/a
- Runtime availability: n/a
- Invocation: `/handoff token expiry change at the auth boundary`
- Inputs: the verbatim intent and the auth module paths found in reconnaissance
- Expected output: one handoff document in the temporary directory
- Exit condition: the handoff file exists and names the verification seams
- Next handoff: the implementation agent, which receives that file's path

## Implementation handoff
- Capability: implementation
- Model: claude-fable-5-1
- Reasoning effort: xhigh
- Runtime availability: unknown

The implementation agent receives the path to step 1's handoff document. The
model recommendation is advice for launching that session.
