FROM mcr.microsoft.com/devcontainers/cpp:3-debian13

ARG REINSTALL_CMAKE_VERSION_FROM_SOURCE="3.22.2"

# Optionally install the cmake for vcpkg
COPY ./reinstall-cmake.sh /tmp/

RUN if [ "${REINSTALL_CMAKE_VERSION_FROM_SOURCE}" != "none" ]; then \
        chmod +x /tmp/reinstall-cmake.sh && /tmp/reinstall-cmake.sh ${REINSTALL_CMAKE_VERSION_FROM_SOURCE}; \
    fi \
    && rm -f /tmp/reinstall-cmake.sh

# [Optional] Uncomment this section to install additional vcpkg ports.
# RUN su vscode -c "${VCPKG_ROOT}/vcpkg install <your-port-name-here>"

# [Optional] Uncomment this section to install additional packages.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends python3-pybind11 pybind11-dev python3-tk python3-venv \
    zstd \
    fonts-noto-color-emoji fonts-noto-core fonts-dejavu-core fonts-noto-extra

# ajouter installation ollama et opencode
# Installation des outils supplémentaires
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Environnement Python et CustomTkinter
RUN python3 -m venv --system-site-packages /opt/bibliotheque-venv \
    && /opt/bibliotheque-venv/bin/python -m pip install --no-cache-dir customtkinter

ENV PATH="/opt/bibliotheque-venv/bin:${PATH}"

# Installation d'Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Installation d'OpenCode
USER vscode

RUN curl -fsSL https://opencode.ai/install | bash

ENV PATH="/home/vscode/.opencode/bin:${PATH}"
