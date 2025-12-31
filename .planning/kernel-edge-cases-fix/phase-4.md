# Phase 4: Implementation and Tests

## Step 1: Add CPU Topology Detection

**File**: `platforms/detection.py`

### 1.1 Add CPUTopology dataclass
```python
@dataclass
class CPUTopology:
    total_cores: int
    total_threads: int
    is_hybrid: bool
    p_cores: List[int]
    e_cores: List[int]
    recommended_isolate: List[int]
```

### 1.2 Add detect_cpu_topology() function
- Parse `/sys/devices/system/cpu/cpu*/topology/`
- Check `/sys/devices/system/cpu/cpu*/cpufreq/cpuinfo_max_freq` for P vs E core detection
- Intel hybrid: E-cores have lower max freq than P-cores
- Fallback: Use last 25% of cores for isolation

### 1.3 Export from platforms/__init__.py

---

## Step 2: Update KernelOptimizer for CPU Topology

**File**: `bazzite-optimizer.py`

### 2.1 Import new detection
```python
from platforms.detection import detect_cpu_topology
```

### 2.2 Replace hardcoded isolcpus
```python
# Old:
if profile_settings.get("isolate_cores", False):
    isolcpus = "nohz_full=4-9 isolcpus=4-9 rcu_nocbs=4-9"

# New:
if profile_settings.get("isolate_cores", False):
    topology = detect_cpu_topology()
    if topology.recommended_isolate:
        cores = ",".join(map(str, topology.recommended_isolate))
        isolcpus = f"nohz_full={cores} isolcpus={cores} rcu_nocbs={cores}"
    else:
        self.logger.warning("Could not detect CPU topology, skipping core isolation")
        isolcpus = ""
```

---

## Step 3: Add eGPU Conditional Kernel Params

**File**: `bazzite-optimizer.py`

### 3.1 Import GPU detection
```python
from platforms.detection import get_primary_gpu
```

### 3.2 Add eGPU params conditionally
```python
# After building kernel_params list:
try:
    primary_gpu = get_primary_gpu()
    if primary_gpu and primary_gpu.is_egpu:
        self.logger.info("eGPU detected, adding Thunderbolt stability params")
        kernel_params.extend([
            "pcie_port_pm=off",
            "thunderbolt.force_power=1",
        ])
except Exception as e:
    self.logger.debug(f"Could not check for eGPU: {e}")
```

---

## Step 4: Add CLI Arguments

**File**: `bazzite-optimizer.py`

### 4.1 Add new arguments in main()
```python
parser.add_argument('--save-baseline', action='store_true',
                    help='Save current kernel params as baseline before optimization')
parser.add_argument('--kernel-profile', type=str, metavar='NAME',
                    help='Apply a saved kernel profile (use --list-kernel-profiles to see available)')
parser.add_argument('--list-kernel-profiles', action='store_true',
                    help='List available kernel profiles')
parser.add_argument('--kernel-diff', type=str, metavar='NAME',
                    help='Show difference between current params and a profile')
```

### 4.2 Add handler logic
```python
# After args parsing, before main optimization:
if args.save_baseline:
    if hasattr(self, 'kernel_params') and hasattr(self.kernel_params, 'save_baseline'):
        if self.kernel_params.save_baseline():
            print_colored("Baseline saved successfully", Colors.OKGREEN)
        else:
            print_colored("Failed to save baseline", Colors.FAIL)
    return 0

if args.list_kernel_profiles:
    if hasattr(self, 'kernel_params') and hasattr(self.kernel_params, 'list_profiles'):
        profiles = self.kernel_params.list_profiles()
        if profiles:
            print("Available kernel profiles:")
            for p in profiles:
                print(f"  - {p}")
        else:
            print("No kernel profiles saved yet. Run --save-baseline first.")
    return 0

if args.kernel_profile:
    if hasattr(self, 'kernel_params') and hasattr(self.kernel_params, 'apply_profile'):
        if self.kernel_params.apply_profile(args.kernel_profile):
            print_colored(f"Applied kernel profile '{args.kernel_profile}'. Reboot required.", Colors.OKGREEN)
        else:
            print_colored(f"Failed to apply profile '{args.kernel_profile}'", Colors.FAIL)
    return 0

if args.kernel_diff:
    if hasattr(self, 'kernel_params') and hasattr(self.kernel_params, 'diff_profile'):
        diff = self.kernel_params.diff_profile(args.kernel_diff)
        if "error" in diff:
            print_colored(diff["error"], Colors.FAIL)
        else:
            print(f"Diff vs '{args.kernel_diff}':")
            if diff["add"]:
                print("  Would add:")
                for p in diff["add"]:
                    print(f"    + {p}")
            if diff["remove"]:
                print("  Would remove:")
                for p in diff["remove"]:
                    print(f"    - {p}")
            if not diff["add"] and not diff["remove"]:
                print("  No differences")
    return 0
```

---

## Step 5: Add Unit Tests

### 5.1 Test CPU topology detection
**File**: `tests/unit/test_platform_detection.py`

```python
def test_detect_cpu_topology_returns_dataclass():
    topology = detect_cpu_topology()
    assert topology.total_cores > 0
    assert topology.total_threads >= topology.total_cores

def test_detect_cpu_topology_recommended_isolate():
    topology = detect_cpu_topology()
    # Should recommend some cores for isolation
    assert isinstance(topology.recommended_isolate, list)
```

### 5.2 Test CLI arguments
**File**: `tests/test_bazzite_optimizer_cli_args.py`

```python
def test_save_baseline_arg():
    # Test that --save-baseline is recognized

def test_kernel_profile_arg():
    # Test that --kernel-profile NAME is recognized

def test_list_kernel_profiles_arg():
    # Test that --list-kernel-profiles is recognized
```

---

## Step 6: Integration Test on User's System

1. Run `sudo ./bazzite-optimizer.py --save-baseline`
2. Check `/var/lib/bazzite-optimizer/kernel-profiles/baseline.conf`
3. Run `./bazzite-optimizer.py --list-kernel-profiles`
4. Run optimization with `--profile balanced`
5. Verify E-cores isolated (not P-cores)
6. Verify eGPU params in GRUB config
7. Run `./bazzite-optimizer.py --kernel-diff baseline`
8. Run `sudo ./bazzite-optimizer.py --kernel-profile baseline` to restore

---

## Exit Criteria
- [ ] CPU topology detection implemented
- [ ] KernelOptimizer uses topology
- [ ] eGPU params conditional added
- [ ] CLI arguments added
- [ ] Unit tests pass
- [ ] Integration test on user's system passes
