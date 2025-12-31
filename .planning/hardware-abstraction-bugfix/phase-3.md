# Phase 3: Fix Design and Validation Plan

**Bug**: Hardware Abstraction Failures (CPU/Memory/Network)
**Team**: TEAM_015
**Status**: Ready for execution

## Root Cause Summary

Hard-coded hardware values (i9-10850K, 64GB, I225-V) in optimizer classes and embedded scripts are applied universally without detecting actual hardware.

## Fix Strategy

Follow the proven TEAM_013 pattern used for GPU abstraction:

### Pattern Applied
1. **Add detection** → `platforms/detection.py`
2. **Add capability dataclass** → Store detected values
3. **Add lazy property** → Optimizer class loads capabilities on demand
4. **Replace hard-coded values** → Use detected values or safe defaults
5. **Update logging** → Show actual hardware in messages

---

## Bug 1: CPU Abstraction

### Fix Requirements
- Detect CPU vendor (Intel/AMD/other)
- Detect CPU model for undervolt safety
- Skip undervolt for unknown/unsupported CPUs
- Use detected core count for isolation

### Proposed Implementation

#### Step 1: Add CPU Detection (`platforms/detection.py`)
```python
@dataclass
class CPUCapabilities:
    vendor: str           # "intel", "amd", "other"
    model: str            # "i9-10850K", "i5-1240P", etc.
    family: str           # "comet_lake", "alder_lake", etc.
    supports_undervolt: bool
    safe_undervolt_mv: int  # 0 if not supported
    core_count: int
    thread_count: int

def detect_cpu_capabilities() -> CPUCapabilities:
    # Read /proc/cpuinfo for model
    # Determine family from model
    # Set safe undervolt based on family
```

#### Step 2: Update CPUOptimizer
- Add `cpu_caps` property (lazy load)
- Replace "i9-10850K" with `self.cpu_caps.model`
- Skip undervolt if `not self.cpu_caps.supports_undervolt`
- Use `self.cpu_caps.safe_undervolt_mv` instead of hard-coded values

### Reversal Strategy
- Keep original embedded scripts as comments
- Add `--legacy-cpu-mode` flag if needed
- Revert by restoring hard-coded values

### Test Strategy
- Test on Intel system: should detect and apply appropriate settings
- Test detection for AMD CPUs: should skip undervolt
- Test unknown CPU: should use conservative defaults

---

## Bug 2: Memory Abstraction

### Fix Requirements
- Use actual RAM size from `system_info["ram_gb"]`
- Calculate ZRAM size as fraction of actual RAM
- Scale vm.dirty_ratio based on RAM

### Proposed Implementation

#### Step 1: Create RAM-aware config generator
```python
def generate_memory_config(ram_gb: int) -> dict:
    return {
        "zram_size": min(ram_gb // 4, 16),  # 1/4 of RAM, max 16GB
        "dirty_ratio": 20 if ram_gb >= 32 else 10,
        "dirty_background_ratio": 5 if ram_gb >= 32 else 3,
    }
```

#### Step 2: Update MemoryOptimizer
- Read `self.system_info["ram_gb"]` (already available)
- Generate config based on actual RAM
- Replace hard-coded "64GB" in logs with actual value

### Reversal Strategy
- Minimal risk - just uses different values
- Can revert by hard-coding values again

### Test Strategy
- Test with different RAM values in system_info
- Verify ZRAM config scales correctly

---

## Bug 3: Network Abstraction

### Fix Requirements
- Detect NIC driver in use (igc, e1000e, r8169, etc.)
- Only apply igc-specific options if igc driver
- Use generic optimizations for other NICs

### Proposed Implementation

#### Step 1: Add NIC Detection (`platforms/detection.py`)
```python
@dataclass
class NICCapabilities:
    driver: str           # "igc", "e1000e", "r8169", etc.
    is_intel: bool
    is_i225_family: bool  # I225-V, I225-LM, I226, etc.
    supports_eee_disable: bool

def detect_nic_capabilities() -> Optional[NICCapabilities]:
    # Check /sys/class/net/*/device/driver
    # Determine if I225 family from device ID
```

#### Step 2: Update NetworkOptimizer
- Add `nic_caps` property (lazy load)
- Only write igc module config if `self.nic_caps.driver == "igc"`
- Only disable EEE if `self.nic_caps.is_i225_family`
- Apply generic optimizations for all NICs

### Reversal Strategy
- Keep original I225-V config as fallback
- Add detection bypass flag if needed

### Test Strategy
- Test on I225-V system: should apply full optimizations
- Test on different NIC: should skip I225-specific fixes
- Test with no NIC: should handle gracefully

---

## Impact Analysis

| Change | Risk | Mitigation |
|--------|------|------------|
| CPU undervolt skip | LOW | Safer - no undervolt is better than wrong undervolt |
| Memory scaling | LOW | Values are reasonable for any RAM size |
| NIC driver check | LOW | Generic optimizations still applied |

## Implementation Order

1. **Memory** (lowest risk, simplest - just use existing `ram_gb`)
2. **Network** (medium - add driver detection)
3. **CPU** (highest risk - undervolt safety critical)

---

## Next Phase

Proceed to **Phase 4: Implementation** with step-by-step UoWs for each fix.
