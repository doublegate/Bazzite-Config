# Phase 2, Step 6 — PlatformServices Factory (PR #5)

**Parent**: [Phase 2](README.md)
**Branch**: `feature/platform-services`
**Dependency**: PRs #1-4 merged
**Estimated Time**: 1 hour

---

## UoW 2.6.1: Create PlatformServices class

**Goal**: Factory that creates platform-specific implementations.

**File**: `platforms/services.py`

**Code**:
```python
import logging
from typing import Optional
from .detection import PlatformInfo, PlatformType
from .base import PackageManager, KernelParamManager

class UnsupportedPlatformError(Exception):
    """Raised when platform is not supported"""
    pass

class PlatformServices:
    """Factory for platform-specific service implementations"""
    
    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self.logger = logging.getLogger(__name__)
        self._package_manager: Optional[PackageManager] = None
        self._kernel_params: Optional[KernelParamManager] = None
    
    @property
    def package_manager(self) -> PackageManager:
        """Get the appropriate package manager for this platform"""
        if self._package_manager is None:
            self._package_manager = self._create_package_manager()
        return self._package_manager
    
    @property
    def kernel_params(self) -> KernelParamManager:
        """Get the appropriate kernel param manager for this platform"""
        if self._kernel_params is None:
            self._kernel_params = self._create_kernel_params()
        return self._kernel_params
    
    def _create_package_manager(self) -> PackageManager:
        if self.platform_info.package_manager == "rpm-ostree":
            from .immutable.rpm_ostree import RpmOstreePackageManager
            return RpmOstreePackageManager()
        elif self.platform_info.package_manager == "dnf":
            from .traditional.rpm import DnfPackageManager
            return DnfPackageManager()
        elif self.platform_info.package_manager == "apt":
            from .traditional.deb import AptPackageManager
            return AptPackageManager()
        else:
            raise UnsupportedPlatformError(
                f"Unsupported package manager: {self.platform_info.package_manager}"
            )
    
    def _create_kernel_params(self) -> KernelParamManager:
        if self.platform_info.boot_method == "rpm-ostree-kargs":
            from .immutable.rpm_ostree import RpmOstreeKernelParams
            return RpmOstreeKernelParams()
        elif self.platform_info.boot_method == "grub":
            from .traditional.grub import GrubKernelParams
            return GrubKernelParams()
        else:
            raise UnsupportedPlatformError(
                f"Unsupported boot method: {self.platform_info.boot_method}"
            )
```

---

## UoW 2.6.2: Update platforms/__init__.py exports

**Goal**: Export PlatformServices and exception.

**Update**: `platforms/__init__.py`

**Code**:
```python
from .detection import PlatformType, PlatformInfo, detect_platform
from .base import PackageManager, KernelParamManager
from .services import PlatformServices, UnsupportedPlatformError

__all__ = [
    "PlatformType", "PlatformInfo", "detect_platform",
    "PackageManager", "KernelParamManager",
    "PlatformServices", "UnsupportedPlatformError"
]
```

---

## UoW 2.6.3: Create unit tests for PlatformServices

**Goal**: Test factory returns correct implementations.

**File**: `tests/unit/test_platform_services.py`

**Code**:
```python
import pytest
from platforms import PlatformType, PlatformInfo, PlatformServices

def make_platform_info(platform_type, pkg_mgr, boot_method):
    return PlatformInfo(
        platform_type=platform_type,
        distro_name="Test",
        distro_version="1.0",
        is_immutable=platform_type in (PlatformType.BAZZITE, PlatformType.FEDORA_OSTREE),
        has_ujust=platform_type == PlatformType.BAZZITE,
        package_manager=pkg_mgr,
        boot_method=boot_method
    )

class TestPlatformServices:
    def test_fedora_traditional_returns_dnf(self):
        info = make_platform_info(PlatformType.FEDORA_TRADITIONAL, "dnf", "grub")
        services = PlatformServices(info)
        assert "Dnf" in type(services.package_manager).__name__
```    
    def test_fedora_traditional_returns_grub(self):
        info = make_platform_info(PlatformType.FEDORA_TRADITIONAL, "dnf", "grub")
        services = PlatformServices(info)
        assert "Grub" in type(services.kernel_params).__name__
```

**Verify**: `pytest tests/unit/test_platform_services.py -v` passes.

---

## Step Exit Criteria

- [ ] `platforms/services.py` exists
- [ ] PlatformServices factory works
- [ ] Unit tests pass
- [ ] Factory returns correct implementations for each platform
