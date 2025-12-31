# Refactor Plan: Generic Platform Support

**Team**: TEAM_001
**Created**: 2025-12-31
**Status**: Planning Complete (UoW Structure)

---

## Executive Summary

Transform `bazzite-config` from a Bazzite-specific gaming optimizer into a **generic Linux gaming optimizer** that supports:

1. **rpm-ostree immutable systems**: Bazzite, Silverblue, Kinoite, Aurora
2. **Traditional RPM systems**: Fedora Workstation, Ultramarine, CentOS Stream
3. **Debian-based systems**: Ubuntu, Debian, Pop!_OS

While keeping **Bazzite as a first-class citizen** with all its features intact.

---

## Document Structure

Each phase document follows this hierarchy:
- **Phase** → High-level goal
- **Step** → One PR (Pull Request)
- **UoW** → Unit of Work (one task for an SLM to execute)

---

## Phase Overview

| Phase | File | PRs | Focus |
|-------|------|-----|-------|
| 1 | [phase-1-discovery.md](phase-1-discovery.md) | None | Audit and baseline |
| 2 | [phase-2-abstraction.md](phase-2-abstraction.md) | #1-5 | Build platform module |
| 3 | [phase-3-migration.md](phase-3-migration.md) | #6-10 | Migrate existing code |
| 4 | [phase-4-cleanup.md](phase-4-cleanup.md) | #11 | Remove dead code |
| 5 | [phase-5-hardening.md](phase-5-hardening.md) | #12 | Docs and release |

---

## PR → Step Mapping

| PR | Step | Description | Testable on Ultramarine |
|----|------|-------------|-------------------------|
| #1 | 2.1-2.2 | Platform detection + base classes | ✅ |
| #2 | 2.5 | rpm-ostree kernel params | ❌ (needs Bazzite) |
| #3 | 2.3 | GRUB kernel params | ✅ |
| #4 | 2.4 | Package managers (dnf, apt) | ✅ |
| #5 | 2.6 | PlatformServices factory | ✅ |
| #6 | 3.1 | Migrate KernelOptimizer | ✅ |
| #7 | 3.2 | Migrate package installation | ✅ |
| #8 | 3.3 | Conditional Bazzite features | ✅ |
| #9 | 3.4 | Dynamic hardware UI | ✅ |
| #10 | 3.5 | Wire up PlatformServices | ✅ |
| #11 | 4.1 | Remove dead code | ✅ |
| #12 | 5.2 | Documentation updates | ✅ |

---

## UoW Count Per Phase

| Phase | Steps | Total UoWs | Avg per Step |
|-------|-------|------------|--------------|
| 1 | 4 | 10 | 2.5 |
| 2 | 6 | 26 | 4.3 |
| 3 | 5 | 22 | 4.4 |
| 4 | 2 | 7 | 3.5 |
| 5 | 3 | 11 | 3.7 |
| **Total** | **20** | **76** | **3.8** |

---

## Quick Start

```bash
# 1. Read Phase 1 (audit)
cat .planning/refactor-generic-platform/phase-1-discovery.md

# 2. Establish baseline
pytest -q

# 3. Start Phase 2, Step 2.1, UoW 2.1.1
mkdir -p platform/immutable platform/traditional
```

---

## Files in This Plan

### Planning Documents
- `README.md` — This overview
- `GITHUB_ISSUES.md` — 21 GitHub issues
- `PULL_REQUESTS.md` — 14 PR descriptions
- `PR_DEPENDENCY_GRAPH.md` — Dependency graph + testing strategy

### Phase Documents (UoW Structure)
- `phase-1-discovery.md` — Audit and baseline (no PRs)
- `phase-2-abstraction.md` — Platform module (PRs #1-5)
- `phase-3-migration.md` — Migration (PRs #6-10)
- `phase-4-cleanup.md` — Dead code removal (PR #11)
- `phase-5-hardening.md` — Docs and release (PR #12)

### Related Files
- `.teams/TEAM_001_refactor_generic_platform_support.md` — Team log
- `bazzite-optimizer.py` — Main script to refactor
