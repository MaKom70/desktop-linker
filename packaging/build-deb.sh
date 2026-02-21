#!/bin/bash
# Builds desktop-linker_VERSION_all.deb
# Run from the repository root: ./build-deb.sh

set -e

VERSION=$(grep "^APP_VERSION" desktop_linker.py | cut -d'"' -f2)
PKG_NAME="desktop-linker_${VERSION}_all"
BUILD_DIR="/tmp/desktop-linker-build/$PKG_NAME"

echo "=== Building desktop-linker v$VERSION (.deb) ==="

# Clean
rm -rf "/tmp/desktop-linker-build"

# Create structure
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/share/desktop-linker"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/doc/desktop-linker"

# Control file
cat > "$BUILD_DIR/DEBIAN/control" << EOF
Package: desktop-linker
Version: $VERSION
Section: utils
Priority: optional
Architecture: all
Depends: python3 (>= 3.8), python3-gi, gir1.2-gtk-4.0, gir1.2-adw-1, python3-gi-cairo, xdg-utils
Maintainer: aumuck
Description: Create desktop shortcuts for files, folders and applications
 Desktop Linker lets you easily create desktop shortcuts on Linux.
 Supports files, folders and installed applications with drag & drop,
 file dialogs and a searchable app list. Supports English and German.
Homepage: https://github.com/MaKom70/desktop-linker
EOF

# Post-install / post-remove scripts
cat > "$BUILD_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
update-desktop-database /usr/share/applications 2>/dev/null || true
EOF

cat > "$BUILD_DIR/DEBIAN/postrm" << 'EOF'
#!/bin/bash
update-desktop-database /usr/share/applications 2>/dev/null || true
EOF

chmod 755 "$BUILD_DIR/DEBIAN/postinst"
chmod 755 "$BUILD_DIR/DEBIAN/postrm"

# App files
cp desktop_linker.py "$BUILD_DIR/usr/share/desktop-linker/"
chmod 644 "$BUILD_DIR/usr/share/desktop-linker/desktop_linker.py"

# Desktop entry
cat > "$BUILD_DIR/usr/share/applications/desktop-linker.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Desktop Linker
Comment=Create desktop shortcuts for files, folders and applications
Exec=python3 /usr/share/desktop-linker/desktop_linker.py
Icon=insert-link
Terminal=false
Categories=Utility;
StartupNotify=true
Keywords=shortcut;desktop;link;folder;
EOF
chmod 644 "$BUILD_DIR/usr/share/applications/desktop-linker.desktop"

# Copyright
cp packaging/copyright "$BUILD_DIR/usr/share/doc/desktop-linker/copyright"

# Build
dpkg-deb --build "$BUILD_DIR" "desktop-linker_${VERSION}_all.deb"

echo ""
echo "✓ Built: desktop-linker_${VERSION}_all.deb"
echo "  Install with: sudo apt install ./desktop-linker_${VERSION}_all.deb"
