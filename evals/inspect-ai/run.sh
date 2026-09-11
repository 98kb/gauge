#!/usr/bin/env bash
# Entry point for the Inspect AI skill evals.
#
# This repository has no root package.json — skills are vendored with `npx
# skills` and every existing eval entry point is a shell script under
# evals/harness/. So this is a shell script too, rather than a new package
# manager convention invented to hold three commands.
#
#   ./run.sh setup                     create the Python env (once)
#   ./run.sh check                     offline validation; no model, no cost
#   ./run.sh smoke   [inspect args]    3 cases
#   ./run.sh gauge   [inspect args]    the full 15-case suite
#   ./run.sh score <log> <scorer>      re-grade a recorded .eval log
#   ./run.sh gate    [log]             apply the quality gates
#   ./run.sh view                      open the Inspect log viewer
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

VENV="$HERE/.venv"
PY="$VENV/bin/python"
INSPECT="$VENV/bin/inspect"
TASK="skill_evals/gauge/task.py"

export INSPECT_LOG_DIR="${INSPECT_LOG_DIR:-$HERE/logs}"

die() { echo "error: $*" >&2; exit 2; }

ensure_env() {
  [ -x "$PY" ] || die "no environment yet — run: ./run.sh setup"
}

require_model() {
  # The model under evaluation is never hard-coded in the task. It comes from
  # --model or INSPECT_EVAL_MODEL, and its credentials from the environment.
  if [ -z "${INSPECT_EVAL_MODEL:-}" ] && [[ ! " $* " =~ " --model " ]]; then
    die "no model selected. Pass --model <provider/model>, or set INSPECT_EVAL_MODEL."
  fi
}

case "${1:-}" in
  setup)
    command -v uv >/dev/null || die "uv is not installed: https://docs.astral.sh/uv/"
    uv venv --python 3.12 "$VENV"
    VIRTUAL_ENV="$VENV" uv pip install -e "$HERE[dev]"
    echo "ready. Next: ./run.sh check"
    ;;

  check)
    # Everything that can be verified without a model or a sandbox: the skill
    # adapter against the real SKILL.md, the case-file contract, and the
    # positive/negative controls that prove the scorers can pass and can fail.
    ensure_env
    "$PY" -m mypy
    "$PY" -m pytest "${@:2}"
    ;;

  check:docker)
    ensure_env
    "$PY" -m pytest -m docker "${@:2}"
    ;;

  smoke)
    ensure_env; require_model "$@"
    "$INSPECT" eval "$TASK" -T smoke=true "${@:2}"
    ;;

  gauge|full)
    ensure_env; require_model "$@"
    "$INSPECT" eval "$TASK" "${@:2}"
    ;;

  score)
    ensure_env
    [ $# -ge 3 ] || die "usage: ./run.sh score <log.eval> <scorer-name>"
    # --action is passed explicitly so the command never blocks on a prompt in CI.
    "$INSPECT" score "$2" --scorer "skill_evals/gauge/scorers.py@$3" --action overwrite "${@:4}"
    ;;

  gate)
    ensure_env
    "$PY" -m skill_evals.gate "${@:2}"
    ;;

  view)
    ensure_env
    "$INSPECT" view --log-dir "$INSPECT_LOG_DIR" "${@:2}"
    ;;

  *)
    sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'
    exit 1
    ;;
esac
