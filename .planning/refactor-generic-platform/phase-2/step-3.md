# Phase 2, Step 3 — GRUB Kernel Params (PR #3)

**Parent**: [Phase 2](README.md)
**Branch**: `feature/grub-kernel-params`
**Dependency**: PR #1 merged
**Estimated Time**: 2-3 hours

---

## UoW 2.3.1: Create GrubKernelParams class skeleton

**Goal**: Create the class file with basic structure.

**File**: `platforms/traditional/grub.py`

**Code**:
```python
import logging
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from ..base import KernelParamManager

class GrubKernelParams(KernelParamManager):
    """Kernel parameter management via GRUB configuration"""
    
    GRUB_DEFAULT = Path("/etc/default/grub")
    GRUB_BACKUP_DIR = Path("/var/backups/grub")
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
```

---

## UoW 2.3.2: Implement get_current_params()

**Goal**: Parse GRUB_CMDLINE_LINUX from /etc/default/grub.

**Add to**: `platforms/traditional/grub.py`

**Code**:
```python
    def get_current_params(self) -> List[str]:
        """Get current kernel parameters from GRUB config"""
        if not self.GRUB_DEFAULT.exists():
            self.logger.warning(f"{self.GRUB_DEFAULT} not found")
            return []
        
        with open(self.GRUB_DEFAULT) as f:
            for line in f:
                if line.startswith("GRUB_CMDLINE_LINUX="):
                    _, _, value = line.partition("=")
                    value = value.strip().strip('"').strip("'")
                    return value.split() if value else []
        return []
```

**Verify**: Returns your current kernel params from grub.

---

## UoW 2.3.3: Implement _backup_grub_config()

**Goal**: Create backup before modifying grub config.

**Add to**: `platforms/traditional/grub.py`

**Code**:
```python
    def _backup_grub_config(self) -> Optional[Path]:
        """Create timestamped backup of grub config"""
        if not self.GRUB_DEFAULT.exists():
            return None
        
        self.GRUB_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.GRUB_BACKUP_DIR / f"grub_{timestamp}"
        shutil.copy2(self.GRUB_DEFAULT, backup_path)
        self.logger.info(f"Backed up grub config to {backup_path}")
        return backup_path
```

---

## UoW 2.3.4: Implement _write_grub_config()

**Goal**: Write updated GRUB_CMDLINE_LINUX to config.

**Add to**: `platforms/traditional/grub.py`

**Code**:
```python
    def _write_grub_config(self, params: List[str]) -> bool:
        """Write kernel parameters to GRUB config"""
        if not self.GRUB_DEFAULT.exists():
            return False
        
        lines = self.GRUB_DEFAULT.read_text().splitlines()
        new_lines = []
        found = False
        param_string = " ".join(params)
        
        for line in lines:
            if line.startswith("GRUB_CMDLINE_LINUX="):
                new_lines.append(f'GRUB_CMDLINE_LINUX="{param_string}"')
                found = True
            else:
                new_lines.append(line)
        
        if not found:
            new_lines.append(f'GRUB_CMDLINE_LINUX="{param_string}"')
        
        self.GRUB_DEFAULT.write_text("\n".join(new_lines) + "\n")
        return True
```

---

## UoW 2.3.5: Implement _run_grub_mkconfig()

**Goal**: Regenerate GRUB config after changes.

**Add to**: `platforms/traditional/grub.py`

**Code**:
```python
    def _run_grub_mkconfig(self) -> bool:
        """Regenerate GRUB configuration"""
        grub_cfg_paths = [
            Path("/boot/grub2/grub.cfg"),           # Fedora BIOS
            Path("/boot/efi/EFI/fedora/grub.cfg"),  # Fedora EFI
            Path("/boot/grub/grub.cfg"),            # Debian/Ubuntu
        ]
        
        grub_cfg = None
        for path in grub_cfg_paths:
            if path.parent.exists():
                grub_cfg = path
                break
        
        if grub_cfg is None:
            self.logger.error("Could not find grub config path")
            return False
        
        cmd = ["grub2-mkconfig", "-o", str(grub_cfg)]
        if not shutil.which("grub2-mkconfig"):
            if shutil.which("update-grub"):
                cmd = ["update-grub"]
            elif shutil.which("grub-mkconfig"):
                cmd = ["grub-mkconfig", "-o", str(grub_cfg)]
            else:
                self.logger.error("Could not find grub-mkconfig or update-grub")
                return False
        
        self.logger.info(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        
        if result.returncode != 0:
            self.logger.error(f"grub-mkconfig failed: {result.stderr.decode()}")
            return False
        
        return True
```

