# PR Dependency Graph & Testing Strategy

## Visual Dependency Graph

```
                                    ┌─────────────────────────┐
                                    │  PR #9: Dynamic HW UI   │
                                    │  (Independent)          │
                                    └───────────┬─────────────┘
                                                │
┌───────────────────────────────────────────────┼───────────────────────────────────────────────┐
│                                               │                                               │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                           PR #1: Platform Detection                                      │  │
│  │                           (Foundation - MUST BE FIRST)                                   │  │
│  └─────────────────────────────────┬───────────────────────────────────────────────────────┘  │
│                                    │                                                          │
│              ┌─────────────────────┼─────────────────────┐                                    │
│              │                     │                     │                                    │
│              ▼                     ▼                     ▼                                    │
│  ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐                            │
│  │ PR #2: rpm-ostree │ │ PR #3: GRUB       │ │ PR #4: Package    │                            │
│  │ Kernel Params     │ │ Kernel Params     │ │ Managers          │                            │
│  │ (Bazzite path)    │ │ (Ultramarine)     │ │ (All platforms)   │                            │
│  └─────────┬─────────┘ └─────────┬─────────┘ └─────────┬─────────┘                            │
│            │                     │                     │                                      │
│            └─────────────────────┼─────────────────────┘                                      │
│                                  │                                                            │
│                                  ▼                                                            │
│                      ┌───────────────────────┐                                                │
│                      │ PR #5: PlatformServices│                                               │
│                      │ Factory               │                                                │
│                      └───────────┬───────────┘                                                │
│                                  │                                                            │
│              ┌───────────────────┼───────────────────┐                                        │
│              │                   │                   │                                        │
│              ▼                   ▼                   ▼                                        │
│  ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐                            │
│  │ PR #6: Migrate    │ │ PR #7: Migrate    │ │ PR #8: Conditional│                            │
│  │ KernelOptimizer   │ │ Package Install   │ │ Bazzite Features  │                            │
│  └─────────┬─────────┘ └─────────┬─────────┘ └─────────┬─────────┘                            │
│            │                     │                     │                                      │
│            └─────────────────────┼─────────────────────┘                                      │
│                                  │                                                            │
│                                  ▼                                                            │
│                      ┌───────────────────────┐◄───────────────────────────────────────────────┘
│                      │ PR #10: Integration   │
│                      │ (Wire everything up)  │
│                      └───────────┬───────────┘
│                                  │
│                                  ▼
│                      ┌───────────────────────┐
│                      │ PR #11: Cleanup       │
│                      │ (Remove dead code)    │
│                      └───────────┬───────────┘
│                                  │
│                                  ▼
│                      ┌───────────────────────┐
│                      │ PR #12: Documentation │
│                      └───────────────────────┘
│
│  Optional Hardware PRs (Independent branch):
│
│  ┌───────────────────┐
│  │ PR #13: Intel GPU │
│  └─────────┬─────────┘
│            │
│            ▼
│  ┌───────────────────┐
│  │ PR #14: Hybrid GPU│
│  └───────────────────┘
```

---

## Logical PR Groups

### Group A: Foundation (Week 1)
| Order | PR | Can Test on Ultramarine? |
|-------|-----|--------------------------|
| 1 | #1 Platform Detection | ✅ Yes - Primary test target |
| 2 | #9 Dynamic HW UI | ✅ Yes - Shows your hardware |

### Group B: Platform Implementations (Week 1-2)
| Order | PR | Can Test on Ultramarine? |
|-------|-----|--------------------------|
| 3 | #3 GRUB Kernel Params | ✅ Yes - Your system uses GRUB |
| 4 | #4 Package Managers | ✅ Yes - Test dnf path |
| 5 | #2 rpm-ostree Kernel Params | ❌ No - Needs Bazzite/Silverblue |

### Group C: Factory & Migration (Week 2)
| Order | PR | Can Test on Ultramarine? |
|-------|-----|--------------------------|
| 6 | #5 PlatformServices Factory | ✅ Yes - Should return GRUB+dnf |
| 7 | #6 Migrate KernelOptimizer | ✅ Yes - Uses GRUB path |
| 8 | #7 Migrate Package Install | ✅ Yes - Uses dnf path |
| 9 | #8 Conditional Bazzite | ✅ Yes - Should skip ujust |

### Group D: Integration & Cleanup (Week 2-3)
| Order | PR | Can Test on Ultramarine? |
|-------|-----|--------------------------|
| 10 | #10 Integration | ✅ Yes - Full system test |
| 11 | #11 Cleanup | ✅ Yes - Regression test |
| 12 | #12 Documentation | ✅ Yes - Verify instructions |

