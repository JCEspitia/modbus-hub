#!/usr/bin/env bash
set -e

# ===============================================================
# 🧱 Modbus Hub Build Script (Linux + Windows via Wine)
# Supports: --linux-only, --windows-only, --version <X.Y.Z>
# ===============================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSETS_DIR="$PROJECT_DIR/assets"
DIST_LINUX="$PROJECT_DIR/dist/linux"
DIST_WINDOWS="$PROJECT_DIR/dist/windows"
SPEC_DIR="$PROJECT_DIR/build/specs"
WINE_PYTHON_DIR="$PROJECT_DIR/.wine-python"

# Default build targets
BUILD_LINUX=true
BUILD_WINDOWS=true
VERSION="vDEV"  # Default version if none provided

# ===============================================================
# 🎛️ Parse arguments
# ===============================================================
while [[ $# -gt 0 ]]; do
    case "$1" in
        --linux-only)
            BUILD_WINDOWS=false
            shift
            ;;
        --windows-only)
            BUILD_LINUX=false
            shift
            ;;
        --version)
            VERSION="v$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: ./build_executables.sh [--linux-only | --windows-only] [--version X.Y.Z]"
            exit 0
            ;;
        *)
            echo "⚠️ Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "🚀 Building Modbus Hub executables..."
echo "=============================================================="
echo "📂 Project directory: $PROJECT_DIR"
echo "🖼️ Assets directory:  $ASSETS_DIR"
echo "🏷️ Version:           $VERSION"
echo "=============================================================="

mkdir -p "$ASSETS_DIR" "$DIST_LINUX" "$DIST_WINDOWS" "$SPEC_DIR"

# ===============================================================
# 🧹 Clean previous builds
# ===============================================================
echo "🧹 Cleaning previous builds..."
rm -rf "$PROJECT_DIR/build" "$PROJECT_DIR/dist"
mkdir -p "$DIST_LINUX" "$DIST_WINDOWS" "$SPEC_DIR"

# ===============================================================
# ✅ Ensure PyInstaller (Linux)
# ===============================================================
if [ "$BUILD_LINUX" = true ]; then
    if ! command -v pyinstaller &> /dev/null; then
        echo "❌ PyInstaller not found for Linux. Installing in venv..."
        python3 -m venv .venv
        source .venv/bin/activate
        pip install --upgrade pip
        pip install pyinstaller
    fi
fi

# ===============================================================
# 🐧 LINUX BUILDS
# ===============================================================
if [ "$BUILD_LINUX" = true ]; then
    echo "🐧 Building Linux executables..."

    pyinstaller master/master_app.py \
      --onefile --windowed \
      --name "ModbusHubMaster_${VERSION}" \
      --icon="$ASSETS_DIR/icons/master/icon_master.png" \
      --add-data "$ASSETS_DIR:assets" \
      --strip --noconfirm --clean \
      --exclude-module tkinter --exclude-module test \
      --distpath "$DIST_LINUX" \
      --specpath "$SPEC_DIR"

    pyinstaller slave/slave_app.py \
      --onefile --windowed \
      --name "ModbusHubSlave_${VERSION}" \
      --icon="$ASSETS_DIR/icons/slave/icon_slave.png" \
      --add-data "$ASSETS_DIR:assets" \
      --strip --noconfirm --clean \
      --exclude-module tkinter --exclude-module test \
      --distpath "$DIST_LINUX" \
      --specpath "$SPEC_DIR"

    echo "✅ Linux executables created in: $DIST_LINUX"
else
    echo "⏭️ Skipping Linux build (--windows-only flag used)"
fi


