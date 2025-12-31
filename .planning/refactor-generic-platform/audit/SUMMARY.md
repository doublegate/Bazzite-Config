# Phase 1 Audit Summary

**Date**: 2025-12-31
**Auditor Team**: TEAM_004
**Commit**: 889c2fe

## Scope

| Category | Files Audited | Total Matches |
|----------|---------------|---------------|
| rpm-ostree | 7 (excl. ref_scripts) | 77 |
| Bazzite/ujust | 56 (excl. ref_scripts) | 349 |
| Hard-coded hardware | 10 (excl. ref_scripts) | 91 |

## Key Findings

### 1. rpm-ostree Call Sites

- **Primary file**: `bazzite-optimizer.py` (38 calls)
- **Other files requiring migration**:
  - `reset-bazzite-defaults.sh` (20 calls) — Impact: **High** (dedicated reset script)
  - `tests/` (13 calls) — Impact: Medium (mock updates needed)
  - `tools/mcp_quick_queries.sh` (6 calls) — Impact: Low (dev tooling)

**Abstraction needed**:
1. `KernelParamManager` for kargs operations
2. `PackageManager` for rpm-ostree install
3. Transaction handling utilities

### 2. Bazzite-Specific Code

- **Features to make conditional**:
  - ujust commands (already disabled, only comments remain)
  - Bazzite detection at line 1945 (use PlatformType)
  - rpm-ostree preference at lines 2336, 3050, 5368

- **Naming/branding decisions needed**:
  - 15+ path references to `/var/log/bazzite-optimizer/`
  - Logger name `bazzite-optimizer`
  - Systemd service descriptions
  - Main script name (optional rename)

### 3. Hard-coded Hardware

- **References to remove/abstract**:
  - RTX 5080: 45 locations across 8 files
  - i9-10850K: 12 locations across 5 files
  - 64GB RAM: 8 locations across 5 files
  - I225-V NIC: 5 locations across 2 files

- **Already have detection functions** that can be extended:
  - `get_cpu_info()` 
  - `check_nvidia_gpu_exists()`
  - RAM via `/proc/meminfo`

## Impact on Later Phases

### Phase 2 Updates Needed

- [x] Step 2.5 covers rpm-ostree kargs extraction ✓
- [x] Step 2.4 covers package manager abstraction ✓
- [ ] **Missing**: No mention of `reset-bazzite-defaults.sh`

### Phase 3 Updates Needed

- [x] Step 3.3 covers conditional Bazzite features ✓
- [x] Step 3.4 covers dynamic hardware UI ✓
- [x] Step 3.4 expanded: `gaming-maintenance-suite.sh`, `gaming-monitor-suite.py` (TEAM_004)
- [x] **Step 3.6 added**: Embedded shell script migration (TEAM_005)
- [x] **Step 3.7 added**: Log message & branding cleanup (TEAM_005)
- [ ] **Decision needed**: Path renaming (`bazzite-optimizer` → `linux-gaming-optimizer`?)

### Phase 4 Updates Needed

- [ ] **Add UoW**: Create `reset-grub-defaults.sh` or make existing script platform-aware
- [ ] Consider dead code from disabled ujust commands

### Phase 5 Updates Needed

- [ ] **Add UoW**: Update test mocks after abstraction layer is added
- [ ] Documentation should reflect dynamic hardware detection

## Test Baseline Status

| Metric | Count |
|--------|-------|
| Total tests | 297 |
| Passing | 292 |
| Failing | 0 |
| Skipped | 5 |
| Import errors | 2 (pandas, websockets — optional deps) |

**Baseline**: ✅ GREEN

## Risks & Blockers

### Risks

1. **Scope creep**: 349 Bazzite references across 56 files is larger than initially estimated
2. **Breaking changes**: Path renaming would affect existing Bazzite users
3. **Test updates**: 13 test files reference rpm-ostree, will need mock updates

### Blockers

None — Phase 2 can proceed.

### Open Questions for User

1. **Path renaming**: Should `/var/log/bazzite-optimizer/` become `/var/log/linux-gaming-optimizer/`?
   - Affects: logs, configs, backups, systemd services
   - Impact: Migration path needed for existing users

2. **Script renaming**: Should `bazzite-optimizer.py` be renamed?
   - Lower priority, can defer to Phase 5

## Detailed Audit Documents

- [rpm-ostree-audit.md](rpm-ostree-audit.md)
- [bazzite-audit.md](bazzite-audit.md)
- [hardware-audit.md](hardware-audit.md)
- [test-summary.md](test-summary.md)
- [test-baseline.txt](test-baseline.txt)
