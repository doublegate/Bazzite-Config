# GitHub Issues: Generic Platform Support Refactor

This file contains all GitHub issues needed to implement multi-platform support.
Copy each issue into GitHub Issues with the appropriate labels.

---

## Epic: Multi-Platform Support

**Labels**: `epic`, `enhancement`, `platform-support`

### Description

Transform bazzite-optimizer from a Bazzite-specific tool into a generic Linux gaming optimizer supporting:
- rpm-ostree immutable systems (Bazzite, Silverblue, Kinoite, Aurora)
- Traditional RPM-based systems (Fedora Workstation, Ultramarine, etc.)
- Debian-based systems (Ubuntu, Debian, Pop!_OS)

**Primary target**: Bazzite (maintain full compatibility)
**Secondary target**: Traditional Fedora-based distros with hybrid GPU configurations

---

## Phase 1: Foundation

### Issue #1: Create platform detection module

**Labels**: `enhancement`, `platform-support`, `priority-high`

**Description**:
Create a platform detection system that identifies:
- OS distribution and version
- Whether system is rpm-ostree based (immutable) or traditional
- Available package manager (rpm-ostree, dnf, apt)
- Boot configuration method (rpm-ostree kargs, grub, systemd-boot)
- Bazzite-specific features availability (ujust)

**Acceptance Criteria**:
- [ ] `PlatformType` enum with values: `BAZZITE`, `FEDORA_OSTREE`, `FEDORA_TRADITIONAL`, `DEBIAN_BASED`, `UNKNOWN`
- [ ] `PlatformInfo` dataclass with all platform metadata
- [ ] `detect_platform()` function that returns `PlatformInfo`
- [ ] Unit tests for each platform type
- [ ] Works correctly on Bazzite, Fedora, and Ubuntu

**Files to create**:
- `platform/__init__.py`
- `platform/detection.py`
- `tests/unit/test_platform_detection.py`

---

### Issue #2: Create abstract base classes for platform operations

**Labels**: `enhancement`, `platform-support`, `priority-high`

**Description**:
Define abstract interfaces for platform-specific operations to enable consistent API across all supported platforms.

**Acceptance Criteria**:
- [ ] `PackageManager` abstract base class with methods: `install()`, `remove()`, `is_installed()`, `update()`
- [ ] `KernelParamManager` abstract base class with methods: `get_current_params()`, `append_params()`, `remove_params()`, `replace_param()`, `requires_reboot()`, `get_pending_params()`
- [ ] Type hints for all methods
- [ ] Docstrings documenting expected behavior

**Files to create**:
- `platform/base.py`

---

### Issue #3: Document all rpm-ostree dependencies in codebase

**Labels**: `documentation`, `platform-support`, `priority-medium`

**Description**:
Audit the codebase and document all locations where rpm-ostree is directly called or assumed.

**Acceptance Criteria**:
- [ ] List of all `rpm-ostree kargs` call sites with line numbers
- [ ] List of all `rpm-ostree install` call sites
- [ ] List of all `rpm-ostree status` call sites
- [ ] Documentation of fallback behavior (if any)
- [ ] Identified hard-coded Bazzite assumptions

**Output**: Update `.planning/refactor-generic-platform/phase-1.md` with findings

---

## Phase 2: Platform Implementations

### Issue #4: Implement RpmOstreeKernelParams for immutable systems

**Labels**: `enhancement`, `platform-support`, `priority-high`

**Description**:
Extract existing rpm-ostree kargs handling into a dedicated class implementing `KernelParamManager`.

**Acceptance Criteria**:
- [ ] `RpmOstreeKernelParams` class implementing `KernelParamManager`
- [ ] Migrated logic from `KernelOptimizer._get_current_kernel_params()`
- [ ] Migrated logic from `KernelOptimizer._apply_kernel_param_batch()`
- [ ] Migrated logic from `KernelOptimizer._ensure_rpm_ostree_ready()`
- [ ] Transaction handling and retry logic preserved
- [ ] Unit tests with mocked rpm-ostree calls
- [ ] No regression on Bazzite/Silverblue

**Files to create**:
- `platform/immutable/rpm_ostree.py`
- `tests/unit/test_rpm_ostree_kernel_params.py`

---

### Issue #5: Implement GrubKernelParams for traditional systems

**Labels**: `enhancement`, `platform-support`, `priority-high`

**Description**:
Create kernel parameter management for systems using GRUB bootloader (traditional RPM and Debian-based systems).

