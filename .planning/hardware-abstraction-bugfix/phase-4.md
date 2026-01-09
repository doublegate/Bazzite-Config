# Phase 4: Implementation

**Bug**: Hardware Abstraction Failures (CPU/Memory/Network)
**Team**: TEAM_015
**Status**: Ready for execution

## Implementation Order

1. Memory (simplest, lowest risk)
2. Network (medium complexity)
3. CPU (most complex, highest risk)

---

## Step 1: Memory Abstraction

**File**: `phase-4-step-1.md`
**Estimated**: 1-2 UoW

### UoW 1.1: Update MemoryOptimizer to Use Detected RAM

**Goal**: Replace hard-coded "64GB" with actual RAM from system_info

**Tasks**:
1. Read `platforms/detection.py` to understand how system_info is populated
2. Update `MemoryOptimizer.configure_zram()` to calculate ZRAM size based on actual RAM
3. Update `SYSCTL_CONFIG` and `ZRAM_CONFIG` to use dynamic values
4. Update log messages to show actual RAM size

**Code Changes**:
```python
# In MemoryOptimizer class
def configure_zram(self) -> bool:
    ram_gb = self.system_info.get("ram_gb", 16)  # Default 16GB if unknown
    zram_size_gb = min(ram_gb // 4, 16)  # 1/4 of RAM, max 16GB
    self.logger.info(f"Configuring ZRAM for {ram_gb}GB system (ZRAM: {zram_size_gb}GB)...")
```

**Validation**:
- Run optimizer on system with known RAM
- Verify log shows correct RAM size
- Verify ZRAM config has scaled values

---

## Step 2: Network Abstraction

**File**: `phase-4-step-2.md`
**Estimated**: 2-3 UoW

### UoW 2.1: Add NIC Detection to platforms/detection.py

**Goal**: Detect NIC driver and capabilities

**Tasks**:
1. Add `NICCapabilities` dataclass
2. Implement `detect_nic_capabilities()` function
3. Export from `platforms/__init__.py`

**Detection Logic**:
```python
def detect_nic_capabilities() -> Optional[NICCapabilities]:
    # Find primary ethernet interface
    for iface in Path("/sys/class/net").iterdir():
        if iface.name.startswith(("eth", "enp", "eno")):
            driver_link = iface / "device" / "driver"
            if driver_link.exists():
                driver = driver_link.resolve().name
                return NICCapabilities(
                    driver=driver,
                    is_intel=driver in ("igc", "e1000e", "igb"),
                    is_i225_family=driver == "igc",
                    supports_eee_disable=driver == "igc"
                )
    return None
```

### UoW 2.2: Update NetworkOptimizer to Use Detection

**Goal**: Only apply I225-V fixes if igc driver detected

**Tasks**:
1. Add `nic_caps` property to NetworkOptimizer
2. Conditionally write igc module config
3. Update log messages to show detected NIC
4. Keep generic optimizations for all NICs

**Code Changes**:
```python
# In NetworkOptimizer class
@property
def nic_caps(self):
    if self._nic_caps is None:
        from platforms.detection import detect_nic_capabilities
        self._nic_caps = detect_nic_capabilities()
    return self._nic_caps

def apply_optimizations(self) -> bool:
    if self.nic_caps and self.nic_caps.is_i225_family:
        self.logger.info(f"Applying Intel I225 optimizations (driver: {self.nic_caps.driver})...")
        # Write igc-specific config
    else:
        self.logger.info("Applying generic network optimizations...")
        # Skip igc-specific config
```

**Validation**:
- Test on I225-V system: full optimizations applied
- Test on non-Intel NIC: only generic optimizations
- Verify no errors on systems without ethernet

---

## Step 3: CPU Abstraction

**File**: `phase-4-step-3.md`
**Estimated**: 3-4 UoW

### UoW 3.1: Add CPU Detection to platforms/detection.py

**Goal**: Detect CPU vendor, model, and undervolt safety

**Tasks**:
1. Add `CPUCapabilities` dataclass
2. Implement `detect_cpu_capabilities()` function
3. Add Intel CPU family detection (Comet Lake, Alder Lake, etc.)
4. Define safe undervolt values per family

**Detection Logic**:
```python
INTEL_FAMILIES = {
    "comet_lake": {"pattern": r"10[0-9]{2}", "safe_undervolt": 80},
    "alder_lake": {"pattern": r"12[0-9]{2}P?", "safe_undervolt": 50},
    "raptor_lake": {"pattern": r"13[0-9]{2}", "safe_undervolt": 50},
}

def detect_cpu_capabilities() -> CPUCapabilities:
    # Parse /proc/cpuinfo
    # Detect vendor and model
    # Match against known families
    # Return capabilities with safe undervolt value
```

### UoW 3.2: Update CPUOptimizer to Use Detection

**Goal**: Skip undervolt for unsupported CPUs, use safe values for supported

**Tasks**:
1. Add `cpu_caps` property to CPUOptimizer
2. Skip undervolt if `not cpu_caps.supports_undervolt`
3. Use `cpu_caps.safe_undervolt_mv` instead of hard-coded values
4. Update log messages to show detected CPU

### UoW 3.3: Update Embedded CPU Scripts

**Goal**: Make CPU_OPTIMIZATION_SCRIPT use detected values

**Tasks**:
1. Parameterize undervolt values in script
2. Pass detected values when writing script
3. Update script output messages

**Code Changes**:
```python
# In CPUOptimizer.apply_optimizations()
if self.cpu_caps.supports_undervolt:
    script = CPU_OPTIMIZATION_SCRIPT.replace(
        "${UNDERVOLT_MV}", str(self.cpu_caps.safe_undervolt_mv)
    )
    self.logger.info(f"Applying {self.cpu_caps.model} optimizations with {self.cpu_caps.safe_undervolt_mv}mV undervolt...")
else:
    self.logger.info(f"Skipping undervolt for {self.cpu_caps.model} (not supported/unknown)")
```

**Validation**:
- Test on Intel CPU: should detect and apply appropriate undervolt
- Test on AMD CPU: should skip undervolt entirely
- Test on unknown CPU: should use conservative defaults

---

## Validation Checklist

After all implementations:

- [ ] Memory: ZRAM scales with actual RAM
- [ ] Network: igc options only applied to igc driver
- [ ] CPU: Undervolt skipped for unsupported CPUs
- [ ] Logs show detected hardware, not hard-coded names
- [ ] No regressions on known hardware (if available for testing)

---

## Next Phase

Proceed to **Phase 5: Cleanup and Handoff** after implementation is complete.
