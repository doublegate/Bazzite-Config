# TEAM_014: Proactive Bug Investigation - Kernel/CLI/UX Edge Cases

**Created**: 2025-12-31
**Status**: In Progress

## Mission

Proactively find and fix bugs related to:
1. Kernel build-time and backup edge cases
2. CLI user experience predictability
3. Help text and description consistency

## Investigation Areas

### Area 1: Kernel Profile Management
- Is baseline save/restore reliable?
- What happens if baseline already exists?
- What if kernel profile directory doesn't exist?
- Edge cases around GRUB vs rpm-ostree

### Area 2: CLI Help Text Consistency
- Are all arguments documented?
- Do descriptions match actual behavior?
- Are error messages helpful?

### Area 3: User Experience Predictability
- Does the optimizer clearly communicate what it will do?
- Are there silent failures?
- Is the output consistent and readable?

## Findings

### Bug 1: Version Mismatch in Help Text
- **Symptom**: `--help` showed "Bazzite DX Ultimate Gaming Optimizer v4" but banner shows "v5.0.0"
- **Fix**: Changed description to use `f'Linux Gaming Optimizer v{SCRIPT_VERSION}'`
- **Status**: FIXED

### Bug 2: Missing Kernel Examples in Help
- **Symptom**: No examples for kernel profile management commands
- **Fix**: Added "Kernel Management" section with examples
- **Status**: FIXED

### Bug 3: Misleading Baseline Save Messages
- **Symptom**: `--save-baseline` said "Failed (may already exist)" when baseline exists, but `save_baseline()` returns True in that case
- **Fix**: Check if baseline exists before calling save, show appropriate message
- **Status**: FIXED

### Bug 4: Inverted Logic in Automatic Baseline
- **Symptom**: During optimization, "baseline saved" shown when it already existed
- **Fix**: Same pattern - check existence first, show correct message
- **Status**: FIXED

### Bug 5: Unhelpful Profile Not Found Errors
- **Symptom**: `--kernel-profile nonexistent` just said "Failed to apply"
- **Fix**: Check if profile exists first, show available profiles
- **Status**: FIXED

### Bug 6: Same for --kernel-diff
- **Symptom**: `--kernel-diff nonexistent` didn't show available profiles
- **Fix**: Added available profiles to error output
- **Status**: FIXED

## Progress Log

- [x] Audit CLI help text
- [x] Check kernel profile edge cases
- [x] Review error handling
- [x] Fix identified issues

## Handoff Notes

All CLI/UX bugs related to kernel management have been fixed. The remaining hardware abstraction issues (i9-10850K, 64GB RAM, I225-V hard-coding) are tracked separately in the Phase 3 planning documents.
