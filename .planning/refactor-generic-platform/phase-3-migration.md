# Phase 3 — Migration

**Team**: TEAM_001
**Purpose**: Migrate existing code to use platform abstraction layer
**Structure**: Each Step = 1 PR, Each UoW = 1 SLM task

---

## Step 3.1: Migrate KernelOptimizer (PR #6)

**Branch**: `feature/migrate-kernel-optimizer`
**Dependency**: PR #5 merged
**Estimated Time**: 3 hours

### UoW 3.1.1: Add platform_services parameter to KernelOptimizer

**Task**: Modify `KernelOptimizer.__init__()` to accept optional `PlatformServices`.

**File**: `bazzite-optimizer.py`
**Location**: `class KernelOptimizer` (around line 4912)

**Current**:
```python
class KernelOptimizer(BaseOptimizer):
    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
```

**Change to**:
```python
class KernelOptimizer(BaseOptimizer):
    def __init__(self, logger: logging.Logger, platform_services=None):
        super().__init__(logger)
        self._platform_services = platform_services
        self._kernel_params = None
    
    @property
    def kernel_params(self):
        """Lazy-load kernel param manager"""
        if self._kernel_params is None:
            if self._platform_services:
                self._kernel_params = self._platform_services.kernel_params
            else:
                # Fallback to rpm-ostree for backward compatibility
                from platform.immutable.rpm_ostree import RpmOstreeKernelParams
                self._kernel_params = RpmOstreeKernelParams()
        return self._kernel_params
```

**Verify**: Class still instantiates without errors.

---

### UoW 3.1.2: Migrate _get_current_kernel_params()

**Task**: Replace internal logic with call to `kernel_params.get_current_params()`.

**File**: `bazzite-optimizer.py`
**Location**: `KernelOptimizer._get_current_kernel_params()` (around line 5120)

**Current**: Complex logic calling `rpm-ostree kargs` and `rpm-ostree status`.

**Change to**:
```python
def _get_current_kernel_params(self) -> List[str]:
    """Get current kernel parameters using platform abstraction"""
    try:
        return self.kernel_params.get_current_params()
    except Exception as e:
        self.logger.error(f"Failed to get kernel params: {e}")
        return []
```

**Verify**: Returns correct params on Ultramarine (from grub).

---

### UoW 3.1.3: Migrate _apply_kernel_param_batch()

**Task**: Replace rpm-ostree kargs calls with `kernel_params.append_params()`.

**File**: `bazzite-optimizer.py`
**Location**: `KernelOptimizer._apply_kernel_param_batch()` (around line 5170)

**Current**: Direct `rpm-ostree kargs --append` calls.

**Change to**:
```python
def _apply_kernel_param_batch(self, params: List[str], mode: str = "append") -> bool:
    """Apply kernel parameters using platform abstraction"""
    try:
        if mode == "append":
            return self.kernel_params.append_params(params)
        elif mode == "replace":
            # For replace mode, remove old then add new
            # This is handled by the implementation
            return self.kernel_params.append_params(params)
        else:
            self.logger.error(f"Unknown mode: {mode}")
            return False
    except Exception as e:
        self.logger.error(f"Failed to apply kernel params: {e}")
        return False
```

**Verify**: Params are written to grub on Ultramarine.

---

### UoW 3.1.4: Migrate _remove_kernel_params()

**Task**: Replace rpm-ostree kargs --delete with `kernel_params.remove_params()`.

**File**: `bazzite-optimizer.py`
**Location**: `KernelOptimizer._remove_kernel_params()` (around line 5480)

**Change to**:
```python
def _remove_kernel_params(self, params: List[str]) -> bool:
    """Remove kernel parameters using platform abstraction"""
    try:
        return self.kernel_params.remove_params(params)
    except Exception as e:
        self.logger.error(f"Failed to remove kernel params: {e}")
        return False
```

---

### UoW 3.1.5: Remove rpm-ostree specific methods from KernelOptimizer

**Task**: Remove methods that are now in `RpmOstreeKernelParams`.

**Methods to remove**:
- `_ensure_rpm_ostree_ready()` (line ~5047)
- `_wait_for_rpm_ostree_transaction()` (line ~5090)

**Note**: Mark as deprecated first, remove in Phase 4.

```python
def _ensure_rpm_ostree_ready(self) -> bool:
    """DEPRECATED: Use self.kernel_params instead"""
    self.logger.warning("_ensure_rpm_ostree_ready is deprecated")
    return True
```

---

### UoW 3.1.6: Update apply_kernel_parameters() main method

**Task**: Simplify the main `apply_kernel_parameters()` method.

