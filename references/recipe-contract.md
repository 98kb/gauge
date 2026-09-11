# Recipe contract

The shape of every Gauge result. Wording may vary; a field that is relevant is never silently omitted, and a field that does not apply says so. The one conditional section is **Installation required**, present only when something needs installing.

## Result schema

````markdown
# Gauge result

## Verdict
- Topology: <G0 Direct | G1 Handoff | G2 Interactive | G3 Navigated>
- Variant: <G3-A route decided | G3-B route foggy | none>
- Modifiers: <none, or the list>
- Confidence: <High | Medium | Low>

## Why this fits
<Short. The facts that selected the topology, the variant, and each modifier, drawn from work topology, knowledge location, continuity, risk, and human context. When the human walked in expecting a different topology or method, say so and name what moved it.>

## Human collaboration contract
- Human decides: <named decision domains>
- Agent may decide: <named delegated domains; assumptions recorded>
- Explain before deciding: <areas, or none>
- Checkpoints: <gates, or "end of step only">

## Resolved planning recipe

### Step 1 — <purpose>
- Capability: <capability from the routing model, or the missing one>
- Skill: <canonical skill | No planning skill | No registry match: <missing capability>>
- Dependencies: <expanded list, or none>
- Availability: <installed | not detected | unknown | n/a>
- Model: <canonical pinned model ID | No model registry match: <binding key>>
- Reasoning effort: <the profile's one reasoning-effort value | n/a on a model registry gap>
- Runtime availability: <unavailable: <named local evidence> | unknown | n/a on a model registry gap>
- Invocation: <exact user action in this harness, or the orchestration action>
- Inputs: <the intent and the artifacts this step receives>
- Expected output: <artifact and where it lands>
- Exit condition: <observable completion>
- Next handoff: <recipient and what it receives>

#### Launch packet
```text
<copy-paste-ready prompt>
```

<Repeat per step.>

## Installation required
<Present only when a bound skill is `not detected` or `unknown`: the route from the registry, every dependency, and the official source. Omitted otherwise.>

## Implementation handoff
- Capability: implementation
- Model: <canonical pinned model ID | No model registry match: <binding key>>
- Reasoning effort: <the profile's one reasoning-effort value | n/a on a model registry gap>
- Runtime availability: <unavailable: <named local evidence> | unknown | n/a on a model registry gap>

<What the implementation agent receives, from which step, and how it is launched. In G0, the one line pointing at the implementation step, with no fields.>

## Escalate or re-Gauge if
- <observable trigger the executing agent can detect>

## Assumptions and unknowns
- <only consequential items; explicit human facts kept separate from labelled inference>
````

**What the result leaves out.** The human model is worked, not printed: its consequential assumptions go under **Assumptions and unknowns**, and **Why this fits** cites only the property that moved a modifier or the topology. Reconnaissance findings appear where a step needs them, inside that step's packet, rather than as a survey. Implementation is described under **Implementation handoff**; it is a recipe step only in G0, where it is the only step.

## Launch packets

A launch packet is the prompt one skill or agent receives. Gauge supplies **what**, **context**, **human interaction**, **output**, and **handoff**; the skill owns **how** it performs its discipline, so the packet never restates or competes with the skill's internal method.

Every packet carries all nine:

1. the target skill or agent role;
2. the original intent, quoted verbatim;
3. relevant environment context and artifact references;
4. confirmed constraints and exclusions;
5. the human collaboration contract as it applies to this step;
6. the required output and its recipient;
7. the completion condition;
8. for a planning step, a firm `Plan; do not implement` boundary; for the implementation step, the verification expectation;
9. escalation conditions.

Template:

