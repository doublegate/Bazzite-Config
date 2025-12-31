# Phase 1 — Discovery and Safeguards

**Team**: TEAM_001
**PR**: None (planning phase only)
**Purpose**: Understand the codebase and establish test baselines

---

## Step 1.1: Audit rpm-ostree Dependencies

**Estimated Time**: 1 hour
**Output**: Documented list of all rpm-ostree call sites

### UoW 1.1.1: Find all rpm-ostree kargs calls

```bash
# Run this command
grep -n "rpm-ostree kargs" bazzite-optimizer.py
```

**Expected Output**: List of line numbers where `rpm-ostree kargs` is called
**Document in**: `.planning/refactor-generic-platform/audit/rpm-ostree-kargs.md`

### UoW 1.1.2: Find all rpm-ostree install calls

```bash
grep -n "rpm-ostree install" bazzite-optimizer.py
```

**Document in**: `.planning/refactor-generic-platform/audit/rpm-ostree-install.md`

### UoW 1.1.3: Find all rpm-ostree status calls

```bash
grep -n "rpm-ostree status" bazzite-optimizer.py
```

**Document in**: `.planning/refactor-generic-platform/audit/rpm-ostree-status.md`

---

## Step 1.2: Audit Bazzite-Specific Code

**Estimated Time**: 30 minutes
**Output**: List of Bazzite-only features

### UoW 1.2.1: Find ujust calls

```bash
grep -n "ujust" bazzite-optimizer.py
```

### UoW 1.2.2: Find Bazzite detection code

```bash
grep -n "bazzite" bazzite-optimizer.py -i
```

---

## Step 1.3: Audit Hard-coded Hardware References

**Estimated Time**: 30 minutes
**Output**: List of hardware references to make dynamic

### UoW 1.3.1: Find GPU model references

```bash
grep -n "RTX 5080\|RTX 4090\|i9-10850K\|Blackwell" bazzite-optimizer.py
```

### UoW 1.3.2: Document banner and UI strings

Look at `print_banner()` and `initialize_optimizers()` for hard-coded strings.

---

## Step 1.4: Establish Test Baseline

**Estimated Time**: 30 minutes
**Output**: Record of all passing tests

### UoW 1.4.1: Run existing tests

```bash
pytest -q 2>&1 | tee .planning/refactor-generic-platform/audit/test-baseline.txt
```

### UoW 1.4.2: Document test count and status

Record:
- Total tests
- Passing tests
- Failing tests (if any)
- Skipped tests

---

## Exit Criteria for Phase 1

- [ ] All rpm-ostree call sites documented
- [ ] All Bazzite-specific code documented
- [ ] All hard-coded hardware references documented
- [ ] Test baseline established
- [ ] Ready to begin Phase 2