# ===============================================================
# 🪟 WINDOWS BUILDS (via Wine, portable)
# ===============================================================
if [ "$BUILD_WINDOWS" = true ]; then
    echo "🪟 Building Windows executables using Wine..."

    if ! command -v wine &> /dev/null; then
        echo "❌ Wine not found. Please install it with:"
        echo "   sudo apt install wine64 wget"
        exit 1
    fi

    cd "$PROJECT_DIR"
    echo "📂 Current directory: $(pwd)"

    # Convert Linux path → Windows format for Wine
    WIN_PROJECT_PATH="Z:\\$(echo "$PROJECT_DIR" | sed 's/\//\\/g')"
    echo "🪟 Windows project path: $WIN_PROJECT_PATH"

    mkdir -p "$WINE_PYTHON_DIR"
    if [ ! -f "$WINE_PYTHON_DIR/python.exe" ]; then
        echo "⚙️ Installing Python 3.11 for Windows under Wine..."
        wget -q https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe -O "$WINE_PYTHON_DIR/python-installer.exe"
        wine "$WINE_PYTHON_DIR/python-installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 TargetDir=C:\\Python311
    fi

    echo "📦 Installing PyInstaller and dependencies under Wine..."
    wine C:\\Python311\\python.exe -m pip install --upgrade pip setuptools wheel
    wine C:\\Python311\\python.exe -m pip install pyinstaller pyside6 pymodbusTCP

    # Build Master
    echo "🏗️ Building ModbusHubMaster_${VERSION}.exe..."
    wine cmd /c "cd ${WIN_PROJECT_PATH} && C:\\Python311\\python.exe -m PyInstaller master\\master_app.py \
      --onefile --windowed \
      --name=ModbusHubMaster_${VERSION} \
      --icon=${WIN_PROJECT_PATH}\\assets\\icons\\master\\icon_master.ico \
      --add-data=${WIN_PROJECT_PATH}\\assets:assets \
      --add-data=C:\\Python311\\Lib\\site-packages\\PySide6\\plugins\\platforms:PySide6\\plugins\\platforms \
      --noconfirm --clean \
      --exclude-module=tkinter --exclude-module=test \
      --distpath=dist\\windows \
      --specpath=build\\specs"

    # Build Slave
    echo "🏗️ Building ModbusHubSlave_${VERSION}.exe..."
    wine cmd /c "cd ${WIN_PROJECT_PATH} && C:\\Python311\\python.exe -m PyInstaller slave\\slave_app.py \
      --onefile --windowed \
      --name=ModbusHubSlave_${VERSION} \
      --icon=${WIN_PROJECT_PATH}\\assets\\icons\\slave\\icon_slave.ico \
      --add-data=${WIN_PROJECT_PATH}\\assets:assets \
      --add-data=C:\\Python311\\Lib\\site-packages\\PySide6\\plugins\\platforms:PySide6\\plugins\\platforms \
      --noconfirm --clean \
      --exclude-module=tkinter --exclude-module=test \
      --distpath=dist\\windows \
      --specpath=build\\specs"

    echo "✅ Windows executables created in: $DIST_WINDOWS"
else
    echo "⏭️ Skipping Windows build (--linux-only flag used)"
fi


# ===============================================================
# 📦 PACKAGING
# ===============================================================
echo "📦 Packaging executables..."

cd "$PROJECT_DIR/dist"
[ -d linux ] && zip -r "ModbusHub_Linux_Binaries_${VERSION}.zip" linux/ >/dev/null 2>&1
[ -d windows ] && zip -r "ModbusHub_Windows_Binaries_${VERSION}.zip" windows/ >/dev/null 2>&1
cd "$PROJECT_DIR"

echo "✅ Build complete!"
echo "--------------------------------------------------------------"
echo "🏷️ Version: $VERSION"
[ "$BUILD_LINUX" = true ] && echo "🐧 Linux executables:   $DIST_LINUX"
[ "$BUILD_WINDOWS" = true ] && echo "🪟 Windows executables: $DIST_WINDOWS"
echo "📦 Packages created:"
[ -f "$PROJECT_DIR/dist/ModbusHub_Linux_Binaries_${VERSION}.zip" ] && echo "  - dist/ModbusHub_Linux_Binaries_${VERSION}.zip"
[ -f "$PROJECT_DIR/dist/ModbusHub_Windows_Binaries_${VERSION}.zip" ] && echo "  - dist/ModbusHub_Windows_Binaries_${VERSION}.zip"
echo "--------------------------------------------------------------"
echo "🎉 All done!"
