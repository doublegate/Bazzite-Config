#!/usr/bin/env bash
set -euo pipefail

# Lints only Python files changed between two refs.
# Intended for CI usage, but safe to run locally.
#
# Environment variables:
#   BASE_REF   Base ref or commit (default: origin/main)
#   HEAD_REF   Head ref or commit (default: HEAD)
#   CI_ALL     If set to 1, runs flake8 on entire repo instead of diff
#
# Examples:
#   BASE_REF=origin/main HEAD_REF=HEAD ./tools/lint_changed.sh
#   CI_ALL=1 ./tools/lint_changed.sh

BASE_REF=${BASE_REF:-origin/main}
HEAD_REF=${HEAD_REF:-HEAD}

if [[ "${CI_ALL:-0}" == "1" ]]; then
  echo "[lint_changed] CI_ALL=1 → running flake8 on entire repo"
  exec flake8
fi

if ! command -v git >/dev/null 2>&1; then
  echo "[lint_changed] git not available; skipping changed-files lint"
  exit 0
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "[lint_changed] not a git repository; skipping changed-files lint"
  exit 0
fi

echo "[lint_changed] Diffing: ${BASE_REF}...${HEAD_REF}"
mapfile -t CHANGED < <(git diff --name-only "${BASE_REF}...${HEAD_REF}" -- '*.py' || true)

FILTERED=()
for f in "${CHANGED[@]:-}"; do
  # Exclude common ephemeral or vendored paths
  if [[ "$f" == .venv/* || "$f" == venv/* || "$f" == dist/* || "$f" == build/* || "$f" == .eggs/* ]]; then
    continue
  fi
  FILTERED+=("$f")
done

if [[ ${#FILTERED[@]} -eq 0 ]]; then
  echo "[lint_changed] No changed Python files detected; nothing to lint"
  exit 0
fi

printf "[lint_changed] Linting %d changed file(s):\n" "${#FILTERED[@]}"
printf ' - %s\n' "${FILTERED[@]}"

exec flake8 "${FILTERED[@]}"

