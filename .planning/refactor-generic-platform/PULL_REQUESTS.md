## PR #1: Add platforms detection module

**Branch**: `feature/platforms-detection`
**Issues**: #1, #2
**Dependencies**: None (can be merged first)
**Size**: ~400 lines

### Description

Add a new `platforms/` module with OS detection, platform type enumeration, and abstract base classes for platform operations.

### Files Added

```
platforms/
├── __init__.py
├── detection.py      # PlatformType enum, PlatformInfo dataclass, detect_platform()
└── base.py           # PackageManager ABC, KernelParamManager ABC

tests/unit/
└── test_platform_detection.py
```

### Key Changes

- `PlatformType` enum: `BAZZITE`, `FEDORA_OSTREE`, `FEDORA_TRADITIONAL`, `UNKNOWN`
- `PlatformInfo` dataclass with: `platform_type`, `distro_name`, `distro_version`, `is_immutable`, `has_ujust`, `package_manager`, `boot_method`
- `detect_platform()` function that parses `/etc/os-release` and checks for rpm-ostree
- Abstract `PackageManager` and `KernelParamManager` base classes

### Testing

```bash
pytest tests/unit/test_platform_detection.py -v
```

### Merge Criteria

- [ ] All new tests pass
- [ ] Existing tests unaffected
- [ ] Works on Bazzite, Fedora (manual verification)

---

## PR #2: Implement rpm-ostree kernel parameter manager

**Branch**: `feature/rpm-ostree-kernel-params`
**Issues**: #4
**Dependencies**: PR #1 merged
**Size**: ~300 lines

### Description

Extract existing rpm-ostree kargs handling into a dedicated class implementing `KernelParamManager`. No changes to existing optimizer behavior yet.

### Files Added/Modified

```
platforms/
└── immutable/
    ├── __init__.py
    └── rpm_ostree.py   # RpmOstreeKernelParams class

tests/unit/
└── test_rpm_ostree_kernel_params.py
```

### Key Changes

- `RpmOstreeKernelParams` implementing `KernelParamManager`
- Migrated logic from `KernelOptimizer` (copy, not move - coexistence)
- Transaction handling and daemon readiness checks
- Parsing rpm-ostree kargs output

### Testing

```bash
pytest tests/unit/test_rpm_ostree_kernel_params.py -v
```

### Merge Criteria

- [ ] All new tests pass
- [ ] No changes to existing optimizer behavior
- [ ] Manual test on rpm-ostree system (Bazzite/Silverblue)

---

## PR #3: Implement GRUB kernel parameter manager

**Branch**: `feature/grub-kernel-params`
**Issues**: #5
**Dependencies**: PR #1 merged
**Size**: ~350 lines

### Description

Add kernel parameter management for traditional systems using GRUB bootloader.

### Files Added

```
platforms/
└── traditional/
    ├── __init__.py
    └── grub.py         # GrubKernelParams class

tests/unit/
└── test_grub_kernel_params.py
```

### Key Changes

- `GrubKernelParams` implementing `KernelParamManager`
- Parse `GRUB_CMDLINE_LINUX` from `/etc/default/grub`
- Safe modification with backup (timestamped)
- Run `grub2-mkconfig`, `update-grub`, or `grub-mkconfig` after changes
- Handle EFI vs BIOS paths
- Parameter deduplication (match rpm-ostree behavior)

### Testing

```bash
pytest tests/unit/test_grub_kernel_params.py -v
# Manual test on traditional Fedora
```

### Merge Criteria

- [ ] All new tests pass
- [ ] Manual test on grub-based system
- [ ] Backup/restore works correctly

---

## PR #4: Implement package managers (rpm-ostree, dnf)

**Branch**: `feature/package-managers`
**Issues**: #6, #7
**Dependencies**: PR #1 merged
**Size**: ~300 lines

