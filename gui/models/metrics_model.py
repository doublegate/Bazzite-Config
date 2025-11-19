#!/usr/bin/env python3
"""
Metrics Model for Bazzite Optimizer GUI

Manages real-time performance metrics data.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from collections import deque


@dataclass
class SystemMetrics:
    """System performance metrics snapshot"""
    timestamp: datetime
    cpu_percent: float = 0.0
    cpu_freq: float = 0.0  # MHz
    cpu_temp: Optional[float] = None  # Celsius
    gpu_percent: float = 0.0
    gpu_memory_used: float = 0.0  # MB
    gpu_memory_total: float = 0.0  # MB
    gpu_temp: Optional[float] = None  # Celsius
    ram_used: float = 0.0  # GB
    ram_total: float = 0.0  # GB
    ram_percent: float = 0.0
    swap_used: float = 0.0  # GB
    swap_total: float = 0.0  # GB
    network_latency: Optional[float] = None  # ms
    fps: Optional[int] = None


class MetricsModel:
    """Model for managing performance metrics history"""

    def __init__(self, max_history: int = 60):
        """
        Initialize metrics model

        Args:
            max_history: Maximum number of data points to keep (default 60 = 1 minute at 1Hz)
        """
        self.max_history = max_history
        self._history: deque = deque(maxlen=max_history)
        self._observers: List = []
        self.current_metrics: Optional[SystemMetrics] = None

    def add_metrics(self, metrics: SystemMetrics):
        """Add new metrics snapshot"""
        self.current_metrics = metrics
        self._history.append(metrics)
        self.notify_observers()

    def get_history(self, count: Optional[int] = None) -> List[SystemMetrics]:
        """
        Get metrics history

        Args:
            count: Number of most recent data points to retrieve (None = all)

        Returns:
            List of SystemMetrics
        """
        if count is None:
            return list(self._history)
        return list(self._history)[-count:]

    def get_cpu_history(self, count: Optional[int] = None) -> List[tuple]:
        """Get CPU usage history as (timestamp, percent) tuples"""
        history = self.get_history(count)
        return [(m.timestamp, m.cpu_percent) for m in history]

    def get_gpu_history(self, count: Optional[int] = None) -> List[tuple]:
        """Get GPU usage history as (timestamp, percent) tuples"""
        history = self.get_history(count)
        return [(m.timestamp, m.gpu_percent) for m in history]

    def get_memory_history(self, count: Optional[int] = None) -> List[tuple]:
        """Get memory usage history as (timestamp, percent) tuples"""
        history = self.get_history(count)
        return [(m.timestamp, m.ram_percent) for m in history]

    def get_temperature_history(self, count: Optional[int] = None) -> dict:
        """Get temperature history for CPU and GPU"""
        history = self.get_history(count)
        return {
            "cpu": [(m.timestamp, m.cpu_temp) for m in history if m.cpu_temp is not None],
            "gpu": [(m.timestamp, m.gpu_temp) for m in history if m.gpu_temp is not None]
        }

    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """Get most recent metrics snapshot"""
        return self.current_metrics

    def clear_history(self):
        """Clear all metrics history"""
        self._history.clear()
        self.notify_observers()

    def attach_observer(self, observer):
        """Attach observer for metrics updates"""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach_observer(self, observer):
        """Detach observer"""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self):
        """Notify all observers of metrics update"""
        for observer in self._observers:
            observer.on_metrics_updated(self.current_metrics)

    def get_statistics(self) -> dict:
        """Calculate statistics from history"""
        if not self._history:
            return {}

        cpu_values = [m.cpu_percent for m in self._history]
        gpu_values = [m.gpu_percent for m in self._history]
        ram_values = [m.ram_percent for m in self._history]

        return {
            "cpu": {
                "current": cpu_values[-1] if cpu_values else 0,
                "average": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                "max": max(cpu_values) if cpu_values else 0,
                "min": min(cpu_values) if cpu_values else 0
            },
            "gpu": {
                "current": gpu_values[-1] if gpu_values else 0,
                "average": sum(gpu_values) / len(gpu_values) if gpu_values else 0,
                "max": max(gpu_values) if gpu_values else 0,
                "min": min(gpu_values) if gpu_values else 0
            },
            "memory": {
                "current": ram_values[-1] if ram_values else 0,
                "average": sum(ram_values) / len(ram_values) if ram_values else 0,
                "max": max(ram_values) if ram_values else 0,
                "min": min(ram_values) if ram_values else 0
            }
        }
