# Phase 5: Cleanup, Regression Protection, and Handoff

**Bug**: Hardware Abstraction Failures (CPU/Memory/Network)
**Team**: TEAM_015
**Status**: Ready for execution

## Cleanup Tasks

### Step 1: Remove Dead Code

**Tasks**:
1. Remove commented-out hard-coded values (after verification)
2. Remove any temporary debug logging added during implementation
3. Remove breadcrumbs marked as CONFIRMED or RULED_OUT

### Step 2: Update Documentation

**Tasks**:
1. Update `README.md` to document hardware detection capabilities
2. Update `CHANGELOG.md` with:
   - "Fixed CPU optimizer applying i9-10850K settings to all CPUs"
   - "Fixed memory optimizer assuming 64GB RAM"
   - "Fixed network optimizer applying I225-V fixes to all NICs"
3. Update any hardware requirements documentation

### Step 3: Code Style Consistency

**Tasks**:
1. Run `black .` for formatting
2. Run `isort .` for import sorting
3. Run `flake8` for linting
4. Ensure new code follows existing patterns

---

## Regression Protection

### New Tests to Add

#### Test: CPU Detection
```python
# tests/test_cpu_detection.py
def test_detect_cpu_capabilities_intel():
    """Test CPU detection returns valid capabilities for Intel."""
    caps = detect_cpu_capabilities()
    assert caps.vendor in ("intel", "amd", "other")
    assert caps.core_count > 0

def test_cpu_undervolt_safety():
    """Test undervolt is skipped for unsupported CPUs."""
    caps = CPUCapabilities(vendor="amd", supports_undervolt=False, ...)
    # Verify optimizer skips undervolt
```

#### Test: Memory Scaling
```python
# tests/test_memory_scaling.py
def test_zram_scales_with_ram():
    """Test ZRAM size scales correctly with RAM."""
    assert calculate_zram_size(16) == 4   # 16GB → 4GB ZRAM
    assert calculate_zram_size(32) == 8   # 32GB → 8GB ZRAM
    assert calculate_zram_size(64) == 16  # 64GB → 16GB ZRAM (max)
    assert calculate_zram_size(128) == 16 # 128GB → 16GB ZRAM (capped)
```

#### Test: NIC Detection
```python
# tests/test_nic_detection.py
def test_detect_nic_capabilities():
    """Test NIC detection returns valid capabilities."""
    caps = detect_nic_capabilities()
    if caps:
        assert caps.driver in ("igc", "e1000e", "r8169", "igb", ...)

def test_igc_options_only_for_igc():
    """Test I225-V options only written for igc driver."""
    # Mock NIC with r8169 driver
    # Verify igc config NOT written
```

### Existing Tests to Verify

- [ ] `tests/test_bazzite_optimizer_core_utils.py` - still passes
- [ ] `tests/unit/test_base_optimizer.py` - still passes
- [ ] Any integration tests

---

## Handoff Checklist

Before marking complete:

- [ ] All Phase 4 implementations done
- [ ] All new tests pass
- [ ] All existing tests pass
- [ ] `black . && isort . && flake8` passes
- [ ] Project builds cleanly
- [ ] CHANGELOG.md updated
- [ ] Team file updated with completion status
- [ ] No remaining TODOs in new code

## Handoff Notes

### For Future Teams

1. **Pattern to follow**: This fix follows the same pattern as TEAM_013's GPU abstraction. When adding new hardware-specific optimizations:
   - Add detection to `platforms/detection.py`
   - Add capability dataclass
   - Add lazy property to optimizer class
   - Use detected values, not hard-coded

2. **Testing hardware detection**: Detection functions should handle missing hardware gracefully (return None or safe defaults).

3. **Safety philosophy**: When in doubt, skip optimization rather than apply potentially wrong values. No optimization is better than wrong optimization.

### Known Limitations

- CPU family detection is based on model name patterns, may need updates for future Intel generations
- NIC detection only covers common ethernet drivers, may miss exotic hardware
- Memory scaling formula may need tuning based on user feedback

---

## Final Verification Commands

```bash
# Run tests
pytest -q

# Check formatting
black --check .
isort --check .
flake8

# Manual verification
python3 bazzite-optimizer.py --validate
python3 bazzite-optimizer.py --list-kernel-profiles
```

---

## Completion Criteria

This bugfix is complete when:

1. Running the optimizer on any system shows **detected hardware** in logs, not hard-coded names
2. CPU undervolt is **skipped** on non-Intel or unknown CPUs
3. Memory settings **scale** with actual RAM
4. NIC-specific options are **conditional** on driver detection
5. All tests pass
6. Documentation updated
