# TEAM_005: Platform services factory for cross-platform Linux gaming optimization
"""
Platform services factory.

Provides a unified interface to get platform-specific implementations
based on detected platform information. This is the main entry point
for consuming code to get the right implementation without knowing
the underlying platform details.

Usage:
    from platforms import detect_platform, PlatformServices
    
    info = detect_platform()
    services = PlatformServices(info)
    
    # Use kernel params (automatically uses GRUB or rpm-ostree)
    services.kernel_params.append_params(["mitigations=off"])
    
    # Use package manager (automatically uses dnf or rpm-ostree)
    services.package_manager.install(["htop"])
"""

import logging
from typing import Optional

from .detection import PlatformInfo, PlatformType
from .base import PackageManager, KernelParamManager


class UnsupportedPlatformError(Exception):
    """Raised when a platform operation is not supported."""
    pass


class PlatformServices:
    """
    Factory for platform-specific service implementations.
    
    Lazily creates and caches the appropriate implementations based on
    the detected platform. This allows code to be written against
    abstract interfaces while getting the correct concrete implementation.
    
    Attributes:
        platform_info: The detected platform metadata
        package_manager: Platform-appropriate package manager
        kernel_params: Platform-appropriate kernel param manager
    
    Example:
        >>> info = detect_platform()
        >>> services = PlatformServices(info)
        >>> print(f"Using {type(services.kernel_params).__name__}")
        'GrubKernelParams'  # on traditional systems
        'RpmOstreeKernelParams'  # on immutable systems
    """
    
    def __init__(self, platform_info: PlatformInfo):
        """
        Initialize with detected platform info.
        
        Args:
            platform_info: Result from detect_platform()
        """
        self.platform_info = platform_info
        self.logger = logging.getLogger(__name__)
        self._package_manager: Optional[PackageManager] = None
        self._kernel_params: Optional[KernelParamManager] = None
    
    @property
    def package_manager(self) -> PackageManager:
        """Get the appropriate package manager for this platform."""
        if self._package_manager is None:
            self._package_manager = self._create_package_manager()
        return self._package_manager
    
    @property
    def kernel_params(self) -> KernelParamManager:
        """Get the appropriate kernel param manager for this platform."""
        if self._kernel_params is None:
            self._kernel_params = self._create_kernel_params()
        return self._kernel_params
    
    def _create_package_manager(self) -> PackageManager:
        """Create the appropriate package manager implementation."""
        pkg_mgr = self.platform_info.package_manager
        
        if pkg_mgr == "rpm-ostree":
            from .immutable.rpm_ostree import RpmOstreePackageManager
            self.logger.debug("Using RpmOstreePackageManager")
            return RpmOstreePackageManager()
        
        elif pkg_mgr == "dnf":
            from .traditional.rpm import DnfPackageManager
            self.logger.debug("Using DnfPackageManager")
            return DnfPackageManager()
        
        elif pkg_mgr == "apt":
            # Future: AptPackageManager
            raise UnsupportedPlatformError(
                f"apt package manager not yet implemented. "
                f"Platform: {self.platform_info.distro_name}"
            )
        
        else:
            raise UnsupportedPlatformError(
                f"Unsupported package manager: {pkg_mgr}. "
                f"Platform: {self.platform_info.distro_name}"
            )
    
    def _create_kernel_params(self) -> KernelParamManager:
        """Create the appropriate kernel param manager implementation."""
        boot_method = self.platform_info.boot_method
        
        if boot_method == "rpm-ostree-kargs":
            from .immutable.rpm_ostree import RpmOstreeKernelParams
            self.logger.debug("Using RpmOstreeKernelParams")
            return RpmOstreeKernelParams()
        
        elif boot_method == "grub":
            from .traditional.grub import GrubKernelParams
            self.logger.debug("Using GrubKernelParams")
            return GrubKernelParams()
        
        elif boot_method == "systemd-boot":
            # Future: SystemdBootKernelParams
            raise UnsupportedPlatformError(
                f"systemd-boot not yet implemented. "
                f"Platform: {self.platform_info.distro_name}"
            )
        
        else:
            raise UnsupportedPlatformError(
                f"Unsupported boot method: {boot_method}. "
                f"Platform: {self.platform_info.distro_name}"
            )
    
    @property
    def is_immutable(self) -> bool:
        """Check if this is an immutable system."""
        return self.platform_info.is_immutable
    
    @property
    def has_ujust(self) -> bool:
        """Check if ujust is available (Bazzite feature)."""
        return self.platform_info.has_ujust
    
    @property 
    def platform_type(self) -> PlatformType:
        """Get the platform type enum."""
        return self.platform_info.platform_type
