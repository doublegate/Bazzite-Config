# Phase 1, Step 3 — Audit Hard-coded Hardware References (All Files)

**Parent**: [Phase 1](README.md)
**Estimated Time**: 45 minutes
**Output**: List of hardware references to make dynamic across entire codebase

---

## UoW 1.3.1: Audit all hard-coded hardware strings

**Goal**: Identify all hard-coded hardware models (CPU/GPU/RAM).

**Task**:
```bash
# Search ALL Python and Shell files in the repo
grep -rn "RTX 5080\|RTX 4090\|i9-10850K\|Blackwell\|64GB\|16GB\|I225-V" --include="*.py" --include="*.sh" .
```

**Expected scope**:
- `bazzite-optimizer.py` — Primary (GPU scripts, CPU scripts, RAM config)
- `ref_scripts/` — Reference implementations
- Embedded shell scripts in Python strings

**Document in**: `.planning/refactor-generic-platform/audit/hardware-audit.md`

**Format**:
```markdown
# Hard-coded Hardware Audit

## Summary
| Hardware | Type | Occurrences | Files |
|----------|------|-------------|-------|
| RTX 5080 | GPU | X | Y |
| Blackwell | GPU Arch | X | Y |
| i9-10850K | CPU | X | Y |
| 64GB | RAM | X | Y |
| 16GB | VRAM | X | Y |
| I225-V | NIC | X | Y |

## Detailed References

### GPU References (RTX 5080 / Blackwell)
| File | Line | Context | Abstraction Needed |
|------|------|---------|--------------------|
FILL

### CPU References (i9-10850K)
| File | Line | Context | Abstraction Needed |
|------|------|---------|--------------------|
FILL

### RAM/VRAM References (64GB / 16GB)
| File | Line | Context | Abstraction Needed |
|------|------|---------|--------------------|
FILL
```

---

## Step Exit Criteria

- [ ] `audit/hardware-audit.md` created with ALL files
- [ ] Each reference categorized by type (GPU, CPU, RAM, NIC)
