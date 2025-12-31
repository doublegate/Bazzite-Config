# Phase 2 — Platform Abstraction Layer

**Team**: TEAM_001
**Purpose**: Build the platform abstraction module

---

## Step 2.1: Platform Detection (PR #1)

**Branch**: `feature/platform-detection`
**Estimated Time**: 2-3 hours

### UoW 2.1.1: Create platform module structure

**Task**: Create the directory structure and `__init__.py` files.

```bash
mkdir -p platform/immutable platform/traditional
touch platform/__init__.py
touch platform/immutable/__init__.py
touch platform/traditional/__init__.py
```

**Files created**:
- `platform/__init__.py`
- `platform/immutable/__init__.py`
- `platform/traditional/__init__.py`

---

### UoW 2.1.2: Create PlatformType enum

**Task**: Create `platform/detection.py` with the `PlatformType` enum.

**File**: `platform/detection.py`

```python
from enum import Enum, auto

class PlatformType(Enum):
    """Supported platform types"""
    BAZZITE = auto()           # Bazzite (immutable, rpm-ostree + ujust)
    FEDORA_OSTREE = auto()     # Silverblue, Kinoite, Aurora
    FEDORA_TRADITIONAL = auto() # Fedora Workstation, Ultramarine
    DEBIAN_BASED = auto()      # Ubuntu, Debian, Pop!_OS
    UNKNOWN = auto()
```

**Verify**: File exists and enum is importable.

---

### UoW 2.1.3: Create PlatformInfo dataclass

**Task**: Add `PlatformInfo` dataclass to `platform/detection.py`.

**Add to**: `platform/detection.py`

```python
from dataclasses import dataclass

@dataclass
class PlatformInfo:
    """Platform metadata"""
    platform_type: PlatformType
    distro_name: str
    distro_version: str
    is_immutable: bool
    has_ujust: bool
    package_manager: str  # "rpm-ostree", "dnf", "apt"
    boot_method: str      # "rpm-ostree-kargs", "grub", "systemd-boot"
```

**Verify**: Dataclass is importable and can be instantiated.

---

### UoW 2.1.4: Implement _parse_os_release()

**Task**: Add helper function to parse `/etc/os-release`.

**Add to**: `platform/detection.py`

```python
from pathlib import Path
from typing import Dict

def _parse_os_release() -> Dict[str, str]:
    """Parse /etc/os-release into a dictionary"""
    result = {}
    os_release = Path("/etc/os-release")
    if os_release.exists():
        with open(os_release) as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    key, _, value = line.partition("=")
                    result[key] = value.strip('"')
    return result
```

**Verify**: Returns dict with keys like `NAME`, `VERSION_ID`, `ID`.

---

### UoW 2.1.5: Implement _check_rpm_ostree_deployment()

**Task**: Add helper to check if system is rpm-ostree based.

**Add to**: `platform/detection.py`

```python
import subprocess
import shutil

def _check_rpm_ostree_deployment() -> bool:
    """Check if system has an rpm-ostree deployment"""
    if not shutil.which("rpm-ostree"):
        return False
    try:
        result = subprocess.run(
            ["rpm-ostree", "status", "--json"],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0 and b"deployments" in result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
```

**Verify**: Returns `False` on Ultramarine, `True` on Bazzite.

---

### UoW 2.1.6: Implement _detect_boot_method()

**Task**: Add helper to detect boot configuration method.

**Add to**: `platform/detection.py`

```python
def _detect_boot_method() -> str:
    """Detect how kernel parameters are configured"""
    # Check for GRUB
    if Path("/etc/default/grub").exists():
        return "grub"
    # Check for systemd-boot
    if Path("/boot/loader/entries").exists():
        return "systemd-boot"
    return "unknown"
```

**Verify**: Returns `"grub"` on Ultramarine.

---

### UoW 2.1.7: Implement detect_platform()

**Task**: Implement the main detection function.

**Add to**: `platform/detection.py`

