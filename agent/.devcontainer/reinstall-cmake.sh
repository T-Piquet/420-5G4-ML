
#!/usr/bin/env bash

#-------------------------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See https://go.microsoft.com/fwlink/?linkid=2090316 for license information.
#-------------------------------------------------------------------------------------------------------------
#

set -euo pipefail


VERSION="${1:-3.22.2}"

if [[ "$VERSION" == "none" ]]; then
    echo "Skipping CMake installation."
    exit 0
fi

echo "Installing CMake ${VERSION}..."

ARCH="$(dpkg --print-architecture)"

case "$ARCH" in
    amd64)
        CMAKE_ARCH="x86_64"
        ;;
    arm64)
        CMAKE_ARCH="aarch64"
        ;;
    *)
        echo "Unsupported architecture: ${ARCH}"
        exit 1
        ;;
esac

URL="https://github.com/Kitware/CMake/releases/download/v${VERSION}/cmake-${VERSION}-linux-${CMAKE_ARCH}.tar.gz"

TEMP_DIR="$(mktemp -d)"

trap 'rm -rf "$TEMP_DIR"' EXIT

curl -fL --retry 3 "$URL" \
    -o "$TEMP_DIR/cmake.tar.gz"

tar -xzf "$TEMP_DIR/cmake.tar.gz" \
    -C "$TEMP_DIR"

INSTALL_DIR="/opt/cmake-${VERSION}"

rm -rf "$INSTALL_DIR"

mv "$TEMP_DIR/cmake-${VERSION}-linux-${CMAKE_ARCH}" \
    "$INSTALL_DIR"

ln -sf "$INSTALL_DIR/bin/cmake" /usr/local/bin/cmake
ln -sf "$INSTALL_DIR/bin/ctest" /usr/local/bin/ctest
ln -sf "$INSTALL_DIR/bin/cpack" /usr/local/bin/cpack

echo "CMake installation completed."

cmake --version
