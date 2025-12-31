# Phase 1: Discovery — eGPU Support

## Feature Summary
Add detection and optimization support for external GPUs (eGPUs) connected via Thunderbolt.

### Problem Statement
Users with Thunderbolt eGPU setups (like Razer Core X + RTX 3060) cannot fully utilize the optimizer because:
1. The optimizer doesn't detect eGPUs as the primary gaming GPU
2. NVIDIA optimizations aren't applied without nvidia-smi
3. No handling for Thunderbolt-specific considerations

### Who Benefits
- Laptop users with Thunderbolt eGPU enclosures
- Users with hybrid iGPU + eGPU setups
- Desktop users with Thunderbolt expansion

## Success Criteria
- [ ] Detect eGPU via Thunderbolt enumeration
- [ ] Identify eGPU as primary gaming GPU (over iGPU)
- [ ] Apply NVIDIA optimizations to eGPU
- [ ] Handle missing nvidia-smi gracefully (offer to install)
- [ ] Warn if eGPU is disconnected

## Current State Analysis

### How detection works today
```python
# In get_system_info() - bazzite-optimizer.py:1982
returncode, stdout, _ = run_command("lspci | grep -E 'VGA|3D|Display'", check=False)
if returncode == 0:
    info["gpus"] = stdout.strip().split("\n")
    gpu_str = stdout.lower()
    if "nvidia" in gpu_str:
        info["gpu_vendor"] = "nvidia"
```

**Problem**: This detects NVIDIA but doesn't distinguish eGPU from internal.

### How NVIDIA detection works today
```python
# check_nvidia_gpu_exists() - bazzite-optimizer.py
returncode, stdout, _ = run_command(
    "nvidia-smi --query-gpu=driver_version --format=csv,noheader", check=False)
```

**Problem**: Requires nvidia-smi which may not be installed.

### Thunderbolt detection (not implemented)
```bash
# Available on user's system:
/sys/bus/thunderbolt/devices/*/device_name
# Returns: "Core X" for Razer enclosure
```

## Codebase Reconnaissance

### Files to modify
| File | Purpose |
|------|---------|
| `bazzite-optimizer.py` | `get_system_info()`, `check_nvidia_gpu_exists()` |
| `platforms/detection.py` | Add eGPU/Thunderbolt detection |
| `platforms/base.py` | Possibly add GPU abstraction |

### Existing GPU-related functions
- `get_system_info()` — line 1929
- `check_nvidia_gpu_exists()` — line 1802
- `check_hardware_compatibility()` — line 2007
- `get_gpu_temperature()` — line 2103
- `validate_gpu_power_mode()` — line 2146

### Tests impacted
- `tests/test_bazzite_optimizer_core_utils.py` — system info tests
- Need new tests for eGPU detection

## Constraints

### Technical
- Thunderbolt hot-plug: eGPU may connect/disconnect
- PCI bus address changes on reconnect
- nvidia-smi may not be installed
- Multiple GPUs: need to identify "primary" for gaming

### User Experience
- Should work without manual configuration
- Should gracefully degrade if eGPU disconnected
- Should offer to install missing packages (nvidia-smi)

## Steps

### Step 1: Document current GPU detection flow
- [x] Trace `get_system_info()` GPU detection
- [x] Trace `check_nvidia_gpu_exists()` 
- [x] Identify gaps

### Step 2: Research Thunderbolt/eGPU detection
- [x] Check `/sys/bus/thunderbolt/devices/`
- [ ] Check `bolt` daemon integration (if available)
- [ ] Check PCI topology for eGPU identification

### Step 3: Identify nvidia-smi alternatives
- [ ] Can we detect NVIDIA without nvidia-smi?
- [ ] What package provides nvidia-smi on Fedora/Ultramarine?

## Exit Criteria
- Current GPU detection fully documented
- Thunderbolt detection method identified
- nvidia-smi installation path identified
- Ready for Phase 2 (Design)