```python
def detect_platform() -> PlatformInfo:
    """Detect the current platform and return metadata"""
    os_info = _parse_os_release()
    is_immutable = _check_rpm_ostree_deployment()
    has_ujust = shutil.which("ujust") is not None
    
    distro_name = os_info.get("NAME", "Unknown")
    distro_version = os_info.get("VERSION_ID", "")
    distro_id = os_info.get("ID", "").lower()
    
    # Determine platform type
    if is_immutable:
        if has_ujust or "bazzite" in distro_id:
            platform_type = PlatformType.BAZZITE
        else:
            platform_type = PlatformType.FEDORA_OSTREE
        package_manager = "rpm-ostree"
        boot_method = "rpm-ostree-kargs"
    elif distro_id in ("fedora", "ultramarine", "nobara", "centos", "rhel"):
        platform_type = PlatformType.FEDORA_TRADITIONAL
        package_manager = "dnf"
        boot_method = _detect_boot_method()
    elif distro_id in ("ubuntu", "debian", "pop", "linuxmint"):
        platform_type = PlatformType.DEBIAN_BASED
        package_manager = "apt"
        boot_method = _detect_boot_method()
    else:
        platform_type = PlatformType.UNKNOWN
        package_manager = "unknown"
        boot_method = "unknown"
    
    return PlatformInfo(
        platform_type=platform_type,
        distro_name=distro_name,
        distro_version=distro_version,
        is_immutable=is_immutable,
        has_ujust=has_ujust,
        package_manager=package_manager,
        boot_method=boot_method
    )
```

**Verify**: Returns correct `PlatformInfo` on Ultramarine.

---

### UoW 2.1.8: Update platform/__init__.py exports

**Task**: Export public API from `platform/__init__.py`.

**File**: `platform/__init__.py`

```python
from .detection import PlatformType, PlatformInfo, detect_platform

__all__ = ["PlatformType", "PlatformInfo", "detect_platform"]
```

---

### UoW 2.1.9: Create unit tests for platform detection

**Task**: Create test file for platform detection.

**File**: `tests/unit/test_platform_detection.py`

```python
import pytest
from unittest.mock import patch, mock_open
from platform.detection import (
    PlatformType, PlatformInfo, detect_platform,
    _parse_os_release, _check_rpm_ostree_deployment
)

class TestParseOsRelease:
    def test_parse_ultramarine(self):
        content = '''NAME="Ultramarine Linux"
ID=ultramarine
VERSION_ID=43'''
        with patch("builtins.open", mock_open(read_data=content)):
            with patch("pathlib.Path.exists", return_value=True):
                result = _parse_os_release()
        assert result["NAME"] == "Ultramarine Linux"
        assert result["ID"] == "ultramarine"
        assert result["VERSION_ID"] == "43"

class TestDetectPlatform:
    def test_fedora_traditional(self):
        with patch("platform.detection._parse_os_release") as mock_os:
            with patch("platform.detection._check_rpm_ostree_deployment", return_value=False):
                with patch("shutil.which", return_value=None):
                    with patch("platform.detection._detect_boot_method", return_value="grub"):
                        mock_os.return_value = {"NAME": "Ultramarine", "ID": "ultramarine", "VERSION_ID": "43"}
                        info = detect_platform()
        assert info.platform_type == PlatformType.FEDORA_TRADITIONAL
        assert info.is_immutable == False
        assert info.package_manager == "dnf"
        assert info.boot_method == "grub"
```

**Verify**: `pytest tests/unit/test_platform_detection.py -v` passes.

---

## Step 2.2: Abstract Base Classes (PR #1 continued)

**Branch**: `feature/platform-detection` (same PR)
**Estimated Time**: 1 hour

### UoW 2.2.1: Create PackageManager ABC

**Task**: Create abstract base class for package management.

**File**: `platform/base.py`

```python
from abc import ABC, abstractmethod
from typing import List

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
```

---

### UoW 2.2.2: Create KernelParamManager ABC

**Task**: Create abstract base class for kernel parameter management.

**Add to**: `platform/base.py`

```python
from typing import Optional

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
        """Get params that will be active after reboot, or None if same as current"""
        pass
```

---

### UoW 2.2.3: Update platform/__init__.py with base classes

**Task**: Export base classes.

**Update**: `platform/__init__.py`

```python
from .detection import PlatformType, PlatformInfo, detect_platform
from .base import PackageManager, KernelParamManager

__all__ = [
    "PlatformType", "PlatformInfo", "detect_platform",
    "PackageManager", "KernelParamManager"
]
```

---

## Step 2.3: GRUB Kernel Params (PR #3)