### Group E: Optional Hardware (Anytime)
| Order | PR | Can Test on Ultramarine? |
|-------|-----|--------------------------|
| - | #13 Intel GPU | ✅ Yes - You have Iris Xe |
| - | #14 Hybrid GPU | ✅ Yes - You have Intel+NVIDIA |

---

## Testing Strategy Per PR

### PR #1: Platform Detection

**Test on Ultramarine** ✅

```bash
# After implementing, run:
cd /home/vince/Projects/Bazzite-Config

# Unit tests
pytest tests/unit/test_platform_detection.py -v

# Manual verification
python3 -c "
from platform.detection import detect_platform
info = detect_platform()
print(f'Platform Type: {info.platform_type}')
print(f'Distro: {info.distro_name} {info.distro_version}')
print(f'Immutable: {info.is_immutable}')
print(f'Has ujust: {info.has_ujust}')
print(f'Package Manager: {info.package_manager}')
print(f'Boot Method: {info.boot_method}')
"

# Expected output on Ultramarine:
# Platform Type: PlatformType.FEDORA_TRADITIONAL
# Distro: Ultramarine Linux 43
# Immutable: False
# Has ujust: False
# Package Manager: dnf
# Boot Method: grub
```

**Pass Criteria**:
- [ ] `platform_type` is `FEDORA_TRADITIONAL`
- [ ] `is_immutable` is `False`
- [ ] `package_manager` is `dnf`
- [ ] `boot_method` is `grub`

---

### PR #3: GRUB Kernel Params

**Test on Ultramarine** ✅

```bash
# Unit tests with mocks
pytest tests/unit/test_grub_kernel_params.py -v

# Integration test (read-only, safe)
python3 -c "
from platform.traditional.grub import GrubKernelParams
grub = GrubKernelParams()
params = grub.get_current_params()
print('Current kernel params:')
for p in params:
    print(f'  {p}')
"

# Expected: Should show params from your /etc/default/grub
# e.g., rhgb, quiet, rd.driver.blacklist=nouveau, etc.

# Test backup creation (dry-run)
python3 -c "
from platform.traditional.grub import GrubKernelParams
grub = GrubKernelParams()
backup_path = grub._backup_grub_config()
print(f'Backup would be created at: {backup_path}')
"
```

**Pass Criteria**:
- [ ] Reads existing params from `/etc/default/grub`
- [ ] Parses `GRUB_CMDLINE_LINUX` correctly
- [ ] Backup mechanism works
- [ ] Unit tests pass

**Write Test (requires sudo, optional)**:
```bash
# Only if you want to test actual writes
# This will require reboot to take effect
sudo python3 -c "
from platform.traditional.grub import GrubKernelParams
grub = GrubKernelParams()
# Add a harmless test param
grub.append_params(['test_param=1'])
print('Param added, check /etc/default/grub')
# Remove it
grub.remove_params(['test_param=1'])
print('Param removed')
"
```

---

### PR #4: Package Managers

**Test on Ultramarine** ✅

```bash
# Unit tests
pytest tests/unit/test_dnf_package_manager.py -v

# Integration test (read-only, safe)
python3 -c "
from platform.traditional.rpm import DnfPackageManager
dnf = DnfPackageManager()
print(f'htop installed: {dnf.is_installed(\"htop\")}')
print(f'python3 installed: {dnf.is_installed(\"python3\")}')
print(f'nonexistent-pkg installed: {dnf.is_installed(\"nonexistent-pkg-12345\")}')
"

# Expected:
# htop installed: True/False (depending on your system)
# python3 installed: True
# nonexistent-pkg installed: False
```

**Pass Criteria**:
- [ ] `is_installed()` returns correct results
- [ ] Unit tests pass with mocked dnf calls

**Install Test (requires sudo, optional)**:
```bash
# Only if you want to test actual installs
sudo python3 -c "
from platform.traditional.rpm import DnfPackageManager
dnf = DnfPackageManager()
# Install a small harmless package
result = dnf.install(['cowsay'])
print(f'Install result: {result}')
# Verify
print(f'cowsay installed: {dnf.is_installed(\"cowsay\")}')
"
```

---

### PR #5: PlatformServices Factory

**Test on Ultramarine** ✅

```bash
# Unit tests
pytest tests/unit/test_platform_services.py -v

# Integration test
python3 -c "
from platform.detection import detect_platform
from platform.services import PlatformServices

info = detect_platform()
services = PlatformServices(info)

print(f'Platform: {info.platform_type}')
print(f'Package Manager Type: {type(services.package_manager).__name__}')
print(f'Kernel Params Type: {type(services.kernel_params).__name__}')
"

# Expected on Ultramarine:
# Platform: PlatformType.FEDORA_TRADITIONAL
# Package Manager Type: DnfPackageManager
# Kernel Params Type: GrubKernelParams
```

