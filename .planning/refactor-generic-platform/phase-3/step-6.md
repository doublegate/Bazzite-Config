# Phase 3, Step 6 — Embedded Shell Script Migration (PR #10 continued)

**Parent**: [Phase 3](README.md)
**Branch**: `feature/integrate-platform-services`
**Dependency**: PRs #6, #7 merged
**Estimated Time**: 1.5 hours
**Added by**: TEAM_005 (gap analysis)

---

## Context

The Phase 1 audit found rpm-ostree calls inside embedded shell scripts that bypass the Python abstraction layer entirely. These scripts are written to disk and executed as bash, so they need their own platform detection.

**Affected scripts**:
- `CPU_OPTIMIZATION_SCRIPT` (line 473-700+)
- `NVIDIA_OPTIMIZATION_SCRIPT` (line 300-470)

---

## UoW 3.6.1: Add platform detection to embedded shell scripts

**Goal**: Make embedded scripts detect platform and use appropriate package manager.

**File**: `bazzite-optimizer.py`
**Location**: `CPU_OPTIMIZATION_SCRIPT` (around line 479-482)

**Current**:
```bash
# Install cpupower if not present
if ! command -v cpupower &> /dev/null; then
    rpm-ostree install kernel-tools 2>/dev/null || dnf install -y kernel-tools 2>/dev/null || true
fi
```

**Change to**:
```bash
# Install cpupower if not present (platform-aware)
if ! command -v cpupower &> /dev/null; then
    if command -v rpm-ostree &> /dev/null && rpm-ostree status &>/dev/null; then
        rpm-ostree install kernel-tools 2>/dev/null || true
    else
        dnf install -y kernel-tools 2>/dev/null || apt-get install -y linux-tools-common 2>/dev/null || true
    fi
fi
```

**Note**: The fallback chain already exists but order should prefer detected platform.

---

## UoW 3.6.2: Update log paths in embedded scripts

**Goal**: Make log paths consistent with platform abstraction.

**File**: `bazzite-optimizer.py`
**Location**: Multiple locations in embedded scripts

**Search for**:
```bash
/var/log/bazzite-optimizer/
```

**Decision needed**: Keep current path or rename to `/var/log/linux-gaming-optimizer/`?

**If keeping**: No change needed.
**If renaming**: Update all embedded script references.

---

## UoW 3.6.3: Remove hardcoded GPU/CPU names from embedded scripts

**Goal**: Make embedded scripts use detected hardware.

**File**: `bazzite-optimizer.py`
**Locations**:
- Line 469: `echo "RTX 5080 Blackwell optimizations v4 applied..."`
- Line 474: `# i9-10850K Gaming Optimization v4`

**Change to**:
```bash
echo "GPU optimizations applied with safety checks!"
```

```bash
# CPU Gaming Optimization v4 - With Stepped Undervolting
```

---

## UoW 3.6.4: Verify embedded scripts work on traditional systems

**Goal**: Test that embedded scripts don't fail on non-rpm-ostree systems.

**Test command**:
```bash
# Extract and test CPU script
grep -A 200 'CPU_OPTIMIZATION_SCRIPT = """' bazzite-optimizer.py | \
    head -100 | tail -98 > /tmp/test-cpu-script.sh
bash -n /tmp/test-cpu-script.sh  # Syntax check only
```

---

## Step Exit Criteria

- [ ] Embedded scripts detect platform before package install
- [ ] Log paths decision made and implemented
- [ ] Hardcoded hardware names removed from scripts
- [ ] Scripts pass syntax check
- [ ] No rpm-ostree errors on Ultramarine
