# Phase 3 — Migration

**Team**: TEAM_001
**Purpose**: Migrate existing code to use platform abstraction layer

---

## Steps

| Step | File | PR | Description | UoWs |
|------|------|----|-------------|------|
| 3.1 | [step-1.md](step-1.md) | #6 | Migrate KernelOptimizer | 7 |
| 3.2 | [step-2.md](step-2.md) | #7 | Migrate package installation | 6 |
| 3.3 | [step-3.md](step-3.md) | #8 | Conditional Bazzite features | 4 |
| 3.4 | [step-4.md](step-4.md) | #9 | Dynamic hardware UI & Cleanup | 6 |
| 3.5 | [step-5.md](step-5.md) | #10 | Wire up PlatformServices | 4 |
| 3.6 | [step-6.md](step-6.md) | #10 | Embedded shell script migration | 4 |
| 3.7 | [step-7.md](step-7.md) | #10 | Log message & branding cleanup | 4 |

**Total UoWs**: 35

> **Note**: Steps 3.6-3.7 added by TEAM_005 after gap analysis of Phase 1 audit findings.

---

## PR Dependencies

```
PR #6, #7, #8 ← PR #5 (PlatformServices)
PR #9 ← None (independent)
PR #10 ← PRs #6, #7, #8, #9
```

---

## Exit Criteria

- [ ] KernelOptimizer uses platform abstraction (PR #6)
- [ ] Package installation uses platform abstraction (PR #7)
- [ ] Bazzite features conditional (PR #8)
- [ ] Dynamic hardware in UI (PR #9)
- [ ] Full integration working (PR #10)
- [ ] Embedded shell scripts platform-aware (PR #10)
- [ ] All tests pass on Ultramarine
- [ ] No rpm-ostree errors on traditional systems
- [ ] No ujust errors on non-Bazzite systems
- [ ] `grep -r "rpm-ostree" bazzite-optimizer.py` returns only comments/logs (no direct calls)
