"""
Custom Profile Editor
Allows users to create, modify, and manage custom gaming profiles
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    import gi
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gtk, GLib, Gio
except ImportError:
    pass


class ProfileEditor(Gtk.Window):
    """Custom gaming profile editor window"""

    def __init__(self, parent_window=None, profile_data: Optional[Dict] = None):
        super().__init__()
        self.set_title("Custom Profile Editor")
        self.set_default_size(800, 600)
        self.set_modal(True)

        if parent_window:
            self.set_transient_for(parent_window)

        self.profile_data = profile_data or self._get_default_profile()
        self.logger = logging.getLogger(__name__)

        self._create_ui()

    def _get_default_profile(self) -> Dict[str, Any]:
        """Get default profile template"""
        return {
            "name": "Custom Profile",
            "description": "User-created custom profile",
            "cpu": {
                "governor": "schedutil",
                "max_cstate": 3,
                "turbo_boost": True,
                "core_isolation": False
            },
            "gpu": {
                "power_mode": 0,  # 0=auto, 1=max performance
                "overclock_gpu": 0,  # MHz offset
                "overclock_mem": 0,  # MHz offset
                "fan_mode": "auto"
            },
            "memory": {
                "swappiness": 10,
                "zram_enabled": True,
                "zram_size_gb": 8,
                "huge_pages": False
            },
            "kernel": {
                "mitigations": "auto",
                "scheduler": "schedutil",
                "preempt": "voluntary"
            },
            "audio": {
                "quantum": 1024,
                "latency": "balanced"
            },
            "network": {
                "congestion_control": "bbr",
                "disable_ipv6": False
            }
        }

    def _create_ui(self):
        """Create the editor UI"""
        # Main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(main_box)

        # Header bar
        header = Gtk.HeaderBar()
        self.set_titlebar(header)

        # Save button
        save_button = Gtk.Button(label="Save Profile")
        save_button.add_css_class("suggested-action")
        save_button.connect("clicked", self._on_save_clicked)
        header.pack_end(save_button)

        # Cancel button
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", self._on_cancel_clicked)
        header.pack_start(cancel_button)

        # Content area with notebook
        notebook = Gtk.Notebook()
        notebook.set_tab_pos(Gtk.PositionType.LEFT)
        main_box.append(notebook)

        # Profile Info Tab
        notebook.append_page(self._create_info_tab(), Gtk.Label(label="Profile Info"))

        # CPU Tab
        notebook.append_page(self._create_cpu_tab(), Gtk.Label(label="CPU"))

        # GPU Tab
        notebook.append_page(self._create_gpu_tab(), Gtk.Label(label="GPU"))

        # Memory Tab
        notebook.append_page(self._create_memory_tab(), Gtk.Label(label="Memory"))

        # Kernel Tab
        notebook.append_page(self._create_kernel_tab(), Gtk.Label(label="Kernel"))

        # Audio Tab
        notebook.append_page(self._create_audio_tab(), Gtk.Label(label="Audio"))

        # Network Tab
        notebook.append_page(self._create_network_tab(), Gtk.Label(label="Network"))

    def _create_info_tab(self) -> Gtk.Widget:
        """Create profile information tab"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(24)
        box.set_margin_end(24)
        box.set_margin_top(24)
        box.set_margin_bottom(24)

        # Profile name
        name_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        name_label = Gtk.Label(label="Profile Name:")
        name_label.set_width_chars(20)
        name_label.set_xalign(0)
        self.name_entry = Gtk.Entry()
        self.name_entry.set_text(self.profile_data.get('name', ''))
        self.name_entry.set_hexpand(True)
        name_box.append(name_label)
        name_box.append(self.name_entry)
        box.append(name_box)

        # Profile description
        desc_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        desc_label = Gtk.Label(label="Description:")
        desc_label.set_width_chars(20)
        desc_label.set_xalign(0)
        desc_label.set_valign(Gtk.Align.START)
        self.desc_text = Gtk.TextView()
        self.desc_text.set_wrap_mode(Gtk.WrapMode.WORD)
        buffer = self.desc_text.get_buffer()
        buffer.set_text(self.profile_data.get('description', ''))
        desc_scroll = Gtk.ScrolledWindow()
        desc_scroll.set_child(self.desc_text)
        desc_scroll.set_min_content_height(100)
        desc_scroll.set_hexpand(True)
        desc_box.append(desc_label)
        desc_box.append(desc_scroll)
        box.append(desc_box)

        return box

    def _create_cpu_tab(self) -> Gtk.Widget:
        """Create CPU settings tab"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(24)
        box.set_margin_end(24)
        box.set_margin_top(24)
        box.set_margin_bottom(24)

        cpu_data = self.profile_data.get('cpu', {})

        # CPU Governor
        self._add_dropdown(box, "CPU Governor:", "cpu_governor",
                          ["performance", "schedutil", "powersave", "ondemand"],
                          cpu_data.get('governor', 'schedutil'))

        # Max C-State
        self._add_spinbutton(box, "Max C-State:", "cpu_max_cstate",
                            0, 10, cpu_data.get('max_cstate', 3))

        # Turbo Boost
        self._add_switch(box, "Turbo Boost:", "cpu_turbo_boost",
                        cpu_data.get('turbo_boost', True))

        # Core Isolation
        self._add_switch(box, "Core Isolation:", "cpu_core_isolation",
                        cpu_data.get('core_isolation', False))

        return box

    def _create_gpu_tab(self) -> Gtk.Widget:
        """Create GPU settings tab"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(24)
        box.set_margin_end(24)
        box.set_margin_top(24)
        box.set_margin_bottom(24)

        gpu_data = self.profile_data.get('gpu', {})

        # Power Mode
        self._add_dropdown(box, "Power Mode:", "gpu_power_mode",
                          ["Auto (0)", "Max Performance (1)", "Quiet (2)"],
                          f"{gpu_data.get('power_mode', 0)}")

        # GPU Overclock
        self._add_spinbutton(box, "GPU Overclock (MHz):", "gpu_overclock_gpu",
                            -200, 200, gpu_data.get('overclock_gpu', 0))

        # Memory Overclock
        self._add_spinbutton(box, "Memory Overclock (MHz):", "gpu_overclock_mem",
                            -200, 800, gpu_data.get('overclock_mem', 0))

        # Fan Mode
        self._add_dropdown(box, "Fan Mode:", "gpu_fan_mode",
                          ["auto", "manual"],
                          gpu_data.get('fan_mode', 'auto'))

        return box

    def _create_memory_tab(self) -> Gtk.Widget:
        """Create memory settings tab"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(24)
        box.set_margin_end(24)
        box.set_margin_top(24)
        box.set_margin_bottom(24)

        mem_data = self.profile_data.get('memory', {})

        # Swappiness
        self._add_spinbutton(box, "Swappiness:", "mem_swappiness",
                            0, 100, mem_data.get('swappiness', 10))

        # ZRAM Enabled
        self._add_switch(box, "ZRAM Enabled:", "mem_zram_enabled",
                        mem_data.get('zram_enabled', True))

        # ZRAM Size
        self._add_spinbutton(box, "ZRAM Size (GB):", "mem_zram_size_gb",
                            1, 32, mem_data.get('zram_size_gb', 8))

        # Huge Pages
        self._add_switch(box, "Huge Pages:", "mem_huge_pages",
                        mem_data.get('huge_pages', False))

        return box

    def _create_kernel_tab(self) -> Gtk.Widget:
        """Create kernel settings tab"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(24)
        box.set_margin_end(24)
        box.set_margin_top(24)
        box.set_margin_bottom(24)

        kernel_data = self.profile_data.get('kernel', {})

        # Mitigations
        self._add_dropdown(box, "Security Mitigations:", "kernel_mitigations",
                          ["auto", "off", "auto,nosmt"],
                          kernel_data.get('mitigations', 'auto'))

        # Scheduler
        self._add_dropdown(box, "Scheduler:", "kernel_scheduler",
                          ["schedutil", "performance", "powersave"],
                          kernel_data.get('scheduler', 'schedutil'))

        # Preemption
        self._add_dropdown(box, "Preemption:", "kernel_preempt",
                          ["none", "voluntary", "full"],
                          kernel_data.get('preempt', 'voluntary'))

        return box

    def _create_audio_tab(self) -> Gtk.Widget:
        """Create audio settings tab"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(24)
        box.set_margin_end(24)
        box.set_margin_top(24)
        box.set_margin_bottom(24)

        audio_data = self.profile_data.get('audio', {})

        # Quantum
        self._add_spinbutton(box, "PipeWire Quantum:", "audio_quantum",
                            64, 8192, audio_data.get('quantum', 1024))

        # Latency
        self._add_dropdown(box, "Latency Mode:", "audio_latency",
                          ["low", "balanced", "high"],
                          audio_data.get('latency', 'balanced'))

        return box

    def _create_network_tab(self) -> Gtk.Widget:
        """Create network settings tab"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(24)
        box.set_margin_end(24)
        box.set_margin_top(24)
        box.set_margin_bottom(24)

        net_data = self.profile_data.get('network', {})

        # Congestion Control
        self._add_dropdown(box, "Congestion Control:", "net_congestion_control",
                          ["bbr", "cubic", "reno"],
                          net_data.get('congestion_control', 'bbr'))

        # Disable IPv6
        self._add_switch(box, "Disable IPv6:", "net_disable_ipv6",
                        net_data.get('disable_ipv6', False))

        return box

    def _add_dropdown(self, parent: Gtk.Box, label: str, key: str,
                     options: List[str], default: str):
        """Add a dropdown selector"""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        label_widget = Gtk.Label(label=label)
        label_widget.set_width_chars(25)
        label_widget.set_xalign(0)

        dropdown = Gtk.DropDown.new_from_strings(options)
        # Find and set default value
        for i, opt in enumerate(options):
            if default in opt or opt in str(default):
                dropdown.set_selected(i)
                break

        dropdown.set_hexpand(True)
        setattr(self, key, dropdown)

        row.append(label_widget)
        row.append(dropdown)
        parent.append(row)

    def _add_spinbutton(self, parent: Gtk.Box, label: str, key: str,
                       min_val: float, max_val: float, default: float):
        """Add a spin button"""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        label_widget = Gtk.Label(label=label)
        label_widget.set_width_chars(25)
        label_widget.set_xalign(0)

        adjustment = Gtk.Adjustment(value=default, lower=min_val, upper=max_val,
                                   step_increment=1, page_increment=10)
        spinbutton = Gtk.SpinButton(adjustment=adjustment, climb_rate=1, digits=0)
        spinbutton.set_hexpand(True)
        setattr(self, key, spinbutton)

        row.append(label_widget)
        row.append(spinbutton)
        parent.append(row)

    def _add_switch(self, parent: Gtk.Box, label: str, key: str, default: bool):
        """Add a toggle switch"""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        label_widget = Gtk.Label(label=label)
        label_widget.set_width_chars(25)
        label_widget.set_xalign(0)

        switch = Gtk.Switch()
        switch.set_active(default)
        switch.set_halign(Gtk.Align.START)
        setattr(self, key, switch)

        row.append(label_widget)
        row.append(switch)
        parent.append(row)

    def _on_save_clicked(self, button):
        """Save profile button clicked"""
        profile = self._collect_profile_data()

        # Save to file
        config_dir = Path.home() / '.config' / 'bazzite-optimizer' / 'custom-profiles'
        config_dir.mkdir(parents=True, exist_ok=True)

        profile_name = profile['name'].lower().replace(' ', '-')
        profile_file = config_dir / f"{profile_name}.json"

        try:
            with open(profile_file, 'w') as f:
                json.dump(profile, f, indent=2)

            self.logger.info(f"Profile saved: {profile_file}")
            self.close()

        except Exception as e:
            self.logger.error(f"Failed to save profile: {e}")
            self._show_error_dialog(f"Failed to save profile: {e}")

    def _collect_profile_data(self) -> Dict[str, Any]:
        """Collect all profile data from UI"""
        # Get text buffer content
        buffer = self.desc_text.get_buffer()
        description = buffer.get_text(buffer.get_start_iter(),
                                     buffer.get_end_iter(), False)

        return {
            "name": self.name_entry.get_text(),
            "description": description,
            "cpu": {
                "governor": self._get_dropdown_value(self.cpu_governor),
                "max_cstate": int(self.cpu_max_cstate.get_value()),
                "turbo_boost": self.cpu_turbo_boost.get_active(),
                "core_isolation": self.cpu_core_isolation.get_active()
            },
            "gpu": {
                "power_mode": self._extract_number(self._get_dropdown_value(self.gpu_power_mode)),
                "overclock_gpu": int(self.gpu_overclock_gpu.get_value()),
                "overclock_mem": int(self.gpu_overclock_mem.get_value()),
                "fan_mode": self._get_dropdown_value(self.gpu_fan_mode)
            },
            "memory": {
                "swappiness": int(self.mem_swappiness.get_value()),
                "zram_enabled": self.mem_zram_enabled.get_active(),
                "zram_size_gb": int(self.mem_zram_size_gb.get_value()),
                "huge_pages": self.mem_huge_pages.get_active()
            },
            "kernel": {
                "mitigations": self._get_dropdown_value(self.kernel_mitigations),
                "scheduler": self._get_dropdown_value(self.kernel_scheduler),
                "preempt": self._get_dropdown_value(self.kernel_preempt)
            },
            "audio": {
                "quantum": int(self.audio_quantum.get_value()),
                "latency": self._get_dropdown_value(self.audio_latency)
            },
            "network": {
                "congestion_control": self._get_dropdown_value(self.net_congestion_control),
                "disable_ipv6": self.net_disable_ipv6.get_active()
            }
        }

    def _get_dropdown_value(self, dropdown: Gtk.DropDown) -> str:
        """Get selected value from dropdown"""
        selected = dropdown.get_selected()
        model = dropdown.get_model()
        if model and selected < model.get_n_items():
            return model.get_item(selected).get_string()
        return ""

    def _extract_number(self, text: str) -> int:
        """Extract number from text like 'Auto (0)'"""
        import re
        match = re.search(r'\((\d+)\)', text)
        return int(match.group(1)) if match else 0

    def _on_cancel_clicked(self, button):
        """Cancel button clicked"""
        self.close()

    def _show_error_dialog(self, message: str):
        """Show error dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error"
        )
        dialog.set_property("secondary-text", message)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()
