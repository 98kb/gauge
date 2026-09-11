# Gauge result

## Verdict
- Topology: G0 Direct
- Variant: none
- Modifiers: Exception-only
- Confidence: High

## Why this fits
A local UI label with no compatibility effect, in a repository the human knows,
with tests already covering the surface. A planning phase would add ceremony
and no information.

## Human collaboration contract
- Human decides: nothing beyond the wording already given
- Agent may decide: standard implementation choices; assumptions recorded
- Explain before deciding: none
- Checkpoints: end of step only

## Resolved planning recipe

### Step 1 — Implement directly
- Capability: context handoff
- Skill: No planning skill
- Dependencies: none
- Availability: n/a
- Model: claude-opus-5
- Reasoning effort: high
- Runtime availability: unknown
- Invocation: paste the packet below into an implementation agent
- Inputs: the verbatim intent
- Expected output: the renamed label and a passing test run
- Exit condition: the existing test suite passes
- Next handoff: none; this is the last step

#### Launch packet
```text
Role: implementation agent as the only step of a Gauge planning recipe.

Intent, verbatim:
"Rename the Save button label to Save changes."

Destination: the label reads "Save changes" everywhere it is rendered.

Context:
- Environment: repository at /workspace, branch main
- Findings that matter for this step: the label is local; no external consumer
- Upstream artifacts: none

Constraints and exclusions:
- No copy change anywhere else

Human collaboration:
- Human decides: nothing further
- You may decide: standard implementation choices; record each assumption
- Explain before deciding: none
- Checkpoints: none

Output: the edited source, for the human.

Done when: the label is changed and the tests pass.

Boundary: Implement within the constraints above; verify by running the
existing test suite before reporting done.

Stop and report if:
- the label turns out to be read by a snapshot test in another package
```

## Implementation handoff
This recipe's only step is the implementation step; its packet is above.

## Escalate or re-Gauge if
- the label proves to be part of a published API surface

## Assumptions and unknowns
- Assumed the human is familiar with this repository, from their own statement.
