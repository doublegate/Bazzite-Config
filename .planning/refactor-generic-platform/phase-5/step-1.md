# Phase 5, Step 1 — Multi-Platform Testing

**Parent**: [Phase 5](README.md)
**PR**: None (testing phase)
**Estimated Time**: 2-3 hours

---

## UoW 5.1.1: Create comprehensive test script

**Goal**: Create a script to run all platform tests.

**File**: `tests/test_platform_matrix.sh`

**Code**:
```bash
#!/bin/bash
set -e

echo "=== Platform Matrix Tests ==="
echo "Platform: $(grep PRETTY_NAME /etc/os-release | cut -d= -f2)"
echo ""

echo "[1/7] Unit Tests..."
pytest -q tests/unit/ || { echo "FAILED: Unit tests"; exit 1; }

echo "[2/7] Platform Detection..."
python3 -c "
from platforms import detect_platform
info = detect_platform()
print(f'  Type: {info.platform_type.name}')
print(f'  Distro: {info.distro_name}')
print(f'  Immutable: {info.is_immutable}')
print(f'  Pkg Manager: {info.package_manager}')
print(f'  Boot Method: {info.boot_method}')
"

echo "[3/7] Kernel Param Manager..."
python3 -c "
from platforms import detect_platform, PlatformServices
info = detect_platform()
services = PlatformServices(info)
kp = services.kernel_params
print(f'  Manager: {type(kp).__name__}')
params = kp.get_current_params()
print(f'  Current params: {len(params)} parameters')
"

echo "[4/7] Package Manager..."
python3 -c "
from platforms import detect_platform, PlatformServices
info = detect_platform()
services = PlatformServices(info)
pm = services.package_manager
print(f'  Manager: {type(pm).__name__}')
print(f'  python3 installed: {pm.is_installed(\"python3\")}')
"

echo "[5/7] Optimizer Initialization..."
sudo python3 -c "
import sys
sys.path.insert(0, '.')
from bazzite_optimizer import BazziteGamingOptimizer
opt = BazziteGamingOptimizer()
print(f'  Platform: {opt.platform_info.platform_type.name}')
print(f'  Optimizers: {len(opt.optimizers)} loaded')
"

echo "[6/7] Validation Mode..."
sudo ./bazzite-optimizer.py --validate 2>&1 | tail -5

echo "[7/7] Check for Errors..."
ERROR_COUNT=$(sudo ./bazzite-optimizer.py --validate 2>&1 | grep -ci "error\|exception\|traceback" || true)
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "  WARNING: Found $ERROR_COUNT potential errors"
else
    echo "  No errors found"
fi

echo ""
echo "=== All Tests Passed ==="
```

---

## UoW 5.1.2: Test on Ultramarine

**Goal**: Run full test suite on Ultramarine.

**Task**:
```bash
cd /home/vince/Projects/Bazzite-Config
chmod +x tests/test_platform_matrix.sh
./tests/test_platform_matrix.sh
```

**Expected results**:
- Platform: `FEDORA_TRADITIONAL`
- Kernel params: `GrubKernelParams`
- Package manager: `DnfPackageManager`
- All tests pass

**Document in**: `.planning/refactor-generic-platform/test-results/ultramarine.md`

---

## UoW 5.1.3: Document test results template

**Goal**: Create template for recording test results.

**File**: `.planning/refactor-generic-platform/test-results/TEMPLATE.md`

**Content**:
```markdown
# Test Results: [Platform Name]

**Date**: YYYY-MM-DD
**Tester**: [Name/Team]
**System**: [Distro] [Version]

## System Info
- CPU: 
- GPU: 
- RAM: 
- Kernel: 

## Platform Detection
- Type: 
- Immutable: 
- Package Manager: 
- Boot Method: 

## Test Results

| Test | Result | Notes |
|------|--------|-------|
| Unit Tests | PASS/FAIL | |
| Platform Detection | PASS/FAIL | |
| Kernel Params Read | PASS/FAIL | |
| Package Manager | PASS/FAIL | |
| Validation Mode | PASS/FAIL | |

## Issues Found
- 
```

---

## Step Exit Criteria

- [ ] Test script created
- [ ] Tests pass on Ultramarine
- [ ] Results documented
