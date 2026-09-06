"""Where things are, resolved once from this file's own location.

Every other module asks here rather than recomputing `parents[n]`, so moving
the harness is a one-line change instead of a grep.
"""

from __future__ import annotations

from pathlib import Path

# .../evals/inspect-ai/skill_evals/shared/paths.py -> repo root
REPO_ROOT = Path(__file__).resolve().parents[4]

INSPECT_ROOT = REPO_ROOT / "evals" / "inspect-ai"
LOG_DIR = INSPECT_ROOT / "logs"
COMPOSE_FILE = INSPECT_ROOT / "compose.yaml"

#: The production Gauge skill. In this standalone repo the skill lives at the
#: repository root (SKILL.md is top-level), not under a nested skills/ tree.
GAUGE_SKILL = REPO_ROOT
