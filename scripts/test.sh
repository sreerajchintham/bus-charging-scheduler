#!/usr/bin/env bash
# Run tests without loading broken third-party pytest plugins (e.g. Conda langsmith).
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

if [[ -x .venv/bin/python ]]; then
  exec .venv/bin/python -m pytest "$@"
fi
exec python -m pytest "$@"
