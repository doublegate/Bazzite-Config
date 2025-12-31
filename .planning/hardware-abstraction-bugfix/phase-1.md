# Phase 1: Understanding and Scoping

**Bug**: Hardware Abstraction Failures (CPU/Memory/Network)
**Team**: TEAM_015
**Status**: Ready for execution

## Bug Summary

The optimizer applies hardware-specific optimizations for the developer's system (i9-10850K, 64GB RAM, Intel I225-V NIC) to **all systems** regardless of actual hardware. This is the same class of bug that was fixed for GPU (RTX 5080 → dynamic detection) in TEAM_013.

**Severity**: HIGH - Could cause system instability (wrong undervolt), suboptimal performance (wrong memory settings), or driver errors (wrong NIC options).

## Reproduction Status

**Reproducible**: YES

**Steps**:
1. Run `python3 bazzite-optimizer.py --profile balanced` on any system
2. Observe logs showing "Intel i9-10850K optimizations" regardless of actual CPU
3. Check `/etc/intel-undervolt.conf` - contains i9-10850K-specific undervolt values
4. Check `/etc/modprobe.d/igc-gaming.conf` - contains I225-V-specific options

**Expected**: Optimizations should match detected hardware
**Actual**: Hard-coded hardware names and values applied universally

## Affected Code Areas

### Bug 1: CPU Optimizer (i9-10850K)
| Location | Hard-coded Reference |
|----------|---------------------|
| Line ~477 | `# Intel i9-10850K CPU Optimization` |
| Line ~479 | `# i9-10850K Gaming Optimization v4` |
| Line ~599 | `echo "Intel i9-10850K optimized..."` |
| Line ~665 | `# Intel i9-10850K Conservative Undervolt` |
| Line ~3479 | `class CPUOptimizer` docstring |
| Line ~3513-3514 | `apply_optimizations()` method |

### Bug 2: Memory Optimizer (64GB)
| Location | Hard-coded Reference |
|----------|---------------------|
| Line ~600 | `# 64GB RAM Gaming Optimizations v4` |
| Line ~728 | `# ZRAM Configuration for 64GB Gaming System` |
| Line ~3499 | `configure_zram()` method |

### Bug 3: Network Optimizer (I225-V)
| Location | Hard-coded Reference |
|----------|---------------------|
| Line ~821-822 | `# Intel I225-V Ethernet Module Configuration` |
| Line ~840 | `# Intel I225-V Ethernet Optimization v4` |
| Line ~871-872 | `# Intel I225-V specific fixes` |
| Line ~893 | `echo "Intel I225-V ethernet optimized..."` |
| Line ~1341 | `# Network Optimizations (Intel I225-V)` |
| Line ~2048 | `check for I225-V` |
| Line ~3664-3668 | `NetworkOptimizer` class and methods |

## Constraints

1. **Backwards Compatibility**: Existing users with matching hardware should see no change
2. **Safety**: Conservative defaults for unknown hardware
3. **Detection Accuracy**: Must correctly identify hardware before applying optimizations
4. **Existing Pattern**: Follow the same pattern used for GPU abstraction (TEAM_013)

## Open Questions

1. Should we skip CPU undervolt entirely for unknown CPUs? (Probably yes - safety)
2. What memory settings are truly universal vs RAM-size-specific?
3. Which NIC optimizations are generic vs I225-V-specific?

---

## Step 1: Consolidate Bug Information

**Status**: Complete (above)

## Step 2: Confirm Scope

### Files to Modify
- `bazzite-optimizer.py` - Main optimizer (CPUOptimizer, MemoryOptimizer, NetworkOptimizer)
- `platforms/detection.py` - Add CPU and NIC detection (memory already available via system_info)

### Estimated Work
- CPU abstraction: ~3-4 UoW
- Memory abstraction: ~2 UoW  
- Network abstraction: ~2-3 UoW
- Testing: ~1 UoW

## Step 3: Identify Detection Requirements

### CPU Detection Needs
- CPU model/family (Intel vs AMD vs other)
- CPU generation (for undervolt safety)
- Core count (for isolation)
- Already have: `platforms/detection.py:detect_cpu_topology()` for hybrid CPU support

### Memory Detection Needs
- Total RAM (already in `get_system_info()`)
- Calculate appropriate ZRAM size based on actual RAM

### Network Detection Needs
- NIC vendor/model
- Driver in use (igc, e1000e, r8169, etc.)
- Already have partial: `check_hardware_capabilities()` checks for `has_intel_nic`

---

## Next Phase

Proceed to **Phase 2: Root Cause Analysis** to map the exact code paths and determine which optimizations are truly hardware-specific vs generic.
