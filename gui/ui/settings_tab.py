#!/usr/bin/env python3
"""
Settings Tab for Bazzite Optimizer GUI

Application configuration and preferences.
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


class SettingsTab(Gtk.Box):
    """Settings tab for application configuration"""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_start(20)
        self.set_margin_end(20)
        self.set_margin_top(20)
        self.set_margin_bottom(20)

        self._create_ui()

    def _create_ui(self):
        """Create settings UI"""
        # Title
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>Settings & Configuration</span>")
        title.set_xalign(0)
        self.append(title)

        # General Settings
        general_frame = Gtk.Frame(label="General")
        general_frame.set_margin_top(10)
        general_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        general_box.set_margin_start(10)
        general_box.set_margin_end(10)
        general_box.set_margin_top(10)
        general_box.set_margin_bottom(10)
        general_frame.set_child(general_box)
        self.append(general_frame)

        # Auto-start option
        autostart_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        general_box.append(autostart_box)

        autostart_label = Gtk.Label(label="Start optimizer GUI on login")
        autostart_label.set_xalign(0)
        autostart_label.set_hexpand(True)
        autostart_box.append(autostart_label)

        autostart_switch = Gtk.Switch()
        autostart_box.append(autostart_switch)

        # Notifications
        notify_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        general_box.append(notify_box)

        notify_label = Gtk.Label(label="Show notifications for optimization events")
        notify_label.set_xalign(0)
        notify_label.set_hexpand(True)
        notify_box.append(notify_label)

        notify_switch = Gtk.Switch()
        notify_switch.set_active(True)
        notify_box.append(notify_switch)

        # Minimize to tray
        tray_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        general_box.append(tray_box)

        tray_label = Gtk.Label(label="Minimize to system tray")
        tray_label.set_xalign(0)
        tray_label.set_hexpand(True)
        tray_box.append(tray_label)

        tray_switch = Gtk.Switch()
        tray_switch.set_active(True)
        tray_box.append(tray_switch)

        # Optimization Settings
        opt_frame = Gtk.Frame(label="Optimization")
        opt_frame.set_margin_top(10)
        opt_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        opt_box.set_margin_start(10)
        opt_box.set_margin_end(10)
        opt_box.set_margin_top(10)
        opt_box.set_margin_bottom(10)
        opt_frame.set_child(opt_box)
        self.append(opt_frame)

        # Apply profile on startup
        startup_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        opt_box.append(startup_box)

        startup_label = Gtk.Label(label="Apply profile on startup")
        startup_label.set_xalign(0)
        startup_label.set_hexpand(True)
        startup_box.append(startup_label)

        startup_switch = Gtk.Switch()
        startup_box.append(startup_switch)

        # Auto profile switching
        auto_profile_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        opt_box.append(auto_profile_box)

        auto_profile_label = Gtk.Label(label="Enable automatic profile switching")
        auto_profile_label.set_xalign(0)
        auto_profile_label.set_hexpand(True)
        auto_profile_box.append(auto_profile_label)

        auto_profile_switch = Gtk.Switch()
        auto_profile_box.append(auto_profile_switch)

        # Default profile
        default_profile_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        opt_box.append(default_profile_box)

        default_profile_label = Gtk.Label(label="Default profile:")
        default_profile_label.set_xalign(0)
        default_profile_box.append(default_profile_label)

        default_profile_combo = Gtk.ComboBoxText()
        default_profile_combo.append_text("Competitive")
        default_profile_combo.append_text("Balanced")
        default_profile_combo.append_text("Streaming")
        default_profile_combo.append_text("Creative")
        default_profile_combo.set_active(1)  # Balanced
        default_profile_box.append(default_profile_combo)

        # Advanced Settings
        advanced_frame = Gtk.Frame(label="Advanced")
        advanced_frame.set_margin_top(10)
        advanced_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        advanced_box.set_margin_start(10)
        advanced_box.set_margin_end(10)
        advanced_box.set_margin_top(10)
        advanced_box.set_margin_bottom(10)
        advanced_frame.set_child(advanced_box)
        self.append(advanced_frame)

        # Action buttons
        advanced_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        advanced_box.append(advanced_buttons)

        view_logs_btn = Gtk.Button(label="View Logs")
        view_logs_btn.connect("clicked", self._on_view_logs)
        advanced_buttons.append(view_logs_btn)

        backup_btn = Gtk.Button(label="Backup Config")
        backup_btn.connect("clicked", self._on_backup_config)
        advanced_buttons.append(backup_btn)

        restore_btn = Gtk.Button(label="Restore Config")
        restore_btn.connect("clicked", self._on_restore_config)
        advanced_buttons.append(restore_btn)

        export_btn = Gtk.Button(label="Export System Info")
        export_btn.connect("clicked", self._on_export_info)
        advanced_buttons.append(export_btn)

        # Reset to defaults
        reset_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        reset_box.set_margin_top(10)
        advanced_box.append(reset_box)

        reset_btn = Gtk.Button(label="Reset to Defaults")
        reset_btn.add_css_class("destructive-action")
        reset_btn.connect("clicked", self._on_reset_defaults)
        reset_box.append(reset_btn)

        # About Section
        about_frame = Gtk.Frame(label="About")
        about_frame.set_margin_top(10)
        about_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        about_box.set_margin_start(10)
        about_box.set_margin_end(10)
        about_box.set_margin_top(10)
        about_box.set_margin_bottom(10)
        about_frame.set_child(about_box)
        self.append(about_frame)

        # Version info
        version_label = Gtk.Label()
        version_label.set_markup("<b>Bazzite Gaming Optimizer</b>\nVersion 1.1.0")
        version_label.set_xalign(0)
        about_box.append(version_label)

        # Links
        links_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        links_box.set_margin_top(5)
        about_box.append(links_box)

        check_updates_btn = Gtk.Button(label="Check for Updates")
        links_box.append(check_updates_btn)

        docs_btn = Gtk.Button(label="Documentation")
        links_box.append(docs_btn)

        github_btn = Gtk.Button(label="GitHub")
        links_box.append(github_btn)

    def _on_view_logs(self, button):
        """View logs"""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="View Logs"
        )
        dialog.set_secondary_text("Log viewer not yet implemented.\nCheck /var/log/bazzite-optimizer.log manually.")
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()

    def _on_backup_config(self, button):
        """Backup configuration"""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Backup Created"
        )
        dialog.set_secondary_text("Configuration backup feature coming soon.")
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()

    def _on_restore_config(self, button):
        """Restore configuration"""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Restore Configuration"
        )
        dialog.set_secondary_text("Configuration restore feature coming soon.")
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()

    def _on_export_info(self, button):
        """Export system information"""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Export System Info"
        )
        dialog.set_secondary_text("System information export feature coming soon.")
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()

    def _on_reset_defaults(self, button):
        """Reset to default settings"""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Reset to Defaults?"
        )
        dialog.set_secondary_text("This will reset all application settings to defaults.")
        dialog.connect("response", self._on_reset_confirm)
        dialog.present()

    def _on_reset_confirm(self, dialog, response):
        """Handle reset confirmation"""
        dialog.destroy()
        if response == Gtk.ResponseType.YES:
            info_dialog = Gtk.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Settings Reset"
            )
            info_dialog.set_secondary_text("Settings have been reset to defaults.")
            info_dialog.connect("response", lambda d, r: d.destroy())
            info_dialog.present()
