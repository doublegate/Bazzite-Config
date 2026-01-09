# TEAM_009: eGPU Design Questions

**Feature**: eGPU (Thunderbolt GPU) Support  
**Status**: Awaiting user decisions  
**Blocking**: Phase 3 Implementation

---

## Q1: eGPU Disconnect Behavior

When your Razer Core X is disconnected, should the optimizer:

- **A)** Error out and refuse to run
- **B)** Fall back to Intel Iris Xe optimizations *(recommended)*
- **C)** Skip all GPU optimizations

**Your answer**: **B** — Fall back to iGPU

---

## Q2: nvidia-smi Installation

Your system is missing `xorg-x11-drv-nvidia-cuda` (provides nvidia-smi for temp/power monitoring). Should we:

- **A)** Automatically install it via DNF
- **B)** Ask you each time before installing *(recommended)*
- **C)** Just warn and skip advanced NVIDIA features

**Your answer**: **B** — Ask before installing

---

## Q3: Primary GPU Selection

When both iGPU (Iris Xe) and eGPU (RTX 3060) are present:

- **A)** Always prefer eGPU for gaming optimizations *(recommended)*
- **B)** Let you choose via CLI flag (`--gpu=egpu` or `--gpu=igpu`)
- **C)** Auto-detect based on active rendering

**Your answer**: **C** — Auto-detect based on active rendering

---

## Status: ✅ ANSWERED

Proceeding to Phase 3 implementation.
