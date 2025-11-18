# Packaging Guide - Bazzite Gaming Optimization Suite

Comprehensive guide for building and distributing packages across multiple Linux distributions.

## Table of Contents

- [Overview](#overview)
- [RPM Packages (Fedora/Bazzite)](#rpm-packages-fedorabazzite)
- [Flatpak Packages](#flatpak-packages)
- [AUR Packages (Arch Linux)](#aur-packages-arch-linux)
- [Copr Repository](#copr-repository)
- [Manual Installation](#manual-installation)

## Overview

The Bazzite Gaming Optimization Suite supports multiple packaging formats:

| Format | Distributions | Location |
|--------|--------------|----------|
| **RPM** | Fedora, Bazzite, RHEL | `packaging/rpm/` |
| **Flatpak** | Universal | `packaging/flatpak/` |
| **AUR** | Arch, Manjaro | `packaging/aur/` |
| **Copr** | Fedora/Bazzite | `packaging/copr/` |

---

## RPM Packages (Fedora/Bazzite)

### Building RPM Packages

#### Prerequisites

```bash
# Fedora/Bazzite
sudo dnf install rpm-build rpmdevtools

# Set up RPM build environment
rpmdev-setuptree
```

#### Build Process

```bash
# Navigate to project root
cd /path/to/Bazzite-Config

# Create source tarball
git archive --format=tar.gz --prefix=bazzite-optimizer-1.1.0/ \
    -o ~/rpmbuild/SOURCES/bazzite-optimizer-1.1.0.tar.gz HEAD

# Build RPM
rpmbuild -ba packaging/rpm/bazzite-optimizer.spec

# Built packages will be in:
# ~/rpmbuild/RPMS/noarch/bazzite-optimizer-1.1.0-1.fc*.noarch.rpm
# ~/rpmbuild/RPMS/noarch/bazzite-optimizer-gui-1.1.0-1.fc*.noarch.rpm
# ~/rpmbuild/SRPMS/bazzite-optimizer-1.1.0-1.fc*.src.rpm
```

### Package Split

- **bazzite-optimizer**: Core CLI optimizer and scripts
- **bazzite-optimizer-gui**: GTK4 graphical interface

### Installation

```bash
# Install both packages
sudo dnf install ~/rpmbuild/RPMS/noarch/bazzite-optimizer-*.rpm

# Or install from Copr repository (recommended)
sudo dnf copr enable doublegate/bazzite-optimizer
sudo dnf install bazzite-optimizer bazzite-optimizer-gui
```

### RPM Spec File

Located at `packaging/rpm/bazzite-optimizer.spec`

**Key Sections**:
- Dependencies (runtime and build)
- File installation
- Post-installation scripts
- Changelog

---

## Flatpak Packages

### Building Flatpak

#### Prerequisites

```bash
# Install flatpak and flatpak-builder
sudo dnf install flatpak flatpak-builder

# Add Flathub repository
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
```

#### Build Process

```bash
# Navigate to project root
cd /path/to/Bazzite-Config

# Build Flatpak
flatpak-builder --force-clean --repo=repo build-dir packaging/flatpak/org.bazzite.optimizer.yml

# Create bundle for distribution
flatpak build-bundle repo bazzite-optimizer.flatpak org.bazzite.optimizer

# Test local installation
flatpak install --user bazzite-optimizer.flatpak

# Run application
flatpak run org.bazzite.optimizer
```

### Publishing to Flathub

1. Fork [flathub/flathub](https://github.com/flathub/flathub)
2. Create `org.bazzite.optimizer` subdirectory
3. Add manifest file
4. Create pull request
5. Wait for review and approval

### Flatpak Manifest

Located at `packaging/flatpak/org.bazzite.optimizer.yml`

**Key Features**:
- GNOME Platform runtime
- System access for hardware monitoring
- PolicyKit integration for privilege escalation
- Network access for updates

---

## AUR Packages (Arch Linux)

### Building from AUR

#### Prerequisites

```bash
# Install base-devel
sudo pacman -S base-devel git

# Install AUR helper (optional)
yay -S aurutils  # or paru, yay, etc.
```

#### Build Process

```bash
# Clone AUR repository (once published)
git clone https://aur.archlinux.org/bazzite-optimizer.git
cd bazzite-optimizer

# Build package
makepkg -si

# Or use AUR helper
yay -S bazzite-optimizer
```

### Publishing to AUR

1. **Create AUR Account**: https://aur.archlinux.org/register/
2. **Add SSH Key**: Upload SSH public key to AUR account
3. **Clone AUR Repository**:
   ```bash
   git clone ssh://aur@aur.archlinux.org/bazzite-optimizer.git
   cd bazzite-optimizer
   ```
4. **Add Files**:
   ```bash
   cp packaging/aur/PKGBUILD .
   cp packaging/aur/.SRCINFO .  # Generated with makepkg --printsrcinfo
   ```
5. **Commit and Push**:
   ```bash
   git add PKGBUILD .SRCINFO
   git commit -m "Initial upload: bazzite-optimizer 1.1.0"
   git push
   ```

### Maintaining AUR Package

**Update Process**:

```bash
# Update PKGBUILD version
vim PKGBUILD

# Generate .SRCINFO
makepkg --printsrcinfo > .SRCINFO

# Commit and push
git add PKGBUILD .SRCINFO
git commit -m "Update to v1.1.0"
git push
```

### PKGBUILD File

Located at `packaging/aur/PKGBUILD`

**Key Sections**:
- Package metadata
- Dependencies
- Source URLs and checksums
- Build and package functions

---

## Copr Repository

Copr is Fedora's user repository system, similar to Ubuntu's PPA.

### Setting Up Copr

#### Prerequisites

```bash
# Install copr-cli
sudo dnf install copr-cli

# Login to Copr
copr-cli login
# Follow instructions to get API token from: https://copr.fedorainfracloud.org/api/
```

#### Create Copr Project

```bash
# Create new project
copr-cli create bazzite-optimizer \
    --chroot fedora-39-x86_64 \
    --chroot fedora-40-x86_64 \
    --chroot fedora-41-x86_64 \
    --description "Professional gaming system optimization suite for Bazzite Linux" \
    --instructions "Install with: sudo dnf install bazzite-optimizer bazzite-optimizer-gui"
```

### Building in Copr

#### Option 1: Automated Build Script

```bash
# Use provided build script
cd packaging/copr
chmod +x copr-build.sh
./copr-build.sh
```

#### Option 2: Manual Build

```bash
# Create source RPM
git archive --format=tar.gz --prefix=bazzite-optimizer-1.1.0/ \
    -o bazzite-optimizer-1.1.0.tar.gz HEAD

rpmbuild -bs packaging/rpm/bazzite-optimizer.spec \
    --define "_sourcedir $(pwd)" \
    --define "_srcrpmdir $(pwd)"

# Submit to Copr
copr-cli build doublegate/bazzite-optimizer bazzite-optimizer-1.1.0-1.*.src.rpm
```

#### Option 3: GitHub Integration

Configure Copr to build automatically from GitHub:

1. Go to Copr project settings
2. Add "Packages" → "New Package" → "PyPI/Custom/SCM"
3. Select "SCM" (Source Code Management)
4. Configure:
   - Type: Git
   - Clone URL: https://github.com/doublegate/Bazzite-Config.git
   - Spec file: packaging/rpm/bazzite-optimizer.spec
   - Auto-rebuild: Yes

### Using Copr Repository

#### Users Install From Copr

```bash
# Enable Copr repository
sudo dnf copr enable doublegate/bazzite-optimizer

# Install packages
sudo dnf install bazzite-optimizer bazzite-optimizer-gui

# Updates will come through normal dnf update
sudo dnf update
```

### Copr Build Script

Located at `packaging/copr/copr-build.sh`

**Features**:
- Automated source tarball creation
- SRPM building
- Copr submission
- Progress monitoring

---

## Manual Installation

For development or testing without packages.

### System-Wide Installation

```bash
# Clone repository
git clone https://github.com/doublegate/Bazzite-Config.git
cd Bazzite-Config

# Run system-wide installer
sudo ./install-gui.sh --system

# Applications will be installed to:
# - /usr/local/bin/bazzite-optimizer
# - /usr/local/bin/bazzite-optimizer-gui
# - /usr/local/bin/reset-bazzite-defaults
# - /usr/local/share/applications/bazzite-optimizer-gui.desktop
```

### User Installation

```bash
# Run user installer
./install-gui.sh

# Applications will be installed to:
# - ~/.local/bin/bazzite-optimizer-gui
# - ~/.local/share/applications/bazzite-optimizer-gui.desktop
```

### Uninstallation

```bash
# System-wide uninstall
sudo ./install-gui.sh --uninstall

# User uninstall
./install-gui.sh --uninstall
```

---

## Package Versioning

### Version Scheme

Follow [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH

1.1.0 → 1.1.1 (patch: bug fixes)
1.1.1 → 1.2.0 (minor: new features, backward compatible)
1.2.0 → 2.0.0 (major: breaking changes)
```

### Release Process

1. **Update Version Files**:
   ```bash
   # Update VERSION file
   vim VERSION

   # Update RPM spec
   vim packaging/rpm/bazzite-optimizer.spec

   # Update AUR PKGBUILD
   vim packaging/aur/PKGBUILD

   # Update Flatpak manifest
   vim packaging/flatpak/org.bazzite.optimizer.yml
   ```

2. **Update Changelog**:
   ```bash
   vim CHANGELOG.md
   ```

3. **Commit and Tag**:
   ```bash
   git add VERSION CHANGELOG.md packaging/
   git commit -m "chore: Bump version to 1.1.0"
   git tag -a v1.1.0 -m "Release v1.1.0: Accessibility Revolution - GTK4 GUI"
   git push origin main --tags
   ```

4. **Build Packages**:
   ```bash
   # Build RPM
   rpmbuild -ba packaging/rpm/bazzite-optimizer.spec

   # Build Flatpak
   flatpak-builder build-dir packaging/flatpak/org.bazzite.optimizer.yml

   # Submit to Copr
   packaging/copr/copr-build.sh

   # Update AUR
   cd /path/to/aur/bazzite-optimizer
   makepkg --printsrcinfo > .SRCINFO
   git add PKGBUILD .SRCINFO
   git commit -m "Update to v1.1.0"
   git push
   ```

5. **Create GitHub Release**:
   - Go to https://github.com/doublegate/Bazzite-Config/releases/new
   - Select tag v1.1.0
   - Add release notes from CHANGELOG.md
   - Attach built packages (optional)
   - Publish release

---

## Distribution-Specific Notes

### Bazzite/Fedora Immutable

For rpm-ostree based systems:

```bash
# Layer package
rpm-ostree install bazzite-optimizer bazzite-optimizer-gui

# Reboot to apply
systemctl reboot
```

### Arch Linux

```bash
# Install from AUR
yay -S bazzite-optimizer

# Or manually
git clone https://aur.archlinux.org/bazzite-optimizer.git
cd bazzite-optimizer
makepkg -si
```

### Universal (Flatpak)

```bash
# Install from Flathub (once published)
flatpak install flathub org.bazzite.optimizer

# Run
flatpak run org.bazzite.optimizer
```

---

## Troubleshooting

### Common Issues

**RPM Build Fails**:
```bash
# Check dependencies
dnf builddep packaging/rpm/bazzite-optimizer.spec

# Clean build environment
rm -rf ~/rpmbuild/BUILD/*
```

**Flatpak Sandbox Issues**:
```bash
# Grant additional permissions
flatpak override --user --filesystem=host org.bazzite.optimizer
```

**Copr Build Timeout**:
```bash
# Check build logs
copr-cli watch-build <build-id>
```

---

## Contributing to Packaging

When contributing packaging improvements:

1. Test on target distribution
2. Update relevant spec/manifest files
3. Document changes in PACKAGING.md
4. Submit PR with packaging tag

---

## Additional Resources

- [RPM Packaging Guide](https://rpm-packaging-guide.github.io/)
- [Flatpak Documentation](https://docs.flatpak.org/)
- [AUR Submission Guidelines](https://wiki.archlinux.org/title/AUR_submission_guidelines)
- [Copr Documentation](https://docs.pagure.org/copr.copr/)