**Branch**: `feature/grub-kernel-params`
**Estimated Time**: 2-3 hours
**Dependency**: PR #1 merged

### UoW 2.3.1: Create GrubKernelParams class skeleton

**Task**: Create the class file with basic structure.

**File**: `platform/traditional/grub.py`

```python
import logging
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from ..base import KernelParamManager

class GrubKernelParams(KernelParamManager):
    """Kernel parameter management via GRUB configuration"""
    
    GRUB_DEFAULT = Path("/etc/default/grub")
    GRUB_BACKUP_DIR = Path("/var/backups/grub")
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
```

---

### UoW 2.3.2: Implement get_current_params()

**Task**: Parse GRUB_CMDLINE_LINUX from /etc/default/grub.

**Add to**: `platform/traditional/grub.py`

```python
    def get_current_params(self) -> List[str]:
        """Get current kernel parameters from GRUB config"""
        if not self.GRUB_DEFAULT.exists():
            self.logger.warning(f"{self.GRUB_DEFAULT} not found")
            return []
        
        with open(self.GRUB_DEFAULT) as f:
            for line in f:
                if line.startswith("GRUB_CMDLINE_LINUX="):
                    # Extract value between quotes
                    _, _, value = line.partition("=")
                    value = value.strip().strip('"').strip("'")
                    return value.split() if value else []
        return []
```

**Verify**: Returns your current kernel params from grub.

---

### UoW 2.3.3: Implement _backup_grub_config()

**Task**: Create backup before modifying grub config.

**Add to**: `platform/traditional/grub.py`

```python
    def _backup_grub_config(self) -> Optional[Path]:
        """Create timestamped backup of grub config"""
        if not self.GRUB_DEFAULT.exists():
            return None
        
        self.GRUB_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.GRUB_BACKUP_DIR / f"grub_{timestamp}"
        shutil.copy2(self.GRUB_DEFAULT, backup_path)
        self.logger.info(f"Backed up grub config to {backup_path}")
        return backup_path
```

---

### UoW 2.3.4: Implement _write_grub_config()

**Task**: Write updated GRUB_CMDLINE_LINUX to config.

**Add to**: `platform/traditional/grub.py`

```python
    def _write_grub_config(self, params: List[str]) -> bool:
        """Write kernel parameters to GRUB config"""
        if not self.GRUB_DEFAULT.exists():
            return False
        
        # Read current config
        lines = self.GRUB_DEFAULT.read_text().splitlines()
        
        # Find and update GRUB_CMDLINE_LINUX
        new_lines = []
        found = False
        param_string = " ".join(params)
        for line in lines:
            if line.startswith("GRUB_CMDLINE_LINUX="):
                new_lines.append(f'GRUB_CMDLINE_LINUX="{param_string}"')
                found = True
            else:
                new_lines.append(line)
        
        if not found:
            new_lines.append(f'GRUB_CMDLINE_LINUX="{param_string}"')
        
        # Write back
        self.GRUB_DEFAULT.write_text("\n".join(new_lines) + "\n")
        return True
```

---

### UoW 2.3.5: Implement _run_grub_mkconfig()

**Task**: Regenerate GRUB config after changes.

**Add to**: `platform/traditional/grub.py`

```python
    def _run_grub_mkconfig(self) -> bool:
        """Regenerate GRUB configuration"""
        # Detect grub config path
        grub_cfg_paths = [
            Path("/boot/grub2/grub.cfg"),           # Fedora BIOS
            Path("/boot/efi/EFI/fedora/grub.cfg"),  # Fedora EFI
            Path("/boot/grub/grub.cfg"),            # Debian/Ubuntu
        ]
        
        grub_cfg = None
        for path in grub_cfg_paths:
            if path.parent.exists():
                grub_cfg = path
                break
        
        if grub_cfg is None:
            self.logger.error("Could not find grub config path")
            return False
        
        # Run grub-mkconfig
        cmd = ["grub2-mkconfig", "-o", str(grub_cfg)]
        if not shutil.which("grub2-mkconfig"):
            cmd[0] = "grub-mkconfig"  # Debian/Ubuntu
        
        self.logger.info(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        
        if result.returncode != 0:
            self.logger.error(f"grub-mkconfig failed: {result.stderr.decode()}")
            return False
        
        return True
```

---

### UoW 2.3.6: Implement append_params()

**Task**: Add new kernel parameters.

