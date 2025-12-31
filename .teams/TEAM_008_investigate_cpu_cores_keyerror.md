# TEAM_008: Investigate cpu_cores KeyError on Ultramarine

## Mission
Ensure bazzite-optimizer runs correctly on user's actual system (Ultramarine Linux 43).

## System Info
- **OS**: Ultramarine Linux 43 (Plasma Edition)
- **Base**: Fedora 43 (traditional, not immutable)
- **Package Manager**: DNF
- **Boot**: GRUB
- **Kernel**: 6.17.12-300.fc43.x86_64
- **CPU**: Intel Alder Lake-P (12 cores / 16 threads)
- **RAM**: 62 GB
- **GPU**: Intel Iris Xe Graphics

## Bug Report
```
Fatal error: 'cpu_cores'
```

## Phase 1: Symptom
- **Expected**: Optimizer runs and shows system info
- **Actual**: Crashes with KeyError for 'cpu_cores'
- **Location**: Line 6960 accessing `self.system_info['cpu_cores']`

## Phase 2: Root Cause
`get_system_info()` function (line 1929) was missing `cpu_cores` and `cpu_threads` fields.

## Phase 3: Fix Applied
Added to `get_system_info()` at line 1966-1967:
```python
info["cpu_cores"] = psutil.cpu_count(logical=False) or 0
info["cpu_threads"] = psutil.cpu_count(logical=True) or 0
```

## Verification
- [x] Platform detection: ✅ FEDORA_TRADITIONAL
- [x] PlatformServices: ✅ DnfPackageManager + GrubKernelParams
- [x] Optimizer --help: ✅ Works
- [x] Optimizer --validate: ✅ Works
- [x] Unit tests: ✅ 296 passed

## Current System State (--validate)
| Check | Status |
|-------|--------|
| cpu_governor | ❌ Not optimized |
| gpu_power_mode | ❌ Not optimized |
| zram_enabled | ✅ |
| mglru_enabled | ✅ |
| system76_scheduler | ✅ |
| thermal_monitoring | ❌ Not configured |

## Handoff
- Bug fixed, optimizer now runs on Ultramarine Linux
- User can now run `sudo ./bazzite-optimizer.py --profile balanced` to apply optimizations
- Reboot required after applying kernel parameters
