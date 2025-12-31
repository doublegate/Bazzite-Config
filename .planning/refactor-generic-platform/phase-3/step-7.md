# Phase 3, Step 7 — Log Message & Branding Cleanup (PR #10 continued)

**Parent**: [Phase 3](README.md)
**Branch**: `feature/integrate-platform-services`
**Dependency**: PR #5 merged
**Estimated Time**: 1 hour
**Added by**: TEAM_005 (gap analysis)

---

## Context

The Phase 1 audit found log messages and branding that assume Bazzite. These should be made platform-aware or generic.

---

## UoW 3.7.1: Update "Bazzite immutable system" log messages

**Goal**: Make log messages platform-aware.

**File**: `bazzite-optimizer.py`

**Search and replace**:

| Line | Current | Change To |
|------|---------|-----------|
| 2336 | `"Installing {package_name} via rpm-ostree"` | `"Installing {package_name} via {self.package_manager.__class__.__name__}"` |
| 4916-4917 | `"Applying kernel parameters via rpm-ostree kargs"` | `"Applying kernel parameters via {type(self.kernel_params).__name__}"` |
| 5368 | `"Bazzite immutable system detected"` | `f"{self._platform_info.distro_name} detected"` |

---

## UoW 3.7.2: Update method name apply_bazzite_kernel_params()

**Goal**: Rename to platform-neutral name.

**File**: `bazzite-optimizer.py`
**Location**: `KernelOptimizer.apply_bazzite_kernel_params()` (line 4915)

**Change**:
```python
# Before
def apply_bazzite_kernel_params(self) -> bool:

# After  
def apply_kernel_params(self) -> bool:
```

**Update all callers** of this method.

---

## UoW 3.7.3: Update banner and version string

**Goal**: Make banner platform-aware (covered by step 3.4, verify here).

**File**: `bazzite-optimizer.py`
**Location**: `print_banner()` (around line 6854)

**Verify**: Banner should show:
- Generic title OR detected platform
- Dynamic hardware (from step 3.4)

---

## UoW 3.7.4: Path renaming decision

**Goal**: Document decision on path renaming.

**Current paths**:
- `/var/log/bazzite-optimizer/`
- `/etc/bazzite-optimizer/`
- `/var/backups/bazzite-optimizer/`
- Logger name: `bazzite-optimizer`

**Options**:
1. **Keep current**: Less disruption for existing Bazzite users
2. **Rename to generic**: `linux-gaming-optimizer` — requires migration script

**Recommendation**: Keep current paths for v1.x, add migration in v2.0.

**If keeping**: Add comment explaining the naming is historical.

---

## Step Exit Criteria

- [ ] No "Bazzite" assumptions in log messages (except when actually on Bazzite)
- [ ] Method names are platform-neutral
- [ ] Banner shows detected platform
- [ ] Path renaming decision documented
