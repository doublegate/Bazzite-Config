# Refactor Plan: Generic Platform Support

**Team**: TEAM_001
**Created**: 2025-12-31
**Status**: Planning Complete (Split into Step/UoW files)

---

## Executive Summary

Transform `bazzite-config` from a Bazzite-specific gaming optimizer into a **generic Linux gaming optimizer** that supports:

1. **rpm-ostree immutable systems**: Bazzite, Silverblue, Kinoite, Aurora
2. **Traditional RPM systems**: Fedora Workstation, Ultramarine, CentOS Stream

While keeping **Bazzite as a first-class citizen** with all its features intact.

> **Scope**: Initial release focuses on RPM-based systems. Debian support (Ubuntu, Pop!_OS) deferred to stretch goals.

---

## Document Structure

```
Phase (high-level goal)
└── phase-N/
    ├── README.md      # Phase overview
    ├── step-1.md      # Step = 1 PR
    ├── step-2.md
    └── ...
        └── UoW X.Y.Z  # Unit of Work (1 SLM task)
```

---

## Phase Overview

| Phase | Directory | PRs | Focus | Steps | UoWs |
|-------|-----------|-----|-------|-------|------|
| 1 | [phase-1/](phase-1/) | — | Audit and baseline | 4 | 5 |
| 2 | [phase-2/](phase-2/) | #1-5 | Build `platforms/` module | 6 | 20 |
| 3 | [phase-3/](phase-3/) | #6-10 | Migrate existing code | 5 | 25 |
| 4 | [phase-4/](phase-4/) | #11 | Remove dead code | 2 | 8 |
| 5 | [phase-5/](phase-5/) | #12 | Docs and release | 3 | 12 |
| **Total** | | **12 PRs** | | **20 steps** | **70 UoWs** |

---

## PR → Step Mapping

| PR | Phase/Step | Description | Testable on Ultramarine |
|----|------------|-------------|-------------------------|
| #1 | 2.1, 2.2 | Platform detection + base classes | ✅ |
| #2 | 2.5 | rpm-ostree kernel params | ❌ (needs Bazzite) |
| #3 | 2.3 | GRUB kernel params | ✅ |
| #4 | 2.4 | Package managers (dnf) | ✅ |
| #5 | 2.6 | PlatformServices factory | ✅ |
| #6 | 3.1 | Migrate KernelOptimizer | ✅ |
| #7 | 3.2 | Migrate package installation | ✅ |
| #8 | 3.3 | Conditional Bazzite features | ✅ |
| #9 | 3.4 | Dynamic hardware UI | ✅ |
| #10 | 3.5 | Wire up PlatformServices | ✅ |
| #11 | 4.1 | Remove dead code | ✅ |
| #12 | 5.2 | Documentation updates | ✅ |

---

## Quick Start

```bash
# 1. Read Phase 1 overview
cat .planning/refactor-generic-platform/phase-1/README.md

# 2. Start with Step 1.1
cat .planning/refactor-generic-platform/phase-1/step-1.md

# 3. Execute UoW 1.1.1
grep -n "rpm-ostree kargs" bazzite-optimizer.py
```

---

## Directory Structure

```
.planning/refactor-generic-platform/
├── README.md                 # This file
├── GITHUB_ISSUES.md          # 21 GitHub issues
├── PULL_REQUESTS.md          # 14 PR descriptions  
├── PR_DEPENDENCY_GRAPH.md    # Dependencies + testing
│
├── phase-1/                  # Discovery
│   ├── README.md
│   ├── step-1.md            # Audit rpm-ostree (1 UoW)
│   ├── step-2.md            # Audit Bazzite code (1 UoW)
│   ├── step-3.md            # Audit hardware refs (1 UoW)
│   └── step-4.md            # Test baseline (2 UoWs)
│
├── phase-2/                  # Abstraction Layer
│   ├── README.md
│   ├── step-1.md            # Platform detection (4 UoWs) → PR #1
│   ├── step-2.md            # Base classes (2 UoWs) → PR #1
│   ├── step-3.md            # GRUB params (7 UoWs) → PR #3
│   ├── step-4.md            # Package managers (2 UoWs) → PR #4
│   ├── step-5.md            # rpm-ostree (2 UoWs) → PR #2
│   └── step-6.md            # PlatformServices (3 UoWs) → PR #5
│
├── phase-3/                  # Migration
│   ├── README.md
│   ├── step-1.md            # KernelOptimizer (7 UoWs) → PR #6
│   ├── step-2.md            # Package install (6 UoWs) → PR #7
│   ├── step-3.md            # Bazzite conditional (4 UoWs) → PR #8
│   ├── step-4.md            # Dynamic UI & Cleanup (4 UoWs) → PR #9
│   └── step-5.md            # Wire up (4 UoWs) → PR #10
│
├── phase-4/                  # Cleanup
│   ├── README.md
│   ├── step-1.md            # Dead code (5 UoWs) → PR #11
│   └── step-2.md            # Module exports cleanup (1 UoW) → PR #11
│
└── phase-5/                  # Hardening
    ├── README.md
    ├── step-1.md            # Testing (3 UoWs)
    ├── step-2.md            # Documentation & TODO (6 UoWs) → PR #12
    └── step-3.md            # Release prep (3 UoWs)
```

---

## Related Files

- `.teams/TEAM_001_refactor_generic_platform_support.md` — Team log
- `bazzite-optimizer.py` — Main script to refactor
