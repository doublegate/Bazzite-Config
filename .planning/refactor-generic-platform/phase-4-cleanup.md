# Phase 4 — Cleanup

**Team**: TEAM_001
**Purpose**: Remove dead code and tighten encapsulation
**Structure**: Each Step = 1 PR, Each UoW = 1 SLM task

---

## Step 4.1: Remove Dead Code (PR #11)

**Branch**: `feature/cleanup-dead-code`
**Dependency**: PR #10 merged and validated
**Estimated Time**: 2 hours

### UoW 4.1.1: Remove enhanced_rpm_ostree_kargs() global function

**Task**: Delete the now-unused global function.

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

### UoW 4.1.2: Remove deprecated methods from KernelOptimizer

**Task**: Remove methods marked as deprecated in Phase 3.

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

### UoW 4.1.3: Remove legacy fallback in install_package()

**Task**: Remove the rpm-ostree → dnf fallback chain.

**File**: `bazzite-optimizer.py`
**Location**: `BaseOptimizer.install_package()` (if any legacy code remains)

**Current** (if exists):
```python
# Try rpm-ostree first
returncode, _, _ = run_command(f"rpm-ostree install {package_name}", ...)
if returncode != 0:
    # Fallback to dnf
    returncode, _, _ = run_command(f"dnf install -y {package_name}", ...)
```

**Action**: Remove fallback logic - now handled by `PackageManager` abstraction.

---

### UoW 4.1.4: Search for and remove any remaining direct rpm-ostree calls

**Task**: Find and remove any leftover direct calls.

```bash
# Find remaining calls
grep -n "rpm-ostree" bazzite-optimizer.py | grep -v "# \|\".*rpm-ostree"

# Should only find:
# - Comments/documentation
# - String literals for logging/messages
# - Imports in platform module (those are fine)
```

**Action**: Remove or migrate any direct subprocess calls found.

---

### UoW 4.1.5: Run tests after cleanup

**Task**: Verify nothing broke.

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

## Step 4.2: Tighten Encapsulation (Optional, can be separate PR)

**Branch**: `feature/encapsulation-cleanup`
**Dependency**: PR #11 merged
**Estimated Time**: 1 hour
**Note**: This step is lower priority

### UoW 4.2.1: Move NVIDIA configs to NvidiaOptimizer

**Task**: Move global NVIDIA configurations to class.

**Current globals**:
- `NVIDIA_MODULE_CONFIG`
- `NVIDIA_XORG_CONFIG`
- `NVIDIA_OPTIMIZATION_SCRIPT`

**Change**: Move to `NvidiaOptimizer` as class constants.

```python
class NvidiaOptimizer(BaseOptimizer):
    _MODULE_CONFIG = """# NVIDIA Gaming Optimizations
    # ... content ...
    """
    
    _XORG_CONFIG = """# NVIDIA X11 Configuration
    # ... content ...
    """
```

---

### UoW 4.2.2: Update platform module __all__ exports

**Task**: Ensure only public API is exported.

**File**: `platform/__init__.py`

```python
__all__ = [
    # Public API only
    "PlatformType",
    "PlatformInfo", 
    "detect_platform",
    "PlatformServices",
    "UnsupportedPlatformError",
    # Base classes for type hints
    "PackageManager",
    "KernelParamManager",
]
```

---

## Exit Criteria for Phase 4

- [ ] No dead code remaining
- [ ] No direct rpm-ostree calls in optimizer classes
- [ ] All tests pass
- [ ] Validation works on Ultramarine
- [ ] Code is cleaner and more maintainable
