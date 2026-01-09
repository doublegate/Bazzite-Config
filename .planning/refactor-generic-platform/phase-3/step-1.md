# Phase 3, Step 1 — Migrate KernelOptimizer (PR #6)

**Parent**: [Phase 3](README.md)
**Branch**: `feature/migrate-kernel-optimizer`
**Dependency**: PR #5 merged
**Estimated Time**: 3 hours

---

## UoW 3.1.1: Add platform_services parameter to KernelOptimizer

**Goal**: Modify `KernelOptimizer.__init__()` to accept optional `PlatformServices`.

**File**: `bazzite-optimizer.py`
**Location**: `class KernelOptimizer` (around line 4912)

**Current**:
```python
class KernelOptimizer(BaseOptimizer):
    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
```

**Change to**:
```python
class KernelOptimizer(BaseOptimizer):
    def __init__(self, logger: logging.Logger, platform_services=None):
        super().__init__(logger)
        self._platform_services = platform_services
        self._kernel_params = None
    
    @property
    def kernel_params(self):
        """Lazy-load kernel param manager"""
        if self._kernel_params is None:
            if self._platform_services:
                self._kernel_params = self._platform_services.kernel_params
            else:
                from platforms.immutable.rpm_ostree import RpmOstreeKernelParams
                self._kernel_params = RpmOstreeKernelParams()
        return self._kernel_params
```

**Verify**: Class still instantiates without errors.

---

## UoW 3.1.2: Migrate _get_current_kernel_params()

**Goal**: Replace internal logic with call to `kernel_params.get_current_params()`.

**File**: `bazzite-optimizer.py`
**Location**: `KernelOptimizer._get_current_kernel_params()` (around line 5120)

**Change to**:
```python
def _get_current_kernel_params(self) -> List[str]:
    """Get current kernel parameters using platform abstraction"""
    try:
        return self.kernel_params.get_current_params()
    except Exception as e:
        self.logger.error(f"Failed to get kernel params: {e}")
        return []
```

**Verify**: Returns correct params on Ultramarine (from grub).

---

## UoW 3.1.3: Migrate _apply_kernel_param_batch()

**Goal**: Replace rpm-ostree kargs calls with `kernel_params.append_params()`.

**File**: `bazzite-optimizer.py`
**Location**: `KernelOptimizer._apply_kernel_param_batch()` (around line 5170)

**Change to**:
```python
def _apply_kernel_param_batch(self, params: List[str], mode: str = "append") -> bool:
    """Apply kernel parameters using platform abstraction"""
    try:
        if mode == "append":
            return self.kernel_params.append_params(params)
        elif mode == "replace":
            return self.kernel_params.append_params(params)
        else:
            self.logger.error(f"Unknown mode: {mode}")
            return False
    except Exception as e:
        self.logger.error(f"Failed to apply kernel params: {e}")
        return False
```

---

## UoW 3.1.4: Migrate _remove_kernel_params()

**Goal**: Replace rpm-ostree kargs --delete with abstraction.

**File**: `bazzite-optimizer.py`
**Location**: `KernelOptimizer._remove_kernel_params()` (around line 5480)

**Change to**:
```python
def _remove_kernel_params(self, params: List[str]) -> bool:
    """Remove kernel parameters using platform abstraction"""
    try:
        return self.kernel_params.remove_params(params)
    except Exception as e:
        self.logger.error(f"Failed to remove kernel params: {e}")
        return False
```

---

## UoW 3.1.5: Mark deprecated methods

**Goal**: Mark rpm-ostree specific methods as deprecated.

**Methods to deprecate**:
- `_ensure_rpm_ostree_ready()`
- `_wait_for_rpm_ostree_transaction()`

**Change**:
```python
def _ensure_rpm_ostree_ready(self) -> bool:
    """DEPRECATED: Use self.kernel_params instead"""
    self.logger.warning("_ensure_rpm_ostree_ready is deprecated")
    return True
```

---

## UoW 3.1.6: Update apply_kernel_parameters() main method

**Goal**: Simplify the main method to use abstraction.

**File**: `bazzite-optimizer.py`
**Location**: `KernelOptimizer.apply_kernel_parameters()` (around line 4916)

**Change to**:
```python
def apply_kernel_parameters(self) -> bool:
    """Apply kernel parameters for selected profile"""
    self.logger.info("Applying kernel parameters...")
    
    params = self._get_profile_kernel_params()
    
    if not self.kernel_params.append_params(params):
        self.logger.error("Failed to apply kernel parameters")
        return False
    
    if self.kernel_params.requires_reboot():
        self.logger.info("Kernel parameter changes require reboot")
    
    return True
```

---

## UoW 3.1.7: Test KernelOptimizer migration

**Goal**: Verify migration works on Ultramarine.

**Test command**:
```bash
sudo python3 -c "
import sys
sys.path.insert(0, '.')
import logging
logging.basicConfig(level=logging.INFO)

from platforms import detect_platform, PlatformServices
from bazzite_optimizer import KernelOptimizer

platform_info = detect_platform()
services = PlatformServices(platform_info)

ko = KernelOptimizer(logging.getLogger(), platform_services=services)
params = ko._get_current_kernel_params()
print(f'Current params: {params}')
print(f'Using: {type(ko.kernel_params).__name__}')
"
```

**Expected on Ultramarine**:
- `Using: GrubKernelParams`
- Params from `/etc/default/grub`

---

## Step Exit Criteria

- [ ] KernelOptimizer accepts platform_services
- [ ] All kernel param methods use abstraction
- [ ] Deprecated methods marked
- [ ] Tests pass on Ultramarine
