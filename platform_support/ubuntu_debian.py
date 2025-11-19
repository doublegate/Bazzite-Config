"""
Ubuntu/Debian Platform Support
Extends optimization support to Ubuntu and Debian distributions
"""

import subprocess
import logging
from pathlib import Path
from typing import List, Optional


class UbuntuDebianOptimizer:
    """Ubuntu/Debian specific optimizations"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_ubuntu = self._detect_ubuntu()
        self.is_debian = self._detect_debian()

    def _detect_ubuntu(self) -> bool:
        """Detect if running on Ubuntu"""
        try:
            if Path('/etc/os-release').exists():
                with open('/etc/os-release') as f:
                    content = f.read()
                    return 'Ubuntu' in content or 'ubuntu' in content.lower()
        except:
            pass
        return False

    def _detect_debian(self) -> bool:
        """Detect if running on Debian"""
        try:
            if Path('/etc/debian_version').exists():
                return True
        except:
            pass
        return False

    def is_supported(self) -> bool:
        """Check if platform is supported"""
        return self.is_ubuntu or self.is_debian

    def install_package(self, package: str) -> bool:
        """Install package using apt"""
        try:
            subprocess.run(
                ['sudo', 'apt', 'install', '-y', package],
                check=True,
                capture_output=True
            )
            self.logger.info(f"Installed package: {package}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install {package}: {e}")
            return False

    def update_packages(self) -> bool:
        """Update package lists"""
        try:
            subprocess.run(['sudo', 'apt', 'update'], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to update packages: {e}")
            return False

    def apply_gaming_optimizations(self) -> bool:
        """Apply Ubuntu/Debian specific gaming optimizations"""
        optimizations = [
            self._optimize_kernel_parameters,
            self._optimize_cpu_governor,
            self._optimize_io_scheduler,
            self._install_gaming_tools
        ]

        results = []
        for optimization in optimizations:
            try:
                results.append(optimization())
            except Exception as e:
                self.logger.error(f"Optimization failed: {e}")
                results.append(False)

        return all(results)

    def _optimize_kernel_parameters(self) -> bool:
        """Optimize kernel parameters for gaming"""
        params = {
            'vm.swappiness': '10',
            'vm.vfs_cache_pressure': '50',
            'kernel.sched_migration_cost_ns': '5000000',
            'kernel.sched_min_granularity_ns': '10000000'
        }

        try:
            for param, value in params.items():
                subprocess.run(
                    ['sudo', 'sysctl', '-w', f'{param}={value}'],
                    check=True,
                    capture_output=True
                )
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to set kernel parameters: {e}")
            return False

    def _optimize_cpu_governor(self) -> bool:
        """Set CPU governor to performance"""
        try:
            subprocess.run(
                ['sudo', 'cpupower', 'frequency-set', '-g', 'performance'],
                check=True,
                capture_output=True
            )
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.logger.warning("cpupower not available")
            return False

    def _optimize_io_scheduler(self) -> bool:
        """Optimize I/O scheduler for SSDs"""
        try:
            # Set scheduler to none for NVMe drives
            for device in Path('/sys/block').glob('nvme*'):
                scheduler_file = device / 'queue' / 'scheduler'
                if scheduler_file.exists():
                    subprocess.run(
                        ['sudo', 'sh', '-c', f'echo none > {scheduler_file}'],
                        check=True,
                        capture_output=True
                    )
            return True
        except Exception as e:
            self.logger.error(f"Failed to optimize I/O scheduler: {e}")
            return False

    def _install_gaming_tools(self) -> bool:
        """Install recommended gaming tools"""
        packages = [
            'gamemode',
            'mangohud',
            'wine-stable',
            'lutris'
        ]

        for package in packages:
            self.install_package(package)

        return True


class PPAManager:
    """Manage PPAs for gaming tools"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def add_ppa(self, ppa: str) -> bool:
        """Add a PPA repository"""
        try:
            subprocess.run(
                ['sudo', 'add-apt-repository', '-y', ppa],
                check=True,
                capture_output=True
            )
            subprocess.run(['sudo', 'apt', 'update'], check=True, capture_output=True)
            self.logger.info(f"Added PPA: {ppa}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to add PPA {ppa}: {e}")
            return False

    def add_gaming_ppas(self) -> bool:
        """Add recommended gaming PPAs"""
        ppas = [
            'ppa:lutris-team/lutris',
            'ppa:kisak/kisak-mesa'  # Updated Mesa drivers
        ]

        results = []
        for ppa in ppas:
            results.append(self.add_ppa(ppa))

        return all(results)