**File**: `bazzite-optimizer.py`
**Location**: `KernelOptimizer.apply_kernel_parameters()` (around line 4916)

**Change**: Remove the rpm-ostree specific checks and use abstraction.

```python
def apply_kernel_parameters(self) -> bool:
    """Apply kernel parameters for selected profile"""
    self.logger.info("Applying kernel parameters...")
    
    # Get profile-specific parameters
    params = self._get_profile_kernel_params()
    
    # Apply using platform abstraction
    if not self.kernel_params.append_params(params):
        self.logger.error("Failed to apply kernel parameters")
        return False
    
    if self.kernel_params.requires_reboot():
        self.logger.info("Kernel parameter changes require reboot")
    
    return True
```

---

### UoW 3.1.7: Test KernelOptimizer migration on Ultramarine

**Task**: Run integration tests.

```bash
# Unit tests
pytest tests/test_bazzite_optimizer_enhanced_kargs.py -v

# Integration test (read-only)
sudo python3 -c "
import sys
sys.path.insert(0, '.')
import logging
logging.basicConfig(level=logging.INFO)

from platform import detect_platform, PlatformServices
from bazzite_optimizer import KernelOptimizer

platform_info = detect_platform()
services = PlatformServices(platform_info)

ko = KernelOptimizer(logging.getLogger(), platform_services=services)
params = ko._get_current_kernel_params()
print(f'Current params: {params}')
print(f'Using: {type(ko.kernel_params).__name__}')
"
```

**Expected on Ultramarine**:
- `Using: GrubKernelParams`
- Params from `/etc/default/grub`

---

## Step 3.2: Migrate Package Installation (PR #7)

**Branch**: `feature/migrate-package-install`
**Dependency**: PR #5 merged
**Estimated Time**: 2 hours

### UoW 3.2.1: Add platform_services to BaseOptimizer

**Task**: Modify `BaseOptimizer.__init__()`.

**File**: `bazzite-optimizer.py`
**Location**: `class BaseOptimizer` (around line 2222)

**Change**:
```python
class BaseOptimizer:
    def __init__(self, logger: logging.Logger, platform_services=None):
        self.logger = logger
        self._platform_services = platform_services
        self._package_manager = None
    
    @property
    def package_manager(self):
        """Lazy-load package manager"""
        if self._package_manager is None:
            if self._platform_services:
                self._package_manager = self._platform_services.package_manager
            else:
                # Fallback for backward compatibility
                from platform.traditional.rpm import DnfPackageManager
                self._package_manager = DnfPackageManager()
        return self._package_manager
```

---

### UoW 3.2.2: Migrate BaseOptimizer.install_package()

**Task**: Replace direct rpm-ostree/dnf calls with abstraction.

**File**: `bazzite-optimizer.py`
**Location**: `BaseOptimizer.install_package()` (around line 2336)

**Current**: Complex logic with rpm-ostree → dnf fallback.

**Change to**:
```python
def install_package(self, package_name: str, timeout: int = 300) -> bool:
    """Install a package using platform-appropriate manager"""
    self.logger.debug(f"Installing package: {package_name}")
    try:
        return self.package_manager.install([package_name], timeout=timeout)
    except Exception as e:
        self.logger.error(f"Failed to install {package_name}: {e}")
        return False
```

---

### UoW 3.2.3: Update all BaseOptimizer subclass __init__ calls

**Task**: Pass `platform_services` through to subclasses.

**Subclasses to update**:
- `NvidiaOptimizer`
- `CPUOptimizer`
- `MemoryOptimizer`
- `NetworkOptimizer`
- `AudioOptimizer`
- `GamingToolsOptimizer`
- `KernelOptimizer` (already done in Step 3.1)
- `SystemdServiceOptimizer`
- `PlasmaOptimizer`
- `BootInfrastructureOptimizer`
- `BazziteOptimizer`

**Example change for NvidiaOptimizer**:
```python
class NvidiaOptimizer(BaseOptimizer):
    def __init__(self, logger: logging.Logger, platform_services=None):
        super().__init__(logger, platform_services)
```

---

### UoW 3.2.4: Migrate NvidiaOptimizer._install_nvidia_drivers()

**Task**: Update NVIDIA driver installation to use abstraction.

**File**: `bazzite-optimizer.py`
**Location**: `NvidiaOptimizer._install_nvidia_drivers()` (around line 3050)

**Current**: Direct `rpm-ostree install` calls.

