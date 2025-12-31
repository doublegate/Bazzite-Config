# TEAM_005: Platform abstraction layer for cross-platform Linux gaming optimization
"""
Platform detection and abstraction module.

Provides:
- PlatformType: Enum of supported platform types
- PlatformInfo: Dataclass with platform metadata
- detect_platform(): Detect current platform
- PackageManager: ABC for package management
- KernelParamManager: ABC for kernel parameter management
- PlatformServices: Factory for platform-specific implementations
"""

from .detection import PlatformType, PlatformInfo, detect_platform
from .base import PackageManager, KernelParamManager
from .services import PlatformServices, UnsupportedPlatformError

__all__ = [
    "PlatformType",
    "PlatformInfo", 
    "detect_platform",
    "PackageManager",
    "KernelParamManager",
    "PlatformServices",
    "UnsupportedPlatformError",
]
