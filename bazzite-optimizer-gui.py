#!/usr/bin/env python3
"""
Bazzite Optimizer GUI - Main Application Entry Point

GTK4-based graphical interface for the Bazzite Gaming Optimization Suite.
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio
import sys
from pathlib import Path

# Add GUI modules to path
sys.path.insert(0, str(Path(__file__).parent / 'gui'))

from ui.main_window import MainWindow
from models.system_state import SystemState
from models.profile_model import ProfileModel
from models.metrics_model import MetricsModel


class BazziteOptimizerApp(Gtk.Application):
    """Main GTK4 application"""

    def __init__(self):
        super().__init__(
            application_id='org.bazzite.optimizer',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.window = None

        # Initialize models
        self.system_state = SystemState()
        self.profile_model = ProfileModel()
        self.metrics_model = MetricsModel()

    def do_activate(self):
        """Activate the application"""
        if not self.window:
            self.window = MainWindow(
                application=self,
                system_state=self.system_state,
                profile_model=self.profile_model,
                metrics_model=self.metrics_model
            )

        self.window.present()

    def do_startup(self):
        """Application startup"""
        Gtk.Application.do_startup(self)

        # Set up actions
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda *args: self.quit())
        self.add_action(quit_action)

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.show_about_dialog)
        self.add_action(about_action)

    def show_about_dialog(self, action, param):
        """Show about dialog"""
        about = Gtk.AboutDialog(transient_for=self.window, modal=True)
        about.set_program_name("Bazzite Gaming Optimizer")
        about.set_version("1.1.0")
        about.set_comments("Professional gaming system optimization for Bazzite Linux")
        about.set_website("https://github.com/doublegate/Bazzite-Config")
        about.set_website_label("GitHub Repository")
        about.set_license_type(Gtk.License.MIT_X11)
        about.set_authors(["Bazzite Optimizer Contributors"])
        about.present()


def main():
    """Main entry point"""
    app = BazziteOptimizerApp()
    return app.run(sys.argv)


if __name__ == '__main__':
    sys.exit(main())
