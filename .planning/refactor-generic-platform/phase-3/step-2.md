# Phase 3, Step 2 — Migrate Package Installation (PR #7)

**Parent**: [Phase 3](README.md)
**Branch**: `feature/migrate-package-install`
**Dependency**: PR #5 merged
**Estimated Time**: 2 hours

---

## UoW 3.2.1: Add platform_services to BaseOptimizer

**Goal**: Modify `BaseOptimizer.__init__()` to accept platform services.

**File**: `bazzite-optimizer.py`
**Location**: `class BaseOptimizer` (around line 2222)

**Change to**:
```python
class BaseOptimizer:
    def __init__(self, logger: logging.Logger, platform_services=None):
        self.logger = logger
        self._platform_services = platform_services
        self._package_manager = None
    
    @property
    def package_manager(self):
        """Lazy-load package manager"""
        if self._package_manager is None:
            if self._platform_services:
                self._package_manager = self._platform_services.package_manager
            else:
                from platforms.traditional.rpm import DnfPackageManager
                self._package_manager = DnfPackageManager()
        return self._package_manager
```

---

## UoW 3.2.2: Migrate BaseOptimizer.install_package()

**Goal**: Replace direct rpm-ostree/dnf calls with abstraction.

**File**: `bazzite-optimizer.py`
**Location**: `BaseOptimizer.install_package()` (around line 2336)

**Change to**:
```python
def install_package(self, package_name: str, timeout: int = 300) -> bool:
    """Install a package using platform-appropriate manager"""
    self.logger.debug(f"Installing package: {package_name}")
    try:
        return self.package_manager.install([package_name], timeout=timeout)
    except Exception as e:
        self.logger.error(f"Failed to install {package_name}: {e}")
        return False
```

---

## UoW 3.2.3: Update all BaseOptimizer subclass __init__ calls

**Goal**: Pass `platform_services` through to all subclasses.

**Subclasses to update**:
- `NvidiaOptimizer`
- `CPUOptimizer`
- `MemoryOptimizer`
- `NetworkOptimizer`
- `AudioOptimizer`
- `GamingToolsOptimizer`
- `SystemdServiceOptimizer`
- `PlasmaOptimizer`
- `BootInfrastructureOptimizer`
- `BazziteOptimizer`

**Example change**:
```python
class NvidiaOptimizer(BaseOptimizer):
    def __init__(self, logger: logging.Logger, platform_services=None):
        super().__init__(logger, platform_services)
```

---

## UoW 3.2.4: Migrate NvidiaOptimizer._install_nvidia_drivers()

**Goal**: Update NVIDIA driver installation to use abstraction.

**File**: `bazzite-optimizer.py`
**Location**: `NvidiaOptimizer._install_nvidia_drivers()` (around line 3050)

**Change to**:
```python
def _install_nvidia_drivers(self) -> bool:
    """Install NVIDIA drivers using platform package manager"""
    packages = [
        "akmod-nvidia-open",
        "xorg-x11-drv-nvidia-open",
        "nvidia-vaapi-driver",
        "nvidia-settings"
    ]
    
    for package in packages:
        if not self.package_manager.is_installed(package):
            self.logger.info(f"Installing {package}")
            if not self.install_package(package):
                self.logger.warning(f"Failed to install {package}")
    
    return True
```

---

## UoW 3.2.5: Migrate GamingToolsOptimizer package installs

**Goal**: Update gaming tools to use abstraction.

**File**: `bazzite-optimizer.py`
**Location**: `class GamingToolsOptimizer` (around line 4655)

**Change**: Replace any direct package manager calls with `self.install_package()`.

---

## UoW 3.2.6: Test package installation

**Goal**: Verify migration works on Ultramarine.

**Test command**:
```bash
sudo python3 -c "
import sys
sys.path.insert(0, '.')
import logging
logging.basicConfig(level=logging.INFO)

from platforms import detect_platform, PlatformServices
from bazzite_optimizer import GamingToolsOptimizer

platform_info = detect_platform()
services = PlatformServices(platform_info)

gto = GamingToolsOptimizer(logging.getLogger(), platform_services=services)
print(f'Using: {type(gto.package_manager).__name__}')
print(f'htop installed: {gto.package_manager.is_installed(\"htop\")}')
"
```

**Expected on Ultramarine**:
- `Using: DnfPackageManager`

---

## Step Exit Criteria

- [ ] BaseOptimizer accepts platform_services
- [ ] All subclasses updated
- [ ] install_package() uses abstraction
- [ ] Tests pass on Ultramarine
