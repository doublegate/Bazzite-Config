# Phase 1, Step 3 — Audit Hard-coded Hardware References

**Parent**: [Phase 1](README.md)
**Estimated Time**: 30 minutes
**Output**: List of hardware references to make dynamic

---

## UoW 1.3.1: Audit all hard-coded hardware strings

**Goal**: Identify all hard-coded hardware models (CPU/GPU/RAM).

**Task**:
```bash
grep -n "RTX 5080\|RTX 4090\|i9-10850K\|Blackwell\|64GB" bazzite-optimizer.py
```

**Document in**: `.planning/refactor-generic-platform/audit/hardware-audit.md`

---

## Step Exit Criteria

- [ ] `audit/hardware-audit.md` created
