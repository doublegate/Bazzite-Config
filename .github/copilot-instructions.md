# Copilot Instructions - Bazzite Gaming Optimization Suite

## Project Overview

The Bazzite Gaming Optimization Suite is a comprehensive, enterprise-grade gaming optimization framework centered around the `bazzite-optimizer.py` master script (7,637 lines, 300KB) with a modern GTK4 graphical interface, complete ML/AI engine, and React Native mobile app. This production system delivers **15-25% performance improvements** for high-end gaming configurations.

**Target Platform**: Bazzite Linux (Fedora-based immutable gaming OS)  
**Primary Hardware**: NVIDIA RTX/AMD RDNA2-3 GPUs, Intel/AMD CPUs, Steam Deck, ROG Ally  
**License**: MIT  
**Current Version**: 1.6.0  
**Codebase**: 34,000+ lines across 84 Python/TypeScript files

## Architecture & Core Components

### Master Script
- **bazzite-optimizer.py** (7,637 lines): Primary entrypoint with 16 specialized optimizer classes
  - Profile-based optimization (Competitive, Balanced, Streaming, Safe Defaults)
  - Intelligent system tuning with validation and rollback capabilities
  - Transaction handling with 100% validation success rate

### Tools Suite
- **gaming-manager-suite.py**: System control and gaming mode management
- **gaming-monitor-suite.py**: Real-time performance metrics with curses dashboard
- **gaming-maintenance-suite.sh**: Automated benchmarking and maintenance
- **undo_bazzite-optimizer.py**: Configuration restore utility

### Advanced Features
- **GUI** (gui/): GTK4 graphical interface (~2,600 lines)
- **ML Engine** (ml_engine/): Machine learning optimizer (~7,300 lines)
  - Real-time data collection (benchmark_collector.py)
  - Model optimization (model_optimizer.py)
- **AI Engine** (ai_engine/): DQN reinforcement learning (dqn_agent.py, 406 lines)
- **Mobile App** (mobile-app/): React Native companion app (~1,200 lines)
- **Mobile API** (mobile_api/): FastAPI WebSocket server (websocket_server.py, 405 lines)

## Technology Stack

### Core Technologies
- **Python 3.8+**: Primary language for all optimization logic
- **Bash**: Shell scripts for system-level operations
- **GTK4**: Modern graphical interface
- **PyTorch**: Deep learning and reinforcement learning
- **React Native**: Mobile companion application
- **FastAPI**: WebSocket server for mobile integration

### Key Dependencies
- `psutil`: System metrics collection
- `stress-ng`, `sysbench`: Benchmarking tools
- `rpm-ostree`: Immutable OS management (Bazzite-specific)
- `ujust`: Bazzite system commands integration
- `system76-scheduler`, `GameMode`: Gaming optimizations

## Code Style & Conventions

### Python Style
- **PEP 8** with 88-character line limit (Black formatter)
- **Type hints** required for all public function parameters and returns
- **Docstrings** mandatory for all classes and public methods (Google/NumPy style)
- **Exception handling**: Graceful with specific error messages

Example:
```python
def collect_metrics(self, interval: int = 2) -> Dict[str, float]:
    """
    Collect system performance metrics.
    
    Args:
        interval: Sampling interval in seconds
        
    Returns:
        Dictionary containing CPU, GPU, memory metrics
        
    Raises:
        SystemError: If metrics collection fails
    """
    try:
        # Implementation
        pass
    except Exception as e:
        raise SystemError(f"Metrics collection failed: {e}")
```

### Shell Script Style
- **Bash shebang**: `#!/bin/bash`
- **Strict mode**: `set -euo pipefail`
- **Quote variables**: Always use `"$variable"`
- **Functions** for code reuse
- **Error handling** with meaningful messages

