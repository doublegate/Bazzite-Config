# Phase 1, Step 1 — Audit rpm-ostree Dependencies

**Parent**: [Phase 1](README.md)
**Estimated Time**: 30 minutes
**Output**: Documented list of all rpm-ostree call sites

---

## UoW 1.1.1: Audit all rpm-ostree calls

**Goal**: Identify every location where `rpm-ostree` is called (kargs, install, status).

**Task**:
```bash
grep -n "rpm-ostree" bazzite-optimizer.py
```

**Document in**: `.planning/refactor-generic-platform/audit/rpm-ostree-audit.md`

**Format**:
```markdown
# rpm-ostree Call Sites Audit

| Line | Command | Context |
|------|---------|---------|
| 1234 | rpm-ostree kargs | _apply_kernel_param_batch() |
| 2338 | rpm-ostree install | BaseOptimizer.install_package() |
| ... | ... | ... |
```

---

## Step Exit Criteria

- [ ] `audit/rpm-ostree-audit.md` created with all call sites
