# Phase 3: Fix Design and Validation Plan

## Root Cause Summary

| Bug | Root Cause | Location |
|-----|------------|----------|
| 1 | Hardcoded `isolcpus=4-9` ignores hybrid CPU topology | `bazzite-optimizer.py:~5195` |
| 2 | No eGPU-specific kernel params | `bazzite-optimizer.py` kernel_params list |
| 3 | No CLI for kernel profile management | `bazzite-optimizer.py` main() |

---

## Fix Strategy

### Fix 1: Alder Lake Hybrid CPU Detection

**Approach**: Add CPU topology detection to `platforms/detection.py`

```python
@dataclass
class CPUTopology:
    total_cores: int
    total_threads: int
    is_hybrid: bool              # True for Alder Lake, Raptor Lake, etc.
    p_cores: List[int]           # Performance core IDs
    e_cores: List[int]           # Efficiency core IDs
    recommended_isolate: List[int]  # Cores safe to isolate

def detect_cpu_topology() -> CPUTopology:
    """Detect CPU topology including hybrid P/E cores."""
    # Parse /sys/devices/system/cpu/cpu*/topology/
    # Check for intel_atom vs intel_core type
```

**Usage in optimizer**:
```python
topology = detect_cpu_topology()
if topology.is_hybrid and topology.e_cores:
    isolcpus = ",".join(map(str, topology.e_cores))
else:
    # Fallback to last N cores
    isolcpus = f"{topology.total_threads - 6}-{topology.total_threads - 1}"
```

### Fix 2: eGPU Thunderbolt Kernel Params

**Approach**: Conditional params based on eGPU detection

```python
# In KernelOptimizer.apply_bazzite_kernel_params()
from platforms.detection import detect_gpus, get_primary_gpu

primary_gpu = get_primary_gpu()
if primary_gpu and primary_gpu.is_egpu:
    kernel_params.extend([
        "pcie_port_pm=off",
        "thunderbolt.force_power=1",
    ])
```

### Fix 3: CLI for Kernel Profile Management

**Approach**: Add new CLI arguments

```python
# New arguments
parser.add_argument('--save-baseline', action='store_true',
                    help='Save current kernel params as baseline')
parser.add_argument('--kernel-profile', type=str, metavar='NAME',
                    help='Apply kernel profile (baseline, balanced, competitive)')
parser.add_argument('--list-kernel-profiles', action='store_true',
                    help='List available kernel profiles')
parser.add_argument('--kernel-diff', type=str, metavar='NAME',
                    help='Show diff between current and profile')
```

---

## Reversal Strategy

| Fix | How to Revert |
|-----|---------------|
| 1 | Remove `detect_cpu_topology()`, revert to hardcoded values |
| 2 | Remove eGPU conditional, revert kernel_params list |
| 3 | Remove CLI args, methods remain but unused |

**Signals to revert**:
- CPU detection returns wrong topology
- eGPU params cause boot issues
- CLI commands break existing workflows

---

## Test Strategy

### Unit Tests

| Test | File | Purpose |
|------|------|---------|
| `test_detect_cpu_topology_hybrid` | `tests/unit/test_platform_detection.py` | Verify hybrid detection |
| `test_detect_cpu_topology_standard` | Same | Verify non-hybrid fallback |
| `test_egpu_kernel_params` | `tests/unit/test_kernel_optimizer.py` | Verify eGPU params added |
| `test_kernel_profile_cli` | `tests/test_bazzite_optimizer_cli_args.py` | Verify new CLI args |

### Integration Tests

1. Run `--save-baseline` on user's system
2. Run optimization with correct E-core isolation
3. Run `--kernel-profile baseline` to restore
4. Verify eGPU params in `/etc/default/grub`

---

## Impact Analysis

| Area | Impact | Risk |
|------|--------|------|
| CPU detection | New function, no breaking changes | Low |
| eGPU params | Additive to kernel_params | Low |
| CLI args | Additive, no breaking changes | Low |
| Existing rpm-ostree systems | No impact (GRUB only for profiles) | None |

---

## Implementation Order

1. **Step 1**: Add `detect_cpu_topology()` to `platforms/detection.py`
2. **Step 2**: Update `KernelOptimizer` to use topology detection
3. **Step 3**: Add eGPU conditional kernel params
4. **Step 4**: Add CLI arguments and wiring
5. **Step 5**: Add unit tests
6. **Step 6**: Test on user's system

---

## Exit Criteria
- [ ] Fix design documented
- [ ] Test strategy defined
- [ ] Implementation order established
- [ ] Ready for Phase 4