**Pass Criteria**:
- [ ] Factory returns `DnfPackageManager` on Ultramarine
- [ ] Factory returns `GrubKernelParams` on Ultramarine
- [ ] Unit tests pass

---

### PR #6: Migrate KernelOptimizer

**Test on Ultramarine** ✅

```bash
# Existing tests still pass
pytest tests/test_bazzite_optimizer_enhanced_kargs.py -v
pytest tests/unit/test_optimizers.py -v

# Integration test (read-only)
sudo python3 -c "
import sys
sys.path.insert(0, '.')
from bazzite_optimizer import KernelOptimizer
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# This should now use GrubKernelParams internally
ko = KernelOptimizer(logger)
# Just test validation, don't apply
result = ko.validate()
print(f'Validation result: {result}')
"
```

**Pass Criteria**:
- [ ] All existing kernel param tests pass
- [ ] `KernelOptimizer` uses `GrubKernelParams` on Ultramarine
- [ ] No rpm-ostree errors

---

### PR #7: Migrate Package Install

**Test on Ultramarine** ✅

```bash
# Existing tests
pytest tests/unit/test_optimizers.py -v

# Integration test
sudo python3 -c "
import sys
sys.path.insert(0, '.')
from bazzite_optimizer import GamingToolsOptimizer
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

gto = GamingToolsOptimizer(logger)
# Just test validation, don't install
result = gto.validate()
print(f'Validation result: {result}')
"
```

**Pass Criteria**:
- [ ] No rpm-ostree calls on Ultramarine
- [ ] Uses dnf for package operations
- [ ] Tests pass

---

### PR #8: Conditional Bazzite

**Test on Ultramarine** ✅

```bash
# Integration test - this is the key test
sudo python3 -c "
import sys
sys.path.insert(0, '.')
from bazzite_optimizer import BazziteOptimizer
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

bo = BazziteOptimizer(logger)
result = bo.apply_optimizations()
print(f'Result: {result}')
# Should see: 'Skipping Bazzite-specific optimizations (not on Bazzite)'
# Should NOT see any ujust errors
"
```

**Pass Criteria**:
- [ ] No ujust errors on Ultramarine
- [ ] Info message about skipping Bazzite features
- [ ] Returns `True` (success, not failure)

---

### PR #9: Dynamic Hardware UI

**Test on Ultramarine** ✅

```bash
# Run the optimizer in validate mode
sudo ./bazzite-optimizer.py --validate 2>&1 | head -20

# Check banner shows YOUR hardware:
# - Intel i5-1240P (not i9-10850K)
# - RTX 3060 or Iris Xe (not RTX 5080)
# - 62GB RAM (not 64GB)
```

**Pass Criteria**:
- [ ] Banner shows "Intel... i5-1240P" (your CPU)
- [ ] Banner shows "RTX 3060" or "Iris Xe" (your GPUs)
- [ ] Banner shows "62GB RAM" (your RAM)
- [ ] No hard-coded "RTX 5080" or "i9-10850K"

---

### PR #10: Integration

**Test on Ultramarine** ✅

```bash
# Full validation run
sudo ./bazzite-optimizer.py --validate

# Expected:
# - Platform detected as Fedora Traditional
# - No rpm-ostree errors
# - No ujust errors
# - Bazzite features skipped gracefully
# - All other validations work

# Check status
./gaming-manager-suite.py --status
```

**Pass Criteria**:
- [ ] Full `--validate` completes without errors
- [ ] All platform-appropriate features work
- [ ] Bazzite-specific features skipped

---

### PR #11: Cleanup

**Test on Ultramarine** ✅

```bash
# Full test suite
pytest -q

# Verify no dead code references
grep -r "enhanced_rpm_ostree_kargs" bazzite-optimizer.py
# Should return nothing

# Full validation
sudo ./bazzite-optimizer.py --validate
```

**Pass Criteria**:
- [ ] All tests pass
- [ ] No dead code remaining
- [ ] Full functionality preserved

---

### PR #13 & #14: Intel & Hybrid GPU

**Test on Ultramarine** ✅

```bash
# Intel GPU detection
python3 -c "
from platform_support.intel_gpu import IntelGpuOptimizer
igo = IntelGpuOptimizer()
print(f'Intel GPU detected: {igo.is_supported()}')
print(f'GPU info: {igo.get_gpu_info()}')
"

# Hybrid GPU detection
python3 -c "
from platform_support.hybrid_gpu import HybridGpuManager
hgm = HybridGpuManager()
print(f'Hybrid config: {hgm.is_hybrid()}')
print(f'iGPU: {hgm.igpu}')
print(f'dGPU: {hgm.dgpu}')
"
```