**Acceptance Criteria**:
- [ ] `GrubKernelParams` class implementing `KernelParamManager`
- [ ] Parse `GRUB_CMDLINE_LINUX` from `/etc/default/grub`
- [ ] Safely modify grub config with backup
- [ ] Run `grub2-mkconfig` (Fedora) or `update-grub` (Debian) after changes
- [ ] Handle EFI vs BIOS boot paths
- [ ] Kernel parameter deduplication (match rpm-ostree behavior)
- [ ] Unit tests with mocked file operations
- [ ] Integration test on non-rpm-ostree system

**Files to create**:
- `platform/traditional/grub.py`
- `tests/unit/test_grub_kernel_params.py`

**Notes**:
- Must backup `/etc/default/grub` before modification
- Must detect grub config output path (`/boot/grub2/grub.cfg` vs `/boot/efi/EFI/fedora/grub.cfg`)

---

### Issue #6: Implement RpmOstreePackageManager

**Labels**: `enhancement`, `platform-support`, `priority-high`

**Description**:
Extract existing rpm-ostree package installation into a dedicated class implementing `PackageManager`.

**Acceptance Criteria**:
- [ ] `RpmOstreePackageManager` class implementing `PackageManager`
- [ ] Migrated logic from `BaseOptimizer.install_package()`
- [ ] Transaction handling preserved
- [ ] Layered package detection
- [ ] Unit tests with mocked rpm-ostree calls

**Files to create**:
- `platform/immutable/rpm_ostree.py` (extend)
- `tests/unit/test_rpm_ostree_package_manager.py`

---

### Issue #7: Implement DnfPackageManager for traditional RPM systems

**Labels**: `enhancement`, `platform-support`, `priority-high`

**Description**:
Create package management for systems using dnf (Fedora, RHEL, CentOS, Ultramarine).

**Acceptance Criteria**:
- [ ] `DnfPackageManager` class implementing `PackageManager`
- [ ] `install()` using `dnf install -y`
- [ ] `remove()` using `dnf remove -y`
- [ ] `is_installed()` using `rpm -q` or `dnf list installed`
- [ ] `update()` using `dnf upgrade`
- [ ] Proper error handling and timeout support
- [ ] Unit tests

**Files to create**:
- `platform/traditional/rpm.py`
- `tests/unit/test_dnf_package_manager.py`

---

### Issue #8: Refactor AptPackageManager from existing code

**Labels**: `enhancement`, `platform-support`, `priority-medium`

**Description**:
Refactor existing `UbuntuDebianOptimizer` from `platform_support/ubuntu_debian.py` into the new platform abstraction.

**Acceptance Criteria**:
- [ ] `AptPackageManager` class implementing `PackageManager`
- [ ] Migrated logic from `UbuntuDebianOptimizer.install_package()`
- [ ] Migrated logic from `UbuntuDebianOptimizer.update_packages()`
- [ ] PPA management preserved
- [ ] Unit tests

**Files to create/modify**:
- `platform/traditional/deb.py`
- `tests/unit/test_apt_package_manager.py`

---

### Issue #9: Create PlatformServices factory

**Labels**: `enhancement`, `platform-support`, `priority-high`

**Description**:
Create a factory class that provides the correct platform-specific implementations based on detected platform.

**Acceptance Criteria**:
- [ ] `PlatformServices` class with lazy-loaded properties
- [ ] `package_manager` property returning correct `PackageManager` implementation
- [ ] `kernel_params` property returning correct `KernelParamManager` implementation
- [ ] `UnsupportedPlatformError` for unknown platforms
- [ ] Unit tests for factory logic

**Files to create**:
- `platform/services.py`
- `tests/unit/test_platform_services.py`

---

## Phase 3: Migration

### Issue #10: Migrate KernelOptimizer to use platform abstraction

**Labels**: `enhancement`, `platform-support`, `refactor`, `priority-high`

**Description**:
Update `KernelOptimizer` to use `PlatformServices.kernel_params` instead of direct rpm-ostree calls.

**Acceptance Criteria**:
- [ ] `KernelOptimizer.__init__()` accepts `PlatformServices`
- [ ] `apply_kernel_parameters()` uses `kernel_params.append_params()`
- [ ] `_get_current_kernel_params()` uses `kernel_params.get_current_params()`
- [ ] `_remove_kernel_params()` uses `kernel_params.remove_params()`
- [ ] Remove rpm-ostree specific helper methods from `KernelOptimizer`
- [ ] All existing kernel param tests pass
- [ ] Works on both rpm-ostree and grub-based systems

**Files to modify**:
- `bazzite-optimizer.py` (KernelOptimizer class)

---

### Issue #11: Migrate package installation to use platform abstraction

**Labels**: `enhancement`, `platform-support`, `refactor`, `priority-high`

