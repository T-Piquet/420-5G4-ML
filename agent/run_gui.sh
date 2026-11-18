#!/usr/bin/env bash
# Build the pybind11 module if needed, then open the Tkinter interface.
#
#   ./agent/run_gui.sh                       # uses agent/data
#   ./agent/run_gui.sh -d /path/to/data      # another folder
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ -z "${DISPLAY:-}" ]]; then
  echo "DISPLAY n'est pas défini : cette application ouvre une fenêtre Tkinter." >&2
  echo "Dans le dev container, le socket X11 et DISPLAY sont fournis par .devcontainer." >&2
  exit 1
fi

cmake -S agent -B agent/build -G Ninja >/dev/null
cmake --build agent/build >/dev/null

has_data_dir=0
for arg in "$@"; do
  if [[ "$arg" == "-d" || "$arg" == "--data-dir" ]]; then
    has_data_dir=1
  fi
done
if [[ "$has_data_dir" -eq 0 ]]; then
  set -- -d agent/data "$@"
fi

exec python3 agent/python/gui.py "$@"