**Change to**:
```python
def _install_nvidia_drivers(self) -> bool:
    """Install NVIDIA drivers using platform package manager"""
    packages = [
        "akmod-nvidia-open",
        "xorg-x11-drv-nvidia-open",
        "nvidia-vaapi-driver",
        "nvidia-settings"
    ]
    
    for package in packages:
        if not self.package_manager.is_installed(package):
            self.logger.info(f"Installing {package}")
            if not self.install_package(package):
                self.logger.warning(f"Failed to install {package}")
    
    return True
```

---

### UoW 3.2.5: Migrate GamingToolsOptimizer package installs

**Task**: Update gaming tools installation.

**File**: `bazzite-optimizer.py`
**Location**: `class GamingToolsOptimizer` (around line 4655)

**Change**: Replace any direct package manager calls with `self.install_package()`.

---

### UoW 3.2.6: Test package installation on Ultramarine

**Task**: Run integration tests.

```bash
# Integration test (read-only)
sudo python3 -c "
import sys
sys.path.insert(0, '.')
import logging
logging.basicConfig(level=logging.INFO)

from platform import detect_platform, PlatformServices
from bazzite_optimizer import GamingToolsOptimizer

platform_info = detect_platform()
services = PlatformServices(platform_info)

gto = GamingToolsOptimizer(logging.getLogger(), platform_services=services)
print(f'Using: {type(gto.package_manager).__name__}')
print(f'htop installed: {gto.package_manager.is_installed(\"htop\")}')
"
```

**Expected on Ultramarine**:
- `Using: DnfPackageManager`

---

## Step 3.3: Make Bazzite Features Conditional (PR #8)

**Branch**: `feature/conditional-bazzite`
**Dependency**: PR #5 merged
**Estimated Time**: 1 hour

### UoW 3.3.1: Add platform_info to BazziteOptimizer

**Task**: Modify `BazziteOptimizer` to accept platform info.

**File**: `bazzite-optimizer.py`
**Location**: `class BazziteOptimizer` (around line 6497)

**Change**:
```python
class BazziteOptimizer(BaseOptimizer):
    """Bazzite-specific optimizations using ujust commands"""
    
    def __init__(self, logger: logging.Logger, platform_services=None, platform_info=None):
        super().__init__(logger, platform_services)
        self._platform_info = platform_info
    
    @property
    def is_bazzite(self) -> bool:
        """Check if running on Bazzite"""
        if self._platform_info:
            return self._platform_info.has_ujust
        # Fallback to checking ujust directly
        import shutil
        return shutil.which("ujust") is not None
```

---

### UoW 3.3.2: Make apply_ujust_commands() conditional

**Task**: Skip ujust commands if not on Bazzite.

**File**: `bazzite-optimizer.py`
**Location**: `BazziteOptimizer.apply_ujust_commands()` (around line 6500)

**Change**:
```python
def apply_ujust_commands(self) -> bool:
    """Execute Bazzite ujust commands (only on Bazzite)"""
    if not self.is_bazzite:
        self.logger.info("Skipping Bazzite-specific optimizations (ujust not available)")
        return True  # Return success, not failure
    
    self.logger.info("Applying Bazzite-specific optimizations...")
    
    for command in BAZZITE_UJUST_COMMANDS:
        self.logger.info(f"Executing: {command}")
        returncode, stdout, stderr = run_command(command, check=False, timeout=120)
        
        if returncode != 0:
            self.logger.warning(f"Command failed: {command}")
            self.logger.warning(f"Error: {stderr}")
        else:
            self.logger.info(f"Successfully executed: {command}")
    
    return True
```

---

### UoW 3.3.3: Make validate() conditional

**Task**: Return empty validation on non-Bazzite.

**File**: `bazzite-optimizer.py`
**Location**: `BazziteOptimizer.validate()` (around line 6520)

**Change**:
```python
def validate(self) -> Dict[str, bool]:
    """Validate Bazzite optimizations"""
    if not self.is_bazzite:
        self.logger.debug("Skipping Bazzite validation (not on Bazzite)")
        return {}
    
    validations = {}
    
    # Check if ujust is available
    returncode, _, _ = run_command("which ujust", check=False)
    validations["ujust_available"] = returncode == 0
    
    return validations
```

---

### UoW 3.3.4: Test on Ultramarine

**Task**: Verify no errors on non-Bazzite system.

```bash
sudo python3 -c "
import sys
sys.path.insert(0, '.')
import logging
logging.basicConfig(level=logging.INFO)

from platform import detect_platform, PlatformServices
from bazzite_optimizer import BazziteOptimizer

platform_info = detect_platform()
services = PlatformServices(platform_info)

bo = BazziteOptimizer(logging.getLogger(), platform_services=services, platform_info=platform_info)
print(f'Is Bazzite: {bo.is_bazzite}')
result = bo.apply_optimizations()
print(f'Result: {result}')
"
```

