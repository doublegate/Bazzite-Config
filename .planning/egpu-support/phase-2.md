# Phase 2: Design — eGPU Support

## Proposed Solution

### High-Level Design
1. **Enhanced GPU Detection**: Detect all GPUs via `/sys/class/drm/` with vendor identification
2. **Thunderbolt Awareness**: Check `/sys/bus/thunderbolt/` for eGPU enclosures
3. **Primary GPU Selection**: Prefer discrete GPU (NVIDIA/AMD) over iGPU for gaming
4. **Graceful nvidia-smi Handling**: Use `/proc/driver/nvidia/version` as fallback
5. **Hot-plug Awareness**: Detect if eGPU is connected before applying optimizations

### Detection Flow
```
1. Enumerate /sys/class/drm/card*/device/vendor
2. Map vendor IDs: 0x10de=NVIDIA, 0x1002=AMD, 0x8086=Intel
3. Check /sys/bus/thunderbolt/devices/ for eGPU enclosure
4. If Thunderbolt device + discrete GPU → mark as eGPU
5. Select primary GPU: eGPU > discrete > iGPU
```

## API Design

### New Function: `detect_gpus()`
```python
def detect_gpus() -> List[GPUInfo]:
    """Detect all GPUs with detailed info."""
    # Returns list of GPUInfo dataclasses

@dataclass
class GPUInfo:
    card_path: str           # /sys/class/drm/card0
    vendor: str              # "nvidia", "amd", "intel"
    vendor_id: str           # "0x10de"
    device_id: str           # "0x2504"
    name: str                # "GeForce RTX 3060"
    is_egpu: bool            # True if via Thunderbolt
    is_primary: bool         # True if selected for gaming
    driver: Optional[str]    # "nvidia", "nouveau", "amdgpu"
```

### New Function: `detect_thunderbolt_devices()`
```python
def detect_thunderbolt_devices() -> List[str]:
    """Return list of Thunderbolt device names."""
    # Reads /sys/bus/thunderbolt/devices/*/device_name
```

### Modified: `check_nvidia_gpu_exists()`
```python
def check_nvidia_gpu_exists() -> bool:
    """Check if NVIDIA GPU exists (with or without nvidia-smi)."""
    # 1. Try nvidia-smi (existing)
    # 2. Fallback: check /proc/driver/nvidia/version
    # 3. Fallback: check /sys/class/drm vendor 0x10de
```

## Behavioral Decisions

### Q1: What if eGPU is disconnected?
**Options**:
- A) Fail with error
- B) Fall back to iGPU optimizations  
- C) Skip GPU optimizations entirely

**Recommendation**: B — Fall back to iGPU, warn user

### Q2: Should we auto-install nvidia-smi package?
**Options**:
- A) Yes, install automatically
- B) No, just warn and skip NVIDIA optimizations
- C) Ask user interactively

**Recommendation**: C — Ask user (respects immutable systems)

### Q3: How to identify eGPU vs internal discrete GPU?
**Options**:
- A) Check Thunderbolt devices, correlate with PCI bus
- B) Check PCI bus topology (external buses have higher numbers)
- C) Both

**Recommendation**: A — Thunderbolt check is most reliable

### Q4: What PCI vendor IDs to support?
- `0x10de` = NVIDIA
- `0x1002` = AMD
- `0x8086` = Intel
- `0x1a03` = ASPEED (server GPUs, skip)

### Q5: Should we support AMD eGPUs?
**Options**:
- A) Yes, full support
- B) Detection only, no AMD-specific optimizations yet
- C) No

**Recommendation**: B — Detect but defer AMD optimizations

## Open Questions for User

### Q1: eGPU Disconnect Behavior
When your Razer Core X is disconnected, should the optimizer:
- **A)** Error out and refuse to run
- **B)** Fall back to Intel Iris Xe optimizations (recommended)
- **C)** Skip all GPU optimizations

### Q2: nvidia-smi Installation
Your system is missing `xorg-x11-drv-nvidia-cuda` (provides nvidia-smi). Should we:
- **A)** Automatically install it via DNF
- **B)** Ask you each time before installing
- **C)** Just warn and skip advanced NVIDIA features (temp monitoring, power modes)

### Q3: Primary GPU Selection
When both iGPU and eGPU are present, should we:
- **A)** Always prefer eGPU for gaming optimizations
- **B)** Let you choose via CLI flag (`--gpu=egpu` or `--gpu=igpu`)
- **C)** Auto-detect based on what's rendering (requires more complexity)

## Design Alternatives Considered

| Approach | Pros | Cons |
|----------|------|------|
| nvidia-smi only | Simple | Fails without package |
| /sys/class/drm | Always works | Less info (no temps) |
| Both with fallback | Best coverage | More complex |

**Chosen**: Both with fallback

## Implementation Phases

### Phase 3 Steps (after questions answered)
1. Add `GPUInfo` dataclass to `platforms/detection.py`
2. Add `detect_gpus()` function
3. Add `detect_thunderbolt_devices()` function  
4. Modify `check_nvidia_gpu_exists()` with fallback
5. Update `get_system_info()` to use new detection
6. Add CLI flag for GPU selection (if Q3=B)
7. Add package installation prompt (if Q2=B)

## Exit Criteria
- [ ] All open questions answered by user
- [ ] Design finalized based on answers
- [ ] Ready for Phase 3 implementation