**Pass Criteria**:
- [ ] Detects Intel Iris Xe
- [ ] Detects NVIDIA RTX 3060
- [ ] Identifies hybrid configuration
- [ ] PRIME offload options available

---

## CI/CD Testing Matrix

For GitHub Actions, create test jobs:

```yaml
# .github/workflows/platform-tests.yml
name: Platform Tests

on: [push, pull_request]

jobs:
  test-detection:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -e .[dev]
      - name: Run platform detection tests
        run: pytest tests/unit/test_platform_detection.py -v

  test-grub:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
      - name: Install dependencies
        run: pip install -e .[dev]
      - name: Run GRUB kernel params tests
        run: pytest tests/unit/test_grub_kernel_params.py -v

  test-package-managers:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
      - name: Install dependencies
        run: pip install -e .[dev]
      - name: Run package manager tests
        run: |
          pytest tests/unit/test_dnf_package_manager.py -v
          pytest tests/unit/test_apt_package_manager.py -v
```

---

## Local Testing Checklist for Ultramarine

Before each PR merge, run this checklist on your Ultramarine system:

```bash
#!/bin/bash
# save as: test-on-ultramarine.sh

echo "=== Ultramarine Platform Test Suite ==="

echo -e "\n[1/6] Running unit tests..."
pytest -q || exit 1

echo -e "\n[2/6] Checking platform detection..."
python3 -c "
from platform.detection import detect_platform
info = detect_platform()
assert info.platform_type.name == 'FEDORA_TRADITIONAL', f'Wrong platform: {info.platform_type}'
assert info.is_immutable == False, 'Should not be immutable'
assert info.package_manager == 'dnf', f'Wrong pkg mgr: {info.package_manager}'
assert info.boot_method == 'grub', f'Wrong boot method: {info.boot_method}'
print('✓ Platform detection correct')
"

echo -e "\n[3/6] Checking kernel params (read-only)..."
python3 -c "
from platform.traditional.grub import GrubKernelParams
grub = GrubKernelParams()
params = grub.get_current_params()
assert len(params) > 0, 'No params found'
print(f'✓ Found {len(params)} kernel parameters')
"

echo -e "\n[4/6] Checking package manager..."
python3 -c "
from platform.traditional.rpm import DnfPackageManager
dnf = DnfPackageManager()
assert dnf.is_installed('python3'), 'python3 should be installed'
print('✓ Package manager working')
"

echo -e "\n[5/6] Checking PlatformServices factory..."
python3 -c "
from platform.detection import detect_platform
from platform.services import PlatformServices
info = detect_platform()
services = PlatformServices(info)
assert 'Grub' in type(services.kernel_params).__name__, 'Should use GrubKernelParams'
assert 'Dnf' in type(services.package_manager).__name__, 'Should use DnfPackageManager'
print('✓ PlatformServices factory correct')
"

echo -e "\n[6/6] Running validation (requires sudo)..."
sudo ./bazzite-optimizer.py --validate 2>&1 | grep -E "(ERROR|FAIL|SUCCESS|Skipping)"

echo -e "\n=== All tests completed ==="
```

---

## Quick Reference: What Can Be Tested Where

| PR | Ultramarine | Bazzite | Ubuntu | CI (mocked) |
|----|-------------|---------|--------|-------------|
| #1 Platform Detection | ✅ | ✅ | ✅ | ✅ |
| #2 rpm-ostree Kernel | ❌ | ✅ | ❌ | ✅ |
| #3 GRUB Kernel | ✅ | ❌ | ✅ | ✅ |
| #4 Package Managers | ✅ dnf | ✅ rpm-ostree | ✅ apt | ✅ |
| #5 PlatformServices | ✅ | ✅ | ✅ | ✅ |
| #6 Migrate Kernel | ✅ | ✅ | ✅ | ✅ |
| #7 Migrate Packages | ✅ | ✅ | ✅ | ✅ |
| #8 Conditional Bazzite | ✅ | ✅ | ✅ | ✅ |
| #9 Dynamic HW UI | ✅ | ✅ | ✅ | ❌ |
| #10 Integration | ✅ | ✅ | ✅ | ⚠️ |
| #11 Cleanup | ✅ | ✅ | ✅ | ✅ |
| #13 Intel GPU | ✅ | ⚠️ | ⚠️ | ✅ |
| #14 Hybrid GPU | ✅ | ⚠️ | ⚠️ | ✅ |

Legend: ✅ Full test | ⚠️ Partial/depends on HW | ❌ Cannot test
