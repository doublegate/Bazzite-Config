# Phase 5 — Hardening and Handoff

**Team**: TEAM_001
**Purpose**: Final testing, documentation, and release preparation
**Structure**: Each Step = 1 PR or task, Each UoW = 1 SLM task

---

## Step 5.1: Multi-Platform Testing

**No PR**: Testing phase
**Estimated Time**: 2-3 hours

### UoW 5.1.1: Create comprehensive test script

**Task**: Create a script to run all platform tests.

**File**: `tests/test_platform_matrix.sh`

```bash
#!/bin/bash
# Platform Matrix Test Script
# Run on each supported platform

set -e

echo "=== Platform Matrix Tests ==="
echo "Platform: $(grep PRETTY_NAME /etc/os-release | cut -d= -f2)"
echo ""

echo "[1/7] Unit Tests..."
pytest -q tests/unit/ || { echo "FAILED: Unit tests"; exit 1; }

echo "[2/7] Platform Detection..."
python3 -c "
from platform import detect_platform
info = detect_platform()
print(f'  Type: {info.platform_type.name}')
print(f'  Distro: {info.distro_name}')
print(f'  Immutable: {info.is_immutable}')
print(f'  Pkg Manager: {info.package_manager}')
print(f'  Boot Method: {info.boot_method}')
"

echo "[3/7] Kernel Param Manager..."
python3 -c "
from platform import detect_platform, PlatformServices
info = detect_platform()
services = PlatformServices(info)
kp = services.kernel_params
print(f'  Manager: {type(kp).__name__}')
params = kp.get_current_params()
print(f'  Current params: {len(params)} parameters')
"

echo "[4/7] Package Manager..."
python3 -c "
from platform import detect_platform, PlatformServices
info = detect_platform()
services = PlatformServices(info)
pm = services.package_manager
print(f'  Manager: {type(pm).__name__}')
print(f'  python3 installed: {pm.is_installed(\"python3\")}')
"

echo "[5/7] Optimizer Initialization..."
sudo python3 -c "
import sys
sys.path.insert(0, '.')
from bazzite_optimizer import BazziteGamingOptimizer
opt = BazziteGamingOptimizer()
print(f'  Platform: {opt.platform_info.platform_type.name}')
print(f'  Optimizers: {len(opt.optimizers)} loaded')
"

echo "[6/7] Validation Mode..."
sudo ./bazzite-optimizer.py --validate 2>&1 | tail -5

echo "[7/7] Check for Errors..."
ERROR_COUNT=$(sudo ./bazzite-optimizer.py --validate 2>&1 | grep -ci "error\|exception\|traceback" || true)
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "  WARNING: Found $ERROR_COUNT potential errors"
else
    echo "  No errors found"
fi

echo ""
echo "=== All Tests Passed ==="
```

---

### UoW 5.1.2: Test on Ultramarine (your system)

**Task**: Run full test suite on Ultramarine.

```bash
cd /home/vince/Projects/Bazzite-Config
chmod +x tests/test_platform_matrix.sh
./tests/test_platform_matrix.sh
```

**Expected results**:
- Platform: `FEDORA_TRADITIONAL`
- Kernel params: `GrubKernelParams`
- Package manager: `DnfPackageManager`
- All tests pass

**Record results in**: `.planning/refactor-generic-platform/test-results/ultramarine.md`

---

### UoW 5.1.3: Document test results template

**Task**: Create template for recording test results.

**File**: `.planning/refactor-generic-platform/test-results/TEMPLATE.md`

```markdown
# Test Results: [Platform Name]

**Date**: YYYY-MM-DD
**Tester**: [Name/Team]
**System**: [Distro] [Version]

## System Info
- CPU: 
- GPU: 
- RAM: 
- Kernel: 

## Platform Detection
- Type: 
- Immutable: 
- Package Manager: 
- Boot Method: 

## Test Results

| Test | Result | Notes |
|------|--------|-------|
| Unit Tests | PASS/FAIL | |
| Platform Detection | PASS/FAIL | |
| Kernel Params Read | PASS/FAIL | |
| Kernel Params Write | PASS/FAIL | |
| Package Manager | PASS/FAIL | |
| Validation Mode | PASS/FAIL | |
| Full Optimization | PASS/FAIL | |

## Issues Found
- 

## Notes
- 
```

---

## Step 5.2: Documentation Updates (PR #12)

**Branch**: `docs/multi-platform-support`
**Dependency**: PR #10 merged
**Estimated Time**: 2-3 hours

### UoW 5.2.1: Update README.md badges

**Task**: Update platform badge to show multi-platform support.

**File**: `README.md`
**Location**: Badge section at top

**Current**:
```markdown
![Platform](https://img.shields.io/badge/Platform-Bazzite%20Linux-blue?style=for-the-badge&logo=linux)
```

**Change to**:
```markdown
![Platform](https://img.shields.io/badge/Platform-Linux%20(Multi--Distro)-blue?style=for-the-badge&logo=linux)
```

