# Phase 1, Step 1 — Audit rpm-ostree Dependencies (All Files)

**Parent**: [Phase 1](README.md)
**Estimated Time**: 45 minutes
**Output**: Documented list of all rpm-ostree call sites across the entire codebase

---

## UoW 1.1.1: Audit all rpm-ostree calls

**Goal**: Identify every location where `rpm-ostree` is called (kargs, install, status).

**Pre-step**: Create audit directory
```bash
mkdir -p .planning/refactor-generic-platform/audit
```

**Task**:
```bash
# Search ALL Python and Shell files in the repo
grep -rn "rpm-ostree" --include="*.py" --include="*.sh" .
```

**Expected scope** (based on initial scan):
- `bazzite-optimizer.py` (~38 matches)
- `reset-bazzite-defaults.sh` (~20 matches)
- `ref_scripts/` (various)
- `tests/` (mocks and fixtures)
- `tools/` (utility scripts)

**Document in**: `.planning/refactor-generic-platform/audit/rpm-ostree-audit.md`

**Format**:
```markdown
# rpm-ostree Call Sites Audit

## Summary
| File | Match Count | Migration Priority |
|------|-------------|--------------------|
| bazzite-optimizer.py | X | High |
| reset-bazzite-defaults.sh | X | High |
| ... | ... | ... |

## Detailed Call Sites

### bazzite-optimizer.py
| Line | Command | Context |
| 1234 | rpm-ostree kargs | _apply_kernel_param_batch() |
| 2338 | rpm-ostree install | BaseOptimizer.install_package() |
| ... | ... | ... |
```

---

## Step Exit Criteria

- [ ] `audit/rpm-ostree-audit.md` created with all call sites
