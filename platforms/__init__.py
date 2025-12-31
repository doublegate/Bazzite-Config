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

from .detection import (
    PlatformType,
    PlatformInfo,
    detect_platform,
    # TEAM_009: eGPU support
    GPUInfo,
    detect_gpus,
    get_primary_gpu,
    detect_thunderbolt_devices,
    # TEAM_012: CPU topology support
    CPUTopology,
    detect_cpu_topology,
    # TEAM_013: GPU capability detection
    NvidiaGPUCapabilities,
    detect_nvidia_capabilities,
    NVIDIA_GENERATIONS,
)
from .base import PackageManager, KernelParamManager
from .services import PlatformServices, UnsupportedPlatformError

__all__ = [
    "PlatformType",
    "PlatformInfo", 
    "detect_platform",
    # TEAM_009: eGPU support
    "GPUInfo",
    "detect_gpus",
    "get_primary_gpu",
    "detect_thunderbolt_devices",
    # TEAM_012: CPU topology support
    "CPUTopology",
    "detect_cpu_topology",
    # TEAM_013: GPU capability detection
    "NvidiaGPUCapabilities",
    "detect_nvidia_capabilities",
    "NVIDIA_GENERATIONS",
    "PackageManager",
    "KernelParamManager",
    "PlatformServices",
    "UnsupportedPlatformError",
]
