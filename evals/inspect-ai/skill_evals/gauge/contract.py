"""Gauge's deterministic contract, as pure functions over the emitted recipe.

`skills/engineering/gauge/references/evaluation-scenarios.md` splits Gauge's
standing invariants into **D** (checkable mechanically from the result text)
and **J** (needs a reader's judgement), following ADR 0003. Everything in this
module is a D invariant. The J invariants are graded by the semantic scorer,
and the two are never blended into one number.

Everything here operates on text plus a small `Evidence` record, so a committed
`.eval` log can be re-scored without re-running a single agent trajectory.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from skill_evals.gauge.registry import (
    MODEL_REGISTRY,
    PROHIBITED_AS_STEP,
    REGISTRY_SKILLS,
    REQUIRED_DEPENDENCIES,
    SKILL_CAPABILITIES,
)

TOPOLOGY_CODES = ("G0", "G1", "G2", "G3")
AVAILABILITY_LABELS = ("installed", "not detected", "unknown", "n/a")

_EMPHASIS = re.compile(r"[*_`]+")
#: Both CommonMark fence characters. Recognising only backticks would false-fail
#: a correct recipe for its punctuation, which is the cry-wolf half of the bar.
_FENCE = re.compile(r"^\s*(```|~~~)")

#: Wording an estimate hides behind. The skill forbids "any numerical
#: complexity score, T-shirt size, story-point, time, or cost estimate".
_ESTIMATE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("story points", re.compile(r"\b\d+(\.\d+)?\s*story[- ]points?\b", re.I)),
    ("person-days", re.compile(r"\b\d+(\.\d+)?\s*(person|man)[- ](days?|hours?|weeks?|months?)\b", re.I)),
    ("t-shirt size", re.compile(r"\b(t-shirt\s+size|size:\s*(xs|s|m|l|xl|xxl))\b", re.I)),
    # `~` is not a word character, so it cannot sit behind a `\b`; spelling the
    # alternation this way is what makes "~3 days" match alongside "about 3 days".
    (
        "duration estimate",
        re.compile(
            r"(?:\babout\b|\bapprox\.?|\bapproximately\b|\broughly\b|~|\best\.?|\bestimated(?:\s+at)?\b)"
            r"\s*\d+(\.\d+)?\s*(minutes?|hours?|days?|weeks?|months?|sprints?)\b",
            re.I,
        ),
    ),
    ("duration estimate", re.compile(r"\b\d+(\.\d+)?\s*(hours?|days?|weeks?|months?|sprints?)\s+(of\s+)?(work|effort|implementation)\b", re.I)),
    # A currency amount, not a shell positional. `$1` in a launch packet's
    # `bash script.sh $1` is not a cost estimate, and launch packets are
    # mandatory fenced shell, so the naive `[$£€]\s?\d` failed real recipes.
    # Requires two digits, a separator, or a scale word — no plausible cost
    # estimate is a bare single digit.
    (
        "cost estimate",
        re.compile(
            r"(?<![\w$])[$£€]\s?(?:\d{2,}|\d{1,3}(?:[,.]\d{3})+|\d+(?:\.\d{2}))\b"
            r"|(?<![\w$])[$£€]\s?\d+\s*(?:k|m|bn|thousand|million|billion)\b",
            re.I,
        ),
    ),
    ("complexity score", re.compile(r"\b(complexity|effort|difficulty)\s*(score|rating)?\s*[:=]\s*\d", re.I)),
    ("effort estimate", re.compile(r"\bestimated\s+effort\b", re.I)),
)

#: Fields the recipe contract requires on every step.
STEP_FIELDS = (
    "skill",
    "dependencies",
    "availability",
    "invocation",
    "inputs",
    "expected output",
    "exit condition",
    "next handoff",
)

#: Fields ADR 0017 requires on every execution boundary: each step, plus the
#: non-G0 Implementation handoff.
MODEL_FIELDS = ("capability", "model", "reasoning effort", "runtime availability")

_MODEL_ID = re.compile(r"\bclaude-[a-z0-9][a-z0-9.-]*[a-z0-9]\b", re.I)
_RUNTIME_LABEL = re.compile(r"^(unavailable|unknown|available|n/a)\b", re.I)
#: Every effort value any registry model supports, read from the registry.
_EFFORT_VALUES: frozenset[str] = frozenset().union(
    *(profile.supported for profile in MODEL_REGISTRY.profiles.values())
)


@dataclass(frozen=True)
class Check:
    """One deterministic verdict, with the detail a reader needs to act on it."""

    id: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class Evidence:
    """What the trajectory established, independent of the recipe's own claims.

    `inventory` is the set of skill names an inventory read actually exposed;
    `None` means no inventory was readable, which is the registry's `unknown`.
    """

    inventory: frozenset[str] | None = None

    #: The human's request, verbatim. The recipe contract *requires* Gauge to
    #: quote the intent back inside every launch packet, so an estimate the
    #: human themselves used would otherwise fail Gauge for the human's wording.
    #: Repeating someone's words is not emitting an estimate.
    human_request: str = ""


@dataclass
class Boundary:
    """An execution boundary: a point in a recipe where an agent session starts
    (CONTEXT.md). Every step is one, and so is the non-G0 Implementation
    handoff, which is not a step. Each carries one model profile."""

    heading: str
    fields: dict[str, str] = field(default_factory=dict)

    def _model_field(self, name: str) -> str:
        return _plain(self.fields.get(name, "")).strip().rstrip(".")

    @property
    def stated_model(self) -> str:
        return self._model_field("model")

    @property
    def capability(self) -> str | None:
        return self._model_field("capability").lower() or None

    @property
    def model_gap_key(self) -> str | None:
        """The binding key a `No model registry match` names; "" when it names
        none; None when the boundary is not a model registry gap."""
        raw = self.stated_model
        if not raw.lower().startswith("no model registry match"):
            return None
        _, _, key = raw.partition(":")
        return " ".join(key.split())

    @property
    def model(self) -> str | None:
        """The recommended model ID, or None on a gap or a missing field."""
        raw = self.stated_model
        if not raw or self.model_gap_key is not None:
            return None
        found = _MODEL_ID.search(raw)
        return found.group(0).lower() if found else raw.split()[0].lower()

    @property
    def model_ids(self) -> frozenset[str]:
        """Every model ID the Model field names; more than one is a fallback list."""
        return frozenset(m.lower() for m in _MODEL_ID.findall(self.stated_model))

    @property
    def effort(self) -> str | None:
        """The first reasoning-effort value, as stated."""
        raw = self._model_field("reasoning effort").lower()
        return raw.split()[0].strip(".,;:()") if raw else None

    @property
    def effort_values(self) -> frozenset[str]:
        """Every registry reasoning-effort value the field names."""
        words = re.findall(r"[a-z]+", self._model_field("reasoning effort").lower())
        return frozenset(words) & _EFFORT_VALUES

    @property
    def runtime(self) -> str | None:
        """The runtime-availability label, apart from any evidence after it."""
        raw = self._model_field("runtime availability").lower()
        if not raw:
            return None
        label = _RUNTIME_LABEL.match(raw)
        return label.group(1) if label else raw

    @property
    def runtime_evidence(self) -> str | None:
        raw = self._model_field("runtime availability")
        label = _RUNTIME_LABEL.match(raw)
        if not label:
            return None
        evidence = raw[label.end() :].strip().strip(":—–-()").strip()
        return evidence or None


@dataclass
class Step(Boundary):
    launch_packet: str | None = None

    @property
    def skill(self) -> str | None:
        """The canonical skill this step binds, or None for a non-binding outcome."""
        raw = self.fields.get("skill", "")
        cleaned = _plain(raw).strip()
        low = cleaned.lower()
        if not cleaned or low.startswith("no planning skill") or low.startswith("no registry match"):
            return None
        return cleaned.split()[0].strip(".,;:") if cleaned else None

    @property
    def binds_no_planning_skill(self) -> bool:
        return _plain(self.fields.get("skill", "")).strip().lower().startswith("no planning skill")

    @property
    def is_no_registry_match(self) -> bool:
        return _plain(self.fields.get("skill", "")).strip().lower().startswith("no registry match")

    @property
    def availability(self) -> str | None:
        raw = _plain(self.fields.get("availability", "")).strip().rstrip(".").lower()
        return raw or None

    @property
    def dependencies(self) -> frozenset[str]:
        raw = _plain(self.fields.get("dependencies", "")).strip().lower()
        if not raw or raw.startswith("none"):
            return frozenset()
        return frozenset(
            part.strip().strip(".,;:")
            for part in re.split(r"[,;]| and ", raw)
            if part.strip()
        )


@dataclass
class Recipe:
    text: str
    topologies: list[str] = field(default_factory=list)
    variant: str | None = None
    modifiers: list[str] = field(default_factory=list)
    confidence: str | None = None
    steps: list[Step] = field(default_factory=list)
    #: The non-G0 Implementation handoff, when it carries boundary fields. A
    #: G0 recipe carries its profile on its only step instead.
    handoff: Boundary | None = None

    @property
    def boundaries(self) -> list[Boundary]:
        """Every execution boundary that carries a model profile."""
        return [*self.steps, *([self.handoff] if self.handoff is not None else [])]

    @property
    def high_assurance(self) -> bool:
        """Whether the verdict attaches High-assurance, which ADR 0017 makes the
        only modifier that changes a model binding. Matched as the modifier's
        name, so a scope note after it still counts."""
        return any(
            modifier.strip().lower().startswith("high-assurance") for modifier in self.modifiers
        )


def parse_recipe(text: str) -> Recipe:
    """Parse an emitted Gauge result into the decisions the contract grades.

    Wording may vary — `evaluation-scenarios.md` is explicit that two results
    with different prose and the same decisions both pass — so parsing keys off
    the contract's field labels rather than its exact headings.
    """
    recipe = Recipe(text=text)

    recipe.topologies = _topology_codes(text)
    recipe.variant = _first_field(text, "variant")
    recipe.confidence = _first_field(text, "confidence")

    modifiers = _first_field(text, "modifiers") or ""
    if modifiers and not modifiers.strip().lower().startswith("none"):
        recipe.modifiers = [
            m.strip().strip(".") for m in re.split(r"[,;]| and ", modifiers) if m.strip()
        ]

    recipe.steps = _parse_steps(text)
    recipe.handoff = _parse_handoff(text)
    return recipe


def check_recipe(recipe: Recipe, evidence: Evidence) -> list[Check]:
    """Every D invariant that applies to this recipe.

    A check is *registered* only when the recipe gives it something to grade —
    a check that could not fail is noise in a report rather than reassurance.
    """
    checks: list[Check] = [
        _check_no_estimates(recipe, evidence),
        _check_single_topology(recipe),
    ]

    if recipe.steps:
        checks.append(_check_step_fields(recipe))
        checks.append(_check_launch_packet(recipe))
        checks.append(_check_availability_vocabulary(recipe))
        checks.append(_check_ask_matt_not_bound(recipe))
        checks.append(_check_no_registry_match_names_capability(recipe))

    bound = [step for step in recipe.steps if step.skill]
    if bound:
        checks.append(_check_registry_membership(bound))
        checks.append(_check_dependency_expansion(bound))
        checks.append(_check_availability_evidence(bound, evidence))
        checks.append(_check_capability_matches_skill(bound))

    if recipe.topologies == ["G0"] and recipe.steps:
        checks.append(_check_g0_binds_no_planning_skill(recipe))

    # --- model profiles (ADR 0017) ---
    if len(recipe.topologies) == 1 and recipe.topologies[0] in TOPOLOGY_CODES and recipe.steps:
        checks.append(_check_implementation_profile(recipe))

    if recipe.boundaries:
        checks.append(_check_model_fields(recipe))
        checks.append(_check_single_profile(recipe))
        checks.append(_check_model_profile_registered(recipe))
        checks.append(_check_model_binding(recipe))
        checks.append(_check_runtime_availability(recipe))
        checks.append(_check_runtime_evidence(recipe))

    return checks


# --- individual checks --------------------------------------------------------


def _check_no_estimates(recipe: Recipe, evidence: Evidence) -> Check:
    quoted = evidence.human_request.lower()
    hits = [
        f"{label}: {match.group(0)!r}"
        for label, pattern in _ESTIMATE_PATTERNS
        for match in pattern.finditer(recipe.text)
        if match.group(0).lower() not in quoted
    ]
    return Check(
        "contract/no-estimates",
        not hits,
        "no size, score, duration or cost estimate" if not hits else "; ".join(hits),
    )


def _check_single_topology(recipe: Recipe) -> Check:
    found = recipe.topologies
    if len(found) == 1 and found[0] in TOPOLOGY_CODES:
        return Check("contract/single-topology", True, f"topology {found[0]}")
    if len(found) == 1:
        return Check(
            "contract/single-topology",
            False,
            f"topology reads {found[0]!r}, which is not one of {', '.join(TOPOLOGY_CODES)}",
        )
    if not found:
        stated = _first_field(recipe.text, "topology")
        return Check(
            "contract/single-topology",
            False,
            f"no line names one of {', '.join(TOPOLOGY_CODES)}"
            + (f" (topology field reads {stated!r})" if stated else ""),
        )
    return Check(
        "contract/single-topology", False, f"{len(found)} topologies named: {found}"
    )


def _check_step_fields(recipe: Recipe) -> Check:
    missing = [
        f"{step.heading}: missing {name}"
        for step in recipe.steps
        for name in STEP_FIELDS
        if name not in step.fields
    ]
    return Check(
        "contract/step-fields",
        not missing,
        "every step carries all eight fields" if not missing else "; ".join(missing),
    )


def _check_launch_packet(recipe: Recipe) -> Check:
    missing = [step.heading for step in recipe.steps if not step.launch_packet]
    return Check(
        "contract/launch-packet",
        not missing,
        "every step carries a fenced launch packet"
        if not missing
        else f"no fenced packet under: {', '.join(missing)}",
    )


def _check_availability_vocabulary(recipe: Recipe) -> Check:
    bad = [
        f"{step.heading}: {step.availability!r}"
        for step in recipe.steps
        if step.availability not in AVAILABILITY_LABELS
    ]
    return Check(
        "contract/availability-vocabulary",
        not bad,
        f"every label is one of {AVAILABILITY_LABELS}"
        if not bad
        else "; ".join(bad) + f" — allowed: {AVAILABILITY_LABELS}",
    )


def _check_ask_matt_not_bound(recipe: Recipe) -> Check:
    bound = sorted(
        {
            step.skill
            for step in recipe.steps
            if step.skill is not None and step.skill in PROHIBITED_AS_STEP
        }
    )
    return Check(
        "contract/ask-matt-not-bound",
        not bound,
        "no prohibited skill is bound as a step"
        if not bound
        else f"registry bars these as steps: {', '.join(bound)}",
    )


def _check_registry_membership(bound: list[Step]) -> Check:
    unknown = sorted(
        {
            step.skill
            for step in bound
            if step.skill is not None and step.skill not in REGISTRY_SKILLS
        }
    )
    return Check(
        "contract/registry-membership",
        not unknown,
        "every bound skill is a registry entry"
        if not unknown
        else f"not in the registry: {', '.join(str(u) for u in unknown)}",
    )


def _check_dependency_expansion(bound: list[Step]) -> Check:
    gaps = [
        f"{step.skill} must list {', '.join(sorted(required - step.dependencies))}"
        for step in bound
        for required in [REQUIRED_DEPENDENCIES.get(step.skill or "", frozenset())]
        if required - step.dependencies
    ]
    return Check(
        "contract/dependency-expansion",
        not gaps,
        "every bound entry point expands its dependencies"
        if not gaps
        else "; ".join(gaps),
    )


def _check_availability_evidence(bound: list[Step], evidence: Evidence) -> Check:
    claimed = [step for step in bound if step.availability == "installed"]
    if not claimed:
        return Check(
            "contract/availability-evidence", True, "nothing claimed as installed"
        )
    if evidence.inventory is None:
        return Check(
            "contract/availability-evidence",
            False,
            f"{', '.join(str(s.skill) for s in claimed)} labelled installed, but the "
            "trajectory read no inventory — the registry's label for that is `unknown`",
        )
    unevidenced = sorted(
        {
            step.skill
            for step in claimed
            if step.skill is not None and step.skill not in evidence.inventory
        }
    )
    return Check(
        "contract/availability-evidence",
        not unevidenced,
        "every `installed` label has inventory evidence"
        if not unevidenced
        else f"labelled installed without inventory evidence: {', '.join(unevidenced)}",
    )


def _check_no_registry_match_names_capability(recipe: Recipe) -> Check:
    # `fields["skill"]` is already the text *after* the field's own colon, so
    # the capability is whatever follows the colon inside "No registry match:
    # <capability>". Re-splitting a value with no colon returned the whole
    # string, which made this check pass unconditionally.
    unnamed = []
    for step in recipe.steps:
        if not step.is_no_registry_match:
            continue
        _, separator, capability = _plain(step.fields["skill"]).partition(":")
        if not separator or not capability.strip():
            unnamed.append(step.heading)
    return Check(
        "contract/no-registry-match-names-capability",
        not unnamed,
        "no unnamed `No registry match`"
        if not unnamed
        else f"`No registry match` names no missing capability: {', '.join(unnamed)}",
    )


def _check_g0_binds_no_planning_skill(recipe: Recipe) -> Check:
    planning = [step.skill for step in recipe.steps if step.skill]
    return Check(
        "contract/g0-no-planning-skill",
        not planning,
        "G0 binds no planning skill"
        if not planning
        else f"G0 but the recipe binds: {', '.join(str(p) for p in planning)}",
    )


def _check_implementation_profile(recipe: Recipe) -> Check:
    """ADR 0017's one topology asymmetry: G0 carries the `implementation`
    profile on its only step; G1-G3 carry it on the Implementation handoff."""
    if recipe.topologies == ["G0"]:
        wrong = [
            f"{step.heading}: capability {step.capability!r}"
            for step in recipe.steps
            if step.capability != "implementation"
        ]
        return Check(
            "contract/implementation-profile",
            not wrong,
            "the G0 step is the `implementation` boundary"
            if not wrong
            else "G0's step must carry capability `implementation`: " + "; ".join(wrong),
        )
    handoff = recipe.handoff
    if handoff is None or handoff.capability != "implementation":
        return Check(
            "contract/implementation-profile",
            False,
            f"{recipe.topologies[0]}'s Implementation handoff carries no `implementation` "
            "boundary: it needs Capability, Model, Reasoning effort and Runtime availability",
        )
    return Check(
        "contract/implementation-profile",
        True,
        "the Implementation handoff is the `implementation` boundary",
    )


def _check_capability_matches_skill(bound: list[Step]) -> Check:
    """A bound skill's step names the capability the planning registry binds it
    to. The model binding is looked up by `Capability`, so a relabelled step
    would otherwise pass that check with another capability's profile."""
    mismatched = [
        f"{step.heading}: {step.skill} provides `{SKILL_CAPABILITIES[step.skill]}`, "
        f"but Capability reads {step.capability!r}"
        for step in bound
        if step.skill in SKILL_CAPABILITIES
        and step.capability is not None
        and step.capability != SKILL_CAPABILITIES[step.skill]
    ]
    return Check(
        "contract/capability-matches-skill",
        not mismatched,
        "every bound skill's step names the capability the registry binds it to"
        if not mismatched
        else "; ".join(mismatched),
    )


