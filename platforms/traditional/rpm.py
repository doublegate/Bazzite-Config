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
        """Install packages via dnf."""
        if not packages:
            return True
        
        cmd = ["sudo", "dnf", "install", "-y"] + packages
        self.logger.info(f"Installing packages: {', '.join(packages)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=timeout)
            if result.returncode != 0:
                self.logger.error(f"dnf install failed: {result.stderr.decode()}")
                return False
            return True
        except subprocess.TimeoutExpired:
            self.logger.error(f"dnf install timed out after {timeout}s")
            return False
        except Exception as e:
            self.logger.error(f"Failed to run dnf: {e}")
            return False
    
    def remove(self, packages: List[str]) -> bool:
        """Remove packages via dnf."""
        if not packages:
            return True
        
        cmd = ["sudo", "dnf", "remove", "-y"] + packages
        self.logger.info(f"Removing packages: {', '.join(packages)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            if result.returncode != 0:
                self.logger.error(f"dnf remove failed: {result.stderr.decode()}")
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
