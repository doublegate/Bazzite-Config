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

## UoW 4.1.5: Run tests after cleanup

**Goal**: Verify nothing broke.

**Task**:
```bash
# All tests
pytest -q

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
- [ ] No direct rpm-ostree calls remaining
- [ ] All tests pass
