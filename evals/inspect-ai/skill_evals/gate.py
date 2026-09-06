"""Apply `gates.json` to an eval log. Exits non-zero when a gate fails.

    python -m skill_evals.gate [path/to/run.eval]

With no argument the most recent log in the log directory is used.

Exit codes, following the same convention as `evals/harness/check.mjs`:

    0  every gate passed
    1  a gate with a threshold was breached
    2  the log or the gate file is unusable
    3  a gate has no threshold yet — a baseline is owed

An unset threshold never reports success: a gate file whose thresholds are all
`null` would otherwise wave through a suite that scored nothing, which is the
failure mode this repository's harness README exists to prevent. It exits **3**
rather than 1 so CI can tell "nobody has recorded a baseline yet" apart from
"the suite regressed", and treat only the second as a build failure.
`catastrophic_failures` is exempt because zero needs no baseline.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from inspect_ai.log import EvalLog, list_eval_logs, read_eval_log

from skill_evals.shared.paths import INSPECT_ROOT, LOG_DIR

GATES_FILE = INSPECT_ROOT / "gates.json"


def latest_log() -> str:
    """The newest log, as the URI Inspect hands back.

    Returned as a string rather than a Path: `list_eval_logs` yields
    `file:/...` URIs, and pushing one through Path mangles it into a relative
    path that does not exist.
    """
    logs = list_eval_logs(str(LOG_DIR))
    if not logs:
        raise SystemExit(f"no eval logs under {LOG_DIR}")
    return sorted(log.name for log in logs)[-1]


def metric_value(log: EvalLog, spec: str) -> float | None:
    """Read `<scorer>/<metric>` out of a log's results."""
    scorer_name, _, metric_name = spec.partition("/")
    if not log.results:
        return None
    for score in log.results.scores:
        if score.name != scorer_name:
            continue
        metric = score.metrics.get(metric_name)
        if metric is not None:
            return float(metric.value)
    return None


BREACHED = 1
UNUSABLE = 2
BASELINE_OWED = 3


def evaluate(log: EvalLog, gates: dict[str, Any]) -> tuple[int, list[str]]:
    """Grade the log against the gates. Returns the worst exit code and a report."""
    lines: list[str] = []
    worst = 0

    for name, gate in gates.items():
        if name.startswith("_"):
            continue
        actual = metric_value(log, gate["metric"])
        if actual is None:
            worst = max(worst, UNUSABLE)
            lines.append(f"✗ {name}: metric {gate['metric']!r} is absent from the log")
            continue

        floor, ceiling = gate.get("min"), gate.get("max")
        if floor is None and ceiling is None:
            worst = max(worst, BASELINE_OWED)
            lines.append(
                f"? {name}: measured {actual:.3f}, but no threshold is set. "
                f"Record this as the baseline and set it in {GATES_FILE.name} — "
                "an unset gate passes everything, so it is not treated as a pass."
            )
        elif floor is not None and actual < floor:
            worst = max(worst, BREACHED)
            lines.append(f"✗ {name}: {actual:.3f} < required {floor}")
        elif ceiling is not None and actual > ceiling:
            worst = max(worst, BREACHED)
            lines.append(f"✗ {name}: {actual:.3f} > allowed {ceiling}")
        else:
            bound = f">= {floor}" if floor is not None else f"<= {ceiling}"
            lines.append(f"✓ {name}: {actual:.3f} ({bound})")

    return worst, lines


def main(argv: list[str]) -> int:
    location = argv[0] if argv else latest_log()
    log = read_eval_log(location)
    gates = json.loads(GATES_FILE.read_text(encoding="utf-8"))

    code, lines = evaluate(log, gates)
    print(f"quality gates — {Path(location).name}")
    for line in lines:
        print(f"  {line}")
    if code == BASELINE_OWED:
        print("\n  No gate was breached, but a baseline is still owed. Exit 3.")
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
