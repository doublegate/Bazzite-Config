# Phase 3, Step 4 — Dynamic Hardware UI & Cleanup (PR #9)

**Parent**: [Phase 3](README.md)
**Branch**: `feature/dynamic-hardware-ui`
**Dependency**: None (independent)
**Estimated Time**: 2 hours

---

## UoW 3.4.1: Update print_banner() to use dynamic hardware

**Goal**: Replace hard-coded hardware strings with detected values.

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
    if len(cpu_name) > 25:
        cpu_name = cpu_name[:22] + "..."
    
    ram_gb = self.system_info.get('ram_gb', '?')
    
    print_colored(f"  Detected: {gpu_name} | {cpu_name} | {ram_gb}GB RAM", Colors.OKCYAN)
```

---

## UoW 3.4.2: Update initialize_optimizers() names

**Goal**: Make optimizer names generic or dynamic.

**File**: `bazzite-optimizer.py`
**Location**: `BazziteGamingOptimizer.initialize_optimizers()` (around line 6969)

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

## UoW 3.4.3: Global hardware string cleanup

**Goal**: Remove all remaining hard-coded RTX 5080, i9-10850K, and 64GB references.

**Task**: Search and replace the following in `bazzite-optimizer.py`:
1. Class docstrings (CPUOptimizer, NetworkOptimizer)
2. Embedded scripts (NVIDIA_OPTIMIZATION_SCRIPT, CPU_OPTIMIZATION_SCRIPT)
3. Log messages in `check_resizable_bar()`
4. Comments in `UNDERVOLT_CONFIG` and `ZRAM_CONFIG`

**Pattern**: Replace specific models with generic terms or dynamic placeholders.

---

## UoW 3.4.4: Test banner output

**Goal**: Verify hardware is correctly displayed.

**Test command**:
```bash
sudo ./bazzite-optimizer.py --validate 2>&1 | head -10
```

---

## Step Exit Criteria

- [ ] Banner shows dynamic hardware
- [ ] No hard-coded "RTX 5080" or "i9-10850K" in banner or logs
- [ ] Optimizer names are generic
- [ ] Global search for hardware models returns 0 results
