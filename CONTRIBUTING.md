# Contributing to Bazzite Gaming Optimization Suite

Thank you for your interest in contributing to the Bazzite Gaming Optimization Suite! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

Before creating an issue, please:

1. **Search existing issues** to avoid duplicates
2. **Test on Bazzite Linux** to ensure the issue is reproducible
3. **Gather system information** using the health check: `./gaming-manager-suite.py --health`

When reporting issues, include:
- Bazzite version and kernel information
- Hardware configuration (CPU, GPU, RAM)
- Steps to reproduce the issue
- Expected vs. actual behavior
- Relevant log files from `/var/log/gaming-benchmark/` or `/var/log/gaming-metrics/`

### Suggesting Features

Feature requests should include:
- **Clear use case** - Why is this feature needed?
- **Target hardware** - Which configurations would benefit?
- **Implementation considerations** - Any technical constraints?
- **Backwards compatibility** - Impact on existing functionality?

## 🛠️ Development Setup

### Prerequisites

- **Bazzite Linux** (latest stable release)
- **Python 3.8+** with development tools
- **Git** for version control
- **Text editor** with Python syntax highlighting

### Environment Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/Bazzite-Config.git
   cd Bazzite-Config
   ```

2. **Install development dependencies:**
   ```bash
   sudo dnf install python3-devel python3-pip stress-ng sysbench
   pip3 install --user pylint black isort mypy
   ```

3. **Make scripts executable:**
   ```bash
   chmod +x gaming-manager-suite.py gaming-monitor-suite.py gaming-maintenance-suite.sh
   ```

4. **Test the setup:**
   ```bash
   ./gaming-manager-suite.py --status
   ./gaming-monitor-suite.py --mode simple --interval 1
   ```

## 📝 Code Guidelines

### Python Code Style

- **Follow PEP 8** with 88-character line limit (Black formatter)
- **Use type hints** for all function parameters and returns
- **Include docstrings** for all classes and public methods
- **Handle exceptions** gracefully with specific error messages

Example:
```python
def get_cpu_metrics(self) -> Dict[str, float]:
    """
    Collect current CPU performance metrics.
    
    Returns:
        Dict containing CPU usage, frequency, and temperature data
        
    Raises:
        SystemError: If CPU metrics cannot be collected
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        raise SystemError(f"Failed to collect CPU metrics: {e}")
```

### Shell Script Style

- **Use bash shebang**: `#!/bin/bash`
- **Enable strict mode**: `set -euo pipefail`
- **Quote variables**: `"$variable"` instead of `$variable`
- **Use functions** for repeated code blocks
- **Include error handling** with meaningful messages

### Color and Formatting

Use the consistent Colors class across all components:
```python
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
```

## 🧪 Testing

### Manual Testing

Before submitting changes:

1. **Test all command-line options** for affected components
2. **Verify on different hardware** when possible (AMD/Intel CPUs, different GPUs)
3. **Check error conditions** - invalid inputs, missing dependencies
4. **Test privilege escalation** - ensure sudo prompts work correctly

### Test Scenarios

- **Gaming Manager**: Enable/disable gaming mode, apply profiles, run health checks
- **Gaming Monitor**: All display modes (dashboard/simple/export) with various intervals
- **Gaming Maintenance**: Benchmark routines with different hardware configurations

### System Integration Testing

- Test with different Bazzite versions
- Verify ujust command integration
- Check System76-scheduler interaction
- Validate file permissions and directory creation

## 📦 Submitting Changes

### Pull Request Process

1. **Create a feature branch** from main:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code guidelines

3. **Test thoroughly** on Bazzite Linux

4. **Update documentation** if needed:
   - Update CHANGELOG.md with your changes
   - Modify README.md if adding new features
   - Update CLAUDE.md for development changes

5. **Commit with descriptive messages**:
   ```bash
   git commit -m "feat: add GPU temperature monitoring to metrics collector
   
   - Implement NVIDIA GPU temperature reading via nvidia-ml-py
   - Add temperature warnings for thermal throttling detection
   - Include GPU temp in dashboard display with color coding
   - Update MetricsCollector class with _get_gpu_temp() method
   
   Tested on RTX 5080 with NVIDIA 570.86.16 drivers"
   ```

6. **Push and create pull request**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

Use conventional commit format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `refactor:` for code refactoring
- `test:` for testing improvements
- `chore:` for maintenance tasks

Include detailed descriptions for complex changes.

## 🏗️ Architecture Guidelines

### Component Interaction

- **Gaming Manager** should handle system state changes
- **Gaming Monitor** should be read-only for metrics collection
- **Gaming Maintenance** should be standalone for benchmarking

### Configuration Management

- Use JSON for structured configuration data
- Store user configs in `~/.config/gaming-manager/`
- Store system state in `/var/run/gaming-mode.state`
- Log to `/var/log/gaming-*` directories

### Hardware Abstraction

When adding hardware support:
- Create detection functions for hardware identification
- Implement fallback behavior for unsupported hardware
- Document hardware-specific optimizations clearly
- Test on multiple configurations when possible

## 🚨 Security Considerations

- **Minimize sudo usage** - only when absolutely necessary
- **Validate all inputs** - especially file paths and system commands
- **Use subprocess safely** - avoid shell injection vulnerabilities
- **Handle sensitive data** carefully (don't log system information)

## 📚 Resources

### Bazzite-Specific Resources
- [Bazzite Documentation](https://universal-blue.org/images/bazzite/)
- [System76 Scheduler](https://github.com/pop-os/system76-scheduler)
- [ujust Commands](https://github.com/ublue-os/bazzite/tree/main/system_files/desktop/shared/usr/share/ublue-os/just)

### Development Tools
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Black Code Formatter](https://black.readthedocs.io/)
- [Pylint](https://pylint.readthedocs.io/)

### Gaming Optimization
- Linux Gaming Subreddit: [r/linux_gaming](https://reddit.com/r/linux_gaming)
- Bazzite Community: [r/bazzite](https://reddit.com/r/bazzite)

## 🏷️ Release Process

Maintainers handle releases, but contributors should:
- Update CHANGELOG.md with their changes
- Follow semantic versioning principles
- Document breaking changes clearly

## 💬 Getting Help

- **GitHub Discussions** for general questions
- **Issues** for bug reports and feature requests
- **Discord** via the Bazzite community server

Thank you for contributing to make Linux gaming better! 🐧🎮