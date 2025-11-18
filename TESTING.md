# Testing Guide - Bazzite Gaming Optimization Suite

Comprehensive testing guide for developers and contributors.

## Table of Contents

- [Overview](#overview)
- [Testing Infrastructure](#testing-infrastructure)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Writing Tests](#writing-tests)
- [CI/CD Pipeline](#cicd-pipeline)
- [Coverage Reports](#coverage-reports)

## Overview

The Bazzite Gaming Optimization Suite has a comprehensive test suite covering:

- **Unit Tests**: 150+ test cases for individual components
- **Integration Tests**: 50+ test cases for workflow validation
- **GUI Tests**: 40+ test cases for GTK4 interface
- **CI/CD**: Automated testing via GitHub Actions
- **Code Quality**: Linting, security scanning, and style checking

**Test Coverage Goal**: >80% code coverage

## Testing Infrastructure

### Dependencies

Install testing dependencies:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Core testing tools
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.1
pytest-timeout>=2.1.0
pytest-xdist>=3.3.1
```

### Directory Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests
│   ├── test_base_optimizer.py
│   ├── test_optimizers.py
│   ├── test_gui_models.py
│   └── test_gui_controllers.py
├── integration/             # Integration tests
│   └── test_profile_workflows.py
├── gui/                     # GUI-specific tests
└── fixtures/                # Test data and fixtures
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_optimizers.py

# Run specific test class
pytest tests/unit/test_optimizers.py::TestNvidiaOptimizer

# Run specific test function
pytest tests/unit/test_optimizers.py::TestNvidiaOptimizer::test_detect_nvidia_gpu
```

### Running by Category

Tests are organized with pytest markers:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only GUI tests
pytest -m gui

# Run slow tests
pytest -m slow

# Exclude slow tests
pytest -m "not slow"

# Run tests not requiring hardware
pytest -m "not requires_hardware"
```

### Parallel Execution

```bash
# Run tests in parallel (4 workers)
pytest -n 4

# Auto-detect CPU count
pytest -n auto
```

### Coverage Reports

```bash
# Run tests with coverage
pytest --cov=. --cov-report=html

# View HTML coverage report
open htmlcov/index.html

# Generate terminal coverage report
pytest --cov=. --cov-report=term-missing

# Generate XML coverage for CI
pytest --cov=. --cov-report=xml
```

## Test Categories

### Unit Tests (tests/unit/)

Test individual components in isolation using mocks.

**BaseOptimizer Tests** (`test_base_optimizer.py`):
- Validation methods
- Package management
- File operations
- Utility functions

**Optimizer Tests** (`test_optimizers.py`):
- NvidiaOptimizer
- CPUOptimizer
- MemoryOptimizer
- NetworkOptimizer
- AudioOptimizer
- GamingToolsOptimizer
- KernelOptimizer
- SystemdServiceOptimizer

**GUI Model Tests** (`test_gui_models.py`):
- SystemState and Observer pattern
- ProfileModel
- MetricsModel
- Data serialization

**GUI Controller Tests** (`test_gui_controllers.py`):
- OptimizerBackend
- MonitorController
- QuickFixBackend

### Integration Tests (tests/integration/)

Test complete workflows and component interactions.

**Profile Workflows** (`test_profile_workflows.py`):
- Complete profile application (Competitive, Balanced, Streaming, Creative)
- Profile switching with rollback
- Gaming mode enable/disable
- System health checks
- Quick fix executions
- Backup and restore workflows
- RPM-ostree integration
- NVIDIA optimization workflows
- Audio system integration
- Benchmarking workflows

### GUI Tests (tests/gui/)

Test GTK4 interface components (requires display server).

**Note**: GUI tests can run with mocked GTK when no display is available:

```bash
# Run GUI tests with GTK mocking
pytest tests/unit/test_gui_*.py -m gui
```

### Hardware-Specific Tests

Tests requiring specific hardware are marked and skipped automatically:

```bash
# Tests requiring NVIDIA GPU
pytest -m requires_nvidia

# Tests requiring AMD GPU
pytest -m requires_amd

# Tests requiring Steam Deck
pytest -m requires_steamdeck

# Tests requiring root privileges
sudo pytest -m requires_root
```

## Writing Tests

### Test Structure

Follow this standard structure:

```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.unit  # Mark test category
class TestMyComponent:
    """Test MyComponent functionality"""

    def test_something_success(self, mock_subprocess):
        """Test successful operation"""
        # Arrange
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

        # Act
        result = my_function()

        # Assert
        assert result is True
        mock_subprocess.assert_called_once()

    def test_something_failure(self, mock_subprocess_failure):
        """Test failure handling"""
        # Test failure case
        pass
```

### Using Fixtures

Common fixtures are defined in `conftest.py`:

```python
def test_with_temp_dir(temp_dir):
    """Use temporary directory fixture"""
    test_file = temp_dir / "test.txt"
    test_file.write_text("Hello")
    assert test_file.exists()

def test_with_mock_gpu(mock_nvidia_gpu):
    """Use mock GPU hardware info"""
    assert mock_nvidia_gpu['vendor'] == 'NVIDIA'
    assert mock_nvidia_gpu['model'] == 'RTX 5080'
```

### Mocking subprocess Calls

```python
def test_subprocess_mock(mock_subprocess):
    """Test with mocked subprocess"""
    mock_subprocess.return_value = Mock(
        returncode=0,
        stdout="Success",
        stderr=""
    )

    result = subprocess.run(['echo', 'test'], capture_output=True)
    assert result.returncode == 0
```

### Testing Async Operations

```python
@pytest.mark.asyncio
async def test_async_operation():
    """Test asynchronous operation"""
    result = await async_function()
    assert result is not None
```

## CI/CD Pipeline

### GitHub Actions Workflow

Located at `.github/workflows/ci-testing.yml`

**Jobs**:
1. **Lint**: Code quality and style checking
   - Black (code formatting)
   - isort (import sorting)
   - Flake8 (style guide)
   - Pylint (code analysis)
   - Bandit (security linting)
   - Safety (dependency security)

2. **Test**: Unit and integration tests
   - Python 3.8, 3.9, 3.10, 3.11, 3.12
   - Unit tests
   - Integration tests
   - Coverage reporting to Codecov

3. **Test-GUI**: GUI tests with mocked GTK
   - Python 3.11
   - GUI unit tests
   - Coverage for GUI modules

4. **Test-Slow**: Extended test suite
   - Runs on schedule or with `[run-slow-tests]` in commit message
   - 30-minute timeout
   - Comprehensive slow tests

5. **Security-Scan**: Security vulnerability scanning
   - Trivy scanner
   - SARIF report upload to GitHub Security

6. **Build-Test**: Installation and build verification
   - User installation test
   - File structure validation

7. **Docs-Build**: Documentation validation
   - Markdown documentation checks
   - Link validation

### Triggering CI/CD

```bash
# Push to trigger CI
git push origin your-branch

# Include slow tests
git commit -m "feat: new feature [run-slow-tests]"
git push
```

### CI Status Badges

Add to README.md:

```markdown
![CI Tests](https://github.com/doublegate/Bazzite-Config/actions/workflows/ci-testing.yml/badge.svg)
![Code Coverage](https://codecov.io/gh/doublegate/Bazzite-Config/branch/main/graph/badge.svg)
```

## Coverage Reports

### Generating Coverage

```bash
# HTML report (most detailed)
pytest --cov=. --cov-report=html
open htmlcov/index.html

# Terminal report
pytest --cov=. --cov-report=term-missing

# XML report (for CI)
pytest --cov=. --cov-report=xml

# All formats
pytest --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml
```

### Coverage Configuration

Defined in `.coveragerc`:

```ini
[run]
source = .
omit =
    tests/*
    ref_scripts/*
    ref_docs/*

[report]
precision = 2
show_missing = True
```

### Coverage Goals

- **Overall**: >80%
- **Core optimizers**: >90%
- **GUI controllers**: >85%
- **Models**: >95%

## Best Practices

### DO:
✅ Write tests for all new features
✅ Use descriptive test names
✅ Mock external dependencies
✅ Test both success and failure cases
✅ Use fixtures for common setup
✅ Mark tests with appropriate categories
✅ Keep tests fast (use `@pytest.mark.slow` for slow tests)
✅ Document complex test scenarios
✅ Maintain >80% code coverage

### DON'T:
❌ Test external libraries
❌ Make tests dependent on each other
❌ Use sleep() for timing (use mocks instead)
❌ Hardcode paths (use fixtures)
❌ Skip writing tests for "simple" code
❌ Commit failing tests
❌ Test implementation details (test behavior)

## Troubleshooting

### Common Issues

**Import Errors**:
```bash
# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

**GTK Import Errors** (expected without display):
```bash
# Run GUI tests with mocking
pytest tests/unit/test_gui_*.py -m gui
```

**Permission Errors**:
```bash
# Run tests requiring root with sudo
sudo pytest -m requires_root
```

**Slow Tests**:
```bash
# Run only fast tests
pytest -m "not slow"

# Use parallel execution
pytest -n auto
```

## Contributing

When submitting PRs:

1. Ensure all tests pass: `pytest`
2. Maintain or improve coverage
3. Add tests for new features
4. Follow existing test patterns
5. Update this guide if adding new test types

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-mock Documentation](https://pytest-mock.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
