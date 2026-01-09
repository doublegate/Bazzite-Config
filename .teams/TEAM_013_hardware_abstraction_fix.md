# TEAM_013: Hardware Abstraction Fix & Dry-Run Implementation

**Created**: 2025-12-31
**Status**: In Progress

## Mission

Fix critical hardware abstraction failures where RTX 5080-specific optimizations are being applied to all NVIDIA GPUs (including user's RTX 3060), and implement dry-run capability.

## Problem Summary

The Phase 3 Step 3.4 planning identified 91 hard-coded hardware references but only implemented UI changes (banner, optimizer names). The actual optimizer logic was **never abstracted**:

| Component | Hard-coded Refs | Impact |
|-----------|-----------------|--------|
| `NvidiaOptimizer` | 30+ RTX 5080/Blackwell | Applies 5080 overclock limits to all GPUs |
| `CPUOptimizer` | 8+ i9-10850K | Applies 10850K undervolt to all Intel CPUs |
| `MemoryOptimizer` | 3+ "64GB" | Assumes 64GB RAM |
| `NetworkOptimizer` | 10+ I225-V | Applies I225-V fixes to all NICs |
| Embedded scripts | All | Hard-coded hardware names in shell scripts |

## User's System

- GPU: RTX 3060 (GA106) via Thunderbolt eGPU
- CPU: Intel i5-1240P (Alder Lake hybrid)
- RAM: 62GB
- Platform: Ultramarine Linux (Fedora Traditional)

## Fix Plan

### Phase 1: GPU Abstraction (Critical)

1. Create GPU capability detection in `platforms/detection.py`:
   - Detect GPU generation (Ampere, Ada, Blackwell, etc.)
   - Detect VRAM size
   - Detect safe overclock limits per generation

2. Update `NvidiaOptimizer` to use detected capabilities:
   - Replace hard-coded "RTX 5080" checks with generation detection
   - Use VRAM-based memory limits
   - Use generation-appropriate overclock limits

### Phase 2: CPU Abstraction

1. Extend CPU detection for:
   - CPU generation
   - Safe undervolt ranges
   - Core count for isolation

2. Update `CPUOptimizer` to be generic

### Phase 3: Memory/Network Abstraction

1. Use detected RAM for ZRAM config
2. Detect NIC type for network optimizations

### Phase 4: Dry-Run Implementation

1. Add `--dry-run` flag
2. Create DryRunContext that intercepts all write operations
3. Log what WOULD happen without executing

### Phase 5: Embedded Script Cleanup

1. Move hard-coded values to variables
2. Pass detected values as script arguments

## Files to Modify

- `platforms/detection.py` - Add GPU/CPU capability detection
- `bazzite-optimizer.py` - NvidiaOptimizer, CPUOptimizer, MemoryOptimizer, NetworkOptimizer
- Embedded scripts (NVIDIA_OPTIMIZATION_SCRIPT, etc.)

## Testing

- Run on RTX 3060 system - should NOT see "5080" or "Blackwell" in logs
- Run on i5-1240P - should NOT see "i9-10850K" in logs
- Dry-run should show all actions without executing

## Progress Log

- [x] Identified scope of abstraction failures
- [x] Verified baseline kernel profile exists
- [ ] Phase 1: GPU Abstraction
- [ ] Phase 2: CPU Abstraction
- [ ] Phase 3: Memory/Network Abstraction
- [ ] Phase 4: Dry-Run Implementation
- [ ] Phase 5: Embedded Script Cleanup