**Description**:
Update all package installation code to use `PlatformServices.package_manager`.

**Acceptance Criteria**:
- [ ] `BaseOptimizer.install_package()` uses `package_manager.install()`
- [ ] `NvidiaOptimizer._install_nvidia_drivers()` uses abstraction
- [ ] `GamingToolsOptimizer` uses abstraction
- [ ] Remove direct rpm-ostree/dnf subprocess calls
- [ ] Works on rpm-ostree, dnf, and apt systems

**Files to modify**:
- `bazzite-optimizer.py` (BaseOptimizer, NvidiaOptimizer, GamingToolsOptimizer)

---

### Issue #12: Make BazziteOptimizer conditional on Bazzite detection

**Labels**: `enhancement`, `platform-support`, `priority-medium`

**Description**:
Update `BazziteOptimizer` to only run ujust commands when on Bazzite, skip gracefully on other platforms.

**Acceptance Criteria**:
- [ ] Check `platform_info.has_ujust` before running ujust commands
- [ ] Log info message when skipping (not error/warning)
- [ ] `apply_optimizations()` returns True even when skipped
- [ ] No errors on non-Bazzite systems
- [ ] Full functionality preserved on Bazzite

**Files to modify**:
- `bazzite-optimizer.py` (BazziteOptimizer class)

---

### Issue #13: Remove hard-coded hardware references from UI

**Labels**: `enhancement`, `ux`, `priority-medium`

**Description**:
Replace all hard-coded hardware references with dynamic detection.

**Current hard-coded values**:
- Banner: "RTX 5080 Blackwell | i9-10850K | 64GB RAM"
- Optimizer names: "NVIDIA RTX 5080 Blackwell", "Intel i9-10850K CPU", "Intel I225-V"

**Acceptance Criteria**:
- [ ] `print_banner()` shows dynamically detected hardware
- [ ] `initialize_optimizers()` uses generic or dynamic names
- [ ] No hard-coded GPU/CPU model names in user-visible output
- [ ] Hardware detection uses existing `system_info` dict

**Files to modify**:
- `bazzite-optimizer.py` (BazziteGamingOptimizer.print_banner, initialize_optimizers)

---

## Phase 4: Cleanup

### Issue #14: Remove dead code and legacy fallbacks

**Labels**: `cleanup`, `tech-debt`, `priority-low`

**Description**:
Remove code that is no longer needed after migration to platform abstraction.

**Acceptance Criteria**:
- [ ] Remove `enhanced_rpm_ostree_kargs()` global function
- [ ] Remove `_ensure_rpm_ostree_ready()` from KernelOptimizer (moved to impl)
- [ ] Remove `_wait_for_rpm_ostree_transaction()` from KernelOptimizer
- [ ] Remove legacy dnf fallback in `install_package()` (now in abstraction)
- [ ] All tests still pass

**Files to modify**:
- `bazzite-optimizer.py`

---

### Issue #15: Move global configs to appropriate classes

**Labels**: `cleanup`, `refactor`, `priority-low`

**Description**:
Improve encapsulation by moving global configuration constants to their relevant classes.

**Items to move**:
- `NVIDIA_MODULE_CONFIG` → `NvidiaOptimizer._MODULE_CONFIG`
- `NVIDIA_XORG_CONFIG` → `NvidiaOptimizer._XORG_CONFIG`
- `NVIDIA_OPTIMIZATION_SCRIPT` → `NvidiaOptimizer._OPTIMIZATION_SCRIPT`

**Acceptance Criteria**:
- [ ] Global configs moved to class constants
- [ ] No functional change
- [ ] All tests pass

---

## Phase 5: Testing & Documentation

### Issue #16: Add integration tests for multi-platform support

**Labels**: `testing`, `platform-support`, `priority-high`

**Description**:
Create integration tests that verify the optimizer works correctly on different platforms.

**Acceptance Criteria**:
- [ ] Test platform detection on mock environments
- [ ] Test kernel param application with mocked system calls
- [ ] Test package installation with mocked system calls
- [ ] Test graceful degradation on unsupported platforms
- [ ] CI matrix for different platform types (if possible)

**Files to create**:
- `tests/integration/test_platform_support.py`

---

### Issue #17: Update documentation for multi-platform support

**Labels**: `documentation`, `priority-medium`

**Description**:
Update all documentation to reflect multi-platform support.

**Acceptance Criteria**:
- [ ] Update README.md with supported platforms list
- [ ] Update README.md with platform-specific installation instructions
- [ ] Create `docs/PLATFORM_SUPPORT.md` with detailed matrix
- [ ] Update "Platform" badge to show multi-platform
- [ ] Add troubleshooting section for platform-specific issues

