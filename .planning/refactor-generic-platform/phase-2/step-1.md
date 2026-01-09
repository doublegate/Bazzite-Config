# Phase 2, Step 1 — Platform Detection (PR #1)

**Parent**: [Phase 2](README.md)
**Branch**: `feature/platform-detection`
**Estimated Time**: 1 hour

---

## UoW 2.1.1: Create platforms module structure

**Goal**: Create the directory structure and `__init__.py` files.

**Task**:
```bash
mkdir -p platforms/immutable platforms/traditional
touch platforms/__init__.py
touch platforms/immutable/__init__.py
touch platforms/traditional/__init__.py
```

**Files created**:
- `platforms/__init__.py`
- `platforms/immutable/__init__.py`
- `platforms/traditional/__init__.py`

**Verify**: Directories exist.

---

## UoW 2.1.2: Create PlatformType and PlatformInfo

**Goal**: Define the supported platform types and metadata structure.

**File**: `platforms/detection.py`

**Code**:
```python
from enum import Enum, auto
from dataclasses import dataclass

class PlatformType(Enum):
    """Supported platform types"""
    BAZZITE = auto()           # Bazzite (immutable, rpm-ostree + ujust)
    FEDORA_OSTREE = auto()     # Silverblue, Kinoite, Aurora
    FEDORA_TRADITIONAL = auto() # Fedora Workstation, Ultramarine
    DEBIAN_BASED = auto()      # Ubuntu, Debian, Pop!_OS
    UNKNOWN = auto()

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

**Verify**: `from platforms.detection import PlatformType` works.

---

## UoW 2.1.3: Implement detection helpers

**Goal**: Implement OS release parsing and rpm-ostree detection.

**Add to**: `platforms/detection.py`

**Code**:
```python
import subprocess
import shutil
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

def _detect_boot_method() -> str:
    """Detect how kernel parameters are configured"""
    if Path("/etc/default/grub").exists():
        return "grub"
    if Path("/boot/loader/entries").exists():
        return "systemd-boot"
    return "unknown"
```

---

## UoW 2.1.4: Implement detect_platform and unit tests

**Goal**: Main detection function and tests.

**Add to**: `platforms/detection.py`

**Code**:
```python
def detect_platform() -> PlatformInfo:
    """Detect the current platform and return metadata"""
    os_info = _parse_os_release()
    is_immutable = _check_rpm_ostree_deployment()
    has_ujust = shutil.which("ujust") is not None
    
    distro_name = os_info.get("NAME", "Unknown")
    distro_version = os_info.get("VERSION_ID", "")
    distro_id = os_info.get("ID", "").lower()
    
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

**Update**: `platforms/__init__.py`

```python
from .detection import PlatformType, PlatformInfo, detect_platform
__all__ = ["PlatformType", "PlatformInfo", "detect_platform"]
```

---

## Step Exit Criteria

- [ ] `platforms/detection.py` exists with all functions
- [ ] `platforms/__init__.py` exports public API
- [ ] Unit tests pass
