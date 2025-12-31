# TEAM_015: Bugfix Plan - Hardware Abstraction (CPU/Memory/Network)

**Created**: 2025-12-31
**Status**: Planning

## Mission

Create bugfix plans for remaining hardware abstraction issues where hard-coded hardware references are applied to all systems regardless of actual hardware.

## Bugs to Address

### Bug 1: CPU Optimizer Hard-coded i9-10850K
- **Location**: `bazzite-optimizer.py`, `CPUOptimizer` class
- **Impact**: Intel i9-10850K undervolt settings applied to all CPUs
- **Risk**: Incorrect undervolt values could cause instability on different CPUs

### Bug 2: Memory Optimizer Hard-coded 64GB
- **Location**: `bazzite-optimizer.py`, `MemoryOptimizer` class, SYSCTL_CONFIG, ZRAM_CONFIG
- **Impact**: 64GB-specific memory settings applied regardless of actual RAM
- **Risk**: Suboptimal or incorrect memory configuration

### Bug 3: Network Optimizer Hard-coded I225-V
- **Location**: `bazzite-optimizer.py`, `NetworkOptimizer` class
- **Impact**: Intel I225-V specific fixes applied to all NICs
- **Risk**: Wrong driver options for different network adapters

## Planning Artifacts

- `.planning/hardware-abstraction-bugfix/phase-1.md` - Understanding and Scoping
- `.planning/hardware-abstraction-bugfix/phase-2.md` - Root Cause Analysis
- `.planning/hardware-abstraction-bugfix/phase-3.md` - Fix Design
- `.planning/hardware-abstraction-bugfix/phase-4.md` - Implementation
- `.planning/hardware-abstraction-bugfix/phase-5.md` - Cleanup and Handoff

## Progress Log

- [x] Registered as TEAM_015
- [x] Created planning directory
- [x] Phase 1: Understanding and Scoping
- [x] Phase 2: Root Cause Analysis
- [x] Phase 3: Fix Design
- [x] Phase 4: Implementation
- [x] Phase 5: Cleanup and Handoff

## Implementation Summary

### Detection Functions Added (`platforms/detection.py`)
- `CPUCapabilities` dataclass with vendor, family, undervolt support
- `detect_cpu_capabilities()` - parses /proc/cpuinfo, detects Intel families
- `INTEL_CPU_FAMILIES` - patterns and safe undervolt values per generation
- `NICCapabilities` dataclass with driver, I225 family detection
- `detect_nic_capabilities()` - scans /sys/class/net for physical NICs
- `INTEL_I225_DEVICE_IDS` - PCI IDs for I225/I226 family

### Optimizer Updates
- **CPUOptimizer**: Skips undervolt for Alder Lake+ CPUs (correctly detected as unsafe)
- **MemoryOptimizer**: Uses actual `ram_gb` from system_info instead of hard-coded 64GB
- **NetworkOptimizer**: Only applies igc module options if I225 family detected

### Tests Added
- `tests/test_hardware_detection.py` - 10 new tests for detection functions
- All 306 tests pass (baseline was 296)

## Handoff Checklist

- [x] All implementations done
- [x] All new tests pass
- [x] All existing tests pass (306 total)
- [x] No regressions