```text
Role: <skill name> as step <n> of a Gauge planning recipe.

Intent, verbatim:
"<the human's original wording>"

Destination: <success state in one or two lines>

Context:
- Environment: <repository and branch | no repository | supplied artifacts>
- Findings that matter for this step: <from reconnaissance>
- Upstream artifacts: <path or URL per artifact; reference, do not restate>

Constraints and exclusions:
- <confirmed constraint>
- <confirmed exclusion>

Human collaboration:
- Human decides: <domains>
- You may decide: <domains>; record each assumption and its consequence
- Explain before deciding: <areas, or none>
- Checkpoints: <gates, or none>

Output: <artifact>, for <recipient>.

Done when: <observable condition>.

Boundary: Plan; do not implement. <Or, for the implementation step: Implement within the constraints above; verify by <expectation> before reporting done.>

Stop and report if:
- <escalation trigger>
```

## Step rules

**Single-step recipe.** The one packet is pasteable directly after the human invokes the named skill; nothing else has to be written.

**Multi-step recipe.** The whole recipe may be handed to an orchestration agent. Each skill receives only its own packet plus the upstream artifacts that packet references. A user-invoked skill (one carrying `disable-model-invocation: true`) can be started only by the human or by the harness's user turn, so a packet never asks an earlier skill to invoke a later user-invoked one.

**G0 recipe.** The recipe stays executable without a planning skill:

- `Topology: G0 Direct`;
- `Skill: No planning skill`, on a step whose `Capability` is `implementation` and which carries that capability's model profile;
- one implementation launch packet;
- the verification expectation; and
- the escalation triggers.

No spec or handoff step is inserted for ceremony, and the **Implementation handoff** section carries no boundary fields, since the step already does.

**Model profiles.** Every execution boundary carries `Capability`, `Model`, `Reasoning effort`, and `Runtime availability`. The boundaries are a tracker-setup step when present, every planning step, and the G0 implementation step. In G1 to G3 they also include the **Implementation handoff**, whose capability is `implementation` and whose one profile G3 implementation sessions share. Dependencies and installation actions carry no profile. Each boundary resolves exactly one profile from [model-registry.md](model-registry.md), by its capability, plus `High-assurance` when the verdict carries it, and independently of the skill outcome. `No registry match` and `No planning skill` never remove a profile, and a model registry gap never changes a skill binding. Never list an ordered fallback, a second model, or a second reasoning effort, and never write an alias for the pinned ID.

**No model registry match.** With no binding, `Model` reads `No model registry match: <capability>` or `No model registry match: <capability> + High-assurance`, and `Reasoning effort` and `Runtime availability` read `n/a`. The base binding, the closest profile, and a lower reasoning effort are not substituted.

**Runtime availability.** Beside a resolved profile, write `unavailable: <evidence>` only when local, read-only evidence proves the exact pair cannot be selected, and otherwise `unknown`. The model registry defines what counts as evidence. `available` is never written. An `unavailable` profile is still recommended exactly as bound.

**Recommendations are advice.** A launch packet may repeat its boundary's model recommendation, but neither the recipe nor a packet claims that a model or reasoning effort was applied, enforced, or selected. Gauge configures no session.

**No registry match.** The step keeps every field. `Skill` reads `No registry match: <missing capability>`; `Availability` is `n/a`; `Invocation` states that the MVP catalog cannot fully resolve the recipe; the packet is written for the capability so it is ready when a skill is supplied. The closest registry entry is not substituted.

**Recipe text is a recommendation, never permission.** The result contains no instruction that could be read as authorising implementation, installation, tracker writes, or skill invocation. The final line may say that the recipe or any single packet can be pasted into the next agent.

## Confidence

Confidence describes the routing decision. It says nothing about whether the implementation will succeed.

- **High:** the intent, continuity, knowledge location, and collaboration posture are clear enough that missing details are unlikely to change the topology.
- **Medium:** assumptions remain, and the selected topology is likely stable.
- **Low:** an unanswered question could reasonably change the topology or decision ownership.

At Low, when one small routing question would resolve it, ask before emitting the final recipe. When the human cannot or does not want to answer, emit the primary recipe with a conditional fork (the alternative topology and the observation that would select it) and name the uncertainty under **Assumptions and unknowns**. Missing repository access lowers confidence and is recorded as an assumption; it never produces an invented repository fact.