---

## UoW 2.3.6: Implement append_params()

**Goal**: Add new kernel parameters with deduplication.

**Add to**: `platforms/traditional/grub.py`

**Code**:
```python
    def append_params(self, params: List[str]) -> bool:
        """Append kernel parameters to GRUB config"""
        self._backup_grub_config()
        current = self.get_current_params()
        
        for param in params:
            param_name = param.split("=")[0]
            current = [p for p in current if not p.startswith(param_name + "=") and p != param_name]
            current.append(param)
        
        if not self._write_grub_config(current):
            return False
        
        return self._run_grub_mkconfig()
```

---

## UoW 2.3.7: Implement remove_params()

**Goal**: Remove kernel parameters.

**Add to**: `platforms/traditional/grub.py`

**Code**:
```python
    def remove_params(self, params: List[str]) -> bool:
        """Remove kernel parameters from GRUB config"""
        self._backup_grub_config()
        current = self.get_current_params()
        
        for param in params:
            param_name = param.split("=")[0]
            current = [p for p in current if not p.startswith(param_name + "=") and p != param_name]
        
        if not self._write_grub_config(current):
            return False
        
        return self._run_grub_mkconfig()
```

---

## UoW 2.3.8: Implement remaining abstract methods

**Goal**: Complete the abstract interface.

**Add to**: `platforms/traditional/grub.py`

**Code**:
```python
    def replace_param(self, old: str, new: str) -> bool:
        """Replace a kernel parameter"""
        self._backup_grub_config()
        current = self.get_current_params()
        old_name = old.split("=")[0]
        
        new_params = []
        for p in current:
            if p.startswith(old_name + "=") or p == old_name:
                new_params.append(new)
            else:
                new_params.append(p)
        
        if not self._write_grub_config(new_params):
            return False
        return self._run_grub_mkconfig()
    
    def requires_reboot(self) -> bool:
        """GRUB changes always require reboot"""
        return True
    
    def get_pending_params(self) -> Optional[List[str]]:
        """For GRUB, pending params are same as config"""
        return None
```

---

## UoW 2.3.9: Create unit tests for GrubKernelParams

**Goal**: Test GRUB kernel params with mocks.

**File**: `tests/unit/test_grub_kernel_params.py`

**Code**:
```python
import pytest
from unittest.mock import patch, mock_open, MagicMock
from platforms.traditional.grub import GrubKernelParams

SAMPLE_GRUB = '''GRUB_TIMEOUT=5
GRUB_CMDLINE_LINUX="rhgb quiet"
GRUB_DISABLE_RECOVERY="true"
'''

class TestGrubKernelParams:
    def test_get_current_params(self):
        with patch("builtins.open", mock_open(read_data=SAMPLE_GRUB)):
            with patch("pathlib.Path.exists", return_value=True):
                grub = GrubKernelParams()
                params = grub.get_current_params()
        assert "rhgb" in params
        assert "quiet" in params
    
    def test_append_deduplicates(self):
        with patch.object(GrubKernelParams, "get_current_params", return_value=["rhgb", "quiet"]):
            with patch.object(GrubKernelParams, "_backup_grub_config"):
                with patch.object(GrubKernelParams, "_write_grub_config") as mock_write:
                    with patch.object(GrubKernelParams, "_run_grub_mkconfig", return_value=True):
                        grub = GrubKernelParams()
                        grub.append_params(["mitigations=off"])
        
        written_params = mock_write.call_args[0][0]
        assert "mitigations=off" in written_params
```

**Verify**: `pytest tests/unit/test_grub_kernel_params.py -v` passes.

---

## Step Exit Criteria

- [ ] `platforms/traditional/grub.py` exists
- [ ] All abstract methods implemented
- [ ] Unit tests pass
