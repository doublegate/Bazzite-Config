# Phase 2, Step 5 — rpm-ostree Implementations (PR #2)

**Parent**: [Phase 2](README.md)
**Branch**: `feature/rpm-ostree-kernel-params`
**Dependency**: PR #1 merged
**Estimated Time**: 3 hours
**Note**: Cannot test on Ultramarine, requires Bazzite/Silverblue

---

## UoW 2.5.1: Create RpmOstreeKernelParams class

**Goal**: Extract kernel param logic from existing KernelOptimizer.

**File**: `platforms/immutable/rpm_ostree.py`

**Source**: Extract from `bazzite-optimizer.py` class `KernelOptimizer`

**Methods to implement**:
- `get_current_params()` — from `_get_current_kernel_params()`
- `append_params()` — from `_apply_kernel_param_batch()`
- `remove_params()` — from `_remove_kernel_params()`
- `_ensure_ready()` — from `_ensure_rpm_ostree_ready()`

**Key code patterns to extract**:
```python
# Get current params
returncode, stdout, stderr = run_command("rpm-ostree kargs", check=False, timeout=30)

# Append params
cmd = f"rpm-ostree kargs {append_args}"

# Remove params
cmd = f"rpm-ostree kargs {delete_args}"

# Ensure ready
returncode, stdout, stderr = run_command("rpm-ostree status --json", check=False, timeout=10)
```

**Verify**: Class implements all abstract methods from KernelParamManager.

---

## UoW 2.5.2: Create RpmOstreePackageManager class

**Goal**: Extract package install logic from existing BaseOptimizer.

**Add to**: `platforms/immutable/rpm_ostree.py`

**Source**: Extract from `bazzite-optimizer.py` method `BaseOptimizer.install_package()`

**Key code patterns to extract**:
```python
# Install
returncode, _, _ = run_command(f"rpm-ostree install {package_name}", check=False, timeout=timeout)

# Check installed
returncode, _, _ = run_command(f"rpm -q {package_name}", check=False)
```

**Verify**: Class implements all abstract methods from PackageManager.

---

## Step Exit Criteria

- [ ] `platforms/immutable/rpm_ostree.py` exists
- [ ] RpmOstreeKernelParams implements KernelParamManager
- [ ] RpmOstreePackageManager implements PackageManager
- [ ] Code extracted from bazzite-optimizer.py without modification