**Expected on Ultramarine**:
- `Is Bazzite: False`
- Log message: "Skipping Bazzite-specific optimizations"
- `Result: True` (success, not failure)

---

## Step 3.4: Dynamic Hardware UI (PR #9)

**Branch**: `feature/dynamic-hardware-ui`
**Dependency**: None (independent)
**Estimated Time**: 1 hour

### UoW 3.4.1: Update print_banner() to use dynamic hardware

**Task**: Replace hard-coded hardware strings.

**File**: `bazzite-optimizer.py`
**Location**: `BazziteGamingOptimizer.print_banner()` (around line 6854)

**Current**:
```python
def print_banner(self):
    print_colored("=" * 62, Colors.HEADER)
    print_colored("    BAZZITE DX ULTIMATE GAMING OPTIMIZER v" +
                  SCRIPT_VERSION, Colors.HEADER + Colors.BOLD)
    print_colored("  Enhanced for RTX 5080 Blackwell | i9-10850K | 64GB RAM", Colors.OKCYAN)
```

**Change to**:
```python
def print_banner(self):
    print_colored("=" * 62, Colors.HEADER)
    print_colored("    LINUX GAMING OPTIMIZER v" +
                  SCRIPT_VERSION, Colors.HEADER + Colors.BOLD)
    
    # Dynamic hardware display
    gpu_name = "Unknown GPU"
    if self.system_info.get('gpus'):
        gpu_name = self.system_info['gpus'][0].split(':')[-1].strip()[:30]
    
    cpu_name = self.system_info.get('cpu_model', 'Unknown CPU')
    # Shorten CPU name if too long
    if len(cpu_name) > 25:
        cpu_name = cpu_name[:22] + "..."
    
    ram_gb = self.system_info.get('ram_gb', '?')
    
    print_colored(f"  Detected: {gpu_name} | {cpu_name} | {ram_gb}GB RAM", Colors.OKCYAN)
```

---

### UoW 3.4.2: Update initialize_optimizers() names

**Task**: Make optimizer names generic or dynamic.

**File**: `bazzite-optimizer.py`
**Location**: `BazziteGamingOptimizer.initialize_optimizers()` (around line 6969)

**Current**:
```python
self.optimizers = [
    ("Boot Infrastructure", BootInfrastructureOptimizer(self.logger)),
    ("NVIDIA RTX 5080 Blackwell", NvidiaOptimizer(self.logger)),
    ("Intel i9-10850K CPU", CPUOptimizer(self.logger)),
    ...
]
```

**Change to**:
```python
def initialize_optimizers(self):
    """Initialize all optimizer modules with selected profile"""
    # Dynamic names based on detected hardware
    gpu_name = "GPU"
    if self.system_info.get('gpus'):
        if "nvidia" in self.system_info['gpus'][0].lower():
            gpu_name = "NVIDIA GPU"
        elif "amd" in self.system_info['gpus'][0].lower():
            gpu_name = "AMD GPU"
        elif "intel" in self.system_info['gpus'][0].lower():
            gpu_name = "Intel GPU"
    
    cpu_name = "CPU"
    cpu_model = self.system_info.get('cpu_model', '').lower()
    if "intel" in cpu_model:
        cpu_name = "Intel CPU"
    elif "amd" in cpu_model:
        cpu_name = "AMD CPU"
    
    self.optimizers = [
        ("Boot Infrastructure", BootInfrastructureOptimizer(self.logger)),
        (gpu_name, NvidiaOptimizer(self.logger)),
        (cpu_name, CPUOptimizer(self.logger)),
        ("Memory & Storage", MemoryOptimizer(self.logger)),
        ("Audio System", AudioOptimizer(self.logger)),
        ("Network", NetworkOptimizer(self.logger)),
        ("Gaming Tools", GamingToolsOptimizer(self.logger)),
        ("Kernel & Boot", KernelOptimizer(self.logger)),
        ("Systemd Services", SystemdServiceOptimizer(self.logger)),
        ("Desktop Environment", PlasmaOptimizer(self.logger)),
        ("Distribution Specific", BazziteOptimizer(self.logger))
    ]
```

---

### UoW 3.4.3: Test banner output on Ultramarine

**Task**: Verify hardware is correctly displayed.

```bash
sudo ./bazzite-optimizer.py --validate 2>&1 | head -10
```

**Expected on Ultramarine**:
```
==============================================================
    LINUX GAMING OPTIMIZER v5.0.0
  Detected: GeForce RTX 3060 | Intel i5-1240P | 62GB RAM
==============================================================
```