def _check_model_fields(recipe: Recipe) -> Check:
    missing = [
        f"{boundary.heading}: missing {name}"
        for boundary in recipe.boundaries
        for name in MODEL_FIELDS
        if name not in boundary.fields
    ]
    return Check(
        "contract/model-fields",
        not missing,
        "every execution boundary carries all four model fields"
        if not missing
        else "; ".join(missing),
    )


def _check_single_profile(recipe: Recipe) -> Check:
    """One model and one effort: an ordered fallback is a second of either."""
    lists: list[str] = []
    for boundary in recipe.boundaries:
        if boundary.model_gap_key is not None:
            continue
        if len(boundary.model_ids) > 1:
            lists.append(f"{boundary.heading}: models {sorted(boundary.model_ids)}")
        if len(boundary.effort_values) > 1:
            lists.append(
                f"{boundary.heading}: reasoning efforts {sorted(boundary.effort_values)}"
            )
    return Check(
        "contract/single-profile",
        not lists,
        "every boundary names one model and one reasoning effort"
        if not lists
        else "no fallback lists — " + "; ".join(lists),
    )


def _check_model_profile_registered(recipe: Recipe) -> Check:
    """A pinned ID paired with a reasoning effort that model supports, as the
    registry records it — never an alias, never an unsupported value."""
    pairs = {(p.model, p.effort) for p in MODEL_REGISTRY.profiles.values()}
    unknown = [
        f"{boundary.heading}: {boundary.model} at {boundary.effort!r}"
        for boundary in recipe.boundaries
        if boundary.model is not None and (boundary.model, boundary.effort) not in pairs
    ]
    return Check(
        "contract/model-profile-registered",
        not unknown,
        "every recommended model and reasoning effort is a model registry profile"
        if not unknown
        else "not a model registry profile: " + "; ".join(unknown),
    )


