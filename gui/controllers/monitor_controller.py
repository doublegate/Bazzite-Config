#!/usr/bin/env python3
"""
Monitor Controller for Bazzite Optimizer GUI

Handles real-time system metrics collection.
"""

import subprocess
import re
from datetime import datetime
from typing import Optional
from pathlib import Path

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

import sys
sys.path.append(str(Path(__file__).parent.parent))
from models.metrics_model import SystemMetrics, MetricsModel


class MonitorController:
    """Controller for real-time system monitoring"""

    def __init__(self, metrics_model: MetricsModel):
        """
        Initialize monitor controller

        Args:
            metrics_model: MetricsModel instance to store metrics
        """
        self.metrics_model = metrics_model
        self.monitoring_active = False

    def collect_metrics(self) -> SystemMetrics:
        """
        Collect current system metrics

        Returns:
            SystemMetrics snapshot
        """
        metrics = SystemMetrics(timestamp=datetime.now())

        if PSUTIL_AVAILABLE:
            metrics = self._collect_with_psutil(metrics)
        else:
            metrics = self._collect_without_psutil(metrics)

        return metrics

    def _collect_with_psutil(self, metrics: SystemMetrics) -> SystemMetrics:
        """Collect metrics using psutil library"""
        # CPU metrics
        metrics.cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            metrics.cpu_freq = cpu_freq.current

        # CPU temperature
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                metrics.cpu_temp = temps['coretemp'][0].current
            elif 'k10temp' in temps:  # AMD
                metrics.cpu_temp = temps['k10temp'][0].current
        except Exception:
            pass

        # Memory metrics
        mem = psutil.virtual_memory()
        metrics.ram_used = mem.used / (1024**3)  # GB
        metrics.ram_total = mem.total / (1024**3)  # GB
        metrics.ram_percent = mem.percent

        # Swap metrics
        swap = psutil.swap_memory()
        metrics.swap_used = swap.used / (1024**3)  # GB
        metrics.swap_total = swap.total / (1024**3)  # GB

        # GPU metrics (NVIDIA)
        self._collect_nvidia_metrics(metrics)

        return metrics

    def _collect_without_psutil(self, metrics: SystemMetrics) -> SystemMetrics:
        """Collect metrics without psutil using system commands"""
        # CPU usage from /proc/stat
        try:
            with open('/proc/stat', 'r') as f:
                cpu_line = f.readline()
                # Simple approximation - would need proper calculation
                metrics.cpu_percent = 50.0  # Placeholder
        except Exception:
            pass

        # Memory from /proc/meminfo
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = {}
                for line in f:
                    parts = line.split(':')
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip().split()[0]
                        meminfo[key] = int(value)

                total = meminfo.get('MemTotal', 0) / (1024**2)  # GB
                available = meminfo.get('MemAvailable', 0) / (1024**2)  # GB
                metrics.ram_total = total
                metrics.ram_used = total - available
                metrics.ram_percent = (metrics.ram_used / metrics.ram_total * 100) if total > 0 else 0
        except Exception:
            pass

        # GPU metrics
        self._collect_nvidia_metrics(metrics)

        return metrics

    def _collect_nvidia_metrics(self, metrics: SystemMetrics):
        """Collect NVIDIA GPU metrics via nvidia-smi"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu',
                 '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                values = result.stdout.strip().split(',')
                if len(values) >= 4:
                    metrics.gpu_percent = float(values[0].strip())
                    metrics.gpu_memory_used = float(values[1].strip())
                    metrics.gpu_memory_total = float(values[2].strip())
                    metrics.gpu_temp = float(values[3].strip())
        except Exception:
            # GPU metrics unavailable
            pass

    def start_monitoring(self, interval_ms: int = 1000) -> bool:
        """
        Start monitoring (to be called with GLib.timeout_add)

        Args:
            interval_ms: Update interval in milliseconds

        Returns:
            True to continue monitoring
        """
        if not self.monitoring_active:
            return False

        metrics = self.collect_metrics()
        self.metrics_model.add_metrics(metrics)
        return True

    def activate_monitoring(self):
        """Activate monitoring"""
        self.monitoring_active = True

    def deactivate_monitoring(self):
        """Deactivate monitoring"""
        self.monitoring_active = False

    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """Get most recent metrics"""
        return self.metrics_model.get_current_metrics()

    def get_statistics(self) -> dict:
        """Get metrics statistics"""
        return self.metrics_model.get_statistics()
