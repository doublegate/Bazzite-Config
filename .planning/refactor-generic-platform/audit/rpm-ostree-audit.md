# rpm-ostree Call Sites Audit

**Date**: 2025-12-31
**Auditor Team**: TEAM_004
**Commit**: 889c2fe

## Summary

| File | Match Count | Migration Priority |
|------|-------------|--------------------|
| `bazzite-optimizer.py` | 38 | **High** — Primary target |
| `reset-bazzite-defaults.sh` | 20 | **High** — Reset script |
| `tests/integration/test_profile_workflows.py` | 5 | Medium — Test fixtures |
| `tests/unit/test_base_optimizer.py` | 4 | Medium — Test mocks |
| `tests/test_bazzite_optimizer_enhanced_kargs.py` | 2 | Medium — Test assertions |
| `tests/unit/test_optimizers.py` | 2 | Medium — Test stubs |
| `tools/mcp_quick_queries.sh` | 6 | Low — Dev tooling |

**Total (excluding ref_scripts/)**: ~77 matches across 7 files

## Detailed Call Sites

### bazzite-optimizer.py (38 matches)

| Line | Command Type | Context | Migration Action |
|------|--------------|---------|------------------|
| 481 | `rpm-ostree install` | Embedded shell script (kernel-tools) | Abstract to PackageManager |
| 1577 | Comment | ujust clean-system conflict note | Keep as documentation |
| 2201-2208 | `rpm-ostree kargs`, `rpm-ostree status` | `enhanced_rpm_ostree_kargs()` | Extract to KernelParamManager |
| 2336-2348 | `rpm-ostree install` | `BaseOptimizer._install_package()` | Extract to PackageManager |
| 3050-3061 | `rpm-ostree install` | `NvidiaOptimizer.install_drivers()` | Use PackageManager |
| 4916-4917 | `rpm-ostree kargs` | `KernelOptimizer.apply_bazzite_kernel_params()` | Rename + extract |
| 4963-4964 | `rpm-ostree` | `_ensure_rpm_ostree_ready()` check | Extract to KernelParamManager |
| 5047-5091 | Multiple | `_ensure_rpm_ostree_ready()`, `_wait_for_transaction_completion()` | Extract to RpmOstreeKernelParams |
| 5122-5138 | `rpm-ostree kargs`, `rpm-ostree status` | `_get_current_kernel_params()` | Extract to KernelParamManager |
| 5169-5196 | `rpm-ostree kargs` | `_replace_kernel_params_batch()`, append logic | Extract to KernelParamManager |
| 5368 | Log message | Bazzite detection | Make conditional |
| 5487 | `rpm-ostree kargs` | Delete kargs | Extract to KernelParamManager |
| 6410 | Log message | Dedup explanation | Keep |

### reset-bazzite-defaults.sh (20 matches)

| Line | Command Type | Context | Migration Action |
|------|--------------|---------|------------------|
| 6 | Comment | Script description | Keep |
| 118 | `need_bin rpm-ostree` | Dependency check | Add platform guard |
| 126-127 | `rpm-ostree status` | System validation | Add platform guard |
| 148-149, 182-183 | `rpm-ostree status`, `rpm-ostree kargs` | Diagnostics | Add platform guard |
| 229, 256, 263, 266, 277 | `rpm-ostree kargs` | Kargs deletion | Add platform guard |
| 501, 540, 551, 558, 561, 575 | `rpm-ostree kargs` | More kargs operations | Add platform guard |

**Note**: This script is Bazzite-specific by design. Consider creating a parallel `reset-grub-defaults.sh` for traditional systems.

### tests/ (13 matches total)

Tests reference rpm-ostree in mocks and assertions. These will need updating when the abstraction layer is added to mock the new interfaces instead.

## Key Patterns to Abstract

1. **Kernel param get**: `rpm-ostree kargs` → `KernelParamManager.get_current_params()`
2. **Kernel param set**: `rpm-ostree kargs --append/--replace/--delete` → `KernelParamManager.{append,replace,remove}_params()`
3. **Transaction handling**: `rpm-ostree status --json` → `KernelParamManager._ensure_ready()`
4. **Package install**: `rpm-ostree install` → `PackageManager.install()`

## Impact on Phase 2

- **Step 2.5 (RpmOstreeKernelParams)**: Covers lines 4916-5487 extraction ✓
- **Step 2.4 (Package managers)**: Covers lines 2336-2348, 3050-3061 ✓
- **Missing**: `reset-bazzite-defaults.sh` not mentioned in Phase 2-5

## Recommendations

1. Add UoW to Phase 3 or 4 to create `reset-grub-defaults.sh` or make existing script platform-aware
2. Update test mocks in Phase 5 after abstraction is complete
