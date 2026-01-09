# Phase 5, Step 3 — Release Preparation

**Parent**: [Phase 5](README.md)
**PR**: None (release tasks)
**Estimated Time**: 1 hour

---

## UoW 5.3.1: Update version numbers

**Goal**: Bump version to 5.1.0.

**Files to update**:
- `bazzite-optimizer.py`: `SCRIPT_VERSION = "5.1.0"`
- `VERSION`: Update content
- `pyproject.toml`: `version = "5.1.0"`

---

## UoW 5.3.2: Create git tag

**Goal**: Tag the release.

**Task**:
```bash
git add -A
git commit -m "feat: Multi-platform support (v5.1.0)

- Add platform abstraction layer
- Support traditional RPM and Debian-based systems
- Automatic platform detection
- Dynamic hardware display
- Conditional Bazzite features

Closes #1, #2, #3, #4, #5, #6, #7, #8, #9, #10, #11"

git tag -a v5.1.0 -m "Multi-Platform Support Release"
```

---

## UoW 5.3.3: Update team file with handoff notes

**Goal**: Document completion in team file.

**File**: `.teams/TEAM_001_refactor_generic_platform_support.md`

**Add**:
```markdown
## Handoff Notes

### Completed Work
- Platform detection module
- Abstract base classes
- GRUB kernel params
- DNF package manager
- APT package manager
- PlatformServices factory
- Migrated KernelOptimizer
- Migrated package installation
- Made Bazzite features conditional
- Updated UI for dynamic hardware
- Cleaned up dead code
- Updated documentation

### Tested Platforms
- Ultramarine Linux 43: ✅ All tests pass

### Future Work (Out of Scope)
- Split bazzite-optimizer.py into modules
- Add Arch Linux support
- Add systemd-boot support
- Intel GPU optimizer
- Hybrid GPU support
```

---

## Step Exit Criteria

- [ ] Version bumped to 5.1.0
- [ ] Git tag created
- [ ] Team file updated with handoff notes
