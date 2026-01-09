# Phase 5, Step 2 — Documentation Updates (PR #12)

**Parent**: [Phase 5](README.md)
**Branch**: `docs/multi-platform-support`
**Dependency**: PR #10 merged
**Estimated Time**: 2-3 hours

---

## UoW 5.2.1: Update README.md badges

**Goal**: Update platform badge to show multi-platform support.

**File**: `README.md`
**Location**: Badge section at top

**Current**:
```markdown
![Platform](https://img.shields.io/badge/Platform-Bazzite%20Linux-blue)
```

**Change to**:
```markdown
![Platform](https://img.shields.io/badge/Platform-Linux%20(Multi--Distro)-blue)
```

---

## UoW 5.2.2: Add Supported Platforms section

**Goal**: Add new section documenting platform support.

**File**: `README.md`
**Location**: After Overview section

**Add**:
```markdown
## 🖥️ Supported Platforms

| Platform | Type | Package Manager | Kernel Params | Status |
|----------|------|-----------------|---------------|--------|
| **Bazzite** | Immutable | rpm-ostree | rpm-ostree kargs | ✅ Full |
| **Fedora Silverblue/Kinoite** | Immutable | rpm-ostree | rpm-ostree kargs | ✅ Full |
| **Fedora Workstation** | Traditional | dnf | GRUB | ✅ Full |
| **Ultramarine Linux** | Traditional | dnf | GRUB | ✅ Full |
| **Ubuntu** | Traditional | apt | GRUB | ✅ Full |
| **Debian** | Traditional | apt | GRUB | ✅ Full |
```

---

## UoW 5.2.3: Update installation instructions

**Goal**: Add per-platform installation instructions.

**File**: `README.md`
**Location**: Installation section

**Add sections for**:
- Bazzite / Fedora Silverblue
- Fedora Workstation / Ultramarine
- Ubuntu / Debian

---

## UoW 5.2.4: Create PLATFORM_SUPPORT.md

**Goal**: Create detailed platform support documentation.

**File**: `docs/PLATFORM_SUPPORT.md`

**Sections**:
- Platform Detection
- Kernel Parameter Management
- Package Management
- Feature Availability
- Troubleshooting

---

## UoW 5.2.5: Update CHANGELOG.md

**Goal**: Add release notes for multi-platform support.

**File**: `CHANGELOG.md`
**Location**: Top of file

**Add**:
```markdown
## v5.1.0 - Multi-Platform Support (YYYY-MM-DD)

### Added
- Platform Abstraction Layer
- GRUB Kernel Params support
- DnfPackageManager
- AptPackageManager
- Automatic Platform Detection
- Dynamic Hardware Display

### Changed
- KernelOptimizer uses platform abstraction
- BazziteOptimizer now conditional
- UI shows dynamic hardware

### Removed
- Hard-coded hardware references
- Direct rpm-ostree calls from optimizers
```

---

## UoW 5.2.6: Update TODO.md with deferred items

**Goal**: Document out-of-scope work in global TODO list (Rule 11).

**File**: `TODO.md` (or equivalent)

**Add entries**:
1. systemd-boot support for KernelParamManager
2. Arch Linux support (PacmanPackageManager)
3. Intel GPU optimizer (optional)
4. Hybrid GPU support (PRIME offload)

---

## Step Exit Criteria

- [ ] README badges updated
- [ ] Supported Platforms section added
- [ ] Installation instructions updated
- [ ] PLATFORM_SUPPORT.md created
- [ ] CHANGELOG.md updated
- [ ] TODO.md updated with deferred items