**Files to modify/create**:
- `README.md`
- `docs/PLATFORM_SUPPORT.md`

---

### Issue #18: Add CONTRIBUTING guide for new platform support

**Labels**: `documentation`, `good-first-issue`, `priority-low`

**Description**:
Document how contributors can add support for new platforms.

**Acceptance Criteria**:
- [ ] Step-by-step guide for adding new platform type
- [ ] Template for new `PackageManager` implementation
- [ ] Template for new `KernelParamManager` implementation
- [ ] Testing requirements for new platforms

**Files to create**:
- `docs/CONTRIBUTING_PLATFORMS.md`

---

## Hardware Support Issues

### Issue #19: Add Intel GPU detection and basic optimization

**Labels**: `enhancement`, `hardware-support`, `priority-medium`

**Description**:
Add detection and basic optimization support for Intel integrated GPUs (Iris Xe, UHD, etc.).

**Acceptance Criteria**:
- [ ] Detect Intel GPU via lspci or sysfs
- [ ] Basic power management settings
- [ ] i915 module options for performance
- [ ] GuC/HuC firmware loading options
- [ ] Works alongside discrete GPU (hybrid setups)

**Files to create/modify**:
- `platform_support/intel_gpu.py` or integrate into existing optimizer

---

### Issue #20: Add hybrid GPU (Optimus/PRIME) support

**Labels**: `enhancement`, `hardware-support`, `priority-medium`

**Description**:
Support systems with both integrated and discrete GPUs (Intel + NVIDIA, AMD + NVIDIA).

**Acceptance Criteria**:
- [ ] Detect hybrid GPU configuration
- [ ] Support PRIME render offload
- [ ] Support nvidia-prime switching
- [ ] Handle power management for both GPUs
- [ ] Profile-aware GPU selection (performance vs battery)

**Notes**:
- Common on laptops
- Secondary target: systems with Intel iGPU + NVIDIA dGPU

---

### Issue #21: Add Intel Alder Lake/Raptor Lake hybrid CPU support

**Labels**: `enhancement`, `hardware-support`, `priority-medium`

**Description**:
Optimize for Intel's hybrid architecture (P-cores + E-cores).

**Acceptance Criteria**:
- [ ] Detect P-core and E-core topology
- [ ] Scheduler hints for gaming workloads (prefer P-cores)
- [ ] `isolcpus` support for E-cores in competitive profile
- [ ] Power management for E-cores
- [ ] Integration with Intel Thread Director

**Notes**:
- Affects 12th, 13th, 14th gen Intel CPUs
- E-cores can cause latency spikes in games if not handled

---

## Labels Reference

| Label | Color | Description |
|-------|-------|-------------|
| `epic` | purple | Large feature spanning multiple issues |
| `enhancement` | blue | New feature or improvement |
| `platform-support` | green | Multi-platform support work |
| `hardware-support` | teal | Hardware-specific features |
| `priority-high` | red | Must have for MVP |
| `priority-medium` | orange | Important but not blocking |
| `priority-low` | yellow | Nice to have |
| `refactor` | gray | Code restructuring |
| `cleanup` | gray | Dead code removal, tech debt |
| `documentation` | light blue | Docs updates |
| `testing` | cyan | Test coverage |
| `good-first-issue` | green | Good for new contributors |
| `tech-debt` | brown | Technical debt |
| `ux` | pink | User experience |

---

## Issue Dependencies

```
#1 (detection) ──┬──> #4 (rpm-ostree kernel)
                 ├──> #5 (grub kernel)
                 ├──> #6 (rpm-ostree pkg)
                 ├──> #7 (dnf pkg)
                 └──> #8 (apt pkg)

#2 (base classes) ──> #4, #5, #6, #7, #8

#4, #5, #6, #7, #8 ──> #9 (factory)

#9 (factory) ──┬──> #10 (migrate kernel)
               ├──> #11 (migrate packages)
               └──> #12 (conditional bazzite)

#10, #11, #12 ──> #14 (cleanup)

#19 (intel gpu) ──> #20 (hybrid gpu)
```

---

## Milestone: v5.1.0 - Multi-Platform Support

**Target Issues**: #1-#14, #16-#17
**Stretch Goals**: #15, #18-#21

**Definition of Done**:
- [ ] Optimizer works on Bazzite (no regression)
- [ ] Optimizer works on Fedora Workstation
- [ ] Optimizer works on Fedora-based distros (Ultramarine, etc.)
- [ ] Optimizer works on Ubuntu
- [ ] All tests pass
- [ ] Documentation updated