### Naming Conventions
- **Scripts**: hyphenated (e.g., `bazzite-optimizer.py`, `gaming-manager-suite.py`)
- **Modules/Functions**: snake_case (e.g., `collect_metrics`, `apply_profile`)
- **Classes**: PascalCase (e.g., `GamingModeController`, `MetricsCollector`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_INTERVAL`, `MAX_RETRIES`)

### Color-Coded Output
Consistent `Colors` class used across all tools:
```python
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
```

## Development Commands

### Prerequisites (Bazzite Linux)
```bash
# System dependencies
sudo dnf install python3-psutil python3-configparser stress-ng sysbench

# Development tools
sudo dnf install python3-pip python3-devel
pip3 install --user black isort flake8 mypy pylint
```

### Environment Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -e .[dev]

# Make scripts executable
chmod +x bazzite-optimizer.py gaming-manager-suite.py gaming-monitor-suite.py gaming-maintenance-suite.sh
```

### Code Quality
```bash
# Format code
black .
isort .

# Lint
flake8

# Type checking
mypy bazzite-optimizer.py
```

### Testing
```bash
# Run all tests
pytest -q

# Run specific test
pytest tests/test_kernel_param_fix.py -v

# Run with coverage
pytest --cov=. --cov-report=html
```

### Building
```bash
# Build Python package
python -m build

# Build standalone binary
pyinstaller --name bazzite-optimizer --onefile bazzite-optimizer.py
```

### Running Components
```bash
# Master optimizer
./bazzite-optimizer.py --list-profiles
sudo ./bazzite-optimizer.py --profile competitive
./bazzite-optimizer.py --verify --profile balanced
sudo ./bazzite-optimizer.py --rollback

# Gaming manager (legacy)
./gaming-manager-suite.py --enable
./gaming-manager-suite.py --status
./gaming-manager-suite.py --health

# Gaming monitor
./gaming-monitor-suite.py --mode dashboard
./gaming-monitor-suite.py --mode simple --interval 5
```

## Testing Guidelines

### Test Organization
- **Location**: `tests/` directory
- **Naming**: `test_*.py` files mirroring source structure
- **Framework**: pytest

### Test Focus Areas
- **Optimizer actions**: Profile application, validation, rollback
- **Kernel parameters**: Deduplication, batching, validation
- **Profile transitions**: Safe Defaults → Competitive → Balanced flows
- **Error handling**: Graceful degradation and recovery
- **Hardware detection**: CPU, GPU, RAM identification

### Integration Tests
```bash
# Quick system checks
./gaming-manager-suite.py --status
./gaming-monitor-suite.py --mode simple
sudo ./bazzite-optimizer.py --validate
```

### Regression Testing
- Add tests for all reported issues
- Verify fixes don't break existing functionality
- Test profile transitions thoroughly

## Security & Safety Guidelines

### Bazzite-Specific Considerations
- **Immutable OS**: Bazzite uses rpm-ostree (immutable filesystem)
- **Idempotent operations**: All changes must be safely reapplied
- **Explicit rollback**: Provide `--rollback` for all system modifications
- **Dry-run mode**: Support `--verify` to preview changes without applying

### Kernel Parameter Management
- **Batch operations**: Use `rpm-ostree kargs` with batching
- **Avoid duplicates**: Check existing parameters before adding
- **Validation**: Verify parameters before and after application
- **Reboot awareness**: Kernel changes require system restart

### System Integration
- **ujust commands**: Respect Bazzite's built-in system commands
- **system76-scheduler**: Don't conflict with existing CPU scheduling
- **GameMode**: Integrate with, don't override GameMode settings
- **Service validation**: Check service state before modifications

### Input Validation
- **Shell injection prevention**: Use `subprocess.run([...], check=True)` with list arguments
- **Path validation**: Verify paths exist and are accessible
- **Permission checks**: Validate sudo requirements before execution
- **Type checking**: Use type hints and runtime validation

### Best Practices
- Minimize `sudo` usage to necessary operations only
- Log all system modifications with timestamps
- Provide clear error messages with resolution steps
- Implement transaction-style operations with atomic rollback

## Key Design Patterns

### Configuration Management
- Gaming mode state: `/var/run/gaming-mode.state`
- Configuration files: `/etc/gaming-mode.conf`
- Game profiles: `~/.config/gaming-manager/profiles/`
- Log directories: `/var/log/gaming-benchmark/`, `/var/log/gaming-metrics/`
- Results storage: `~/.local/share/gaming-benchmarks/`

### Modular Architecture
- Separate classes for distinct functional areas
- JSON-based profiles and configuration
- Plugin-style optimizer classes
- Service-oriented mobile API

### Hardware Detection
- Automatic CPU/GPU/RAM detection via psutil, GPUtil
- NVIDIA-specific optimizations (-open driver variant)
- AMD RDNA2/RDNA3 support
- Intel/AMD CPU tuning

## Commit & Pull Request Guidelines

### Commit Message Format
Follow Conventional Commits:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Test additions/modifications
- `chore:` Maintenance tasks

Example:
```
feat: Add DQN reinforcement learning optimizer

- Implement PyTorch-based DQN agent (406 lines)
- Add experience replay buffer with named tuples
- Create gaming environment simulator for training
- Include model checkpointing and loss tracking

Tested on Bazzite 3.5.0 with RTX 5080
Closes #123
```

### Pull Request Requirements
- **Description**: Clear explanation of changes and motivation
- **Affected components**: List modified modules/scripts
- **Test evidence**: Include command outputs, logs
- **Screenshots**: For UI or terminal output changes
- **Documentation updates**: Update README.md, CHANGELOG.md for user-facing changes
- **Breaking changes**: Clearly mark and document

## Project Documentation

### Primary Documentation Files
- **README.md**: Overview, features, installation
- **CONTRIBUTING.md**: Development setup, contribution guidelines
- **WARP.md**: Quick reference for Warp.dev AI assistant
- **CLAUDE.md**: Guidelines for Claude AI assistant
- **AGENTS.md**: Repository-wide agent guidelines
- **CHANGELOG.md**: Version history and release notes

### Technical Documentation (docs/)
- `TECHNICAL_ARCHITECTURE.md`: System architecture details
- `INSTALLATION_SETUP.md`: Installation procedures
- `TROUBLESHOOTING.md`: Common issues and solutions
- `BOOT_INFRASTRUCTURE_IMPLEMENTATION.md`: Boot parameter handling
- `USER_GUIDE.md`: Comprehensive user documentation
- `INSTALLATION_GUIDE.md`: Platform-specific installation
- `FAQ.md`: Frequently asked questions

## Important Context

### Critical Rules
1. **Always read before write**: Verify file existence, read content, plan changes, then edit
2. **Minimal modifications**: Make surgical changes, avoid drive-by fixes
3. **Validation first**: Use `--verify` mode to test changes before applying
4. **Safety nets**: Implement rollback capabilities for all system modifications
5. **Test focus**: Add tests for critical paths and reported issues only

### Platform Limitations
- Bazzite is immutable - some directories are read-only
- Kernel parameter changes require reboot
- rpm-ostree operations can be slow
- SystemD service modifications need careful handling

### Hardware Considerations
- Optimized for high-end gaming setups
- NVIDIA RTX 5080 (Blackwell architecture) specific tuning
- Intel i9-10850K (Comet Lake) optimizations
- Samsung 990 EVO Plus NVMe benchmarks
- Steam Deck and ROG Ally compatibility

## Getting Help

- **Issues**: Use GitHub issue templates for bug reports and feature requests
- **Discussions**: For questions and general discussion
- **Health Check**: Run `./gaming-manager-suite.py --health` for diagnostics
- **Logs**: Check `/var/log/gaming-benchmark/` and `/var/log/gaming-metrics/`
- **Validation**: Use `./bazzite-optimizer.py --validate` to verify system state

## References

- Repository: https://github.com/doublegate/Bazzite-Config
- Bazzite Linux: https://bazzite.gg/
- Steam Deck: https://www.steamdeck.com/
- GameMode: https://github.com/FeralInteractive/gamemode
- System76 Scheduler: https://github.com/pop-os/system76-scheduler