**Add to**: `platform/traditional/grub.py`

```python
    def append_params(self, params: List[str]) -> bool:
        """Append kernel parameters to GRUB config"""
        self._backup_grub_config()
        
        current = self.get_current_params()
        
        # Add new params, avoiding duplicates
        for param in params:
            param_name = param.split("=")[0]
            # Remove any existing param with same name
            current = [p for p in current if not p.startswith(param_name + "=") and p != param_name]
            current.append(param)
        
        if not self._write_grub_config(current):
            return False
        
        return self._run_grub_mkconfig()
```

---

### UoW 2.3.7: Implement remove_params()

**Task**: Remove kernel parameters.

**Add to**: `platform/traditional/grub.py`

```python
    def remove_params(self, params: List[str]) -> bool:
        """Remove kernel parameters from GRUB config"""
        self._backup_grub_config()
        
        current = self.get_current_params()
        
        # Remove specified params
        for param in params:
            param_name = param.split("=")[0]
            current = [p for p in current if not p.startswith(param_name + "=") and p != param_name]
        
        if not self._write_grub_config(current):
            return False
        
        return self._run_grub_mkconfig()
```

---

### UoW 2.3.8: Implement remaining abstract methods

**Task**: Implement `replace_param()`, `requires_reboot()`, `get_pending_params()`.

**Add to**: `platform/traditional/grub.py`

```python
    def replace_param(self, old: str, new: str) -> bool:
        """Replace a kernel parameter"""
        self._backup_grub_config()
        
        current = self.get_current_params()
        old_name = old.split("=")[0]
        
        new_params = []
        for p in current:
            if p.startswith(old_name + "=") or p == old_name:
                new_params.append(new)
            else:
                new_params.append(p)
        
        if not self._write_grub_config(new_params):
            return False
        
        return self._run_grub_mkconfig()
    
    def requires_reboot(self) -> bool:
        """GRUB changes always require reboot"""
        return True
    
    def get_pending_params(self) -> Optional[List[str]]:
        """Get params that will be active after reboot"""
        # For GRUB, pending params are same as what's in config
        # (no staged deployments like rpm-ostree)
        return None
```

---

### UoW 2.3.9: Create unit tests for GrubKernelParams

**Task**: Create test file.

**File**: `tests/unit/test_grub_kernel_params.py`

```python
import pytest
from unittest.mock import patch, mock_open, MagicMock
from platform.traditional.grub import GrubKernelParams

SAMPLE_GRUB = '''GRUB_TIMEOUT=5
GRUB_CMDLINE_LINUX="rhgb quiet"
GRUB_DISABLE_RECOVERY="true"
'''

class TestGrubKernelParams:
    def test_get_current_params(self):
        with patch("builtins.open", mock_open(read_data=SAMPLE_GRUB)):
            with patch("pathlib.Path.exists", return_value=True):
                grub = GrubKernelParams()
                params = grub.get_current_params()
        assert "rhgb" in params
        assert "quiet" in params
    
    def test_append_deduplicates(self):
        with patch.object(GrubKernelParams, "get_current_params", return_value=["rhgb", "quiet"]):
            with patch.object(GrubKernelParams, "_backup_grub_config"):
                with patch.object(GrubKernelParams, "_write_grub_config") as mock_write:
                    with patch.object(GrubKernelParams, "_run_grub_mkconfig", return_value=True):
                        grub = GrubKernelParams()
                        grub.append_params(["mitigations=off"])
        
        # Check that write was called with deduplicated params
        written_params = mock_write.call_args[0][0]
        assert "mitigations=off" in written_params
        assert written_params.count("mitigations=off") == 1
```

---

## Step 2.4: Package Managers (PR #4)

**Branch**: `feature/package-managers`
**Estimated Time**: 2 hours
**Dependency**: PR #1 merged

### UoW 2.4.1: Implement DnfPackageManager class