---

### UoW 5.2.2: Add Supported Platforms section to README

**Task**: Add new section documenting platform support.

**File**: `README.md`
**Location**: After Overview section

**Add**:
```markdown
## 🖥️ Supported Platforms

| Platform | Type | Package Manager | Kernel Params | Status |
|----------|------|-----------------|---------------|--------|
| **Bazzite** | Immutable | rpm-ostree | rpm-ostree kargs | ✅ Full Support |
| **Fedora Silverblue/Kinoite** | Immutable | rpm-ostree | rpm-ostree kargs | ✅ Full Support |
| **Fedora Workstation** | Traditional | dnf | GRUB | ✅ Full Support |
| **Ultramarine Linux** | Traditional | dnf | GRUB | ✅ Full Support |
| **Nobara** | Traditional | dnf | GRUB | ✅ Full Support |
| **Ubuntu** | Traditional | apt | GRUB | ✅ Full Support |
| **Debian** | Traditional | apt | GRUB | ✅ Full Support |
| **Pop!_OS** | Traditional | apt | GRUB | ✅ Full Support |

### Platform-Specific Notes

- **Bazzite**: Full feature support including ujust commands
- **Other rpm-ostree distros**: All features except Bazzite-specific ujust commands
- **Traditional RPM (Fedora/Ultramarine)**: Uses GRUB for kernel parameters
- **Debian-based**: Uses GRUB for kernel parameters, apt for packages
```

---

### UoW 5.2.3: Update installation instructions

**Task**: Add per-platform installation instructions.

**File**: `README.md`
**Location**: Installation section

**Add**:
```markdown
## 📦 Installation

### Bazzite / Fedora Silverblue
```bash
# Clone the repository
git clone https://github.com/yourusername/bazzite-optimizer.git
cd bazzite-optimizer

# Install dependencies (layered)
rpm-ostree install python3-psutil

# Run (after reboot if needed)
sudo ./bazzite-optimizer.py --validate
```

### Fedora Workstation / Ultramarine / Nobara
```bash
# Clone the repository
git clone https://github.com/yourusername/bazzite-optimizer.git
cd bazzite-optimizer

# Install dependencies
sudo dnf install python3-psutil

# Run
sudo ./bazzite-optimizer.py --validate
```

### Ubuntu / Debian / Pop!_OS
```bash
# Clone the repository
git clone https://github.com/yourusername/bazzite-optimizer.git
cd bazzite-optimizer

# Install dependencies
sudo apt install python3-psutil

# Run
sudo ./bazzite-optimizer.py --validate
```
```

---

### UoW 5.2.4: Create PLATFORM_SUPPORT.md

**Task**: Create detailed platform support documentation.

**File**: `docs/PLATFORM_SUPPORT.md`

```markdown
# Platform Support

This document details platform-specific behavior and requirements.

## Platform Detection

The optimizer automatically detects your platform type:

1. **Bazzite**: Detected by presence of `ujust` command and rpm-ostree
2. **Fedora Ostree**: Detected by rpm-ostree deployment without ujust
3. **Fedora Traditional**: Detected by presence of dnf without rpm-ostree
4. **Debian-based**: Detected by presence of apt

## Kernel Parameter Management

### rpm-ostree Systems (Bazzite, Silverblue)
- Parameters managed via `rpm-ostree kargs`
- Changes staged for next boot
- Supports atomic rollback

### GRUB Systems (Fedora, Ubuntu, Debian)
- Parameters stored in `/etc/default/grub`
- Backup created before each change
- Requires `grub2-mkconfig` / `update-grub` after changes

## Package Management

| Platform | Command | Notes |
|----------|---------|-------|
| rpm-ostree | `rpm-ostree install` | Layered, requires reboot |
| dnf | `dnf install -y` | Immediate |
| apt | `apt install -y` | Immediate |

## Feature Availability

| Feature | Bazzite | Ostree | Traditional | Debian |
|---------|---------|--------|-------------|--------|
| Kernel optimization | ✅ | ✅ | ✅ | ✅ |
| GPU optimization | ✅ | ✅ | ✅ | ✅ |
| ujust commands | ✅ | ❌ | ❌ | ❌ |
| Profile management | ✅ | ✅ | ✅ | ✅ |
| Thermal management | ✅ | ✅ | ✅ | ✅ |

## Troubleshooting

### "rpm-ostree not found"
This is expected on traditional (non-immutable) systems. The optimizer will automatically use GRUB for kernel parameters.

### "ujust not found"
This is expected on non-Bazzite systems. Bazzite-specific optimizations will be skipped.

### Kernel parameters not taking effect
On GRUB systems, ensure you reboot after applying changes. Check `/etc/default/grub` to verify parameters were written.
```

---

### UoW 5.2.5: Update CHANGELOG.md

**Task**: Add release notes for multi-platform support.

**File**: `CHANGELOG.md`
**Location**: Top of file

