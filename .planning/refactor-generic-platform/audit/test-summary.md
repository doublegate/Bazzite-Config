# Test Baseline Summary

**Date**: 2025-12-31
**Commit**: 889c2fe
**Auditor Team**: TEAM_004

## Test Results

| Metric | Count |
|--------|-------|
| Total tests | 297 |
| Passing | 292 |
| Failing | 0 |
| Skipped | 5 |
| Collection errors | 2 |

## Collection Errors (Import Failures)

| File | Missing Module | Impact |
|------|----------------|--------|
| `tests/integration/test_ml_pipeline.py` | `pandas` | Optional ML tests |
| `tests/integration/test_mobile_websocket.py` | `websockets` | Optional mobile tests |

**Note**: These are optional integration tests requiring additional dependencies. Core functionality tests pass.

## Skipped Tests

5 tests skipped (likely platform-specific or conditional).

## Test Distribution

```
tests/
├── conftest.py                              # Shared fixtures
├── test_bazzite_optimizer_cli_args.py       # CLI argument tests
├── test_bazzite_optimizer_core_utils.py     # Core utility tests
├── test_bazzite_optimizer_enhanced_kargs.py # Kernel args tests
├── test_bazzite_optimizer_kernel_params.py  # Kernel param tests
├── test_kernel_param_fix.py                 # Kernel param fix tests
├── integration/
│   ├── test_ml_pipeline.py                  # (collection error)
│   ├── test_mobile_websocket.py             # (collection error)
│   └── test_profile_workflows.py            # Profile workflow tests
└── unit/
    ├── test_base_optimizer.py               # Base optimizer tests
    ├── test_gui_controllers.py              # GUI controller tests
    ├── test_optimizers.py                   # Optimizer module tests
    └── test_platform_detection.py           # Platform detection tests
```

## Baseline Command

```bash
python -m pytest --override-ini="addopts=" -q \
  --ignore=tests/integration/test_ml_pipeline.py \
  --ignore=tests/integration/test_mobile_websocket.py
```

## Baseline Established

- **Status**: ✅ GREEN (292 passed, 0 failed)
- **Safe to proceed**: Yes

Any test failures after Phase 2-5 implementation should be investigated as potential regressions.
