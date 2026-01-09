# Phase 3, Step 3 — Conditional Bazzite Features (PR #8)

**Parent**: [Phase 3](README.md)
**Branch**: `feature/conditional-bazzite`
**Dependency**: PR #5 merged
**Estimated Time**: 1 hour

---

## UoW 3.3.1: Add platform_info to BazziteOptimizer

**Goal**: Modify `BazziteOptimizer` to accept platform info.

**File**: `bazzite-optimizer.py`
**Location**: `class BazziteOptimizer` (around line 6497)

**Change to**:
```python
class BazziteOptimizer(BaseOptimizer):
    """Bazzite-specific optimizations using ujust commands"""
    
    def __init__(self, logger: logging.Logger, platform_services=None, platform_info=None):
        super().__init__(logger, platform_services)
        self._platform_info = platform_info
    
    @property
    def is_bazzite(self) -> bool:
        """Check if running on Bazzite"""
        if self._platform_info:
            return self._platform_info.has_ujust
        import shutil
        return shutil.which("ujust") is not None
```

---

## UoW 3.3.2: Make apply_ujust_commands() conditional

**Goal**: Skip ujust commands if not on Bazzite.

**File**: `bazzite-optimizer.py`
**Location**: `BazziteOptimizer.apply_ujust_commands()` (around line 6500)

**Change to**:
```python
def apply_ujust_commands(self) -> bool:
    """Execute Bazzite ujust commands (only on Bazzite)"""
    if not self.is_bazzite:
        self.logger.info("Skipping Bazzite-specific optimizations (ujust not available)")
        return True  # Return success, not failure
    
    self.logger.info("Applying Bazzite-specific optimizations...")
    
    for command in BAZZITE_UJUST_COMMANDS:
        self.logger.info(f"Executing: {command}")
        returncode, stdout, stderr = run_command(command, check=False, timeout=120)
        
        if returncode != 0:
            self.logger.warning(f"Command failed: {command}")
            self.logger.warning(f"Error: {stderr}")
        else:
            self.logger.info(f"Successfully executed: {command}")
    
    return True
```

---

## UoW 3.3.3: Make validate() conditional

**Goal**: Return empty validation on non-Bazzite.

**File**: `bazzite-optimizer.py`
**Location**: `BazziteOptimizer.validate()` (around line 6520)

**Change to**:
```python
def validate(self) -> Dict[str, bool]:
    """Validate Bazzite optimizations"""
    if not self.is_bazzite:
        self.logger.debug("Skipping Bazzite validation (not on Bazzite)")
        return {}
    
    validations = {}
    returncode, _, _ = run_command("which ujust", check=False)
    validations["ujust_available"] = returncode == 0
    return validations
```

---

## UoW 3.3.4: Test on Ultramarine

**Goal**: Verify no errors on non-Bazzite system.

**Test command**:
```bash
sudo python3 -c "
import sys
sys.path.insert(0, '.')
import logging
logging.basicConfig(level=logging.INFO)

from platforms import detect_platform, PlatformServices
from bazzite_optimizer import BazziteOptimizer

platform_info = detect_platform()
services = PlatformServices(platform_info)

bo = BazziteOptimizer(logging.getLogger(), platform_services=services, platform_info=platform_info)
print(f'Is Bazzite: {bo.is_bazzite}')
result = bo.apply_optimizations()
print(f'Result: {result}')
"
```

**Expected on Ultramarine**:
- `Is Bazzite: False`
- Log: "Skipping Bazzite-specific optimizations"
- `Result: True`

---

## Step Exit Criteria

- [ ] BazziteOptimizer accepts platform_info
- [ ] apply_ujust_commands() skips gracefully
- [ ] validate() returns empty on non-Bazzite
- [ ] No ujust errors on Ultramarine