def _check_model_binding(recipe: Recipe) -> Check:
    """Each boundary recommends exactly its capability's binding.

    Catches a substituted model, a lowered reasoning effort, a High-assurance
    boundary falling back to its base binding, a gap naming the wrong key or
    carrying a reasoning effort, and a skill gap erasing a profile the
    capability does have.
    """
    high_assurance = recipe.high_assurance
    problems: list[str] = []
    for boundary in recipe.boundaries:
        capability = boundary.capability
        if capability is None or "model" not in boundary.fields:
            continue
        key = f"{capability} + High-assurance" if high_assurance else capability
        want = MODEL_REGISTRY.binding(capability, high_assurance=high_assurance)
        stated = boundary.stated_model
        if want is None:
            if boundary.model_gap_key is None or _binding_key(boundary.model_gap_key) != _binding_key(key):
                problems.append(
                    f"{boundary.heading}: `{key}` is unbound, so Model must read "
                    f"`No model registry match: {key}`; it reads {stated!r}"
                )
            elif boundary.effort != "n/a":
                problems.append(
                    f"{boundary.heading}: a model registry gap carries no reasoning "
                    f"effort, so it must read `n/a`; it reads {boundary.effort!r}"
                )
        elif (boundary.model, boundary.effort) != (want.model, want.effort):
            coupling = (
                " — a skill outcome never removes a model profile"
                if boundary.model_gap_key is not None
                and isinstance(boundary, Step)
                and (boundary.is_no_registry_match or boundary.binds_no_planning_skill)
                else ""
            )
            problems.append(
                f"{boundary.heading}: `{key}` binds {want.key} ({want.model} at "
                f"{want.effort}); the recipe says {stated!r} at {boundary.effort!r}{coupling}"
            )
    return Check(
        "contract/model-binding",
        not problems,
        "every boundary recommends its capability's model registry binding"
        if not problems
        else "; ".join(problems),
    )


