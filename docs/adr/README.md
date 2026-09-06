# ADR index — gauge

One flat log. This repo hosts a single skill; every ADR here either binds gauge
directly or is a cross-cutting decision gauge adopts.

## The rule in three lines

- An ADR **binds** its owning skill, plus everything if it is cross-cutting.
- Another skill's ADR is **precedent, not authority**. It may be transposed, and the transposing ADR must declare the transposition.
- Once transposed, cite the **transposing ADR** for the transposed wording. The origin is cited only for what the origin actually says.

## Cross-cutting

Carried over from [98kb/skills](https://github.com/98kb/skills) because gauge adopts them.

| ADR | Decision |
| --- | --- |
| [0001](0001-distinct-label-for-child-maps.md) | Distinct label for child maps, not reused `wayfinder:map` + parent inference |
| [0002](0002-composition-mode-keyed-on-disable-model-invocation.md) | Composition mode keyed on `disable-model-invocation`, scoped to Claude Code only |
| [0003](0003-eval-grading-is-deterministic-plus-llm-judge-split.md) | Eval grading splits deterministic checks from LLM-as-judge rubric grading |
| [0016](0016-a-phase-number-forward-references-a-map-that-does-not-exist.md) | A phase number is a forward reference to a map that does not exist |

## How gauge adopts 0002 and 0003

`gauge` adopts both, and neither adoption is carried by an ADR of its own:

- **0003.** Declared in the skill, at the head of the standing invariants in [`references/evaluation-scenarios.md`](../../references/evaluation-scenarios.md) — every invariant is marked **D** (mechanical) or **J** (judged), *"following the deterministic-plus-judge split this repository records in ADR 0003, adopted here for a skill outside the product pipeline"*. The eval suite implements that split: `skill_evals/gauge/contract.py` grades only the D invariants and `gauge_semantic_quality` only the J ones, and the two are reported as separate metrics rather than blended.
- **0002.** Relied on rather than reasoned about: `gauge` carries `disable-model-invocation: true`, which is what makes it user-invoked, and the eval harness preserves that key through `skill_evals/shared/skills.py` so the evaluated skill keeps the composition mode the shipped one has.
