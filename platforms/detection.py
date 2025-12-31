# TEAM_005: Platform detection for cross-platform Linux gaming optimization
"""
Platform detection module.

Detects the current Linux distribution and determines:
- Platform type (Bazzite, Fedora ostree, Fedora traditional, Debian-based)
- Package manager (rpm-ostree, dnf, apt)
- Boot method (rpm-ostree-kargs, grub, systemd-boot)
- Special features (ujust availability)
"""

import subprocess
import shutil
from enum import Enum, auto
from dataclasses import dataclass
from pathlib import Path
from typing import Dict


class PlatformType(Enum):
    """Supported platform types for the optimizer."""
    BAZZITE = auto()            # Bazzite (immutable, rpm-ostree + ujust)
    FEDORA_OSTREE = auto()      # Silverblue, Kinoite, Aurora (immutable, rpm-ostree)
    FEDORA_TRADITIONAL = auto()  # Fedora Workstation, Ultramarine, Nobara
    DEBIAN_BASED = auto()       # Ubuntu, Debian, Pop!_OS, Linux Mint
    UNKNOWN = auto()


@dataclass
class PlatformInfo:
    """Platform metadata collected during detection."""
    platform_type: PlatformType
    distro_name: str
    distro_version: str
    is_immutable: bool
    has_ujust: bool
    package_manager: str   # "rpm-ostree", "dnf", "apt"
    boot_method: str       # "rpm-ostree-kargs", "grub", "systemd-boot"


def _parse_os_release() -> Dict[str, str]:
    """Parse /etc/os-release into a dictionary."""
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
    """Check if system has an rpm-ostree deployment."""
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


def _detect_boot_method(is_immutable: bool) -> str:
    """Detect how kernel parameters are configured."""
    if is_immutable:
        return "rpm-ostree-kargs"
    if Path("/etc/default/grub").exists():
        return "grub"
    if Path("/boot/loader/entries").exists():
        return "systemd-boot"
    return "unknown"


def detect_platform() -> PlatformInfo:
    """
    Detect the current platform and return metadata.
    
    This is the main entry point for platform detection. It examines
    the system to determine:
    - Distribution name and version
    - Whether the system is immutable (rpm-ostree based)
    - Available package manager
    - Boot configuration method
    - Special features like ujust
    
    Returns:
        PlatformInfo with all detected metadata
    
    Example:
        >>> info = detect_platform()
        >>> print(f"Running on {info.distro_name}")
        >>> if info.is_immutable:
        ...     print("Using rpm-ostree for packages")
    """
    os_info = _parse_os_release()
    is_immutable = _check_rpm_ostree_deployment()
    has_ujust = shutil.which("ujust") is not None
    
    distro_name = os_info.get("NAME", "Unknown")
    distro_version = os_info.get("VERSION_ID", "")
    distro_id = os_info.get("ID", "").lower()
    variant_id = os_info.get("VARIANT_ID", "").lower()
    
    # Determine platform type
    if is_immutable:
        if has_ujust or "bazzite" in distro_id or "bazzite" in variant_id:
            platform_type = PlatformType.BAZZITE
        else:
            platform_type = PlatformType.FEDORA_OSTREE
        package_manager = "rpm-ostree"
    elif distro_id in ("fedora", "ultramarine", "nobara", "centos", "rhel", "rocky", "alma"):
        platform_type = PlatformType.FEDORA_TRADITIONAL
        package_manager = "dnf"
    elif distro_id in ("ubuntu", "debian", "pop", "linuxmint", "elementary", "zorin"):
        platform_type = PlatformType.DEBIAN_BASED
        package_manager = "apt"
    else:
        platform_type = PlatformType.UNKNOWN
        # Try to detect package manager
        if shutil.which("dnf"):
            package_manager = "dnf"
        elif shutil.which("apt"):
            package_manager = "apt"
        else:
            package_manager = "unknown"
    
    boot_method = _detect_boot_method(is_immutable)
    
    return PlatformInfo(
        platform_type=platform_type,
        distro_name=distro_name,
        distro_version=distro_version,
        is_immutable=is_immutable,
        has_ujust=has_ujust,
        package_manager=package_manager,
        boot_method=boot_method
    )
