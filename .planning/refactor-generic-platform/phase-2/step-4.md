# Phase 2, Step 4 — Package Managers (PR #4)

**Parent**: [Phase 2](README.md)
**Branch**: `feature/package-managers`
**Estimated Time**: 45 minutes

> **Note**: AptPackageManager deferred to stretch goals. This step focuses on DnfPackageManager only.

---

## UoW 2.4.1: Implement DnfPackageManager

**Goal**: Create package manager for dnf-based systems.

**Files**: 
- `platforms/traditional/rpm.py` (Dnf)

**Dnf Implementation**:
```python
import logging
import subprocess
from typing import List
from ..base import PackageManager

class DnfPackageManager(PackageManager):
    """Package management via dnf"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def install(self, packages: List[str], timeout: int = 300) -> bool:
        cmd = ["sudo", "dnf", "install", "-y"] + packages
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=timeout)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
    
    def remove(self, packages: List[str]) -> bool:
        cmd = ["sudo", "dnf", "remove", "-y"] + packages
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        return result.returncode == 0
    
    def is_installed(self, package: str) -> bool:
        result = subprocess.run(["rpm", "-q", package], capture_output=True)
        return result.returncode == 0
    
    def update(self) -> bool:
        result = subprocess.run(["sudo", "dnf", "makecache"], capture_output=True, timeout=120)
        return result.returncode == 0
```

---

## UoW 2.4.2: Create unit tests for DnfPackageManager

**Goal**: Test DnfPackageManager with mocks.

**File**: `tests/unit/test_dnf_package_manager.py`

**Code**:
```python
import pytest
from unittest.mock import patch, MagicMock
from platforms.traditional.rpm import DnfPackageManager

class TestDnfPackageManager:
    def test_is_installed_true(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            dnf = DnfPackageManager()
            assert dnf.is_installed("python3") == True
    
    def test_is_installed_false(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            dnf = DnfPackageManager()
            assert dnf.is_installed("nonexistent-pkg") == False
```

---

## Step Exit Criteria

- [ ] `platforms/traditional/rpm.py` exists with DnfPackageManager
- [ ] Unit tests pass

> **Deferred**: `platforms/traditional/deb.py` (AptPackageManager) moved to stretch goals
