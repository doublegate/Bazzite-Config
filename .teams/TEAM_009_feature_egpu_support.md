# TEAM_009: Feature Plan - eGPU (Thunderbolt GPU) Support

## Mission
Add support for external GPUs connected via Thunderbolt (eGPU) to bazzite-optimizer.

## User System Context
- **Host**: Intel Alder Lake-P laptop with Iris Xe iGPU
- **eGPU Enclosure**: Razer Core X (Thunderbolt 3)
- **External GPU**: NVIDIA RTX 3060 LHR (GA106)
- **Driver**: nvidia (loaded)
- **Missing**: nvidia-smi (xorg-x11-drv-nvidia-cuda package)

## User Design Decisions
- **Q1 (Disconnect)**: B — Fall back to iGPU
- **Q2 (nvidia-smi)**: B — Ask before installing
- **Q3 (Primary GPU)**: C — Auto-detect based on active rendering

## Implementation Complete ✅

### Files Modified
| File | Changes |
|------|---------|
| `platforms/detection.py` | Added `GPUInfo`, `detect_gpus()`, `get_primary_gpu()`, `detect_thunderbolt_devices()` |
| `platforms/__init__.py` | Exported new GPU functions |
| `bazzite-optimizer.py` | Updated `get_system_info()` to use new GPU detection |

### New Capabilities
- ✅ Detects all GPUs via `/sys/class/drm/`
- ✅ Identifies Thunderbolt eGPU enclosures (Razer Core X, etc.)
- ✅ Marks eGPU correctly (RTX 3060 on PCI bus 0x3c)
- ✅ Auto-detects active rendering GPU
- ✅ Selects primary GPU for gaming optimizations
- ✅ Falls back to iGPU if eGPU disconnected

### Verification
```
=== GPUs Detected ===
GA106 [GeForce RTX 3060 Lite Hash Rate]
  Vendor: nvidia, Driver: nvidia
  eGPU: True, Primary: True, Rendering: True

Alder Lake-P GT2 [Iris Xe Graphics]
  Vendor: intel, Driver: i915
  eGPU: False, Primary: False, Rendering: False
```

### Tests
- All 296 tests passing

## Status
- [x] Team registered
- [x] System analyzed
- [x] Phase 1: Discovery
- [x] Phase 2: Design
- [x] Phase 3: Implementation
- [x] Phase 4: Testing

## Remaining Work (Future)
- [ ] Package install prompt for nvidia-smi (Q2:B implementation)
- [ ] Hot-plug detection (eGPU connect/disconnect at runtime)
- [ ] AMD eGPU optimization support
