# Phase 1: Understanding and Scoping

## Bug Summary

### Bug 1: Alder Lake Hybrid CPU Core Mapping
- **Severity**: High — Wrong core isolation can hurt performance
- **Description**: Optimizer hardcodes `isolcpus=4-9` which targets P-cores instead of E-cores on hybrid CPUs
- **Impact**: Gaming performance degradation, wrong cores isolated

### Bug 2: Missing eGPU Thunderbolt Kernel Params
- **Severity**: Medium — eGPU stability issues possible
- **Description**: No Thunderbolt-specific kernel params for eGPU setups
- **Impact**: Potential eGPU disconnects, PCIe power management issues

### Bug 3: Missing CLI for Kernel Profile Management
- **Severity**: Low — Feature gap, not a crash
- **Description**: Kernel profile methods exist but no CLI interface
- **Impact**: Users can't easily switch between stock and optimized params

---

## Reproduction Status

### Bug 1: Alder Lake CPU
**Reproducible**: Yes

**Current hardcoded values** (bazzite-optimizer.py):
```python
if profile_settings.get("isolate_cores", False):
    isolcpus = "nohz_full=4-9 isolcpus=4-9 rcu_nocbs=4-9"
```

**User's actual CPU topology**:
```
Intel i5-1240P:
- CPUs 0-7:  P-cores (4 physical, 8 threads) — SHOULD NOT BE ISOLATED
- CPUs 8-15: E-cores (8 physical, 8 threads) — SHOULD BE ISOLATED
```

**Expected**: `isolcpus=8-15` (E-cores)
**Actual**: `isolcpus=4-9` (mix of P and E cores)

### Bug 2: eGPU Thunderbolt
**Reproducible**: N/A — Missing feature

**Missing params for eGPU stability**:
```
pcie_port_pm=off           # Disable PCIe power management
thunderbolt.force_power=1  # Keep Thunderbolt controller powered
pci=noaer                  # Optional: reduce PCIe error reporting noise
```

### Bug 3: CLI Commands
**Reproducible**: Yes — Commands don't exist

---

## Context

### Code Areas Affected

| File | Component | Issue |
|------|-----------|-------|
| `bazzite-optimizer.py` | `KernelOptimizer.apply_bazzite_kernel_params()` | Hardcoded core ranges |
| `platforms/detection.py` | Missing | No CPU topology detection |
| `platforms/traditional/grub.py` | Profile methods | No CLI exposure |
| `bazzite-optimizer.py` | `main()` arg parsing | No profile CLI args |

### Recent Changes
- TEAM_009: Added eGPU detection (GPUInfo, detect_gpus)
- TEAM_011: Added kernel profile management methods to GrubKernelParams

---

## Constraints

1. **Backwards compatibility**: Must not break existing Bazzite/rpm-ostree systems
2. **Platform awareness**: Detection must work on both GRUB and rpm-ostree
3. **Safe defaults**: If detection fails, use conservative settings

---

## Open Questions

1. **Q1**: Should E-core isolation be optional or always-on for hybrid CPUs?
   - **Recommendation**: Optional, controlled by profile

2. **Q2**: Should eGPU params be auto-detected or user-enabled?
   - **Recommendation**: Auto-detect via Thunderbolt + discrete GPU

3. **Q3**: What should happen if CPU topology detection fails?
   - **Recommendation**: Skip core isolation, log warning

---

## Exit Criteria
- [x] All three bugs documented
- [x] Reproduction confirmed
- [x] Code areas identified
- [x] Constraints documented
- [ ] Ready for Phase 2
