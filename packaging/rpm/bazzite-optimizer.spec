Name:           bazzite-optimizer
Version:        1.2.0
Release:        1%{?dist}
Summary:        Professional gaming system optimization suite for Bazzite Linux

License:        MIT
URL:            https://github.com/doublegate/Bazzite-Config
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

Requires:       python3 >= 3.8
Requires:       python3-psutil
Requires:       python3-gobject
Requires:       gtk4
Requires:       systemd
Requires:       rpm-ostree
Requires:       stress-ng
Requires:       sysbench

# NVIDIA GPU support (optional)
Recommends:     nvidia-settings
Recommends:     xorg-x11-drv-nvidia

# AMD GPU support (optional)
Recommends:     rocm-smi

# Gaming tools
Recommends:     gamemode
Recommends:     mangohud

# v1.2.0 Advanced features (optional)
Recommends:     python3-matplotlib
Recommends:     python3-requests

# Platform expansion support (optional)
Recommends:     ryzenadj

%description
Bazzite Gaming Optimization Suite is a comprehensive system optimization
tool designed for Linux gaming systems with support for 7 platforms
(Bazzite, Fedora, Ubuntu, Debian, Arch, Steam Deck, ROG Ally). It provides
intelligent hardware detection, automated gaming optimizations, real-time
performance monitoring, and a professional GTK4 graphical interface with
advanced features including AI-based auto-tuning and remote management.

Features:
- 4 gaming profiles (Competitive, Balanced, Streaming, Creative)
- Multi-GPU support (NVIDIA + AMD + Intel simultaneous)
- Real-time performance monitoring with historical graphs
- Community profile sharing and cloud benchmarking
- AI-based auto-tuning with intelligent recommendations
- REST API for remote management (7 endpoints)
- Progressive GPU overclocking with safety limits
- Platform expansion (Ubuntu/Debian, ROG Ally, mobile AMD APUs)
- Multi-monitor gaming profiles
- Complete backup and rollback capabilities

%package gui
Summary:        GTK4 graphical interface for Bazzite Gaming Optimizer
Requires:       %{name} = %{version}-%{release}
Requires:       gtk4 >= 4.6
Requires:       python3-gobject >= 3.44

%description gui
This package provides a professional GTK4 graphical user interface for
the Bazzite Gaming Optimization Suite, making gaming optimizations
accessible through an intuitive point-and-click interface with advanced
features including historical metrics graphs, custom profile editor,
and multi-GPU management.

Features:
- 5-tab interface (Dashboard, Profiles, Monitoring, Quick Fixes, Settings)
- Historical metrics graphs with 5-minute rolling history
- Custom profile editor with 7 configuration tabs
- Multi-GPU management (NVIDIA + AMD + Intel)
- Settings persistence across sessions
- Real-time system metrics visualization
- One-click profile application
- Desktop application menu integration

%prep
%autosetup

%build
# Nothing to build - Python scripts

%install
# Create directory structure
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_datadir}/%{name}
install -d %{buildroot}%{_datadir}/applications
install -d %{buildroot}%{_sysconfdir}/%{name}
install -d %{buildroot}%{_sysconfdir}/%{name}/profiles

# Install main script
install -m 0755 bazzite-optimizer.py %{buildroot}%{_bindir}/bazzite-optimizer
install -m 0755 reset-bazzite-defaults.sh %{buildroot}%{_bindir}/reset-bazzite-defaults

# Install GUI
install -m 0755 bazzite-optimizer-gui.py %{buildroot}%{_bindir}/bazzite-optimizer-gui
cp -r gui %{buildroot}%{_datadir}/%{name}/

# Install platform support modules
cp -r platform_support %{buildroot}%{_datadir}/%{name}/

# Install desktop file
install -m 0644 bazzite-optimizer-gui.desktop %{buildroot}%{_datadir}/applications/

# Install documentation
install -d %{buildroot}%{_docdir}/%{name}
install -m 0644 README.md %{buildroot}%{_docdir}/%{name}/
install -m 0644 CHANGELOG.md %{buildroot}%{_docdir}/%{name}/
cp -r docs %{buildroot}%{_docdir}/%{name}/

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/bazzite-optimizer
%{_bindir}/reset-bazzite-defaults
%{_sysconfdir}/%{name}
%{_docdir}/%{name}

%files gui
%{_bindir}/bazzite-optimizer-gui
%{_datadir}/%{name}/
%{_datadir}/applications/bazzite-optimizer-gui.desktop

%post
# Create necessary directories
mkdir -p /etc/bazzite-optimizer/profiles
mkdir -p /var/log/gaming-benchmark
mkdir -p /var/log/gaming-metrics

# Set proper permissions
chmod 755 %{_bindir}/bazzite-optimizer
chmod 755 %{_bindir}/bazzite-optimizer-gui
chmod 755 %{_bindir}/reset-bazzite-defaults

%postun
# Cleanup on uninstall
if [ $1 -eq 0 ]; then
    # Only on complete removal, not upgrade
    rm -rf /etc/bazzite-optimizer 2>/dev/null || true
fi

%changelog
* Mon Nov 18 2025 Bazzite Optimizer Team <noreply@github.com> - 1.2.0-1
- v1.2.0 Release: Professional Gaming Suite - Advanced Features + Extended Platform Support
- Added GUI enhancements: historical metrics graphs, custom profile editor, multi-GPU manager
- Added settings persistence with window state and profile caching
- Added community profile sharing with rating system
- Added cloud benchmarking with percentile ranking
- Added AI-based auto-tuning with intelligent recommendations
- Added remote management REST API with 7 endpoints
- Added Ubuntu/Debian platform support with apt integration
- Added ROG Ally support with handheld profiles and TDP management
- Added mobile AMD APU optimization for 10+ APU models
- Added multi-monitor gaming profiles with X11/Wayland support
- Code growth: 10,245 → 14,500+ lines (+41%)
- Platform support expanded from 3 to 7 distributions

* Mon Nov 18 2025 Bazzite Optimizer Team <noreply@github.com> - 1.1.0-1
- v1.1.0 Release: Accessibility Revolution - GTK4 Graphical Interface
- Added complete GTK4-based GUI with 5-tab interface
- Added 16 GUI modules (models, controllers, UI components)
- Added real-time performance monitoring
- Added one-click profile application
- Added comprehensive quick fixes
- Enhanced documentation and testing framework

* Mon Sep 09 2025 Bazzite Optimizer Team <noreply@github.com> - 1.0.8-1
- v1.0.8+ Release: Security Excellence + Advanced System Restoration
- Added SecurityValidator framework
- Added reset-bazzite-defaults.sh restoration tool
- Fixed format string security issues
- Enhanced boot infrastructure optimization
- Improved kernel parameter deduplication

* Thu Aug 15 2025 Bazzite Optimizer Team <noreply@github.com> - 1.0.0-1
- Initial RPM package release
- Complete bazzite-optimizer.py implementation
- 4 gaming profiles support
- Hardware-specific optimizations
