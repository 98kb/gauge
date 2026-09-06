# Gauge

Gauge is a pre-planning engagement and routing skill for AI-native software
development. Given an intent, the environment it lands in, the human engaging
with it, and a curated registry of planning skills, it answers one question:

> What exact process should produce the plan for this intent, or should a
> separate planning step be skipped?

The answer is a **planning recipe**: a base topology, the modifiers attached to
it, the exact skills to start in order, one copy-paste-ready launch packet per
step, the human's decision rights, and the triggers that send the work back
here.

## Topologies

| Code | Name        | Contract |
| ---- | ----------- | -------- |
| G0   | Direct      | Skip a separate planning phase. Hand the intent straight to implementation. |
| G1   | Handoff     | Produce a bounded context/specification handoff without a substantive human interview. |
| G2   | Interactive | Elicit human-held knowledge or judgement before creating the implementation handoff. |
| G3   | Navigated   | Preserve decisions and decomposition across multiple planning or implementation sessions. |

## Installing

```
npx skills add 98kb/gauge
```

## Layout

- **`SKILL.md`** — the skill definition (the installable unit)
- **`agents/`** — runtime declarations (e.g. OpenAI agent config)
- **`references/`** — normative reference documents the skill reads at runtime
- **`docs/`** — implementation spec and architectural decision records
- **`evals/`** — [Inspect AI](https://inspect.aisi.org.uk/) evaluation suite

## Evaluation

The eval suite lives under `evals/inspect-ai/`. See
[`evals/inspect-ai/README.md`](evals/inspect-ai/README.md) for setup and
usage. Quick start:

```bash
cd evals/inspect-ai
./run.sh setup                     # create the Python env (once)
./run.sh check                     # offline validation; no model, no cost
./run.sh smoke --model <provider/model>   # 3-case smoke subset
./run.sh gauge --model <provider/model>   # full 14-case suite
```

## Docs

- [Implementation Specification](docs/gauge-implementation-spec.md)
- [Inspect AI Eval Setup](docs/INSPECT_AI_GAUGE_EVAL_SETUP.md)
- [Architectural Decision Records](docs/adr/)

## Origin

Extracted from [98kb/skills](https://github.com/98kb/skills), where Gauge was
developed alongside the product-planning skill pipeline. This repo hosts the
gauge skill only — the product skills (`to-vision`, `to-pitch`, etc.) remain in
`98kb/skills`.
