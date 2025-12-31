# TEAM_005: GRUB kernel parameter management for traditional Linux systems
"""
GRUB-based kernel parameter management.

This implementation handles kernel parameters for traditional (non-immutable)
Linux distributions that use GRUB as their bootloader. It:
- Reads/writes /etc/default/grub
- Creates timestamped backups before changes
- Runs grub-mkconfig to apply changes
- Supports Fedora, Ubuntu, and Debian path conventions
"""

import logging
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from ..base import KernelParamManager


class GrubKernelParams(KernelParamManager):
    """
    Kernel parameter management via GRUB configuration.
    
    Modifies GRUB_CMDLINE_LINUX in /etc/default/grub and regenerates
    the GRUB configuration. All changes require a reboot to take effect.
    
    Example:
        >>> grub = GrubKernelParams()
        >>> grub.append_params(["mitigations=off", "nowatchdog"])
        >>> # Changes staged, reboot to apply
    """
    
    GRUB_DEFAULT = Path("/etc/default/grub")
    GRUB_BACKUP_DIR = Path("/var/backups/grub")
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_current_params(self) -> List[str]:
        """Get current kernel parameters from GRUB config."""
        if not self.GRUB_DEFAULT.exists():
            self.logger.warning(f"{self.GRUB_DEFAULT} not found")
            return []
        
        try:
            with open(self.GRUB_DEFAULT) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GRUB_CMDLINE_LINUX="):
                        _, _, value = line.partition("=")
                        value = value.strip().strip('"').strip("'")
                        return value.split() if value else []
        except Exception as e:
            self.logger.error(f"Failed to read GRUB config: {e}")
        return []
    
    def _backup_grub_config(self) -> Optional[Path]:
        """Create timestamped backup of grub config."""
        if not self.GRUB_DEFAULT.exists():
            return None
        
        try:
            self.GRUB_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.GRUB_BACKUP_DIR / f"grub_{timestamp}"
            shutil.copy2(self.GRUB_DEFAULT, backup_path)
            self.logger.info(f"Backed up grub config to {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.warning(f"Failed to backup grub config: {e}")
            return None
    
    def _write_grub_config(self, params: List[str]) -> bool:
        """Write kernel parameters to GRUB config."""
        if not self.GRUB_DEFAULT.exists():
            self.logger.error(f"{self.GRUB_DEFAULT} not found")
            return False
        
        try:
            lines = self.GRUB_DEFAULT.read_text().splitlines()
            new_lines = []
            found = False
            param_string = " ".join(params)
            
            for line in lines:
                if line.strip().startswith("GRUB_CMDLINE_LINUX="):
                    new_lines.append(f'GRUB_CMDLINE_LINUX="{param_string}"')
                    found = True
                else:
                    new_lines.append(line)
            
            if not found:
                new_lines.append(f'GRUB_CMDLINE_LINUX="{param_string}"')
            
            self.GRUB_DEFAULT.write_text("\n".join(new_lines) + "\n")
            return True
        except Exception as e:
            self.logger.error(f"Failed to write GRUB config: {e}")
            return False
    
    def _run_grub_mkconfig(self) -> bool:
        """Regenerate GRUB configuration."""
        grub_cfg_paths = [
            Path("/boot/grub2/grub.cfg"),           # Fedora BIOS
            Path("/boot/efi/EFI/fedora/grub.cfg"),  # Fedora EFI
            Path("/boot/grub/grub.cfg"),            # Debian/Ubuntu BIOS
            Path("/boot/efi/EFI/ubuntu/grub.cfg"),  # Ubuntu EFI
        ]
        
        grub_cfg = None
        for path in grub_cfg_paths:
            if path.parent.exists():
                grub_cfg = path
                break
        
        if grub_cfg is None:
            self.logger.error("Could not find grub config path")
            return False
        
        # Determine which command to use
        if shutil.which("grub2-mkconfig"):
            cmd = ["grub2-mkconfig", "-o", str(grub_cfg)]
        elif shutil.which("update-grub"):
            cmd = ["update-grub"]
        elif shutil.which("grub-mkconfig"):
            cmd = ["grub-mkconfig", "-o", str(grub_cfg)]
        else:
            self.logger.error("Could not find grub-mkconfig or update-grub")
            return False
        
        self.logger.info(f"Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            if result.returncode != 0:
                self.logger.error(f"grub-mkconfig failed: {result.stderr.decode()}")
                return False
            return True
        except subprocess.TimeoutExpired:
            self.logger.error("grub-mkconfig timed out")
            return False
        except Exception as e:
            self.logger.error(f"Failed to run grub-mkconfig: {e}")
            return False
    
    def append_params(self, params: List[str]) -> bool:
        """Append kernel parameters to GRUB config with deduplication."""
        self._backup_grub_config()
        current = self.get_current_params()
        
        for param in params:
            param_name = param.split("=")[0]
            # Remove existing param with same name
            current = [p for p in current if not p.startswith(param_name + "=") and p != param_name]
            current.append(param)
        
        if not self._write_grub_config(current):
            return False
        
        return self._run_grub_mkconfig()
    
    def remove_params(self, params: List[str]) -> bool:
        """Remove kernel parameters from GRUB config."""
        self._backup_grub_config()
        current = self.get_current_params()
        
        for param in params:
            param_name = param.split("=")[0]
            current = [p for p in current if not p.startswith(param_name + "=") and p != param_name]
        
        if not self._write_grub_config(current):
            return False
        
        return self._run_grub_mkconfig()
    
    def replace_param(self, old: str, new: str) -> bool:
        """Replace a kernel parameter with a new value."""
        self._backup_grub_config()
        current = self.get_current_params()
        old_name = old.split("=")[0]
        
        new_params = []
        replaced = False
        for p in current:
            if p.startswith(old_name + "=") or p == old_name:
                new_params.append(new)
                replaced = True
            else:
                new_params.append(p)
        
        if not replaced:
            new_params.append(new)
        
        if not self._write_grub_config(new_params):
            return False
        return self._run_grub_mkconfig()
    
    def requires_reboot(self) -> bool:
        """GRUB changes always require reboot."""
        return True
    
    def get_pending_params(self) -> Optional[List[str]]:
        """For GRUB, pending params are same as config (returns None)."""
        return None
