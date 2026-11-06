FROM mcr.microsoft.com/devcontainers/cpp:3-debian13

ARG REINSTALL_CMAKE_VERSION_FROM_SOURCE="none"

# Optionally install the cmake for vcpkg
COPY ./reinstall-cmake.sh /tmp/

RUN if [ "${REINSTALL_CMAKE_VERSION_FROM_SOURCE}" != "none" ]; then \
        chmod +x /tmp/reinstall-cmake.sh && /tmp/reinstall-cmake.sh ${REINSTALL_CMAKE_VERSION_FROM_SOURCE}; \
    fi \
    && rm -f /tmp/reinstall-cmake.sh

# Dépendances système, Python 3, Pybind11, Tkinter et polices
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        curl \
        ca-certificates \
        git \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
        python3-tk \
        python3-pybind11 \
        pybind11-dev \
        zstd \
        fonts-noto-color-emoji \
        fonts-noto-core \
        fonts-dejavu-core \
        fonts-noto-extra \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Dépendances Python pour l'interface graphique GUI (customtkinter)
RUN pip3 install --no-cache-dir --break-system-packages customtkinter packaging

# Installation de OpenCode CLI
RUN curl -fsSL https://opencode.ai/v2/install | bash \
    && if [ -d /root/.opencode/bin ]; then \
           cp -f /root/.opencode/bin/opencode /usr/local/bin/opencode 2>/dev/null || true; \
       fi \
    && chmod 755 /usr/local/bin/opencode 2>/dev/null || true
