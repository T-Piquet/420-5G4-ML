
FROM mcr.microsoft.com/devcontainers/cpp:3-debian13

ARG REINSTALL_CMAKE_VERSION=3.22.2

# Install C++ and Python development dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gdb \
    ninja-build \
    git \
    curl \
    wget \
    pkg-config \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-tk \
    python3-pyqt5 \
    x11-apps \
    x11-utils \
    x11-xserver-utils \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libgl1 \
    libglib2.0-0 \
    libegl1 \
    libsm6 \
    libice6 \
    libxcb-xinerama0 \
    mesa-utils \
    && rm -rf /var/lib/apt/lists/*

# Install selected CMake version
COPY reinstall-cmake.sh /tmp/reinstall-cmake.sh

RUN chmod +x /tmp/reinstall-cmake.sh \
    && /tmp/reinstall-cmake.sh ${REINSTALL_CMAKE_VERSION} \
    && rm -f /tmp/reinstall-cmake.sh

# Install OpenCV and Python scientific dependencies
RUN python3 -m venv /opt/venv --system-site-packages

ENV PATH="/opt/venv/bin:${PATH}"

RUN pip install --no-cache-dir \
    numpy \
    matplotlib \
    opencv-python \
    pandas \
    scipy \
    scikit-learn \
    jupyter \
    pyqt5

# Ensure GUI environment is available
ENV QT_X11_NO_MITSHM=1

WORKDIR /workspaces

USER vscode
