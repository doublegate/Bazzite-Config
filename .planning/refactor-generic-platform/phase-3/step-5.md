# Phase 3, Step 5 — Wire Up PlatformServices (PR #10)

**Parent**: [Phase 3](README.md)
**Branch**: `feature/integrate-platform-services`
**Dependency**: PRs #6, #7, #8, #9 merged
**Estimated Time**: 2 hours

---

## UoW 3.5.1: Add platform detection to BazziteGamingOptimizer.__init__()

**Goal**: Initialize platform services in main orchestrator.

**File**: `bazzite-optimizer.py`
**Location**: `BazziteGamingOptimizer.__init__()` (around line 6842)

**Change to**:
```python
def __init__(self):
    self.logger = setup_logging()
    
    # Platform detection
    from platforms import detect_platform, PlatformServices
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

## UoW 3.5.2: Pass platform_services to all optimizers

**Goal**: Update `initialize_optimizers()` to pass services to all optimizers.

**File**: `bazzite-optimizer.py`
**Location**: `BazziteGamingOptimizer.initialize_optimizers()` (around line 6969)

**Change to**:
```python
def initialize_optimizers(self):
    """Initialize all optimizer modules with selected profile"""
    ps = self.platform_services
    pi = self.platform_info
    
    # ... dynamic names from Step 3.4 ...
    
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

## UoW 3.5.3: Update check_prerequisites() to use platform_info

**Goal**: Replace `bazzite_os` check with platform detection.

**File**: `bazzite-optimizer.py`
**Location**: `BazziteGamingOptimizer.check_prerequisites()` (around line 6940)

**Change to**:
```python
# Platform-specific warnings
from platforms import PlatformType
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

## UoW 3.5.4: Full integration test

**Goal**: Run complete validation on Ultramarine.

**Test commands**:
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
- All validations use appropriate platform services

---

## Step Exit Criteria

- [ ] Platform detection in main orchestrator
- [ ] All optimizers receive platform_services
- [ ] check_prerequisites() uses platform_info
- [ ] Full integration works on Ultramarine
