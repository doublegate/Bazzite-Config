#!/usr/bin/env bash
#
# install-gui.sh - Bazzite Optimizer GUI Installer
#
# Installs the Bazzite Gaming Optimizer GUI to the local user directory
# or system-wide (with sudo).
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_BIN="$HOME/.local/bin"
USER_SHARE="$HOME/.local/share"
SYSTEM_BIN="/usr/local/bin"
SYSTEM_SHARE="/usr/local/share"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

check_dependencies() {
    print_info "Checking dependencies..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "Error: Python 3 is required but not installed."
        exit 1
    fi

    # Check GTK4
    if ! python3 -c "import gi; gi.require_version('Gtk', '4.0')" 2>/dev/null; then
        print_warning "GTK4 for Python not found. Installing..."
        if command -v dnf &> /dev/null; then
            sudo dnf install -y python3-gobject gtk4
        elif command -v apt &> /dev/null; then
            sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-4.0
        else
            echo "Error: Please install python3-gobject and GTK4 manually."
            exit 1
        fi
    fi

    # Check psutil (optional but recommended)
    if ! python3 -c "import psutil" 2>/dev/null; then
        print_warning "psutil not found. Installing..."
        pip3 install --user psutil || python3 -m pip install --user psutil || true
    fi

    print_success "Dependencies check complete"
}

install_user() {
    print_info "Installing to user directory..."

    # Create directories
    mkdir -p "$USER_BIN"
    mkdir -p "$USER_SHARE/applications"
    mkdir -p "$USER_SHARE/icons/hicolor/scalable/apps"

    # Copy GUI files
    print_info "Copying GUI application..."
    cp "$SCRIPT_DIR/bazzite-optimizer-gui.py" "$USER_BIN/bazzite-optimizer-gui"
    chmod +x "$USER_BIN/bazzite-optimizer-gui"

    # Copy GUI modules
    print_info "Copying GUI modules..."
    mkdir -p "$USER_SHARE/bazzite-optimizer"
    cp -r "$SCRIPT_DIR/gui" "$USER_SHARE/bazzite-optimizer/"

    # Copy backend script
    cp "$SCRIPT_DIR/bazzite-optimizer.py" "$USER_SHARE/bazzite-optimizer/"

    # Update paths in GUI launcher
    sed -i "s|/usr/local/bin/bazzite-optimizer-gui|$USER_BIN/bazzite-optimizer-gui|g" \
        "$SCRIPT_DIR/bazzite-optimizer-gui.desktop"

    # Copy desktop file
    print_info "Installing desktop entry..."
    cp "$SCRIPT_DIR/bazzite-optimizer-gui.desktop" "$USER_SHARE/applications/"

    # Update desktop database
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$USER_SHARE/applications" 2>/dev/null || true
    fi

    print_success "GUI installed to user directory"
    print_info "You may need to logout and login again for the application menu to update"
}

install_system() {
    print_info "Installing system-wide..."

    if [ "$EUID" -ne 0 ]; then
        echo "Error: System-wide installation requires root privileges."
        echo "Please run with sudo: sudo ./install-gui.sh --system"
        exit 1
    fi

    # Copy GUI application
    print_info "Copying GUI application..."
    cp "$SCRIPT_DIR/bazzite-optimizer-gui.py" "$SYSTEM_BIN/bazzite-optimizer-gui"
    chmod +x "$SYSTEM_BIN/bazzite-optimizer-gui"

    # Copy GUI modules
    print_info "Copying GUI modules..."
    mkdir -p "$SYSTEM_SHARE/bazzite-optimizer"
    cp -r "$SCRIPT_DIR/gui" "$SYSTEM_SHARE/bazzite-optimizer/"
    cp "$SCRIPT_DIR/bazzite-optimizer.py" "$SYSTEM_SHARE/bazzite-optimizer/"

    # Copy desktop file
    print_info "Installing desktop entry..."
    cp "$SCRIPT_DIR/bazzite-optimizer-gui.desktop" "$SYSTEM_SHARE/applications/"

    # Update desktop database
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$SYSTEM_SHARE/applications" 2>/dev/null || true
    fi

    print_success "GUI installed system-wide"
}

uninstall_user() {
    print_info "Uninstalling from user directory..."

    rm -f "$USER_BIN/bazzite-optimizer-gui"
    rm -rf "$USER_SHARE/bazzite-optimizer"
    rm -f "$USER_SHARE/applications/bazzite-optimizer-gui.desktop"

    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$USER_SHARE/applications" 2>/dev/null || true
    fi

    print_success "GUI uninstalled from user directory"
}

uninstall_system() {
    print_info "Uninstalling system-wide..."

    if [ "$EUID" -ne 0 ]; then
        echo "Error: System-wide uninstallation requires root privileges."
        echo "Please run with sudo: sudo ./install-gui.sh --uninstall --system"
        exit 1
    fi

    rm -f "$SYSTEM_BIN/bazzite-optimizer-gui"
    rm -rf "$SYSTEM_SHARE/bazzite-optimizer"
    rm -f "$SYSTEM_SHARE/applications/bazzite-optimizer-gui.desktop"

    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$SYSTEM_SHARE/applications" 2>/dev/null || true
    fi

    print_success "GUI uninstalled from system"
}

show_usage() {
    cat << EOF
Bazzite Optimizer GUI Installer

Usage: $0 [OPTIONS]

Options:
    --system        Install system-wide (requires sudo)
    --user          Install to user directory (default)
    --uninstall     Uninstall the GUI
    --help          Show this help message

Examples:
    $0                      # Install to user directory
    sudo $0 --system        # Install system-wide
    $0 --uninstall          # Uninstall from user directory
    sudo $0 --uninstall --system  # Uninstall system-wide

EOF
}

# Main installation logic
main() {
    local INSTALL_SYSTEM=false
    local UNINSTALL=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --system)
                INSTALL_SYSTEM=true
                shift
                ;;
            --user)
                INSTALL_SYSTEM=false
                shift
                ;;
            --uninstall)
                UNINSTALL=true
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    echo "========================================="
    echo "Bazzite Gaming Optimizer GUI Installer"
    echo "========================================="
    echo

    if [ "$UNINSTALL" = true ]; then
        if [ "$INSTALL_SYSTEM" = true ]; then
            uninstall_system
        else
            uninstall_user
        fi
    else
        check_dependencies

        if [ "$INSTALL_SYSTEM" = true ]; then
            install_system
        else
            install_user
        fi

        echo
        print_success "Installation complete!"
        echo
        echo "You can now launch the GUI from:"
        if [ "$INSTALL_SYSTEM" = true ]; then
            echo "  - Application menu (System Settings → Bazzite Gaming Optimizer)"
            echo "  - Command line: bazzite-optimizer-gui"
        else
            echo "  - Application menu (after logout/login)"
            echo "  - Command line: $USER_BIN/bazzite-optimizer-gui"
        fi
        echo
    fi
}

main "$@"
