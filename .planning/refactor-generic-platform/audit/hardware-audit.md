# Hard-coded Hardware Audit

**Date**: 2025-12-31
**Auditor Team**: TEAM_004
**Commit**: 889c2fe

## Summary

| Hardware | Type | Occurrences | Files |
|----------|------|-------------|-------|
| RTX 5080 | GPU | 45 | 8 |
| Blackwell | GPU Arch | 15 | 3 |
| i9-10850K | CPU | 12 | 5 |
| 64GB | RAM | 8 | 5 |
| 16GB | VRAM/RAM | 6 | 4 |
| I225-V | NIC | 5 | 2 |

**Total (excluding ref_scripts/)**: ~91 matches across 10 files

## Detailed References

### GPU References (RTX 5080 / Blackwell)

| File | Line | Context | Abstraction Needed |
|------|------|---------|-------------------|
| `bazzite-optimizer.py` | 419 | `# VRAM optimization for 16GB RTX 5080` | Detect VRAM dynamically |
| `bazzite-optimizer.py` | 469 | `echo "RTX 5080 Blackwell optimizations..."` | Generic GPU message |
| `bazzite-optimizer.py` | 1330 | `# GPU Optimizations (NVIDIA RTX 5080)` | Generic comment |
| `bazzite-optimizer.py` | 2993-3040 | `check_resizable_bar()` — RTX 5080 specific detection | Make GPU-agnostic |
| `bazzite-optimizer.py` | 3084-3179 | `apply_optimizations()` — RTX 5080 messages | Generic GPU messages |
| `bazzite-optimizer.py` | 3106-3112 | `nvidia-blackwell.conf` filename | Generic or detect arch |
| `bazzite-optimizer.py` | 3200-3351 | Progressive overclock, power validation | Parameterize by GPU |
| `bazzite-optimizer.py` | 4941 | PCIe params comment | Generic comment |
| `bazzite-optimizer.py` | 6211 | Section comment | Generic comment |
| `bazzite-optimizer.py` | 6859 | Banner line | Dynamic hardware info |
| `bazzite-optimizer.py` | 6973 | `("NVIDIA RTX 5080 Blackwell", NvidiaOptimizer...)` | Detect GPU name |
| `gaming-maintenance-suite.sh` | 79, 692, 744, 748 | Benchmark/report labels | Dynamic detection |
| `gaming-monitor-suite.py` | 324, 397, 657 | Display labels | Dynamic detection |
| `gaming-manager-suite.py` | 733, 735 | Driver version check | Parameterize threshold |
| `tests/conftest.py` | 83-92 | Mock GPU fixture | Keep as test fixture |
| `tests/unit/test_optimizers.py` | 18, 49, 304 | Test assertions | Keep as test fixture |
| `ml_engine/tests/test_api_server.py` | 154, 334 | Test data | Keep as test fixture |

### CPU References (i9-10850K)

| File | Line | Context | Abstraction Needed |
|------|------|---------|-------------------|
| `bazzite-optimizer.py` | 472-588 | `CPU_OPTIMIZATION_SCRIPT` | Parameterize by CPU |
| `bazzite-optimizer.py` | 654 | `UNDERVOLT_CONFIG` comment | Generic comment |
| `bazzite-optimizer.py` | 3365 | Class docstring | Generic docstring |
| `bazzite-optimizer.py` | 3399-3400 | `apply_optimizations()` log | Generic message |
| `bazzite-optimizer.py` | 6859 | Banner line | Dynamic hardware info |
| `bazzite-optimizer.py` | 6974 | `("Intel i9-10850K CPU", CPUOptimizer...)` | Detect CPU name |
| `gaming-maintenance-suite.sh` | 187, 691, 749 | Benchmark labels | Dynamic detection |
| `tests/conftest.py` | 113-116 | Mock CPU fixture | Keep as test fixture |
| `ml_engine/tests/test_api_server.py` | 151, 331 | Test data | Keep as test fixture |

