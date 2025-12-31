# Phase 1, Step 2 — Audit Bazzite-Specific Code

**Parent**: [Phase 1](README.md)
**Estimated Time**: 20 minutes
**Output**: List of Bazzite-only features

---

## UoW 1.2.1: Audit ujust and Bazzite detection

**Goal**: Identify all Bazzite-specific code (ujust and "bazzite" string).

**Task**:
```bash
grep -n "ujust\|bazzite" bazzite-optimizer.py -i
```

**Document in**: `.planning/refactor-generic-platform/audit/bazzite-audit.md`

---

## Step Exit Criteria

- [ ] `audit/bazzite-audit.md` created
