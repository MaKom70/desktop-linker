#!/bin/bash
# Desktop Linker – Universal install script
# Supports: apt (Debian/Ubuntu/Pop!OS), dnf (Fedora), pacman (Arch), zypper (openSUSE)

set -e

INSTALL_DIR="/opt/desktop-linker"
DESKTOP_FILE="$HOME/.local/share/applications/desktop_linker.desktop"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
err()  { echo -e "${RED}✗${NC} $1"; }

echo ""
echo "╔═══════════════════════════════════════╗"
echo "║     Desktop Linker – Installation     ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# Detect package manager
detect_package_manager() {
    if command -v apt &>/dev/null; then
        echo "apt"
    elif command -v dnf &>/dev/null; then
        echo "dnf"
    elif command -v pacman &>/dev/null; then
        echo "pacman"
    elif command -v zypper &>/dev/null; then
        echo "zypper"
    else
        echo "unknown"
    fi
}

PKG_MANAGER=$(detect_package_manager)

if [ "$PKG_MANAGER" = "unknown" ]; then
    err "No supported package manager found (apt/dnf/pacman/zypper)."
    err "Please install the dependencies manually and run this script again."
    exit 1
fi

ok "Package manager detected: $PKG_MANAGER"

# Install function per package manager
install_packages() {
    case "$PKG_MANAGER" in
        apt)
            sudo apt update -qq
            sudo apt install -y "$@"
            ;;
        dnf)
            sudo dnf install -y "$@"
            ;;
        pacman)
            sudo pacman -Sy --noconfirm "$@"
            ;;
        zypper)
            sudo zypper install -y "$@"
            ;;
    esac
}

# Package names per distro
get_package_names() {
    case "$PKG_MANAGER" in
        apt)
            echo "python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 python3-gi-cairo xdg-utils"
            ;;
        dnf)
            echo "python3-gobject gtk4 libadwaita xdg-utils"
            ;;
        pacman)
            echo "python-gobject gtk4 libadwaita xdg-utils"
            ;;
        zypper)
            echo "python3-gobject typelib-1_0-Gtk-4_0 typelib-1_0-Adw-1 xdg-utils"
            ;;
    esac
}

# Check & install dependencies
echo "Checking dependencies..."
echo ""

NEED_INSTALL=false

# 1. Python3
if command -v python3 &>/dev/null; then
    ok "python3 ($(python3 --version 2>&1))"
else
    err "python3 not found!"
    NEED_INSTALL=true
fi

# 2. python3-gi
if python3 -c "import gi" 2>/dev/null; then
    ok "python3-gi"
else
    warn "python3-gi missing"
    NEED_INSTALL=true
fi

# 3. GTK4
if python3 -c "import gi; gi.require_version('Gtk', '4.0'); from gi.repository import Gtk" 2>/dev/null; then
    ok "GTK4"
else
    warn "GTK4 missing"
    NEED_INSTALL=true
fi

# 4. libadwaita
if python3 -c "import gi; gi.require_version('Adw', '1'); from gi.repository import Adw" 2>/dev/null; then
    ok "libadwaita"
else
    warn "libadwaita missing"
    NEED_INSTALL=true
fi

# 5. xdg-open
if command -v xdg-open &>/dev/null; then
    ok "xdg-open"
else
    warn "xdg-open missing"
    NEED_INSTALL=true
fi

echo ""

if [ "$NEED_INSTALL" = true ]; then
    echo "Installing missing packages..."
    install_packages $(get_package_names)
    ok "Packages installed"
else
    ok "All dependencies are already installed"
fi

echo ""

# Check if script is run from the correct directory
if [ ! -f "desktop_linker.py" ]; then
    err "desktop_linker.py not found!"
    err "Please run this script from the folder where desktop_linker.py is located."
    exit 1
fi

# Install app files
echo "Installing to $INSTALL_DIR ..."
sudo mkdir -p "$INSTALL_DIR"
sudo cp desktop_linker.py "$INSTALL_DIR/desktop_linker.py"
sudo chmod 755 "$INSTALL_DIR"
sudo chmod 644 "$INSTALL_DIR/desktop_linker.py"
ok "Files copied"

# Create .desktop entry
echo "Registering app in menu..."
mkdir -p "$HOME/.local/share/applications"

cat > "$DESKTOP_FILE" << DESKTOP
[Desktop Entry]
Version=1.0
Type=Application
Name=Desktop Linker
Comment=Create desktop shortcuts for files, folders and applications
Exec=python3 $INSTALL_DIR/desktop_linker.py
Icon=insert-link
Terminal=false
Categories=Utility;
StartupNotify=true
DESKTOP

chmod +x "$DESKTOP_FILE"
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null && ok "App menu updated" || true

echo ""
echo "╔═══════════════════════════════════════╗"
echo "║      ✓ Installation complete!         ║"
echo "╚═══════════════════════════════════════╝"
echo ""
echo "  Desktop Linker is now available in your app menu."
echo "  Tip: Launch Desktop Linker and create a shortcut"
echo "  for itself right on your desktop! :-)"
echo ""