**File**: `platform/traditional/rpm.py`

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
        """Install packages via dnf"""
        cmd = ["sudo", "dnf", "install", "-y"] + packages
        self.logger.info(f"Installing: {' '.join(packages)}")
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=timeout)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            self.logger.error("Package installation timed out")
            return False
    
    def remove(self, packages: List[str]) -> bool:
        """Remove packages via dnf"""
        cmd = ["sudo", "dnf", "remove", "-y"] + packages
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        return result.returncode == 0
    
    def is_installed(self, package: str) -> bool:
        """Check if package is installed"""
        result = subprocess.run(
            ["rpm", "-q", package],
            capture_output=True
        )
        return result.returncode == 0
    
    def update(self) -> bool:
        """Update package database"""
        result = subprocess.run(
            ["sudo", "dnf", "makecache"],
            capture_output=True,
            timeout=120
        )
        return result.returncode == 0
```

---

### UoW 2.4.2: Implement AptPackageManager class

**File**: `platform/traditional/deb.py`

```python
import logging
import subprocess
from typing import List
from ..base import PackageManager

class AptPackageManager(PackageManager):
    """Package management via apt"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def install(self, packages: List[str], timeout: int = 300) -> bool:
        """Install packages via apt"""
        cmd = ["sudo", "apt", "install", "-y"] + packages
        self.logger.info(f"Installing: {' '.join(packages)}")
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=timeout)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            self.logger.error("Package installation timed out")
            return False
    
    def remove(self, packages: List[str]) -> bool:
        """Remove packages via apt"""
        cmd = ["sudo", "apt", "remove", "-y"] + packages
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        return result.returncode == 0
    
    def is_installed(self, package: str) -> bool:
        """Check if package is installed"""
        result = subprocess.run(
            ["dpkg", "-s", package],
            capture_output=True
        )
        return result.returncode == 0
    
    def update(self) -> bool:
        """Update package database"""
        result = subprocess.run(
            ["sudo", "apt", "update"],
            capture_output=True,
            timeout=120
        )
        return result.returncode == 0
```

---

### UoW 2.4.3: Create unit tests for package managers

**File**: `tests/unit/test_package_managers.py`

```python
import pytest
from unittest.mock import patch, MagicMock
from platform.traditional.rpm import DnfPackageManager
from platform.traditional.deb import AptPackageManager

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

class TestAptPackageManager:
    def test_is_installed_true(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            apt = AptPackageManager()
            assert apt.is_installed("python3") == True
```

---

## Step 2.5: rpm-ostree Implementations (PR #2)

**Branch**: `feature/rpm-ostree-kernel-params`
**Estimated Time**: 3 hours
**Dependency**: PR #1 merged
**Note**: Cannot test on Ultramarine, requires Bazzite/Silverblue

### UoW 2.5.1: Create RpmOstreeKernelParams class

**File**: `platform/immutable/rpm_ostree.py`

Extract logic from existing `KernelOptimizer` in `bazzite-optimizer.py`.

Key methods to implement:
- `get_current_params()` - from `_get_current_kernel_params()`
- `append_params()` - from `_apply_kernel_param_batch()`
- `remove_params()` - from `_remove_kernel_params()`
- `_ensure_ready()` - from `_ensure_rpm_ostree_ready()`

---

### UoW 2.5.2: Create RpmOstreePackageManager class

**Add to**: `platform/immutable/rpm_ostree.py`

Extract logic from existing `BaseOptimizer.install_package()`.

---

## Step 2.6: PlatformServices Factory (PR #5)

**Branch**: `feature/platform-services`
**Estimated Time**: 1 hour
**Dependency**: PRs #1-4 merged

### UoW 2.6.1: Create PlatformServices class

**File**: `platform/services.py`

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

### UoW 2.6.2: Update platform/__init__.py exports

**Update**: `platform/__init__.py`

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

### UoW 2.6.3: Create unit tests for PlatformServices

**File**: `tests/unit/test_platform_services.py`

```python
import pytest
from unittest.mock import patch, MagicMock
from platform import PlatformType, PlatformInfo, PlatformServices

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
    
    def test_fedora_traditional_returns_grub(self):
        info = make_platform_info(PlatformType.FEDORA_TRADITIONAL, "dnf", "grub")
        services = PlatformServices(info)
        assert "Grub" in type(services.kernel_params).__name__
```

---

## Exit Criteria for Phase 2

- [ ] `platform/` module exists with all files
- [ ] All abstract methods implemented for each platform
- [ ] All unit tests pass
- [ ] Platform detection works on Ultramarine
- [ ] GrubKernelParams works on Ultramarine
- [ ] DnfPackageManager works on Ultramarine
- [ ] PlatformServices factory returns correct implementations
