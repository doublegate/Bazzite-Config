# Bazzite-Specific Code Audit

**Date**: 2025-12-31
**Auditor Team**: TEAM_004
**Commit**: 889c2fe

## Summary

| File | Match Count | Type | Migration Action |
|------|-------------|------|------------------|
| `bazzite-optimizer.py` | 97 | Core | Make conditional / rename |
| `tests/test_bazzite_optimizer_cli_args.py` | 75 | Tests | Update imports/names |
| `install-gui.sh` | 27 | Install script | Make platform-aware |
| `reset-bazzite-defaults.sh` | 11 | Reset script | Platform guard |
| `bazzite-optimizer-gui.py` | 9 | GUI wrapper | Rename consideration |
| `ml_engine/tests/test_api_server.py` | 9 | Tests | Update fixtures |
| `tests/test_bazzite_optimizer_kernel_params.py` | 7 | Tests | Update imports |
| `mobile-app/build-ios.sh` | 7 | Mobile build | Update refs |
| `gui/utils/remote_api.py` | 6 | GUI | Update API paths |
| `ml_engine/cloud_api/api_server.py` | 6 | API | Update paths |
| `tests/test_bazzite_optimizer_core_utils.py` | 6 | Tests | Update imports |
| (41 more files) | 1-5 each | Various | Various |

**Total (excluding ref_scripts/)**: 349 matches across 56 files

## Categories

### 1. ujust Commands (make conditional on `has_ujust`)

| File | Line | Code |
|------|------|------|
| `bazzite-optimizer.py` | 1564-1578 | `BAZZITE_UJUST_COMMANDS = []` (already empty, but comments reference ujust) |

**Note**: ujust commands are already disabled. Only comments remain.

### 2. Bazzite Detection (use `PlatformType.BAZZITE`)

| File | Line | Code |
|------|------|------|
| `bazzite-optimizer.py` | 1945 | `if variant in ["silverblue", "kinoite", "sericea", "bazzite"]:` |
| `bazzite-optimizer.py` | 2172 | `"""Validate System76 scheduler... (replaces GameMode in Bazzite)"""` |
| `bazzite-optimizer.py` | 2336 | `# Install via rpm-ostree first for Bazzite immutable system` |
| `bazzite-optimizer.py` | 3050 | `# For Bazzite, use rpm-ostree` |
| `bazzite-optimizer.py` | 4916 | `def apply_bazzite_kernel_params(self)` |
| `bazzite-optimizer.py` | 5368 | `"Bazzite immutable system detected"` |

### 3. Bazzite-branded Strings (rename to generic)

| File | Line | String | Suggested Replacement |
|------|------|--------|----------------------|
| `bazzite-optimizer.py` | 3 | `Universal Support for Fedora-based Systems (Bazzite, Silverblue, Workstation)` | Keep (accurate) |
| `bazzite-optimizer.py` | 457, 576 | `/var/log/bazzite-optimizer/` | `/var/log/linux-gaming-optimizer/` |
| `bazzite-optimizer.py` | 1076-1104 | `LOGROTATE_CONFIG` paths | Update paths |
| `bazzite-optimizer.py` | 1117 | `BACKUP_DIR="/var/backups/bazzite-optimizer"` | `/var/backups/linux-gaming-optimizer` |
| `bazzite-optimizer.py` | 1281 | `# Bazzite DX Complete Gaming Mode` | `# Linux Gaming Mode` |
| `bazzite-optimizer.py` | 1314 | `/etc/bazzite-optimizer/profiles/` | `/etc/linux-gaming-optimizer/profiles/` |
| `bazzite-optimizer.py` | 1467 | `Description=Bazzite Gaming Performance` | `Linux Gaming Performance` |
| `bazzite-optimizer.py` | 1588 | `bazzite-optimizer/logs` | `linux-gaming-optimizer/logs` |
| `bazzite-optimizer.py` | 1626 | `logger = logging.getLogger('bazzite-optimizer')` | `linux-gaming-optimizer` |
| `bazzite-optimizer.py` | 1656 | `/etc/logrotate.d/bazzite-optimizer` | Update path |
| `bazzite-optimizer.py` | 1858 | `bazzite-optimizer/backups` | Update path |
| `bazzite-optimizer.py` | 2842-2854 | Systemd timer descriptions | Update names |

### 4. Log/Config Paths with "bazzite"

| Path Pattern | Occurrences | Files |
|--------------|-------------|-------|
| `/var/log/bazzite-optimizer/` | ~15 | bazzite-optimizer.py |
| `/etc/bazzite-optimizer/` | ~5 | bazzite-optimizer.py |
| `/var/backups/bazzite-optimizer/` | ~3 | bazzite-optimizer.py |
| `/etc/logrotate.d/bazzite-optimizer` | 1 | bazzite-optimizer.py |

### 5. File/Script Names with "bazzite"

| Current Name | Suggested Rename | Impact |
|--------------|------------------|--------|
| `bazzite-optimizer.py` | Keep or `linux-gaming-optimizer.py` | High — main script |
| `bazzite-optimizer-gui.py` | Keep or `linux-gaming-optimizer-gui.py` | Medium |
| `reset-bazzite-defaults.sh` | Keep (Bazzite-specific) | Low |
| `install-gui.sh` | No change needed | — |

### 6. Test Files

56 test files reference "bazzite" in:
- Import statements (`from bazzite_optimizer import ...`)
- Fixture names
- Test class/function names
- Mock paths

**Recommendation**: If main script is renamed, all tests need import updates.

## Impact on Phase 2-5

### Phase 2 Impact
- Detection logic in step 2.1 should handle the VARIANT_ID check at line 1945

### Phase 3 Impact
- Step 3.3 (Conditional Bazzite features) should cover lines 1564-1578, 2172, 2336, 3050, 5368
- **Missing**: Path renaming not covered in current plan

### Phase 4 Impact
- Dead code removal should consider if any Bazzite-only code paths become unreachable

### Phase 5 Impact
- Documentation updates should reflect new paths if renamed
- Test updates should cover import changes

## Recommendations

1. **Decision needed**: Rename paths from `bazzite-optimizer` to `linux-gaming-optimizer`?
   - Pro: More generic, matches project goal
   - Con: Breaking change for existing users, migration needed

2. Add UoW to Phase 3 or 4 for path/name migration if renaming is approved

3. Test file updates should be a dedicated UoW in Phase 5
