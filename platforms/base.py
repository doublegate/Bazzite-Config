# TEAM_005: Abstract base classes for platform operations
"""
Abstract base classes defining the interface for platform-specific operations.

These ABCs ensure that all platform implementations provide consistent
interfaces for:
- Package management (install, remove, query)
- Kernel parameter management (get, set, remove)

Adding support for a new platform requires implementing these interfaces.
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class PackageManager(ABC):
    """
    Abstract base class for package management operations.
    
    Implementations:
    - RpmOstreePackageManager: For immutable rpm-ostree systems
    - DnfPackageManager: For traditional Fedora/RHEL systems
    - AptPackageManager: For Debian/Ubuntu systems (future)
    
    Example:
        >>> pm = DnfPackageManager()
        >>> if not pm.is_installed("htop"):
        ...     pm.install(["htop"])
    """
    
    @abstractmethod
    def install(self, packages: List[str], timeout: int = 300) -> bool:
        """
        Install one or more packages.
        
        Args:
            packages: List of package names to install
            timeout: Maximum seconds to wait for installation
            
        Returns:
            True if all packages installed successfully
        """
        pass
    
    @abstractmethod
    def remove(self, packages: List[str]) -> bool:
        """
        Remove one or more packages.
        
        Args:
            packages: List of package names to remove
            
        Returns:
            True if all packages removed successfully
        """
        pass
    
    @abstractmethod
    def is_installed(self, package: str) -> bool:
        """
        Check if a package is installed.
        
        Args:
            package: Package name to check
            
        Returns:
            True if package is installed
        """
        pass
    
    @abstractmethod
    def update(self) -> bool:
        """
        Update package database/cache.
        
        Returns:
            True if update succeeded
        """
        pass


class KernelParamManager(ABC):
    """
    Abstract base class for kernel parameter management.
    
    Implementations:
    - RpmOstreeKernelParams: Uses rpm-ostree kargs for immutable systems
    - GrubKernelParams: Edits /etc/default/grub for traditional systems
    
    All implementations handle:
    - Reading current parameters
    - Adding/appending parameters (with deduplication)
    - Removing parameters
    - Replacing parameter values
    
    Example:
        >>> kp = GrubKernelParams()
        >>> current = kp.get_current_params()
        >>> kp.append_params(["mitigations=off", "nowatchdog"])
    """
    
    @abstractmethod
    def get_current_params(self) -> List[str]:
        """
        Get list of current kernel parameters.
        
        Returns:
            List of kernel parameter strings (e.g., ["quiet", "splash", "mitigations=off"])
        """
        pass
    
    @abstractmethod
    def append_params(self, params: List[str]) -> bool:
        """
        Append kernel parameters, deduplicating by parameter name.
        
        If a parameter with the same name exists, it will be replaced.
        Changes take effect after reboot.
        
        Args:
            params: List of parameters to add (e.g., ["mitigations=off"])
            
        Returns:
            True if parameters were successfully staged
        """
        pass
    
    @abstractmethod
    def remove_params(self, params: List[str]) -> bool:
        """
        Remove kernel parameters.
        
        Args:
            params: List of parameters to remove (can be just the name or full param)
            
        Returns:
            True if parameters were successfully removed
        """
        pass
    
    @abstractmethod
    def replace_param(self, old: str, new: str) -> bool:
        """
        Replace a kernel parameter with a new value.
        
        Args:
            old: Parameter to replace (name or full param)
            new: New parameter value
            
        Returns:
            True if replacement succeeded
        """
        pass
    
    @abstractmethod
    def requires_reboot(self) -> bool:
        """
        Check if changes require a reboot to take effect.
        
        Returns:
            True if reboot is required (always True for kernel params)
        """
        pass
    
    @abstractmethod
    def get_pending_params(self) -> Optional[List[str]]:
        """
        Get parameters that will be active after reboot.
        
        Returns:
            List of pending params, or None if same as current
        """
        pass
