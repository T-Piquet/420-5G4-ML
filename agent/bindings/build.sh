#!/usr/bin/env bash
# Compile le module Python bibliotheque_core avec le Python du venv de l'UI.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$ROOT/UI/.venv/bin/python"

if [ ! -x "$PYTHON" ]; then
    echo "Python du venv introuvable : $PYTHON" >&2
    echo "Créez-le avec : cd UI && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt" >&2
    exit 1
fi

if ! "$PYTHON" -c "import pybind11" >/dev/null 2>&1; then
    echo "pybind11 est absent du venv." >&2
    echo "Installez-le avec : $PYTHON -m pip install -r $ROOT/UI/requirements-dev.txt" >&2
    exit 1
fi

PYBIND11_DIR="${PYBIND11_DIR:-$("$PYTHON" -m pybind11 --cmakedir)}"
BUILD_DIR="$ROOT/build-pybind11"

cmake -S "$ROOT" -B "$BUILD_DIR" \
    -DBUILD_PYTHON_BINDINGS=ON \
    -DPython_EXECUTABLE="$PYTHON" \
    -Dpybind11_DIR="$PYBIND11_DIR"

cmake --build "$BUILD_DIR" --target bibliotheque_core -j "$(nproc)"

echo "Module compilé : $ROOT/UI/app/bibliotheque_core*.so"
