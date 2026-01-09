# Phase 2: Root Cause Analysis

## Bug 1: Alder Lake Hybrid CPU Core Mapping

### Root Cause
**Location**: `bazzite-optimizer.py` line ~5195 in `KernelOptimizer.apply_bazzite_kernel_params()`

```python
if profile_settings.get("isolate_cores", False):
    isolcpus = "nohz_full=4-9 isolcpus=4-9 rcu_nocbs=4-9"
```

**Problem**: Hardcoded `4-9` assumes:
- Desktop CPU with 10+ cores
- No hybrid architecture
- Cores 0-3 for system, 4-9 for isolation

**Reality for Alder Lake**:
- Hybrid P-core + E-core architecture
- E-cores should be isolated (they're efficiency, not performance)
- Core numbering varies by CPU model

### Evidence
```bash
$ lscpu
CPU(s):              16
Thread(s) per core:  2
Core(s) per socket:  12
# This is 4 P-cores (8 threads) + 8 E-cores (8 threads)
```

### Fix Location
Need to add CPU topology detection in `platforms/detection.py`

---

## Bug 2: Missing eGPU Thunderbolt Kernel Params

### Root Cause
**Location**: `bazzite-optimizer.py` `KernelOptimizer.apply_bazzite_kernel_params()`

**Problem**: Kernel params list doesn't include Thunderbolt/eGPU specific tuning:
```python
kernel_params = [
    # ... existing params
    # MISSING: pcie_port_pm=off
    # MISSING: thunderbolt.force_power=1
]
```

**Why needed**:
- `pcie_port_pm=off`: Prevents PCIe power management from disrupting eGPU
- `thunderbolt.force_power=1`: Keeps Thunderbolt controller active
- eGPUs are on external PCIe via Thunderbolt, need stable power

### Evidence
eGPU already detected (TEAM_009):
```python
GPUInfo(is_egpu=True, vendor="nvidia", ...)
```

But no conditional kernel params for eGPU.

### Fix Location
Add eGPU detection check and conditional params in `KernelOptimizer`

---

## Bug 3: Missing CLI for Kernel Profile Management

### Root Cause
**Location**: `bazzite-optimizer.py` `main()` argument parsing

**Problem**: TEAM_011 added these methods to `GrubKernelParams`:
- `save_baseline()`
- `apply_profile(name)`
- `list_profiles()`
- `diff_profile(name)`
- `restore_baseline()`

But no CLI arguments to invoke them.

### Evidence
```python
# Current args (line ~7493):
parser.add_argument('--profile', ...)
parser.add_argument('--validate', ...)
parser.add_argument('--rollback', ...)
# MISSING: --save-baseline
# MISSING: --kernel-profile
# MISSING: --list-kernel-profiles
```

### Fix Location
Add new CLI arguments in `main()` and wire to `GrubKernelParams` methods

---

## Hypotheses Summary

| Bug | Hypothesis | Confidence | Status |
|-----|------------|------------|--------|
| 1 | Hardcoded core ranges ignore CPU topology | High | Confirmed |
| 2 | No eGPU-aware kernel params | High | Confirmed |
| 3 | Missing CLI wiring for profile methods | High | Confirmed |

---

## Investigation Complete

All three root causes are confirmed and located. Ready for Phase 3.
