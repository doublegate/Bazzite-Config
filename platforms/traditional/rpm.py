# TEAM_005: DNF package manager for traditional RPM-based Linux systems
"""
DNF package management for traditional Fedora/RHEL systems.

This implementation handles package operations for non-immutable
RPM-based distributions like Fedora Workstation, Ultramarine, CentOS, etc.
"""

import logging
import subprocess
from typing import List

from ..base import PackageManager


class DnfPackageManager(PackageManager):
    """
    Package management via DNF.
    
    Handles package installation, removal, and queries for traditional
    RPM-based Linux distributions.
    
    Example:
        >>> dnf = DnfPackageManager()
        >>> if not dnf.is_installed("htop"):
        ...     dnf.install(["htop"])
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def install(self, packages: List[str], timeout: int = 300) -> bool:
        """Install packages via dnf with idempotent behavior matching rpm-ostree."""
        if not packages:
            return True
        
        # Filter out already-installed packages (matches rpm-ostree idempotent behavior)
        packages_to_install = []
        for package in packages:
            if not self.is_installed(package):
                packages_to_install.append(package)
            else:
                self.logger.debug(f"Package {package} already installed")
        
        if not packages_to_install:
            self.logger.debug("All packages already installed")
            return True
        
        cmd = ["sudo", "dnf", "install", "-y"] + packages_to_install
        self.logger.info(f"Installing packages: {', '.join(packages_to_install)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=timeout)
            if result.returncode != 0:
                stderr = result.stderr.decode()
                # Handle "already installed" or "nothing to do" cases gracefully
                if "already installed" in stderr.lower() or "nothing to do" in stderr.lower():
                    self.logger.debug(f"Packages already satisfied: {', '.join(packages_to_install)}")
                    return True
                self.logger.error(f"dnf install failed: {stderr}")
                return False
            return True
        except subprocess.TimeoutExpired:
            self.logger.error(f"dnf install timed out after {timeout}s")
            return False
        except Exception as e:
            self.logger.error(f"Failed to run dnf: {e}")
            return False
    
    def remove(self, packages: List[str]) -> bool:
        """Remove packages via dnf with graceful handling matching rpm-ostree."""
        if not packages:
            return True
        
        # Filter to only installed packages (matches rpm-ostree behavior)
        packages_to_remove = []
        for package in packages:
            if self.is_installed(package):
                packages_to_remove.append(package)
            else:
                self.logger.debug(f"Package {package} not installed, skipping")
        
        if not packages_to_remove:
            self.logger.debug("No packages to remove (none installed)")
            return True
        
        cmd = ["sudo", "dnf", "remove", "-y"] + packages_to_remove
        self.logger.info(f"Removing packages: {', '.join(packages_to_remove)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            if result.returncode != 0:
                stderr = result.stderr.decode()
                # Handle "not installed" case gracefully (matches rpm-ostree)
                if "not installed" in stderr.lower() or "no match" in stderr.lower():
                    self.logger.debug(f"Packages not installed: {', '.join(packages_to_remove)}")
                    return True
                self.logger.error(f"dnf remove failed: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Failed to remove packages: {e}")
            return False
    
    def is_installed(self, package: str) -> bool:
        """Check if a package is installed via rpm."""
        try:
            result = subprocess.run(
                ["rpm", "-q", package],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def update(self) -> bool:
        """Update dnf package cache."""
        self.logger.info("Updating dnf cache")
        try:
            result = subprocess.run(
                ["sudo", "dnf", "makecache"],
                capture_output=True,
                timeout=120
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Failed to update cache: {e}")
            return False
