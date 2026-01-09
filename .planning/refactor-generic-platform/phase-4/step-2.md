# Phase 4, Step 2 — Module Exports Cleanup (PR #11 continued)

**Parent**: [Phase 4](README.md)
**Branch**: `feature/cleanup-dead-code`
**Dependency**: PR #10 merged
**Estimated Time**: 30 minutes

> **Note**: `ubuntu_debian.py` cleanup deferred to stretch goals (Debian support).

---

## UoW 4.2.1: Update platforms module __all__ exports

**Goal**: Ensure only public API is exported.

**File**: `platforms/__init__.py`

```python
__all__ = [
    "PlatformType",
    "PlatformInfo", 
    "detect_platform",
    "PlatformServices",
    "UnsupportedPlatformError",
    "PackageManager",
    "KernelParamManager",
]
```

---

## Step Exit Criteria

- [ ] Platforms module exports cleaned up
- [ ] All tests pass

> **Deferred**: `platform_support/ubuntu_debian.py` cleanup moved to stretch goals (requires Debian support)
