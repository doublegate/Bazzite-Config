#!/usr/bin/env python3
"""
Monitoring Tab for Bazzite Optimizer GUI

Real-time performance monitoring with graphs.
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class MonitoringTab(Gtk.Box):
    """Monitoring tab for real-time performance metrics"""

    def __init__(self, metrics_model, monitor_controller):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_start(20)
        self.set_margin_end(20)
        self.set_margin_top(20)
        self.set_margin_bottom(20)

        self.metrics_model = metrics_model
        self.monitor_controller = monitor_controller
        self.monitoring_active = False
        self.update_timer_id = None

        # Attach as observer
        self.metrics_model.attach_observer(self)

        self._create_ui()

    def _create_ui(self):
        """Create monitoring UI"""
        # Title and controls
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.append(header_box)

        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>Real-Time Performance Monitoring</span>")
        title.set_xalign(0)
        title.set_hexpand(True)
        header_box.append(title)

        # Control buttons
        self.start_button = Gtk.Button(label="▶ Start Monitoring")
        self.start_button.connect("clicked", self._on_start_monitoring)
        header_box.append(self.start_button)

        self.stop_button = Gtk.Button(label="◼ Stop Monitoring")
        self.stop_button.connect("clicked", self._on_stop_monitoring)
        self.stop_button.set_sensitive(False)
        header_box.append(self.stop_button)

        # Metrics grid
        metrics_grid = Gtk.Grid()
        metrics_grid.set_column_spacing(20)
        metrics_grid.set_row_spacing(15)
        metrics_grid.set_margin_top(20)
        self.append(metrics_grid)

        # CPU Section
        cpu_frame = self._create_metric_frame("CPU Usage")
        metrics_grid.attach(cpu_frame, 0, 0, 1, 1)

        cpu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        cpu_frame.set_child(cpu_box)

        self.cpu_progress = Gtk.ProgressBar()
        cpu_box.append(self.cpu_progress)

        self.cpu_label = Gtk.Label(label="CPU: 0%")
        self.cpu_label.set_xalign(0)
        cpu_box.append(self.cpu_label)

        self.cpu_freq_label = Gtk.Label(label="Frequency: -- MHz")
        self.cpu_freq_label.set_xalign(0)
        cpu_box.append(self.cpu_freq_label)

        self.cpu_temp_label = Gtk.Label(label="Temperature: --°C")
        self.cpu_temp_label.set_xalign(0)
        cpu_box.append(self.cpu_temp_label)

        # GPU Section
        gpu_frame = self._create_metric_frame("GPU Usage")
        metrics_grid.attach(gpu_frame, 1, 0, 1, 1)

        gpu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        gpu_frame.set_child(gpu_box)

        self.gpu_progress = Gtk.ProgressBar()
        gpu_box.append(self.gpu_progress)

        self.gpu_label = Gtk.Label(label="GPU: 0%")
        self.gpu_label.set_xalign(0)
        gpu_box.append(self.gpu_label)

        self.gpu_mem_label = Gtk.Label(label="VRAM: 0 MB / 0 MB")
        self.gpu_mem_label.set_xalign(0)
        gpu_box.append(self.gpu_mem_label)

        self.gpu_temp_label = Gtk.Label(label="Temperature: --°C")
        self.gpu_temp_label.set_xalign(0)
        gpu_box.append(self.gpu_temp_label)

        # Memory Section
        mem_frame = self._create_metric_frame("Memory Usage")
        metrics_grid.attach(mem_frame, 0, 1, 1, 1)

        mem_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        mem_frame.set_child(mem_box)

        self.ram_progress = Gtk.ProgressBar()
        mem_box.append(self.ram_progress)

        self.ram_label = Gtk.Label(label="RAM: 0 GB / 0 GB")
        self.ram_label.set_xalign(0)
        mem_box.append(self.ram_label)

        self.swap_label = Gtk.Label(label="Swap: 0 GB / 0 GB")
        self.swap_label.set_xalign(0)
        mem_box.append(self.swap_label)

        # Statistics Section
        stats_frame = self._create_metric_frame("Statistics")
        metrics_grid.attach(stats_frame, 1, 1, 1, 1)

        stats_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        stats_frame.set_child(stats_box)

        self.cpu_avg_label = Gtk.Label(label="CPU Average: --")
        self.cpu_avg_label.set_xalign(0)
        stats_box.append(self.cpu_avg_label)

        self.gpu_avg_label = Gtk.Label(label="GPU Average: --")
        self.gpu_avg_label.set_xalign(0)
        stats_box.append(self.gpu_avg_label)

        self.uptime_label = Gtk.Label(label="Monitoring Time: 0s")
        self.uptime_label.set_xalign(0)
        stats_box.append(self.uptime_label)

        # Note about graphs
        note = Gtk.Label()
        note.set_markup(
            "<i>Note: Historical graphs require Cairo drawing implementation.\n"
            "Current view shows real-time metrics only.</i>"
        )
        note.set_margin_top(20)
        self.append(note)

    def _create_metric_frame(self, title):
        """Create a metric frame"""
        frame = Gtk.Frame(label=title)
        frame.set_margin_start(5)
        frame.set_margin_end(5)
        frame.set_margin_top(5)
        frame.set_margin_bottom(5)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)

        return frame

    def _on_start_monitoring(self, button):
        """Start monitoring"""
        self.start_monitoring()

    def _on_stop_monitoring(self, button):
        """Stop monitoring"""
        self.stop_monitoring()

    def start_monitoring(self):
        """Start monitoring metrics"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_controller.activate_monitoring()

            # Start update timer (1000ms = 1 second)
            self.update_timer_id = GLib.timeout_add(1000, self._update_metrics)

            self.start_button.set_sensitive(False)
            self.stop_button.set_sensitive(True)
            self.monitoring_start_time = GLib.get_real_time()

    def stop_monitoring(self):
        """Stop monitoring metrics"""
        if self.monitoring_active:
            self.monitoring_active = False
            self.monitor_controller.deactivate_monitoring()

            if self.update_timer_id:
                GLib.source_remove(self.update_timer_id)
                self.update_timer_id = None

            self.start_button.set_sensitive(True)
            self.stop_button.set_sensitive(False)

    def _update_metrics(self):
        """Update metrics (called by timer)"""
        if not self.monitoring_active:
            return False

        # Collect metrics
        self.monitor_controller.start_monitoring()

        # Update uptime
        if hasattr(self, 'monitoring_start_time'):
            elapsed = (GLib.get_real_time() - self.monitoring_start_time) // 1000000
            self.uptime_label.set_text(f"Monitoring Time: {elapsed}s")

        return True  # Continue timer

    def on_metrics_updated(self, metrics):
        """Observer callback for metrics updates"""
        if metrics:
            GLib.idle_add(self._update_ui_from_metrics, metrics)

    def _update_ui_from_metrics(self, metrics):
        """Update UI from metrics (in main thread)"""
        # CPU
        self.cpu_progress.set_fraction(metrics.cpu_percent / 100.0)
        self.cpu_label.set_text(f"CPU: {metrics.cpu_percent:.1f}%")
        self.cpu_freq_label.set_text(f"Frequency: {metrics.cpu_freq:.0f} MHz")
        if metrics.cpu_temp:
            self.cpu_temp_label.set_text(f"Temperature: {metrics.cpu_temp:.1f}°C")

        # GPU
        self.gpu_progress.set_fraction(metrics.gpu_percent / 100.0)
        self.gpu_label.set_text(f"GPU: {metrics.gpu_percent:.1f}%")
        self.gpu_mem_label.set_text(
            f"VRAM: {metrics.gpu_memory_used:.0f} MB / {metrics.gpu_memory_total:.0f} MB"
        )
        if metrics.gpu_temp:
            self.gpu_temp_label.set_text(f"Temperature: {metrics.gpu_temp:.1f}°C")

        # Memory
        self.ram_progress.set_fraction(metrics.ram_percent / 100.0)
        self.ram_label.set_text(f"RAM: {metrics.ram_used:.1f} GB / {metrics.ram_total:.1f} GB")
        self.swap_label.set_text(f"Swap: {metrics.swap_used:.1f} GB / {metrics.swap_total:.1f} GB")

        # Statistics
        stats = self.monitor_controller.get_statistics()
        if stats and 'cpu' in stats:
            self.cpu_avg_label.set_text(f"CPU Average: {stats['cpu']['average']:.1f}%")
            self.gpu_avg_label.set_text(f"GPU Average: {stats['gpu']['average']:.1f}%")

        return False