def _check_runtime_availability(recipe: Recipe) -> Check:
    bad: list[str] = []
    for boundary in recipe.boundaries:
        if "runtime availability" not in boundary.fields:
            continue
        gap = boundary.model_gap_key is not None
        allowed = ("n/a",) if gap else ("unavailable", "unknown")
        if boundary.runtime not in allowed:
            bad.append(
                f"{boundary.heading}: {boundary.runtime!r}, allowed "
                + ("`n/a` on a model registry gap" if gap else "`unavailable` or `unknown`")
            )
    return Check(
        "contract/runtime-availability",
        not bad,
        "every runtime label is `unavailable`, `unknown`, or `n/a` on a gap; never `available`"
        if not bad
        else "; ".join(bad),
    )


def _check_runtime_evidence(recipe: Recipe) -> Check:
    unevidenced = [
        boundary.heading
        for boundary in recipe.boundaries
        if boundary.runtime == "unavailable" and not boundary.runtime_evidence
    ]
    return Check(
        "contract/runtime-evidence",
        not unevidenced,
        "every `unavailable` names its local evidence"
        if not unevidenced
        else f"`unavailable` without named evidence: {', '.join(unevidenced)}",
    )


def _binding_key(text: str) -> str:
    return re.sub(r"\s*\+\s*", " + ", " ".join(text.lower().split()))