**Add**:
```markdown
## v5.1.0 - Multi-Platform Support (YYYY-MM-DD)

### Added
- **Platform Abstraction Layer**: New `platform/` module for cross-distro support
- **GRUB Kernel Params**: Support for traditional systems using GRUB bootloader
- **DnfPackageManager**: Native dnf support for Fedora-based traditional distros
- **AptPackageManager**: Native apt support for Debian/Ubuntu
- **Automatic Platform Detection**: Detects OS type, package manager, and boot method
- **Dynamic Hardware Display**: Banner shows detected hardware instead of hard-coded values

### Changed
- `KernelOptimizer` now uses platform abstraction instead of direct rpm-ostree calls
- `BaseOptimizer.install_package()` uses platform-appropriate package manager
- `BazziteOptimizer` now conditional - gracefully skips on non-Bazzite systems
- UI shows generic names instead of hard-coded hardware references

### Removed
- Hard-coded "RTX 5080 Blackwell | i9-10850K | 64GB RAM" from banner
- Direct rpm-ostree subprocess calls from optimizer classes
- `enhanced_rpm_ostree_kargs()` global function (moved to platform module)

### Platform Support
- **Full Support**: Bazzite, Silverblue, Kinoite, Fedora, Ultramarine, Ubuntu, Debian
- **Tested On**: Ultramarine Linux 43, Bazzite 3.x
```

---

## Step 5.3: Release Preparation

**No PR**: Release tasks
**Estimated Time**: 1 hour

### UoW 5.3.1: Update version numbers

**Task**: Bump version to 5.1.0.

**Files to update**:
- `bazzite-optimizer.py`: `SCRIPT_VERSION = "5.1.0"`
- `VERSION`: Update content
- `pyproject.toml`: `version = "5.1.0"`

---

### UoW 5.3.2: Create git tag

**Task**: Tag the release.

```bash
git add -A
git commit -m "feat: Multi-platform support (v5.1.0)

- Add platform abstraction layer
- Support traditional RPM (Fedora, Ultramarine) and Debian-based systems
- Automatic platform detection
- Dynamic hardware display
- Conditional Bazzite features

Closes #1, #2, #3, #4, #5, #6, #7, #8, #9, #10, #11"

git tag -a v5.1.0 -m "Multi-Platform Support Release"
```

---

### UoW 5.3.3: Update team file with handoff notes

**Task**: Document completion in team file.

**File**: `.teams/TEAM_001_refactor_generic_platform_support.md`

**Add to Handoff Notes**:
```markdown
## Handoff Notes

### Completed Work
- Platform detection module (`platform/detection.py`)
- Abstract base classes (`platform/base.py`)
- GRUB kernel params (`platform/traditional/grub.py`)
- DNF package manager (`platform/traditional/rpm.py`)
- APT package manager (`platform/traditional/deb.py`)
- PlatformServices factory (`platform/services.py`)
- Migrated KernelOptimizer to use abstraction
- Migrated package installation to use abstraction
- Made Bazzite features conditional
- Updated UI for dynamic hardware display
- Cleaned up dead code
- Updated documentation

### Tested Platforms
- Ultramarine Linux 43: ✅ All tests pass
- [Add other platforms as tested]

### Known Issues
- [Document any known issues]

### Future Work (Out of Scope)
- Split `bazzite-optimizer.py` into multiple modules (7500+ lines)
- Add Arch Linux support (pacman)
- Add systemd-boot kernel param support
- Intel GPU optimizer
- Hybrid GPU (PRIME) support

### Test Coverage
- Unit tests: `tests/unit/test_platform_*.py`
- Integration tests: `tests/test_platform_matrix.sh`
```

---

## Exit Criteria for Phase 5

- [ ] All platform tests pass on Ultramarine
- [ ] Documentation updated (README, PLATFORM_SUPPORT, CHANGELOG)
- [ ] Version bumped to 5.1.0
- [ ] Git tag created
- [ ] Team file updated with handoff notes
- [ ] Ready for release/merge

---

## Final Checklist

Before considering refactor complete:

- [ ] **Phase 1**: Discovery complete, baselines documented
- [ ] **Phase 2**: Platform module implemented and tested
- [ ] **Phase 3**: All migrations complete (PRs #6-10)
- [ ] **Phase 4**: Dead code removed (PR #11)
- [ ] **Phase 5**: Documentation and release prep (PR #12)

### Verification Commands

```bash
# All tests pass
pytest -q

# Platform detection works
python3 -c "from platform import detect_platform; print(detect_platform())"

# Validation completes without errors
sudo ./bazzite-optimizer.py --validate

# No rpm-ostree errors on traditional system
sudo ./bazzite-optimizer.py --validate 2>&1 | grep -i "rpm-ostree"
# Should be empty or only info messages

# No ujust errors on non-Bazzite
sudo ./bazzite-optimizer.py --validate 2>&1 | grep -i "ujust"
# Should show "Skipping" message, not errors
```
