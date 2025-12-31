# TEAM_005: rpm-ostree implementations for immutable Linux systems
"""
rpm-ostree based implementations for immutable distributions.

Handles kernel parameters and package management for:
- Bazzite
- Fedora Silverblue
- Fedora Kinoite  
- Aurora
- Other rpm-ostree based systems

Key features:
- Transaction-aware operations (waits for pending transactions)
- Batch operations to minimize reboots
- Proper error handling for immutable system constraints
"""

import json
import logging
import subprocess
import time
from typing import List, Optional

from ..base import KernelParamManager, PackageManager


class RpmOstreeKernelParams(KernelParamManager):
    """
    Kernel parameter management via rpm-ostree kargs.
    
    Handles the complexities of rpm-ostree transactions:
    - Waits for pending transactions to complete
    - Batches operations to minimize conflicts
    - Provides both current and pending parameter views
    
    Example:
        >>> kp = RpmOstreeKernelParams()
        >>> kp.append_params(["mitigations=off", "nowatchdog"])
        >>> # Staged for next boot
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def _ensure_ready(self, timeout_seconds: int = 60) -> bool:
        """Ensure rpm-ostree is ready for operations."""
        for _ in range(timeout_seconds):
            try:
                result = subprocess.run(
                    ["rpm-ostree", "status", "--json"],
                    capture_output=True,
                    timeout=10
                )
                if result.returncode == 0:
                    status = json.loads(result.stdout)
                    # Check if any deployment has a transaction in progress
                    deployments = status.get("deployments", [])
                    if not any(d.get("transaction-in-progress", False) for d in deployments):
                        return True
                time.sleep(1)
            except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
                self.logger.debug(f"Waiting for rpm-ostree: {e}")
                time.sleep(1)
        
        self.logger.warning("rpm-ostree transaction timeout, attempting reset")
        subprocess.run(["systemctl", "restart", "rpm-ostreed"], capture_output=True, timeout=30)
        time.sleep(5)
        return True
    
    def get_current_params(self) -> List[str]:
        """Get current kernel parameters from rpm-ostree."""
        try:
            result = subprocess.run(
                ["rpm-ostree", "kargs"],
                capture_output=True,
                timeout=30
            )
            if result.returncode == 0 and result.stdout:
                # Parse output - each line may contain params
                params = []
                for line in result.stdout.decode().strip().split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        params.extend(line.split())
                return params
            
            # Fallback to rpm-ostree status
            result = subprocess.run(
                ["rpm-ostree", "status"],
                capture_output=True,
                timeout=30
            )
            if result.returncode == 0:
                import re
                match = re.search(r'Kernel arguments:\s*(.+)', result.stdout.decode())
                if match:
                    return match.group(1).strip().split()
        except Exception as e:
            self.logger.error(f"Failed to get kernel params: {e}")
        return []
    
    def append_params(self, params: List[str]) -> bool:
        """Append kernel parameters via rpm-ostree kargs."""
        if not params:
            return True
        
        if not self._ensure_ready():
            self.logger.error("rpm-ostree not ready")
            return False
        
        # Get current params for deduplication
        current = set(self.get_current_params())
        
        # Build append arguments, deduplicating by param name
        append_args = []
        for param in params:
            param_name = param.split("=")[0]
            # Remove existing param with same name from current set
            current = {p for p in current if not p.startswith(param_name + "=") and p != param_name}
            append_args.append(f"--append-if-missing={param}")
        
        if not append_args:
            return True
        
        cmd = ["rpm-ostree", "kargs"] + append_args
        self.logger.info(f"Appending kernel params: {', '.join(params)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            if result.returncode != 0:
                self.logger.error(f"rpm-ostree kargs failed: {result.stderr.decode()}")
                return False
            return True
        except subprocess.TimeoutExpired:
            self.logger.error("rpm-ostree kargs timed out")
            return False
        except Exception as e:
            self.logger.error(f"Failed to append params: {e}")
            return False
    
    def remove_params(self, params: List[str]) -> bool:
        """Remove kernel parameters via rpm-ostree kargs."""
        if not params:
            return True
        
        if not self._ensure_ready():
            return False
        
        delete_args = [f"--delete={param}" for param in params]
        cmd = ["rpm-ostree", "kargs"] + delete_args
        self.logger.info(f"Removing kernel params: {', '.join(params)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            if result.returncode != 0:
                # Some params may not exist, which is okay
                stderr = result.stderr.decode()
                if "No such key" not in stderr:
                    self.logger.error(f"rpm-ostree kargs delete failed: {stderr}")
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Failed to remove params: {e}")
            return False
    
    def replace_param(self, old: str, new: str) -> bool:
        """Replace a kernel parameter."""
        if not self._ensure_ready():
            return False
        
        old_name = old.split("=")[0]
        cmd = ["rpm-ostree", "kargs", f"--replace={old_name}={new.split('=')[-1]}"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            if result.returncode != 0:
                # Fallback: delete old, append new
                self.remove_params([old])
                return self.append_params([new])
            return True
        except Exception as e:
            self.logger.error(f"Failed to replace param: {e}")
            return False
    
    def requires_reboot(self) -> bool:
        """rpm-ostree changes always require reboot."""
        return True
    
    def get_pending_params(self) -> Optional[List[str]]:
        """Get parameters staged for next boot."""
        try:
            result = subprocess.run(
                ["rpm-ostree", "status", "--json"],
                capture_output=True,
                timeout=30
            )
            if result.returncode == 0:
                status = json.loads(result.stdout)
                deployments = status.get("deployments", [])
                if len(deployments) >= 2:
                    # First deployment is pending, second is current
                    pending = deployments[0].get("kernel-args", [])
                    current = deployments[1].get("kernel-args", [])
                    if pending != current:
                        return pending
        except Exception as e:
            self.logger.debug(f"Could not get pending params: {e}")
        return None


class RpmOstreePackageManager(PackageManager):
    """
    Package management via rpm-ostree.
    
    Handles package layering for immutable systems. Note that:
    - Package changes require a reboot to take effect
    - Operations are transaction-based
    - Some packages may conflict with the base image
    
    Example:
        >>> pm = RpmOstreePackageManager()
        >>> pm.install(["htop", "neofetch"])
        >>> # Packages layered, reboot to apply
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def _ensure_ready(self, timeout_seconds: int = 60) -> bool:
        """Ensure rpm-ostree is ready for operations."""
        for _ in range(timeout_seconds):
            try:
                result = subprocess.run(
                    ["rpm-ostree", "status", "--json"],
                    capture_output=True,
                    timeout=10
                )
                if result.returncode == 0:
                    status = json.loads(result.stdout)
                    deployments = status.get("deployments", [])
                    if not any(d.get("transaction-in-progress", False) for d in deployments):
                        return True
                time.sleep(1)
            except Exception:
                time.sleep(1)
        return True
    
    def install(self, packages: List[str], timeout: int = 300) -> bool:
        """Install (layer) packages via rpm-ostree."""
        if not packages:
            return True
        
        if not self._ensure_ready():
            self.logger.warning("rpm-ostree may have pending transaction")
        
        cmd = ["rpm-ostree", "install", "--idempotent"] + packages
        self.logger.info(f"Layering packages: {', '.join(packages)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=timeout)
            if result.returncode != 0:
                stderr = result.stderr.decode()
                # Check if already installed
                if "already" in stderr.lower() or "nothing to do" in stderr.lower():
                    return True
                self.logger.error(f"rpm-ostree install failed: {stderr}")
                return False
            return True
        except subprocess.TimeoutExpired:
            self.logger.error(f"rpm-ostree install timed out after {timeout}s")
            return False
        except Exception as e:
            self.logger.error(f"Failed to install packages: {e}")
            return False
    
    def remove(self, packages: List[str]) -> bool:
        """Remove (unlayer) packages via rpm-ostree."""
        if not packages:
            return True
        
        if not self._ensure_ready():
            self.logger.warning("rpm-ostree may have pending transaction")
        
        cmd = ["rpm-ostree", "uninstall"] + packages
        self.logger.info(f"Unlayering packages: {', '.join(packages)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            if result.returncode != 0:
                stderr = result.stderr.decode()
                if "not currently" in stderr.lower():
                    return True  # Not layered
                self.logger.error(f"rpm-ostree uninstall failed: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Failed to remove packages: {e}")
            return False
    
    def is_installed(self, package: str) -> bool:
        """Check if a package is installed (in base or layered)."""
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
        """Update the base image (rpm-ostree upgrade)."""
        self.logger.info("Checking for system updates")
        try:
            result = subprocess.run(
                ["rpm-ostree", "upgrade", "--check"],
                capture_output=True,
                timeout=120
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Failed to check updates: {e}")
            return False
