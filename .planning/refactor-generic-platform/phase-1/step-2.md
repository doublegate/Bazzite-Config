# Phase 1, Step 2 — Audit Bazzite-Specific Code (All Files)

**Parent**: [Phase 1](README.md)
**Estimated Time**: 60 minutes
**Output**: List of Bazzite-only features across entire codebase

---

## UoW 1.2.1: Audit ujust and Bazzite detection

**Goal**: Identify all Bazzite-specific code (ujust and "bazzite" string).

**Task**:
```bash
# Search ALL Python and Shell files in the repo
grep -rn "ujust\|bazzite" --include="*.py" --include="*.sh" -i .
```

**Expected scope** (based on initial scan — 69 files!):
- `bazzite-optimizer.py` (~97 matches) — Primary target
- `tests/test_bazzite_optimizer_*.py` — Test fixtures
- `gui/` module — GUI references
- `install-gui.sh` (~27 matches) — Install script
- `ref_scripts/` — Reference implementations
- `steamdeck_support/` — Steam Deck code
- `mobile_api/` — API server

**Document in**: `.planning/refactor-generic-platform/audit/bazzite-audit.md`

**Format**:
```markdown
# Bazzite-Specific Code Audit

## Summary
| File | Match Count | Type | Migration Action |
|------|-------------|------|------------------|
| bazzite-optimizer.py | 97 | Core | Make conditional |
| gui/*.py | X | GUI | Make conditional |
| tests/*.py | X | Tests | Update fixtures |
| ... | ... | ... | ... |

## Categories

### 1. ujust Commands (make conditional on has_ujust)
| File | Line | Command |
|------|------|---------|FILL

### 2. Bazzite Detection (use PlatformType.BAZZITE)
| File | Line | Code |
|------|------|------|FILL

### 3. Bazzite-branded strings (rename to generic)
| File | Line | String | Suggested Replacement |
|------|------|--------|----------------------|FILL

### 4. Log/config paths with "bazzite" (consider renaming)
| File | Line | Path |
|------|------|------|FILL
```

---

## Step Exit Criteria

- [ ] `audit/bazzite-audit.md` created with ALL files
- [ ] Matches categorized by type (ujust, detection, branding, paths)
