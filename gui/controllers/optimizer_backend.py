#!/usr/bin/env python3
"""
Optimizer Backend Controller for Bazzite Optimizer GUI

Handles communication with the bazzite-optimizer.py backend script.
"""

import subprocess
import os
import sys
from pathlib import Path
from typing import Optional, Tuple, Callable
import threading


class OptimizerBackend:
    """Backend controller for bazzite-optimizer.py integration"""

    def __init__(self, script_path: Optional[Path] = None):
        """
        Initialize optimizer backend

        Args:
            script_path: Path to bazzite-optimizer.py (auto-detected if None)
        """
        if script_path is None:
            # Auto-detect script path
            current_dir = Path(__file__).parent.parent.parent
            self.script_path = current_dir / "bazzite-optimizer.py"
        else:
            self.script_path = Path(script_path)

        if not self.script_path.exists():
            raise FileNotFoundError(f"Optimizer script not found: {self.script_path}")

    def _run_command(self, args: list, require_root: bool = False) -> Tuple[int, str, str]:
        """
        Run optimizer command

        Args:
            args: Command arguments
            require_root: Whether command requires root privileges

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        cmd = [sys.executable, str(self.script_path)] + args

        if require_root and os.geteuid() != 0:
            # Use pkexec for privilege escalation
            cmd = ['pkexec'] + cmd

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Operation timed out after 5 minutes"
        except Exception as e:
            return -1, "", str(e)

    def _run_async(self, args: list, callback: Callable, require_root: bool = False):
        """
        Run command asynchronously in background thread

        Args:
            args: Command arguments
            callback: Callback function called with (return_code, stdout, stderr)
            require_root: Whether command requires root privileges
        """
        def worker():
            result = self._run_command(args, require_root)
            if callback:
                callback(*result)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def list_profiles(self) -> Tuple[int, list, str]:
        """
        List available profiles

        Returns:
            Tuple of (return_code, profiles_list, error_message)
        """
        returncode, stdout, stderr = self._run_command(['--list-profiles'])
        if returncode == 0:
            profiles = [line.strip() for line in stdout.split('\n') if line.strip()]
            return returncode, profiles, ""
        return returncode, [], stderr

    def apply_profile(self, profile_name: str, callback: Optional[Callable] = None):
        """
        Apply optimization profile

        Args:
            profile_name: Name of profile to apply (competitive, balanced, streaming, creative)
            callback: Optional async callback(return_code, stdout, stderr)
        """
        if callback:
            self._run_async(['--profile', profile_name], callback, require_root=True)
        else:
            return self._run_command(['--profile', profile_name], require_root=True)

    def validate_system(self, callback: Optional[Callable] = None):
        """
        Validate system configuration

        Args:
            callback: Optional async callback(return_code, stdout, stderr)
        """
        if callback:
            self._run_async(['--validate'], callback)
        else:
            return self._run_command(['--validate'])

    def run_benchmark(self, callback: Optional[Callable] = None):
        """
        Run system benchmark

        Args:
            callback: Optional async callback(return_code, stdout, stderr)
        """
        if callback:
            self._run_async(['--benchmark'], callback, require_root=True)
        else:
            return self._run_command(['--benchmark'], require_root=True)

    def test_stability(self, callback: Optional[Callable] = None):
        """
        Test system stability

        Args:
            callback: Optional async callback(return_code, stdout, stderr)
        """
        if callback:
            self._run_async(['--test-stability'], callback, require_root=True)
        else:
            return self._run_command(['--test-stability'], require_root=True)

    def rollback(self, callback: Optional[Callable] = None):
        """
        Rollback to previous configuration

        Args:
            callback: Optional async callback(return_code, stdout, stderr)
        """
        if callback:
            self._run_async(['--rollback'], callback, require_root=True)
        else:
            return self._run_command(['--rollback'], require_root=True)

    def get_version(self) -> str:
        """Get optimizer script version"""
        returncode, stdout, stderr = self._run_command(['--version'])
        if returncode == 0:
            return stdout.strip()
        return "Unknown"

    def check_root_available(self) -> bool:
        """Check if we can obtain root privileges via pkexec"""
        try:
            result = subprocess.run(
                ['pkexec', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False


class QuickFixBackend:
    """Backend for quick fix operations"""

    def __init__(self):
        pass

    def _run_fix(self, command: list, callback: Optional[Callable] = None) -> Tuple[int, str, str]:
        """Run a fix command with optional async callback"""
        def worker():
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                return result.returncode, result.stdout, result.stderr
            except Exception as e:
                return -1, "", str(e)

        if callback:
            def async_worker():
                result = worker()
                callback(*result)
            threading.Thread(target=async_worker, daemon=True).start()
        else:
            return worker()

    def fix_steam(self, callback: Optional[Callable] = None):
        """Fix Steam client issues"""
        commands = [
            ['pkexec', 'systemctl', 'restart', 'steam'],
            ['rm', '-rf', os.path.expanduser('~/.steam/steam/appcache')],
        ]
        # Run first command (restart)
        return self._run_fix(commands[0], callback)

    def fix_audio(self, callback: Optional[Callable] = None):
        """Restart audio services"""
        commands = [
            ['systemctl', '--user', 'restart', 'pipewire'],
            ['systemctl', '--user', 'restart', 'pipewire-pulse'],
            ['systemctl', '--user', 'restart', 'wireplumber']
        ]
        # Run commands sequentially
        def run_sequence():
            for cmd in commands:
                returncode, stdout, stderr = self._run_fix(cmd)
                if returncode != 0:
                    if callback:
                        callback(returncode, stdout, stderr)
                    return returncode, stdout, stderr
            if callback:
                callback(0, "Audio services restarted successfully", "")
            return 0, "Audio services restarted successfully", ""

        if callback:
            threading.Thread(target=run_sequence, daemon=True).start()
        else:
            return run_sequence()

    def reset_gpu(self, callback: Optional[Callable] = None):
        """Reset GPU to defaults"""
        command = ['pkexec', 'nvidia-settings', '--restore-defaults']
        return self._run_fix(command, callback)

    def clear_caches(self, callback: Optional[Callable] = None):
        """Clear system caches"""
        cache_dirs = [
            os.path.expanduser('~/.cache'),
            '/tmp'
        ]
        # Just clear user cache for safety
        command = ['rm', '-rf', os.path.expanduser('~/.cache/*')]
        return self._run_fix(command, callback)

    def restart_gaming_services(self, callback: Optional[Callable] = None):
        """Restart gaming-related services"""
        command = ['pkexec', 'systemctl', 'restart', 'system76-scheduler']
        return self._run_fix(command, callback)
