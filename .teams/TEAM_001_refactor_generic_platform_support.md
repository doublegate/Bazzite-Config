# TEAM_001: Generic Platform Support Refactor

**Created**: 2025-12-31
**Status**: Active
**Focus**: Refactor bazzite-config to support all rpm-ostree OSes and traditional RPM-based OSes

## Team Mission

Transform the Bazzite-specific gaming optimizer into a generic Linux gaming optimizer that:
1. Keeps Bazzite as a first-class citizen (with all its features)
2. Supports all rpm-ostree immutable OSes (Silverblue, Kinoite, Aurora, etc.)
3. Supports traditional RPM-based OSes (Fedora Workstation, Ultramarine, etc.)
4. Removes hard-coded hardware references (author's RTX 5080, i9-10850K)

## Target System Analysis

**User's System (Ultramarine Linux 43)**:
- **OS Type**: Traditional RPM (NOT rpm-ostree)
- **Package Manager**: dnf
- **Kernel Params**: `/etc/default/grub` + `grub2-mkconfig`
- **CPU**: Intel i5-1240P (Alder Lake-P, 12 cores, 16 threads, hybrid P+E cores)
- **GPUs**: Intel Iris Xe (integrated) + NVIDIA RTX 3060 LHR (discrete)
- **RAM**: 62GB
- **Kernel**: 6.17.12-300.fc43.x86_64

## Key Changes Required

### 1. Platform Detection Layer
- Detect rpm-ostree vs traditional RPM vs apt-based
- Abstract system type into enum: `IMMUTABLE_OSTREE`, `TRADITIONAL_RPM`, `TRADITIONAL_DEB`

### 2. Package Management Abstraction
- `rpm-ostree install` → for immutable systems
- `dnf install` → for traditional RPM
- `apt install` → for Debian/Ubuntu

### 3. Kernel Parameter Application
- rpm-ostree: `rpm-ostree kargs --append=...`
- Traditional: Edit `/etc/default/grub` GRUB_CMDLINE_LINUX + `grub2-mkconfig`

### 4. Hardware Abstraction
- Remove hard-coded "RTX 5080 Blackwell | i9-10850K | 64GB RAM"
- Dynamic hardware detection and profile matching
- Support hybrid Intel/NVIDIA GPU configurations

### 5. Bazzite-Specific Features
- Make `ujust` commands conditional (only on Bazzite)
- Keep Bazzite as tier-1 supported platform

## Progress Log

- **2025-12-31**: Team created, investigation complete, refactor plan complete

## Handoff Notes

_To be updated as work progresses_