# --- parsing helpers ----------------------------------------------------------


def _plain(text: str) -> str:
    return _EMPHASIS.sub("", text)


def _outside_fences(text: str) -> list[str]:
    """The lines of `text` that are not inside a fenced block.

    Launch packets restate the verdict back to the receiving skill, so a packet
    saying `Topology: G2` used to be counted as a second topology and false-fail
    `contract/single-topology`. Step fields were already parsed fence-aware;
    the verdict fields were not.
    """
    lines: list[str] = []
    inside = False
    for line in text.splitlines():
        if _FENCE.match(line):
            inside = not inside
            continue
        if not inside:
            lines.append(line)
    return lines


def _topology_codes(text: str) -> list[str]:
    """Every topology code named on a `Topology:` line, in order."""
    found: list[str] = []
    for line in _outside_fences(text):
        label, _, value = _plain(line).lstrip("-* \t").partition(":")
        if label.strip().lower() != "topology":
            continue
        codes = re.findall(r"\bG[0-9]\b", value)
        if codes:
            found.extend(codes)
        elif value.strip():
            found.append(value.strip())
    return found


def _first_field(text: str, name: str) -> str | None:
    for line in _outside_fences(text):
        label, sep, value = _plain(line).lstrip("-* \t").partition(":")
        if sep and label.strip().lower() == name:
            return value.strip()
    return None


