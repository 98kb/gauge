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
    PROHIBITED_AS_STEP,
    REGISTRY_SKILLS,
    REQUIRED_DEPENDENCIES,
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
class Step:
    heading: str
    fields: dict[str, str] = field(default_factory=dict)
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

    if recipe.topologies == ["G0"] and recipe.steps:
        checks.append(_check_g0_binds_no_planning_skill(recipe))

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
    starts = [
        i
        for i, line in enumerate(lines)
        if line.startswith("###") and not line.startswith("####")
    ]
    steps: list[Step] = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
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
        if sep and key in STEP_FIELDS and key not in fields:
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
