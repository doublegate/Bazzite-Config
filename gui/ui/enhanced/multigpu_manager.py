"""
Multi-GPU Management Interface
Manages multiple GPUs (NVIDIA + AMD) simultaneously
"""

import logging
import subprocess
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

try:
    import gi
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gtk, GLib
except ImportError:
    pass


class GPUVendor(Enum):
    """GPU Vendor types"""
    NVIDIA = "NVIDIA"
    AMD = "AMD"
    INTEL = "Intel"
    UNKNOWN = "Unknown"


@dataclass
class GPUInfo:
    """Individual GPU information"""
    index: int
    vendor: GPUVendor
    model: str
    pci_id: str
    driver: str
    vram_total: int  # MB
    current_usage: int  # %
    current_temp: float  # °C
    power_usage: float  # W
    fan_speed: int  # %
    enabled: bool = True


class MultiGPUDetector:
    """Detect and enumerate all GPUs in the system"""

    @staticmethod
    def detect_all_gpus() -> List[GPUInfo]:
        """Detect all GPUs in the system"""
        gpus = []

        # Try to detect NVIDIA GPUs
        nvidia_gpus = MultiGPUDetector._detect_nvidia_gpus()
        gpus.extend(nvidia_gpus)

        # Try to detect AMD GPUs
        amd_gpus = MultiGPUDetector._detect_amd_gpus()
        gpus.extend(amd_gpus)

        # Try to detect Intel GPUs
        intel_gpus = MultiGPUDetector._detect_intel_gpus()
        gpus.extend(intel_gpus)

        return gpus

    @staticmethod
    def _detect_nvidia_gpus() -> List[GPUInfo]:
        """Detect NVIDIA GPUs"""
        gpus = []
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=index,name,pci.bus_id,driver_version,memory.total,utilization.gpu,temperature.gpu,power.draw,fan.speed',
                 '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                check=False,
                timeout=5
            )

            if result.returncode == 0:
                for line in result.stdout.strip().splitlines():
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 9:
                        gpus.append(GPUInfo(
                            index=int(parts[0]),
                            vendor=GPUVendor.NVIDIA,
                            model=parts[1],
                            pci_id=parts[2],
                            driver=f"nvidia {parts[3]}",
                            vram_total=int(float(parts[4])) if parts[4] else 0,
                            current_usage=int(float(parts[5])) if parts[5] else 0,
                            current_temp=float(parts[6]) if parts[6] else 0.0,
                            power_usage=float(parts[7]) if parts[7] else 0.0,
                            fan_speed=int(float(parts[8])) if parts[8] else 0
                        ))
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
            pass

        return gpus

    @staticmethod
    def _detect_amd_gpus() -> List[GPUInfo]:
        """Detect AMD GPUs"""
        gpus = []
        try:
            # Use rocm-smi if available
            result = subprocess.run(
                ['rocm-smi', '--showid', '--showtemp', '--showuse', '--showmeminfo', 'vram', '--showpower'],
                capture_output=True,
                text=True,
                check=False,
                timeout=5
            )

            if result.returncode == 0:
                # Parse rocm-smi output (simplified - actual parsing would be more complex)
                # For now, just detect presence
                result_lspci = subprocess.run(
                    ['lspci', '-nn'],
                    capture_output=True,
                    text=True,
                    check=False
                )

                index = 0
                for line in result_lspci.stdout.splitlines():
                    if 'VGA' in line and ('AMD' in line or 'Advanced Micro Devices' in line):
                        model = line.split(':')[-1].split('[')[0].strip()
                        pci_id = line.split()[0]
                        gpus.append(GPUInfo(
                            index=index,
                            vendor=GPUVendor.AMD,
                            model=model,
                            pci_id=pci_id,
                            driver="amdgpu",
                            vram_total=0,  # Would need sysfs parsing
                            current_usage=0,
                            current_temp=0.0,
                            power_usage=0.0,
                            fan_speed=0
                        ))
                        index += 1

        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return gpus

    @staticmethod
    def _detect_intel_gpus() -> List[GPUInfo]:
        """Detect Intel integrated GPUs"""
        gpus = []
        try:
            result = subprocess.run(
                ['lspci', '-nn'],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                index = 0
                for line in result.stdout.splitlines():
                    if 'VGA' in line and 'Intel' in line:
                        model = line.split(':')[-1].split('[')[0].strip()
                        pci_id = line.split()[0]
                        gpus.append(GPUInfo(
                            index=index,
                            vendor=GPUVendor.INTEL,
                            model=model,
                            pci_id=pci_id,
                            driver="i915/xe",
                            vram_total=0,
                            current_usage=0,
                            current_temp=0.0,
                            power_usage=0.0,
                            fan_speed=0
                        ))
                        index += 1

        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return gpus


class GPUCard(Gtk.Box):
    """Widget representing a single GPU"""

    def __init__(self, gpu_info: GPUInfo, on_settings_clicked=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.add_css_class("card")
        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(12)
        self.set_margin_bottom(12)

        self.gpu_info = gpu_info
        self.on_settings_clicked = on_settings_clicked

        self._create_ui()

    def _create_ui(self):
        """Create GPU card UI"""
        # Header with vendor icon and model
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header.set_margin_start(12)
        header.set_margin_end(12)
        header.set_margin_top(12)

        # Vendor icon (emoji)
        vendor_icons = {
            GPUVendor.NVIDIA: "🟢",  # Green
            GPUVendor.AMD: "🔴",     # Red
            GPUVendor.INTEL: "🔵",   # Blue
            GPUVendor.UNKNOWN: "⚪"
        }
        icon_label = Gtk.Label()
        icon_label.set_markup(f"<span size='xx-large'>{vendor_icons.get(self.gpu_info.vendor, '⚪')}</span>")

        # Model and vendor
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        model_label = Gtk.Label()
        model_label.set_markup(f"<b>{self.gpu_info.model}</b>")
        model_label.set_xalign(0)
        vendor_label = Gtk.Label(label=f"{self.gpu_info.vendor.value} ({self.gpu_info.driver})")
        vendor_label.set_xalign(0)
        vendor_label.add_css_class("dim-label")
        info_box.append(model_label)
        info_box.append(vendor_label)

        header.append(icon_label)
        header.append(info_box)

        # Settings button
        settings_btn = Gtk.Button(icon_name="emblem-system-symbolic")
        settings_btn.set_valign(Gtk.Align.CENTER)
        settings_btn.connect("clicked", self._on_settings_clicked)
        header.append(settings_btn)

        self.append(header)

        # Separator
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.append(sep)

        # Metrics grid
        grid = Gtk.Grid()
        grid.set_column_spacing(24)
        grid.set_row_spacing(12)
        grid.set_margin_start(12)
        grid.set_margin_end(12)
        grid.set_margin_bottom(12)

        # VRAM
        self._add_metric(grid, 0, 0, "VRAM", f"{self.gpu_info.vram_total} MB")

        # Usage
        self._add_metric(grid, 1, 0, "Usage", f"{self.gpu_info.current_usage}%")

        # Temperature
        self._add_metric(grid, 0, 1, "Temp", f"{self.gpu_info.current_temp}°C")

        # Power
        self._add_metric(grid, 1, 1, "Power", f"{self.gpu_info.power_usage}W")

        # Fan
        self._add_metric(grid, 0, 2, "Fan", f"{self.gpu_info.fan_speed}%")

        # PCI ID
        self._add_metric(grid, 1, 2, "PCI", self.gpu_info.pci_id)

        self.append(grid)

    def _add_metric(self, grid: Gtk.Grid, col: int, row: int, label: str, value: str):
        """Add a metric to the grid"""
        label_widget = Gtk.Label(label=f"{label}:")
        label_widget.set_xalign(0)
        label_widget.add_css_class("dim-label")

        value_widget = Gtk.Label(label=value)
        value_widget.set_xalign(0)
        value_widget.set_hexpand(True)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box.append(label_widget)
        box.append(value_widget)

        grid.attach(box, col, row, 1, 1)

    def _on_settings_clicked(self, button):
        """Settings button clicked"""
        if self.on_settings_clicked:
            self.on_settings_clicked(self.gpu_info)


class MultiGPUManager(Gtk.Box):
    """Multi-GPU management panel"""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        self.gpus: List[GPUInfo] = []
        self.gpu_cards: List[GPUCard] = []
        self.logger = logging.getLogger(__name__)

        self._create_ui()
        self.refresh_gpus()

    def _create_ui(self):
        """Create the UI"""
        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header.set_margin_start(12)
        header.set_margin_end(12)
        header.set_margin_top(12)

        title = Gtk.Label()
        title.set_markup("<big><b>Multi-GPU Management</b></big>")
        title.set_hexpand(True)
        title.set_xalign(0)

        refresh_btn = Gtk.Button(icon_name="view-refresh-symbolic")
        refresh_btn.connect("clicked", lambda b: self.refresh_gpus())

        header.append(title)
        header.append(refresh_btn)
        self.append(header)

        # GPU count label
        self.count_label = Gtk.Label()
        self.count_label.set_xalign(0)
        self.count_label.set_margin_start(12)
        self.append(self.count_label)

        # Scrolled window for GPU cards
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)

        # GPU cards container
        self.cards_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        scrolled.set_child(self.cards_box)

        self.append(scrolled)

    def refresh_gpus(self):
        """Refresh GPU detection"""
        self.logger.info("Detecting GPUs...")

        # Detect all GPUs
        self.gpus = MultiGPUDetector.detect_all_gpus()

        # Update count label
        nvidia_count = sum(1 for g in self.gpus if g.vendor == GPUVendor.NVIDIA)
        amd_count = sum(1 for g in self.gpus if g.vendor == GPUVendor.AMD)
        intel_count = sum(1 for g in self.gpus if g.vendor == GPUVendor.INTEL)

        count_text = f"Detected: {len(self.gpus)} total"
        if nvidia_count > 0:
            count_text += f" ({nvidia_count} NVIDIA"
        if amd_count > 0:
            count_text += f", {amd_count} AMD" if nvidia_count > 0 else f" ({amd_count} AMD"
        if intel_count > 0:
            count_text += f", {intel_count} Intel" if nvidia_count > 0 or amd_count > 0 else f" ({intel_count} Intel"
        if nvidia_count > 0 or amd_count > 0 or intel_count > 0:
            count_text += ")"

        self.count_label.set_text(count_text)

        # Clear existing cards
        while self.cards_box.get_first_child():
            self.cards_box.remove(self.cards_box.get_first_child())
        self.gpu_cards.clear()

        # Create cards for each GPU
        for gpu in self.gpus:
            card = GPUCard(gpu, on_settings_clicked=self._on_gpu_settings_clicked)
            self.cards_box.append(card)
            self.gpu_cards.append(card)

        if len(self.gpus) == 0:
            # No GPUs found
            no_gpu_label = Gtk.Label()
            no_gpu_label.set_markup("<big>No GPUs detected</big>")
            no_gpu_label.set_valign(Gtk.Align.CENTER)
            no_gpu_label.add_css_class("dim-label")
            self.cards_box.append(no_gpu_label)

    def _on_gpu_settings_clicked(self, gpu_info: GPUInfo):
        """GPU settings button clicked"""
        self.logger.info(f"Settings clicked for GPU: {gpu_info.model}")
        # Would open GPU-specific settings dialog
        # For now, just log

    def get_detected_gpus(self) -> List[GPUInfo]:
        """Get list of detected GPUs"""
        return self.gpus.copy()