> **Note**: AptPackageManager (Issue #8) deferred to stretch goals.

### Description

Add `PackageManager` implementations for RPM-based package managers.

### Files Added/Modified

```
platforms/
├── immutable/
    └── rpm_ostree.py   # Add RpmOstreePackageManager
└── traditional/
    └── rpm.py          # DnfPackageManager

tests/unit/
├── test_rpm_ostree_package_manager.py
└── test_dnf_package_manager.py
```

### Key Changes

- `RpmOstreePackageManager`: `rpm-ostree install/uninstall`
- `DnfPackageManager`: `dnf install/remove`

### Testing

```bash
pytest tests/unit/test_*_package_manager.py -v
```

### Merge Criteria

- [ ] All new tests pass
- [ ] Manual test on each platform type

---

## PR #5: Add PlatformServices factory

**Branch**: `feature/platforms-services`
**Issues**: #9
**Dependencies**: PR #1, #2, #3, #4 merged
**Size**: ~150 lines

### Description

Create factory class that provides correct platform-specific implementations based on detected platforms.

### Files Added

```
platforms/
└── services.py         # PlatformServices factory class

tests/unit/
└── test_platform_services.py
```

### Key Changes

- `PlatformServices` class with lazy-loaded properties
- `package_manager` property → correct `PackageManager` impl
- `kernel_params` property → correct `KernelParamManager` impl
- `UnsupportedPlatformError` exception

### Testing

```bash
pytest tests/unit/test_platform_services.py -v
```

### Merge Criteria

- [ ] Factory returns correct implementations per platform
- [ ] All tests pass

---

## PR #6: Migrate KernelOptimizer to platforms abstraction

**Branch**: `feature/migrate-kernel-optimizer`
**Issues**: #10
**Dependencies**: PR #5 merged
**Size**: ~200 lines changed

### Description

Update `KernelOptimizer` to use `PlatformServices.kernel_params` instead of direct rpm-ostree calls.

### Files Modified

```
bazzite-optimizer.py   # KernelOptimizer class
```

### Key Changes

- `KernelOptimizer.__init__()` accepts optional `PlatformServices`
- Replace `_get_current_kernel_params()` internals with `kernel_params.get_current_params()`
- Replace `_apply_kernel_param_batch()` internals with `kernel_params.append_params()`
- Replace `_remove_kernel_params()` internals with `kernel_params.remove_params()`
- Keep method signatures unchanged for backward compatibility

### Testing

```bash
pytest tests/test_bazzite_optimizer_enhanced_kargs.py -v
pytest tests/unit/test_optimizers.py -v
# Manual test on both rpm-ostree and grub systems
```

### Merge Criteria

- [ ] All existing kernel param tests pass
- [ ] Works on Bazzite (rpm-ostree)
- [ ] Works on Fedora/Ultramarine (grub)
- [ ] No regression in functionality

---

## PR #7: Migrate package installation to platforms abstraction

**Branch**: `feature/migrate-package-install`
**Issues**: #11
**Dependencies**: PR #5 merged
**Size**: ~150 lines changed

### Description

Update all package installation code to use `PlatformServices.package_manager`.

### Files Modified

```
bazzite-optimizer.py   # BaseOptimizer, NvidiaOptimizer, GamingToolsOptimizer
```

### Key Changes

- `BaseOptimizer.install_package()` uses `package_manager.install()`
- `NvidiaOptimizer._install_nvidia_drivers()` uses abstraction
- `GamingToolsOptimizer` package installs use abstraction
- Remove direct rpm-ostree/dnf subprocess calls

### Testing

```bash
pytest tests/unit/test_optimizers.py -v
# Manual test package installation on each platform
```

### Merge Criteria

- [ ] All tests pass
- [ ] Package installation works on rpm-ostree and dnf systems

---

## PR #8: Make Bazzite features conditional

**Branch**: `feature/conditional-bazzite`
**Issues**: #12
**Dependencies**: PR #5 merged
**Size**: ~50 lines changed

### Description

Update `BazziteOptimizer` to only run ujust commands when on Bazzite.

### Files Modified

```
bazzite-optimizer.py   # BazziteOptimizer class
```

### Key Changes

- Check `platform_info.has_ujust` before running ujust commands
- Log info message when skipping: "Skipping Bazzite-specific optimizations (not on Bazzite)"
- `apply_optimizations()` returns `True` even when skipped
- `validate()` returns empty dict when not on Bazzite

### Testing

```bash
# On non-Bazzite system:
sudo ./bazzite-optimizer.py --validate
# Should complete without errors, show skip message
```

### Merge Criteria

- [ ] No errors on non-Bazzite systems
- [ ] Full functionality on Bazzite
- [ ] Skip message logged appropriately

---

## PR #9: Dynamic hardware display in UI & Cleanup

**Branch**: `feature/dynamic-hardware-ui`
**Issues**: #13
**Dependencies**: None (can be merged anytime)
**Size**: ~150 lines changed

### Description

Replace hard-coded hardware references with dynamic detection and clean up legacy strings.

### Files Modified

```
bazzite-optimizer.py   # BazziteGamingOptimizer.print_banner(), initialize_optimizers()
```

### Key Changes

- Dynamic banner based on `system_info`
- Generic or dynamic optimizer names
- Remove all 30+ RTX 5080/i9-10850K hard-coded strings

### Testing

```bash
sudo ./bazzite-optimizer.py --validate
# Verify banner shows actual hardware
# Verify no hard-coded models in logs
```

### Merge Criteria

- [ ] No hard-coded GPU/CPU model names in user-visible output
- [ ] Correct hardware displayed on various systems
- [ ] Codebase free of hard-coded RTX 5080 references

---

## PR #10: Wire up PlatformServices to main optimizer

**Branch**: `feature/integrate-platforms-services`
**Issues**: Part of #10, #11
**Dependencies**: PR #6, #7, #8 merged
**Size**: ~100 lines changed

### Description

Integrate `PlatformServices` into the main `BazziteGamingOptimizer` orchestrator.

### Files Modified

```
bazzite-optimizer.py   # BazziteGamingOptimizer class
```

### Key Changes

- Add `platform_info` and `platform_services` in `__init__()`
- Pass `platform_services` to optimizers during `initialize_optimizers()`
- Use platform info in `check_prerequisites()` instead of `bazzite_os` check

### Testing

```bash
pytest -q
sudo ./bazzite-optimizer.py --validate
```

### Merge Criteria

- [ ] Full integration working
- [ ] All tests pass
- [ ] Works on all supported platforms

---

## PR #11: Remove dead code and address distribution support

**Branch**: `feature/cleanup-dead-code`
**Issues**: #14
**Dependencies**: PR #10 merged, validated on all platforms
**Size**: ~250 lines removed

### Description

Remove code that is no longer needed after migration and cleanup distribution-specific files.

### Files Modified

```
bazzite-optimizer.py
# platform_support/ubuntu_debian.py (DELETE) - DEFERRED
```

### Key Changes

- Remove `enhanced_rpm_ostree_kargs()` global function
- Remove `_ensure_rpm_ostree_ready()` from KernelOptimizer
- Remove `_wait_for_rpm_ostree_transaction()` from KernelOptimizer
- Remove legacy dnf fallback in `install_package()`
- ~~Remove `platform_support/ubuntu_debian.py`~~ (deferred - Debian support in stretch goals)

### Testing

```bash
pytest -q
# Full regression test on all platforms
```

### Merge Criteria

- [ ] All tests pass
- [ ] No functionality lost
- [ ] Works on all platforms

---

## PR #12: Update documentation for multi-platforms support

**Branch**: `docs/multi-platforms-support`
**Issues**: #17
**Dependencies**: PR #10 merged (feature complete)
**Size**: ~500 lines docs

### Description

Update all documentation to reflect multi-platforms support.

### Files Modified/Added

```
README.md                           # Update badges, add platform section
docs/PLATFORM_SUPPORT.md            # NEW: Detailed platforms matrix
docs/INSTALLATION_GUIDE.md          # Update with per-platforms instructions
```

### Key Changes

- Update "Platform" badge to show multi-platforms
- Add "Supported Platforms" section to README
- Create `PLATFORM_SUPPORT.md` with detailed matrix
- Platforms-specific installation instructions
- Update TODO.md with deferred items (systemd-boot, Arch, etc.)

### Merge Criteria

- [ ] Documentation accurate for all platforms
- [ ] Installation instructions tested
- [ ] Global TODO list updated

---

## PR #13: Add Intel GPU support (optional)

**Branch**: `feature/intel-gpu-support`
**Issues**: #19
**Dependencies**: None (standalone feature)
**Size**: ~300 lines

### Description

Add detection and basic optimization for Intel integrated GPUs.

### Files Added

```
platform_support/intel_gpu.py       # IntelGpuOptimizer class

tests/unit/
└── test_intel_gpu_optimizer.py
```

### Key Changes

- Detect Intel GPU via lspci/sysfs
- Basic i915 module options
- Power management settings
- GuC/HuC firmware options

### Merge Criteria

- [ ] Intel GPU detected correctly
- [ ] No interference with discrete GPU
- [ ] Tests pass

---

## PR #14: Add hybrid GPU (PRIME) support (optional)

**Branch**: `feature/hybrid-gpu-support`
**Issues**: #20
**Dependencies**: PR #13 merged (Intel GPU support)
**Size**: ~400 lines

### Description

Support systems with both integrated and discrete GPUs.

### Files Added/Modified

```
platform_support/hybrid_gpu.py      # HybridGpuManager class
bazzite-optimizer.py                # Integration

tests/unit/
└── test_hybrid_gpu.py
```

### Key Changes

- Detect hybrid GPU configuration
- PRIME render offload support
- nvidia-prime switching
- Profile-aware GPU selection

### Merge Criteria

- [ ] Hybrid GPU detected correctly
- [ ] PRIME offload works
- [ ] Battery profile uses iGPU

---

## PR Merge Order

```
Independent (can merge anytime):
├── PR #9  (dynamic hardware UI)

Sequential dependency chain:
├── PR #1  (platform detection) ─────────────────────────┐
├── PR #2  (rpm-ostree kernel) ──────────┐               │
├── PR #3  (grub kernel) ────────────────┤               │
├── PR #4  (package managers) ───────────┤               │
│                                        ▼               │
├── PR #5  (platform services) ◄─────────┴───────────────┘
│                                        │
├── PR #6  (migrate kernel optimizer) ◄──┤
├── PR #7  (migrate package install) ◄───┤
├── PR #8  (conditional bazzite) ◄───────┤
│                                        │
├── PR #10 (integrate platform services) ◄───────────────┘
│
├── PR #11 (cleanup dead code)
├── PR #12 (documentation)

Optional features (independent):
├── PR #13 (Intel GPU)
└── PR #14 (hybrid GPU) ← requires PR #13
```

---

## MVP for Traditional Fedora Support

**Minimum PRs needed**: #1, #3, #4, #5, #6, #7, #8, #9, #10

This gives you:
- Platform detection
- GRUB kernel params
- dnf package manager
- All migrations complete
- Dynamic hardware UI
- Works on Ultramarine/Fedora Workstation

---

## Quick Reference

| PR | Title | Dependencies | Size |
|----|-------|--------------|------|
| #1 | Platform detection | None | ~400 |
| #2 | rpm-ostree kernel params | #1 | ~300 |
| #3 | GRUB kernel params | #1 | ~350 |
| #4 | Package managers (rpm-ostree, dnf) | #1 | ~300 |
| #5 | PlatformServices factory | #1-4 | ~150 |
| #6 | Migrate KernelOptimizer | #5 | ~200 |
| #7 | Migrate package install | #5 | ~150 |
| #8 | Conditional Bazzite | #5 | ~50 |
| #9 | Dynamic hardware UI | None | ~100 |
| #10 | Integrate PlatformServices | #6-8 | ~100 |
| #11 | Cleanup dead code | #10 | ~200 |
| #12 | Documentation | #10 | ~500 |
| #13 | Intel GPU (optional) | None | ~300 |
| #14 | Hybrid GPU (optional) | #13 | ~400 |