---

## Step 3.5: Wire Up PlatformServices (PR #10)

**Branch**: `feature/integrate-platform-services`
**Dependency**: PRs #6, #7, #8 merged
**Estimated Time**: 2 hours

### UoW 3.5.1: Add platform detection to BazziteGamingOptimizer.__init__()

**Task**: Initialize platform services in main orchestrator.

**File**: `bazzite-optimizer.py`
**Location**: `BazziteGamingOptimizer.__init__()` (around line 6842)

**Change**:
```python
def __init__(self):
    self.logger = setup_logging()
    
    # Platform detection
    from platform import detect_platform, PlatformServices
    self.platform_info = detect_platform()
    self.platform_services = PlatformServices(self.platform_info)
    self.logger.info(f"Detected platform: {self.platform_info.platform_type.name}")
    self.logger.info(f"Package manager: {self.platform_info.package_manager}")
    self.logger.info(f"Boot method: {self.platform_info.boot_method}")
    
    self.optimizers = []
    self.needs_reboot = False
    self.system_info = get_system_info()
    # ... rest unchanged
```

---

### UoW 3.5.2: Pass platform_services to all optimizers

**Task**: Update `initialize_optimizers()` to pass services.

**File**: `bazzite-optimizer.py`
**Location**: `BazziteGamingOptimizer.initialize_optimizers()` (around line 6969)

**Change**:
```python
def initialize_optimizers(self):
    """Initialize all optimizer modules with selected profile"""
    ps = self.platform_services
    pi = self.platform_info
    
    # ... dynamic names from UoW 3.4.2 ...
    
    self.optimizers = [
        ("Boot Infrastructure", BootInfrastructureOptimizer(self.logger, ps)),
        (gpu_name, NvidiaOptimizer(self.logger, ps)),
        (cpu_name, CPUOptimizer(self.logger, ps)),
        ("Memory & Storage", MemoryOptimizer(self.logger, ps)),
        ("Audio System", AudioOptimizer(self.logger, ps)),
        ("Network", NetworkOptimizer(self.logger, ps)),
        ("Gaming Tools", GamingToolsOptimizer(self.logger, ps)),
        ("Kernel & Boot", KernelOptimizer(self.logger, ps)),
        ("Systemd Services", SystemdServiceOptimizer(self.logger, ps)),
        ("Desktop Environment", PlasmaOptimizer(self.logger, ps)),
        ("Distribution Specific", BazziteOptimizer(self.logger, ps, pi))
    ]
```

---

### UoW 3.5.3: Update check_prerequisites() to use platform_info

**Task**: Replace `bazzite_os` check with platform detection.

**File**: `bazzite-optimizer.py`
**Location**: `BazziteGamingOptimizer.check_prerequisites()` (around line 6940)

**Current**:
```python
if not self.hardware_checks["bazzite_os"]:
    print_colored("\nWARNING: Bazzite not detected...", Colors.WARNING)
```

**Change to**:
```python
# Platform-specific warnings
if self.platform_info.platform_type == PlatformType.UNKNOWN:
    print_colored("\nWARNING: Unknown platform detected.", Colors.WARNING)
    print_colored("Some optimizations may not work correctly.", Colors.WARNING)
    print_colored("Continue anyway? (y/n): ", Colors.WARNING, end="")
    if input().lower() != 'y':
        return False
elif not self.platform_info.is_immutable:
    print_colored(f"\nINFO: Running on {self.platform_info.distro_name}", Colors.OKBLUE)
    print_colored("Using GRUB for kernel parameters.", Colors.OKBLUE)
```

---

### UoW 3.5.4: Full integration test on Ultramarine

**Task**: Run complete validation.

```bash
# Full validation
sudo ./bazzite-optimizer.py --validate

# Check for errors
sudo ./bazzite-optimizer.py --validate 2>&1 | grep -i "error\|fail\|exception"

# Should be empty or minimal
```

**Expected**:
- Platform detected as `FEDORA_TRADITIONAL`
- No rpm-ostree errors
- Bazzite features skipped gracefully
- All validations run using appropriate platform services

---

## Exit Criteria for Phase 3

- [ ] KernelOptimizer uses platform abstraction (PR #6)
- [ ] Package installation uses platform abstraction (PR #7)
- [ ] Bazzite features conditional (PR #8)
- [ ] Dynamic hardware in UI (PR #9)
- [ ] Full integration working (PR #10)
- [ ] All tests pass on Ultramarine
- [ ] No rpm-ostree errors on traditional systems
- [ ] No ujust errors on non-Bazzite systems
