# TEAM_012: Bugfix Plan — Kernel Edge Cases

## Mission
Fix kernel parameter edge cases for:
1. Alder Lake hybrid CPU (P-core/E-core mapping)
2. eGPU via Thunderbolt (stability params)
3. CLI commands for kernel profile switching

## Bug Summary
The optimizer has hardcoded kernel parameters that don't account for:
- Hybrid CPU architectures (Intel 12th+ gen)
- External GPUs via Thunderbolt
- No CLI interface to use the new kernel profile management

## User System
- **CPU**: Intel i5-1240P (4 P-cores + 8 E-cores = 12 cores / 16 threads)
- **GPU**: RTX 3060 via Razer Core X (Thunderbolt eGPU)
- **Platform**: Ultramarine Linux 43 (GRUB-based)

## Planning Artifacts
- `.planning/kernel-edge-cases-fix/phase-1.md` — Understanding & Scoping
- `.planning/kernel-edge-cases-fix/phase-2.md` — Root Cause Analysis
- `.planning/kernel-edge-cases-fix/phase-3.md` — Fix Design
- `.planning/kernel-edge-cases-fix/phase-4.md` — Implementation

## Status
- [x] Team registered
- [x] Phase 1: Understanding & Scoping
- [x] Phase 2: Root Cause Analysis
- [x] Phase 3: Fix Design
- [x] Phase 4: Implementation
- [x] Phase 5: Testing & Handoff

## Implementation Complete ✅

### Files Modified
| File | Changes |
|------|---------|
| `platforms/detection.py` | Added `CPUTopology`, `detect_cpu_topology()` |
| `platforms/__init__.py` | Exported new CPU topology functions |
| `platforms/traditional/grub.py` | Added kernel profile management (TEAM_011) |
| `bazzite-optimizer.py` | Updated isolcpus to use topology, added eGPU params, added CLI |

### Verified Working
- CPU topology detection: ✅ Correctly identifies P-cores (0-7) and E-cores (8-15)
- eGPU params: ✅ Adds `pcie_port_pm=off`, `thunderbolt.force_power=1` when eGPU detected
- CLI commands: ✅ `--save-baseline`, `--list-kernel-profiles`, `--kernel-profile`, `--kernel-diff`
- Baseline saved: ✅ `/var/lib/bazzite-optimizer/kernel-profiles/baseline.conf`
- All tests: ✅ 296 passed
