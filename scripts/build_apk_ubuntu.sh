#!/usr/bin/env bash
# ==============================================================================
# Potaria: Automated One-Click Android APK Build Pipeline for Ubuntu Linux
# ==============================================================================
set -euo pipefail

echo "=================================================================="
echo "  POTARIA: Ubuntu One-Click Android APK Build Pipeline"
echo "=================================================================="

# Check for root execution
if [ "$(id -u)" -eq 0 ]; then
    echo "WARNING: Running Buildozer as root is not recommended."
    echo "It is recommended to run this script as a normal user with sudo privileges."
fi

# Step 1: Install system packages
echo ""
echo "[Step 1/6] Updating APT repositories and installing build packages..."
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    zip \
    unzip \
    tar \
    build-essential \
    ccache \
    pkg-config \
    cmake \
    autoconf \
    automake \
    libtool \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-setuptools \
    openjdk-17-jdk \
    libffi-dev \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libsqlite3-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libreadline-dev \
    liblzma-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev

# Step 2: Configure Java environment
echo ""
echo "[Step 2/6] Configuring Java OpenJDK 17 environment..."
JAVA_BIN=$(readlink -f /usr/bin/javac 2>/dev/null || which javac)
if [ -n "$JAVA_BIN" ]; then
    export JAVA_HOME=$(dirname "$(dirname "$JAVA_BIN")")
else
    export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
fi
export PATH="$JAVA_HOME/bin:$PATH"
echo "Configured JAVA_HOME: $JAVA_HOME"

# Step 3: Configure Python virtual environment for Buildozer
echo ""
echo "[Step 3/6] Setting up Python virtual environment and Buildozer..."
VENV_DIR="$HOME/.potaria_build_venv"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

pip install --upgrade pip setuptools wheel
pip install --upgrade "Cython<3.0" buildozer virtualenv

export PATH="$HOME/.local/bin:$VENV_DIR/bin:$PATH"

# Step 4: Verify repository directory
echo ""
echo "[Step 4/6] Verifying Potaria repository root and buildozer.spec..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

if [ ! -f "buildozer.spec" ]; then
    echo "ERROR: buildozer.spec not found in $PROJECT_ROOT"
    exit 1
fi
echo "Verified workspace root: $PROJECT_ROOT"

# Step 5: Execute Buildozer build
echo ""
echo "[Step 5/6] Compiling Android APK (downloading Android SDK/NDK and packaging)..."
echo "Note: The initial run downloads the Android SDK and NDK and may take several minutes."
yes | buildozer -v android debug

# Step 6: Verify and report generated APK
echo ""
echo "[Step 6/6] Verifying compiled APK..."
APK_FILE=$(find bin -maxdepth 1 -name "*.apk" -type f 2>/dev/null | head -n 1)

if [ -n "$APK_FILE" ] && [ -f "$APK_FILE" ]; then
    APK_SIZE=$(du -h "$APK_FILE" | cut -f1)
    echo "=================================================================="
    echo "  SUCCESS: Potaria Android APK built successfully!"
    echo "  Package: $PROJECT_ROOT/$APK_FILE"
    echo "  Size:    $APK_SIZE"
    echo "=================================================================="
    echo "To install on your Android 12 device via ADB (with USB debugging):"
    echo "  adb install -r \"$PROJECT_ROOT/$APK_FILE\""
else
    echo "ERROR: Build process finished but no APK file was found in bin/."
    exit 1
fi