def _parse_steps(text: str) -> list[Step]:
    """Every `###` block that binds something, with its fields and packet.

    A step is identified by carrying a `Skill:` field rather than by its
    heading text, so a differently-worded heading still grades.
    """
    lines = text.splitlines()
    steps: list[Step] = []
    for start, end in _sections(lines, level=3):
        block = lines[start:end]
        fields = _parse_fields(block)
        if "skill" not in fields:
            continue
        steps.append(
            Step(
                heading=_plain(lines[start].lstrip("# ")).strip(),
                fields=fields,
                launch_packet=_first_fenced_block(block),
            )
        )
    return steps


def _parse_handoff(text: str) -> Boundary | None:
    """The first `##` section that carries a `Capability:` field but no skill.

    Keyed off the field rather than the heading text, like steps are.
    """
    lines = text.splitlines()
    for start, end in _sections(lines, level=2):
        fields = _parse_fields(lines[start:end])
        if "capability" in fields and "skill" not in fields:
            return Boundary(heading=_plain(lines[start].lstrip("# ")).strip(), fields=fields)
    return None


def _sections(lines: list[str], *, level: int) -> list[tuple[int, int]]:
    """(start, end) of each heading at `level`, ending at the next heading of
    level 3 or above, so a step never runs on into the section after it."""
    inside = False
    headings: list[tuple[int, int]] = []
    for index, line in enumerate(lines):
        if _FENCE.match(line):
            inside = not inside
            continue
        match = re.match(r"^(#{1,3})\s", line)
        if not inside and match:
            headings.append((index, len(match.group(1))))
    return [
        (start, next((i for i, _ in headings if i > start), len(lines)))
        for start, depth in headings
        if depth == level
    ]


def _parse_fields(block: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    inside_fence = False
    for line in block:
        if _FENCE.match(line):
            inside_fence = not inside_fence
            continue
        if inside_fence or not line.lstrip().startswith(("-", "*")):
            continue
        label, sep, value = _plain(line).lstrip("-* \t").partition(":")
        key = label.strip().lower()
        if sep and (key in STEP_FIELDS or key in MODEL_FIELDS) and key not in fields:
            fields[key] = value.strip()
    return fields


def _first_fenced_block(block: list[str]) -> str | None:
    collected: list[str] | None = None
    for line in block:
        if _FENCE.match(line):
            if collected is None:
                collected = []
                continue
            return "\n".join(collected)
        if collected is not None:
            collected.append(line)
    return None
