# Phase 1 — Discovery and Safeguards

**Team**: TEAM_001
**PR**: None (planning phase only)
**Purpose**: Understand the codebase and establish test baselines

---

## Steps

| Step | File | Description | UoWs |
|------|------|-------------|------|
| 1.1 | [step-1.md](step-1.md) | Audit rpm-ostree dependencies (all files) | 1 |
| 1.2 | [step-2.md](step-2.md) | Audit Bazzite-specific code (all files) | 1 |
| 1.3 | [step-3.md](step-3.md) | Audit hard-coded hardware (all files) | 1 |
| 1.4 | [step-4.md](step-4.md) | Establish test baseline | 2 |
| 1.5 | [step-5.md](step-5.md) | **Consolidate findings & update later phases** | 2 |

**Total UoWs**: 7

---

## Exit Criteria

- [ ] All rpm-ostree call sites documented (across ALL files, not just bazzite-optimizer.py)
- [ ] All Bazzite-specific code documented (across ALL files)
- [ ] All hard-coded hardware references documented (across ALL files)
- [ ] Test baseline established
- [ ] **Consolidated audit summary created**
- [ ] **Phase 2-5 reviewed and updated based on findings**
- [ ] Ready to begin Phase 2
