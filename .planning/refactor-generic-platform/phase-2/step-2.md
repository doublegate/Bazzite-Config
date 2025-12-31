# Phase 2, Step 2 — Abstract Base Classes (PR #1 continued)

**Parent**: [Phase 2](README.md)
**Branch**: `feature/platform-detection` (same PR as Step 2.1)
**Estimated Time**: 45 minutes

---

## UoW 2.2.1: Create PackageManager and KernelParamManager ABCs

**Goal**: Define abstract interfaces for platform operations.

**File**: `platforms/base.py`

**Code**:
```python
from abc import ABC, abstractmethod
from typing import List, Optional

class PackageManager(ABC):
    """Abstract base class for package management"""
    
    @abstractmethod
    def install(self, packages: List[str], timeout: int = 300) -> bool:
        """Install one or more packages"""
        pass
    
    @abstractmethod
    def remove(self, packages: List[str]) -> bool:
        """Remove one or more packages"""
        pass
    
    @abstractmethod
    def is_installed(self, package: str) -> bool:
        """Check if a package is installed"""
        pass
    
    @abstractmethod
    def update(self) -> bool:
        """Update package database"""
        pass

class KernelParamManager(ABC):
    """Abstract base class for kernel parameter management"""
    
    @abstractmethod
    def get_current_params(self) -> List[str]:
        """Get list of current kernel parameters"""
        pass
    
    @abstractmethod
    def append_params(self, params: List[str]) -> bool:
        """Append kernel parameters (takes effect after reboot)"""
        pass
    
    @abstractmethod
    def remove_params(self, params: List[str]) -> bool:
        """Remove kernel parameters (takes effect after reboot)"""
        pass
    
    @abstractmethod
    def replace_param(self, old: str, new: str) -> bool:
        """Replace a kernel parameter with a new value"""
        pass
    
    @abstractmethod
    def requires_reboot(self) -> bool:
        """Return True if changes require reboot"""
        pass
    
    @abstractmethod
    def get_pending_params(self) -> Optional[List[str]]:
        """Get params that will be active after reboot, or None if same"""
        pass
```

---

## UoW 2.2.2: Update platforms/__init__.py with base classes

**Goal**: Export base classes for type hints.

**Update**: `platforms/__init__.py`

**Code**:
```python
from .detection import PlatformType, PlatformInfo, detect_platform
from .base import PackageManager, KernelParamManager

__all__ = [
    "PlatformType", "PlatformInfo", "detect_platform",
    "PackageManager", "KernelParamManager"
]
```

---

## Step Exit Criteria

- [ ] `platforms/base.py` exists with both ABCs
- [ ] `platforms/__init__.py` exports base classes
- [ ] Both ABCs are importable
