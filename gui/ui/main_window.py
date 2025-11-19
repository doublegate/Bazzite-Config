#!/usr/bin/env python3
"""
Main Window for Bazzite Optimizer GUI

Contains the main tabbed interface and overall application layout.
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio
from pathlib import Path
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.dashboard_tab import DashboardTab
from ui.profiles_tab import ProfilesTab
from ui.monitoring_tab import MonitoringTab
from ui.quickfix_tab import QuickFixTab
from ui.settings_tab import SettingsTab
from controllers.optimizer_backend import OptimizerBackend
from controllers.monitor_controller import MonitorController
from models.system_state import SystemStateLoader


class MainWindow(Gtk.ApplicationWindow):
    """Main application window with tabbed interface"""

    def __init__(self, application, system_state, profile_model, metrics_model):
        super().__init__(application=application)

        self.system_state = system_state
        self.profile_model = profile_model
        self.metrics_model = metrics_model

        # Initialize backend
        try:
            self.backend = OptimizerBackend()
        except FileNotFoundError as e:
            self.show_error_dialog("Backend Not Found", str(e))
            self.backend = None

        # Initialize controllers
        self.monitor_controller = MonitorController(metrics_model)

        # Configure window
        self.set_title("Bazzite Gaming Optimizer")
        self.set_default_size(900, 700)

        # Create UI
        self._create_ui()

        # Load initial data
        self._load_system_data()

    def _create_ui(self):
        """Create the main UI layout"""
        # Main vertical box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(main_box)

        # Header bar
        header_bar = Gtk.HeaderBar()
        self.set_titlebar(header_bar)

        # Menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        header_bar.pack_end(menu_button)

        # Create menu
        menu = Gio.Menu()
        menu.append("About", "app.about")
        menu.append("Quit", "app.quit")
        menu_button.set_menu_model(menu)

        # Create notebook (tabs)
        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.TOP)
        main_box.append(self.notebook)

        # Create tabs
        self.dashboard_tab = DashboardTab(self.system_state, self.profile_model, self.backend)
        self.profiles_tab = ProfilesTab(self.profile_model, self.backend)
        self.monitoring_tab = MonitoringTab(self.metrics_model, self.monitor_controller)
        self.quickfix_tab = QuickFixTab(self.backend)
        self.settings_tab = SettingsTab()

        # Add tabs to notebook
        self.notebook.append_page(
            self.dashboard_tab,
            Gtk.Label(label="Dashboard")
        )
        self.notebook.append_page(
            self.profiles_tab,
            Gtk.Label(label="Profiles")
        )
        self.notebook.append_page(
            self.monitoring_tab,
            Gtk.Label(label="Monitoring")
        )
        self.notebook.append_page(
            self.quickfix_tab,
            Gtk.Label(label="Quick Fixes")
        )
        self.notebook.append_page(
            self.settings_tab,
            Gtk.Label(label="Settings")
        )

        # Status bar
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        status_box.set_margin_start(10)
        status_box.set_margin_end(10)
        status_box.set_margin_top(5)
        status_box.set_margin_bottom(5)

        self.status_label = Gtk.Label(label="Status: Ready")
        self.status_label.set_xalign(0)
        status_box.append(self.status_label)

        # Spacer
        spacer = Gtk.Label()
        spacer.set_hexpand(True)
        status_box.append(spacer)

        self.gaming_mode_label = Gtk.Label(label="Gaming Mode: Disabled")
        status_box.append(self.gaming_mode_label)

        main_box.append(status_box)

        # Connect signals
        self.notebook.connect("switch-page", self._on_tab_switched)

    def _load_system_data(self):
        """Load initial system data"""
        # Load hardware info in background
        def load_worker():
            hardware = SystemStateLoader.load_hardware_info()
            optimization = SystemStateLoader.load_optimization_status()

            # Update UI in main thread
            GLib.idle_add(self._update_system_data, hardware, optimization)

        import threading
        threading.Thread(target=load_worker, daemon=True).start()

    def _update_system_data(self, hardware, optimization):
        """Update system data in UI (called in main thread)"""
        self.system_state.update_hardware_info(hardware)
        self.system_state.update_optimization_status(optimization)

        # Update status bar
        if optimization.gaming_mode_enabled:
            self.gaming_mode_label.set_text("Gaming Mode: ● Enabled")
        else:
            self.gaming_mode_label.set_text("Gaming Mode: ○ Disabled")

        if optimization.active_profile != "None":
            self.status_label.set_text(f"Status: {optimization.active_profile.capitalize()} Profile Active")
        else:
            self.status_label.set_text("Status: No Profile Active")

        return False  # Don't repeat

    def _on_tab_switched(self, notebook, page, page_num):
        """Handle tab switch events"""
        # Stop monitoring when leaving monitoring tab
        if hasattr(self, 'monitoring_tab'):
            if page_num == 2:  # Monitoring tab
                self.monitoring_tab.start_monitoring()
            else:
                self.monitoring_tab.stop_monitoring()

    def show_error_dialog(self, title, message):
        """Show error dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.set_secondary_text(message)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()

    def show_info_dialog(self, title, message):
        """Show info dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.set_secondary_text(message)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()

    def update_status(self, message):
        """Update status bar message"""
        self.status_label.set_text(f"Status: {message}")
