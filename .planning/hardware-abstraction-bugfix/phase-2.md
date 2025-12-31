# Phase 2: Root Cause Analysis

**Bug**: Hardware Abstraction Failures (CPU/Memory/Network)
**Team**: TEAM_015
**Status**: Ready for execution

## Root Cause Summary

The root cause is identical across all three bugs: **hard-coded hardware values in embedded scripts and optimizer classes** that were written for the original developer's system and never abstracted.

This is the same pattern found and fixed for GPU (TEAM_013 fixed RTX 5080 → dynamic detection).

## Hypotheses

### H1: Missing Detection Layer (CONFIRMED)
- **Evidence**: `platforms/detection.py` has GPU detection but no CPU model detection or NIC detection
- **Confidence**: HIGH
- The detection layer exists for platform and GPU, but CPU/NIC detection was never implemented

### H2: Embedded Scripts Bypass Detection (CONFIRMED)
- **Evidence**: Shell scripts like `CPU_OPTIMIZATION_SCRIPT` have hard-coded values that don't use any detection
- **Confidence**: HIGH
- Even if detection existed, the embedded scripts wouldn't use it

### H3: Optimizer Classes Don't Query Hardware (CONFIRMED)
- **Evidence**: `CPUOptimizer`, `MemoryOptimizer`, `NetworkOptimizer` don't call any detection functions
- **Confidence**: HIGH
- Unlike `NvidiaOptimizer` (now fixed), these classes have no hardware capability properties

## Key Code Areas

### CPU Optimizer Flow
```
CPUOptimizer.apply_optimizations()
  → Logs "Applying Intel i9-10850K optimizations"
  → Writes CPU_OPTIMIZATION_SCRIPT (hard-coded undervolt values)
  → Writes UNDERVOLT_CONFIG (hard-coded i9-10850K values)
  → No detection of actual CPU
```

### Memory Optimizer Flow
```
MemoryOptimizer.configure_zram()
  → Logs "Configuring ZRAM for 64GB system"
  → Writes ZRAM_CONFIG with hard-coded 64GB assumptions
  → SYSCTL_CONFIG has 64GB-specific values
  → No check of actual RAM size
```

### Network Optimizer Flow
```
NetworkOptimizer.apply_optimizations()
  → Logs "Applying Intel I225-V network optimizations"
  → Writes IGC_MODULE_CONFIG (I225-V specific options)
  → Writes ETHERNET_OPTIMIZE_SCRIPT (I225-V specific fixes)
  → Only checks if Intel NIC exists, not which model
```

## Investigation Results

### CPU: Which values are hardware-specific?

| Setting | Hardware-Specific? | Notes |
|---------|-------------------|-------|
| Undervolt values | YES - CRITICAL | Wrong values cause instability/crashes |
| Governor settings | NO | Generic across Intel CPUs |
| C-state limits | PARTIAL | Safe to use conservative defaults |
| Core isolation | PARTIAL | Depends on core count |

**Recommendation**: Skip undervolt for unknown CPUs, use generic governor/c-state

### Memory: Which values are hardware-specific?

| Setting | Hardware-Specific? | Notes |
|---------|-------------------|-------|
| ZRAM size | YES | Should be fraction of actual RAM |
| vm.swappiness | NO | Can be generic |
| vm.dirty_ratio | PARTIAL | Should scale with RAM |
| Huge pages | NO | Generic optimization |

**Recommendation**: Calculate ZRAM as `min(RAM/4, 16GB)`, scale dirty_ratio

### Network: Which values are hardware-specific?

| Setting | Hardware-Specific? | Notes |
|---------|-------------------|-------|
| igc module options | YES | Only for I225-V/I226 |
| EEE disable | PARTIAL | I225-V has known EEE bugs |
| Ring buffer sizes | NO | Generic for most NICs |
| Interrupt coalescing | PARTIAL | Driver-dependent |

**Recommendation**: Detect NIC driver, only apply igc options if igc driver

## Validated Root Causes

1. **CPU**: `CPUOptimizer` applies i9-10850K undervolt values without detecting CPU model
2. **Memory**: `MemoryOptimizer` assumes 64GB RAM without checking `system_info["ram_gb"]`
3. **Network**: `NetworkOptimizer` applies I225-V fixes without checking NIC model/driver

## Fix Strategy Preview

Follow the TEAM_013 pattern for GPU:
1. Add detection functions to `platforms/detection.py`
2. Add capability properties to optimizer classes
3. Replace hard-coded values with detected values
4. Use conservative defaults for unknown hardware

---

## Next Phase

Proceed to **Phase 3: Fix Design and Validation Plan** to define the exact implementation approach.
