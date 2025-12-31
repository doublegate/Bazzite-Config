# Phase 1, Step 4 — Establish Test Baseline

**Parent**: [Phase 1](README.md)
**Estimated Time**: 30 minutes
**Output**: Record of all passing tests

---

## UoW 1.4.1: Run existing tests

**Goal**: Capture current test state as baseline.

**Task**:
```bash
# Note: --override-ini needed if pytest.ini has coverage options without pytest-cov installed
pytest -q --override-ini="addopts=" 2>&1 | tee .planning/refactor-generic-platform/audit/test-baseline.txt
```

**Expected Output**: Test summary saved to file.

---

## UoW 1.4.2: Document test count and status

**Goal**: Create a summary of test health.

**Task**: Parse the test output and document:

**Document in**: `.planning/refactor-generic-platform/audit/test-summary.md`

**Format**:
```markdown
# Test Baseline Summary

**Date**: YYYY-MM-DD
**Commit**: <git hash>

| Metric | Count |
|--------|-------|
| Total tests | X |
| Passing | X |
| Failing | X |
| Skipped | X |

## Failing Tests (if any)

- `test_name`: Reason
```

---

## Step Exit Criteria

- [ ] `audit/test-baseline.txt` created
- [ ] `audit/test-summary.md` created
- [ ] All test results documented
