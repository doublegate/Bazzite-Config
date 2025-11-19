#!/usr/bin/env python3
"""
Dashboard Tab for Bazzite Optimizer GUI

Displays system overview and status information.
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class DashboardTab(Gtk.Box):
    """Dashboard tab showing system overview"""

    def __init__(self, system_state, profile_model, backend):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_start(20)
        self.set_margin_end(20)
        self.set_margin_top(20)
        self.set_margin_bottom(20)

        self.system_state = system_state
        self.profile_model = profile_model
        self.backend = backend

        # Attach as observer
        self.system_state.attach_observer(self)

        self._create_ui()

    def _create_ui(self):
        """Create dashboard UI"""
        # Title
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>System Overview</span>")
        title.set_xalign(0)
        self.append(title)

        # Hardware Information Section
        hardware_frame = Gtk.Frame(label="Hardware Information")
        hardware_frame.set_margin_top(10)
        hardware_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hardware_box.set_margin_start(10)
        hardware_box.set_margin_end(10)
        hardware_box.set_margin_top(10)
        hardware_box.set_margin_bottom(10)
        hardware_frame.set_child(hardware_box)
        self.append(hardware_frame)

        # CPU Card
        cpu_card = self._create_info_card("CPU")
        self.cpu_model_label = Gtk.Label(label="Loading...")
        self.cpu_model_label.set_xalign(0)
        cpu_card.append(self.cpu_model_label)
        self.cpu_cores_label = Gtk.Label(label="")
        self.cpu_cores_label.set_xalign(0)
        cpu_card.append(self.cpu_cores_label)
        hardware_box.append(cpu_card)

        # GPU Card
        gpu_card = self._create_info_card("GPU")
        self.gpu_model_label = Gtk.Label(label="Loading...")
        self.gpu_model_label.set_xalign(0)
        gpu_card.append(self.gpu_model_label)
        self.gpu_vram_label = Gtk.Label(label="")
        self.gpu_vram_label.set_xalign(0)
        gpu_card.append(self.gpu_vram_label)
        hardware_box.append(gpu_card)

        # Memory Card
        mem_card = self._create_info_card("Memory")
        self.ram_label = Gtk.Label(label="Loading...")
        self.ram_label.set_xalign(0)
        mem_card.append(self.ram_label)
        self.zram_label = Gtk.Label(label="")
        self.zram_label.set_xalign(0)
        mem_card.append(self.zram_label)
        hardware_box.append(mem_card)

        # Current Profile Section
        profile_frame = Gtk.Frame(label="Current Configuration")
        profile_frame.set_margin_top(10)
        profile_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        profile_box.set_margin_start(10)
        profile_box.set_margin_end(10)
        profile_box.set_margin_top(10)
        profile_box.set_margin_bottom(10)
        profile_frame.set_child(profile_box)
        self.append(profile_frame)

        # Profile info
        profile_info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        profile_box.append(profile_info_box)

        self.profile_label = Gtk.Label()
        self.profile_label.set_markup("<span size='large'>Profile: <b>None</b></span>")
        self.profile_label.set_xalign(0)
        self.profile_label.set_hexpand(True)
        profile_info_box.append(self.profile_label)

        # Gaming mode toggle
        gaming_mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        gaming_mode_label = Gtk.Label(label="Gaming Mode:")
        gaming_mode_box.append(gaming_mode_label)
        self.gaming_mode_switch = Gtk.Switch()
        self.gaming_mode_switch.connect("state-set", self._on_gaming_mode_toggled)
        gaming_mode_box.append(self.gaming_mode_switch)
        profile_info_box.append(gaming_mode_box)

        # Apply/Disable buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        profile_box.append(button_box)

        self.apply_button = Gtk.Button(label="Apply Current Profile")
        self.apply_button.connect("clicked", self._on_apply_clicked)
        self.apply_button.set_sensitive(False)
        button_box.append(self.apply_button)

        self.disable_button = Gtk.Button(label="Disable Optimizations")
        self.disable_button.connect("clicked", self._on_disable_clicked)
        button_box.append(self.disable_button)

        # System Health Section
        health_frame = Gtk.Frame(label="System Health")
        health_frame.set_margin_top(10)
        health_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        health_box.set_margin_start(10)
        health_box.set_margin_end(10)
        health_box.set_margin_top(10)
        health_box.set_margin_bottom(10)
        health_frame.set_child(health_box)
        self.append(health_frame)

        # Health progress bar
        health_label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        health_box.append(health_label_box)

        health_label = Gtk.Label(label="System Health:")
        health_label.set_xalign(0)
        health_label_box.append(health_label)

        self.health_percent_label = Gtk.Label(label="--")
        health_label_box.append(self.health_percent_label)

        self.health_progress = Gtk.ProgressBar()
        self.health_progress.set_fraction(0.85)
        health_box.append(self.health_progress)

        # Additional info
        info_grid = Gtk.Grid()
        info_grid.set_column_spacing(20)
        info_grid.set_row_spacing(5)
        health_box.append(info_grid)

        info_grid.attach(Gtk.Label(label="Last Optimized:", xalign=0), 0, 0, 1, 1)
        self.last_optimized_label = Gtk.Label(label="Never", xalign=0)
        info_grid.attach(self.last_optimized_label, 1, 0, 1, 1)

        info_grid.attach(Gtk.Label(label="Performance:", xalign=0), 0, 1, 1, 1)
        self.performance_label = Gtk.Label(label="--", xalign=0)
        info_grid.attach(self.performance_label, 1, 1, 1, 1)

        info_grid.attach(Gtk.Label(label="Kernel Version:", xalign=0), 0, 2, 1, 1)
        self.kernel_label = Gtk.Label(label="--", xalign=0)
        info_grid.attach(self.kernel_label, 1, 2, 1, 1)

    def _create_info_card(self, title):
        """Create an information card"""
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        card.set_hexpand(True)

        title_label = Gtk.Label()
        title_label.set_markup(f"<b>{title}</b>")
        title_label.set_xalign(0)
        card.append(title_label)

        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        card.append(separator)

        return card

    def on_state_changed(self, state):
        """Observer callback for state changes"""
        GLib.idle_add(self._update_ui_from_state, state)

    def _update_ui_from_state(self, state):
        """Update UI from system state (in main thread)"""
        # Update hardware info
        hw = state.hardware
        self.cpu_model_label.set_text(hw.cpu_model[:50])  # Truncate if too long
        self.cpu_cores_label.set_text(f"{hw.cpu_cores} cores")
        self.gpu_model_label.set_text(hw.gpu_model[:30])
        self.gpu_vram_label.set_text(hw.gpu_vram)
        self.ram_label.set_text(hw.total_ram)
        self.zram_label.set_text(f"ZRAM: {hw.zram_size}")
        self.kernel_label.set_text(hw.kernel_version)

        # Update optimization status
        opt = state.optimization
        if opt.active_profile and opt.active_profile != "None":
            self.profile_label.set_markup(
                f"<span size='large'>Profile: <b>{opt.active_profile.capitalize()}</b></span>"
            )
            self.apply_button.set_sensitive(True)
        else:
            self.profile_label.set_markup("<span size='large'>Profile: <b>None</b></span>")
            self.apply_button.set_sensitive(False)

        self.gaming_mode_switch.set_active(opt.gaming_mode_enabled)

        if opt.last_optimized:
            self.last_optimized_label.set_text(opt.last_optimized)

        self.performance_label.set_text(opt.performance_improvement)

        if opt.system_health > 0:
            self.health_progress.set_fraction(opt.system_health / 100.0)
            self.health_percent_label.set_text(f"{opt.system_health}%")

        return False

    def _on_gaming_mode_toggled(self, switch, state):
        """Handle gaming mode toggle"""
        self.system_state.set_gaming_mode(state)
        # TODO: Actually enable/disable gaming mode via backend
        return False

    def _on_apply_clicked(self, button):
        """Handle apply profile button click"""
        profile = self.system_state.optimization.active_profile
        if profile and profile != "None" and self.backend:
            # Show progress dialog
            self._show_progress_dialog("Applying Profile", f"Applying {profile} profile...")

            def callback(returncode, stdout, stderr):
                GLib.idle_add(self._on_apply_complete, returncode, stdout, stderr)

            self.backend.apply_profile(profile, callback)

    def _on_disable_clicked(self, button):
        """Handle disable optimizations button click"""
        # Show confirmation dialog
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Disable Optimizations?"
        )
        dialog.set_secondary_text("This will rollback all optimizations to default settings.")
        dialog.connect("response", self._on_disable_confirm)
        dialog.present()

    def _on_disable_confirm(self, dialog, response):
        """Handle disable confirmation"""
        dialog.destroy()
        if response == Gtk.ResponseType.YES and self.backend:
            self._show_progress_dialog("Disabling Optimizations", "Rolling back to defaults...")

            def callback(returncode, stdout, stderr):
                GLib.idle_add(self._on_rollback_complete, returncode, stdout, stderr)

            self.backend.rollback(callback)

    def _show_progress_dialog(self, title, message):
        """Show progress dialog"""
        self.progress_dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.NONE,
            text=title
        )
        self.progress_dialog.set_secondary_text(message)

        content_area = self.progress_dialog.get_message_area()
        progress_bar = Gtk.ProgressBar()
        progress_bar.set_pulse_step(0.1)
        content_area.append(progress_bar)

        # Pulse progress bar
        def pulse():
            if hasattr(self, 'progress_dialog') and self.progress_dialog:
                progress_bar.pulse()
                return True
            return False

        GLib.timeout_add(100, pulse)
        self.progress_dialog.present()

    def _on_apply_complete(self, returncode, stdout, stderr):
        """Handle profile apply completion"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.destroy()
            del self.progress_dialog

        if returncode == 0:
            self._show_success_dialog("Profile Applied", "Optimization profile applied successfully!")
        else:
            self._show_error_dialog("Apply Failed", f"Failed to apply profile:\n{stderr}")

        return False

    def _on_rollback_complete(self, returncode, stdout, stderr):
        """Handle rollback completion"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.destroy()
            del self.progress_dialog

        if returncode == 0:
            self._show_success_dialog("Rollback Complete", "Optimizations have been disabled.")
        else:
            self._show_error_dialog("Rollback Failed", f"Failed to rollback:\n{stderr}")

        return False

    def _show_success_dialog(self, title, message):
        """Show success dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.set_secondary_text(message)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()

    def _show_error_dialog(self, title, message):
        """Show error dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.set_secondary_text(message)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()