### RAM/VRAM References (64GB / 16GB)

| File | Line | Context | Abstraction Needed |
|------|------|---------|-------------------|
| `bazzite-optimizer.py` | 419-421 | VRAM limits (16GB) | Detect VRAM dynamically |
| `bazzite-optimizer.py` | 592 | `SYSCTL_CONFIG` comment (64GB) | Detect RAM dynamically |
| `bazzite-optimizer.py` | 720 | `ZRAM_CONFIG` comment (64GB) | Detect RAM dynamically |
| `bazzite-optimizer.py` | 3461 | `configure_zram()` docstring | Generic docstring |
| `bazzite-optimizer.py` | 6859 | Banner line (64GB) | Dynamic detection |
| `gaming-maintenance-suite.sh` | 693 | Report label | Dynamic detection |
| `gaming-manager-suite.py` | 773 | RAM check threshold | Parameterize |
| `tests/conftest.py` | 90, 154, 312 | Mock fixtures | Keep as test fixture |
| `tests/unit/test_optimizers.py` | 128, 132 | Test names | Keep as test names |
| `steamdeck_support/steamdeck_optimizer.py` | 24, 38 | Steam Deck specs | Keep (device-specific) |
| `platform_support/handheld_extended.py` | 32 | Handheld specs | Keep (device-specific) |

### Network References (Intel I225-V)

| File | Line | Context | Abstraction Needed |
|------|------|---------|-------------------|
| `bazzite-optimizer.py` | 1333 | Script comment | Generic or detect |
| `bazzite-optimizer.py` | 3626-3640 | `NetworkOptimizer` class/methods | Detect NIC dynamically |
| `bazzite-optimizer.py` | 6977 | `("Network (Intel I225-V)", NetworkOptimizer...)` | Detect NIC name |
| `tests/unit/test_optimizers.py` | 169 | Test name | Keep as test name |

## Abstraction Strategy

### 1. Dynamic Hardware Detection (Already Partially Exists)

The codebase already has some detection:
- `get_cpu_info()` — can be extended
- `check_nvidia_gpu_exists()` — can return model info
- RAM detection via `/proc/meminfo`

### 2. Files Requiring Changes

| File | Priority | Changes Needed |
|------|----------|----------------|
| `bazzite-optimizer.py` | High | Replace 60+ hard-coded refs with dynamic detection |
| `gaming-maintenance-suite.sh` | Medium | Add detection functions |
| `gaming-monitor-suite.py` | Medium | Add detection functions |
| `gaming-manager-suite.py` | Low | Parameterize thresholds |

### 3. Test Fixtures (Keep As-Is)

Test files use hard-coded values intentionally for deterministic testing. These should NOT be changed to dynamic detection.

## Impact on Phase 2-5

### Phase 2 Impact
- None directly — Phase 2 builds abstraction layer

### Phase 3 Impact
- **Step 3.4 (Dynamic hardware UI)** covers this ✓
- May need expansion for gaming-maintenance-suite.sh and gaming-monitor-suite.py

### Phase 4 Impact
- After dynamic detection, some hard-coded fallbacks may become dead code

### Phase 5 Impact
- Documentation should reflect dynamic hardware support

## Recommendations

1. **Expand Step 3.4** to include:
   - `gaming-maintenance-suite.sh` hardware labels
   - `gaming-monitor-suite.py` display strings
   - `gaming-manager-suite.py` thresholds

2. Create hardware detection utility module:
   ```python
   # platforms/hardware.py
   def detect_gpu() -> GpuInfo
   def detect_cpu() -> CpuInfo
   def detect_ram() -> RamInfo
   def detect_nic() -> NicInfo
   ```

3. Banner line at 6859 should use detected values:
   ```python
   f"Enhanced for {gpu.name} | {cpu.name} | {ram.total_gb}GB RAM"
   ```
