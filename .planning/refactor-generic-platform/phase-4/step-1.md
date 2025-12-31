# Phase 4, Step 1 — Remove Dead Code (PR #11)

**Parent**: [Phase 4](README.md)
**Branch**: `feature/cleanup-dead-code`
**Dependency**: PR #10 merged and validated
**Estimated Time**: 2 hours

---

## UoW 4.1.1: Remove enhanced_rpm_ostree_kargs() function

**Goal**: Delete the now-unused global function.

**File**: `bazzite-optimizer.py`
**Location**: Around line 2200

**Current**:
```python
def enhanced_rpm_ostree_kargs() -> str:
    """Enhanced rpm-ostree kargs command that handles API changes"""
    # ... implementation ...
```

**Action**: Delete entire function (approximately 20 lines).

**Verify**:
```bash
grep -n "enhanced_rpm_ostree_kargs" bazzite-optimizer.py
# Should return nothing after deletion
```

---

## UoW 4.1.2: Remove deprecated methods from KernelOptimizer

**Goal**: Remove methods marked as deprecated in Phase 3.

**File**: `bazzite-optimizer.py`

**Methods to remove**:
- `_ensure_rpm_ostree_ready()` (~40 lines)
- `_wait_for_rpm_ostree_transaction()` (~40 lines)

**Verify**:
```bash
grep -n "_ensure_rpm_ostree_ready\|_wait_for_rpm_ostree_transaction" bazzite-optimizer.py
# Should return nothing
```

---

## UoW 4.1.3: Remove legacy fallback in install_package()

**Goal**: Remove any remaining rpm-ostree → dnf fallback code.

**File**: `bazzite-optimizer.py`
**Location**: `BaseOptimizer.install_package()` (if any legacy code remains)

**Action**: Remove fallback logic - now handled by `PackageManager` abstraction.

---

## UoW 4.1.4: Search for remaining direct rpm-ostree calls

**Goal**: Find and remove any leftover direct calls.

**Task**:
```bash
grep -n "rpm-ostree" bazzite-optimizer.py | grep -v "# \|\".*rpm-ostree"
```

**Expected**: Should only find:
- Comments/documentation
- String literals for logging/messages
- Platform module imports (those are fine)

**Action**: Remove or migrate any direct subprocess calls found.

---

## UoW 4.1.5: Make reset-bazzite-defaults.sh platform-aware

**Goal**: Add platform detection to reset script or create GRUB alternative.

**File**: `reset-bazzite-defaults.sh`
**Issue**: Script has 20 rpm-ostree calls and only works on immutable systems.

**Options** (choose one):
1. Add platform guard at script start, exit gracefully on non-rpm-ostree systems
2. Create parallel `reset-grub-defaults.sh` for traditional systems
3. Make script detect platform and use appropriate method

**Recommended**: Option 1 (minimal change, script is Bazzite-specific by design)

**Implementation**:
```bash
# Add after line 127 (after rpm-ostree status check)
if ! rpm-ostree status >/dev/null 2>&1; then
  echo "This script is designed for rpm-ostree systems (Bazzite, Silverblue, etc.)"
  echo "For traditional systems, manually edit /etc/default/grub and run grub2-mkconfig"
  exit 1
fi
```

**Note**: Added based on Phase 1 audit findings (TEAM_004)

---

## UoW 4.1.6: Run tests after cleanup

**Goal**: Verify nothing broke.

**Task**:
```bash
# All tests
pytest -q --override-ini="addopts="

# Full validation on Ultramarine
sudo ./bazzite-optimizer.py --validate
```

**Pass criteria**:
- All tests pass
- No runtime errors
- Validation completes successfully

---

## Step Exit Criteria

- [ ] `enhanced_rpm_ostree_kargs()` removed
- [ ] Deprecated methods removed
- [ ] No direct rpm-ostree calls remaining in main script
- [ ] `reset-bazzite-defaults.sh` has platform guard
- [ ] All tests pass
