#!/usr/bin/env python3
"""
Quick Fix Tab for Bazzite Optimizer GUI

One-click solutions for common issues.
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from controllers.optimizer_backend import QuickFixBackend


class QuickFixTab(Gtk.Box):
    """Quick fixes tab for common gaming issues"""

    def __init__(self, backend):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_start(20)
        self.set_margin_end(20)
        self.set_margin_top(20)
        self.set_margin_bottom(20)

        self.backend = backend
        self.quickfix_backend = QuickFixBackend()

        self._create_ui()

    def _create_ui(self):
        """Create quick fix UI"""
        # Title
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>Quick System Fixes</span>")
        title.set_xalign(0)
        self.append(title)

        subtitle = Gtk.Label(label="One-click solutions for common gaming issues")
        subtitle.set_xalign(0)
        subtitle.set_margin_bottom(10)
        self.append(subtitle)

        # Fix buttons grid
        grid = Gtk.Grid()
        grid.set_column_spacing(15)
        grid.set_row_spacing(15)
        grid.set_column_homogeneous(True)
        self.append(grid)

        # Steam Fix
        steam_fix = self._create_fix_card(
            "🎮 Fix Steam",
            "Restart Steam client and clear cache",
            "Fixes Steam client freezing, login issues, and download problems",
            self._on_fix_steam
        )
        grid.attach(steam_fix, 0, 0, 1, 1)

        # Audio Fix
        audio_fix = self._create_fix_card(
            "🔊 Fix Audio",
            "Restart audio services",
            "Fixes audio crackling, no sound issues, and audio device detection",
            self._on_fix_audio
        )
        grid.attach(audio_fix, 1, 0, 1, 1)

        # GPU Reset
        gpu_reset = self._create_fix_card(
            "🎨 Reset GPU",
            "Reset GPU to default settings",
            "Resets GPU overclocking and fixes display issues",
            self._on_reset_gpu
        )
        grid.attach(gpu_reset, 0, 1, 1, 1)

        # Clear Caches
        clear_caches = self._create_fix_card(
            "🧹 Clear Caches",
            "Clean system caches",
            "Frees up disk space and can resolve various performance issues",
            self._on_clear_caches
        )
        grid.attach(clear_caches, 1, 1, 1, 1)

        # Restart Services
        restart_services = self._create_fix_card(
            "🔄 Restart Gaming Services",
            "Restart system76-scheduler and related services",
            "Fixes game prioritization and system responsiveness issues",
            self._on_restart_services
        )
        grid.attach(restart_services, 0, 2, 2, 1)

        # Recent fixes log
        log_frame = Gtk.Frame(label="Recent Fixes")
        log_frame.set_margin_top(20)
        self.append(log_frame)

        log_scroll = Gtk.ScrolledWindow()
        log_scroll.set_min_content_height(150)
        log_scroll.set_vexpand(True)
        log_frame.set_child(log_scroll)

        self.log_textview = Gtk.TextView()
        self.log_textview.set_editable(False)
        self.log_textview.set_cursor_visible(False)
        self.log_textview.set_margin_start(10)
        self.log_textview.set_margin_end(10)
        self.log_textview.set_margin_top(10)
        self.log_textview.set_margin_bottom(10)
        log_scroll.set_child(self.log_textview)

        self.log_buffer = self.log_textview.get_buffer()
        self._log_message("Ready. Select a fix to apply.")

    def _create_fix_card(self, title, subtitle, description, callback):
        """Create a fix card"""
        frame = Gtk.Frame()

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_start(15)
        box.set_margin_end(15)
        box.set_margin_top(15)
        box.set_margin_bottom(15)
        frame.set_child(box)

        # Title
        title_label = Gtk.Label()
        title_label.set_markup(f"<span size='large'><b>{title}</b></span>")
        title_label.set_xalign(0)
        box.append(title_label)

        # Subtitle
        subtitle_label = Gtk.Label(label=subtitle)
        subtitle_label.set_xalign(0)
        subtitle_label.add_css_class("dim-label")
        box.append(subtitle_label)

        # Description
        desc_label = Gtk.Label(label=description)
        desc_label.set_xalign(0)
        desc_label.set_wrap(True)
        desc_label.set_margin_top(5)
        box.append(desc_label)

        # Apply button
        apply_button = Gtk.Button(label="Apply Fix")
        apply_button.connect("clicked", callback)
        box.append(apply_button)

        return frame

    def _log_message(self, message):
        """Log a message to the log view"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        end_iter = self.log_buffer.get_end_iter()
        self.log_buffer.insert(end_iter, log_entry)

        # Auto-scroll to bottom
        mark = self.log_buffer.create_mark(None, end_iter, False)
        self.log_textview.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)

    def _show_progress(self, title, message):
        """Show progress dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.NONE,
            text=title
        )
        dialog.set_secondary_text(message)
        dialog.present()
        return dialog

    def _on_fix_steam(self, button):
        """Handle Steam fix"""
        self._log_message("Applying Steam fix...")
        dialog = self._show_progress("Fixing Steam", "Restarting Steam client...")

        def callback(returncode, stdout, stderr):
            GLib.idle_add(self._on_fix_complete, dialog, "Steam", returncode, stdout, stderr)

        self.quickfix_backend.fix_steam(callback)

    def _on_fix_audio(self, button):
        """Handle audio fix"""
        self._log_message("Applying audio fix...")
        dialog = self._show_progress("Fixing Audio", "Restarting audio services...")

        def callback(returncode, stdout, stderr):
            GLib.idle_add(self._on_fix_complete, dialog, "Audio", returncode, stdout, stderr)

        self.quickfix_backend.fix_audio(callback)

    def _on_reset_gpu(self, button):
        """Handle GPU reset"""
        self._log_message("Resetting GPU...")
        dialog = self._show_progress("Resetting GPU", "Restoring default GPU settings...")

        def callback(returncode, stdout, stderr):
            GLib.idle_add(self._on_fix_complete, dialog, "GPU", returncode, stdout, stderr)

        self.quickfix_backend.reset_gpu(callback)

    def _on_clear_caches(self, button):
        """Handle cache clearing"""
        # Show confirmation
        confirm_dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Clear System Caches?"
        )
        confirm_dialog.set_secondary_text(
            "This will clear user cache directories.\n"
            "You may need to re-login to some applications."
        )

        def on_response(dialog, response):
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                self._log_message("Clearing caches...")
                progress_dialog = self._show_progress("Clearing Caches", "Removing cached files...")

                def callback(returncode, stdout, stderr):
                    GLib.idle_add(
                        self._on_fix_complete, progress_dialog, "Cache", returncode, stdout, stderr
                    )

                self.quickfix_backend.clear_caches(callback)

        confirm_dialog.connect("response", on_response)
        confirm_dialog.present()

    def _on_restart_services(self, button):
        """Handle service restart"""
        self._log_message("Restarting gaming services...")
        dialog = self._show_progress("Restarting Services", "Restarting system services...")

        def callback(returncode, stdout, stderr):
            GLib.idle_add(self._on_fix_complete, dialog, "Services", returncode, stdout, stderr)

        self.quickfix_backend.restart_gaming_services(callback)

    def _on_fix_complete(self, dialog, fix_name, returncode, stdout, stderr):
        """Handle fix completion"""
        dialog.destroy()

        if returncode == 0:
            self._log_message(f"✓ {fix_name} fix applied successfully")
            success_dialog = Gtk.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text=f"{fix_name} Fix Applied"
            )
            success_dialog.set_secondary_text(f"{fix_name} has been fixed successfully.")
            success_dialog.connect("response", lambda d, r: d.destroy())
            success_dialog.present()
        else:
            self._log_message(f"✗ {fix_name} fix failed: {stderr[:100]}")
            error_dialog = Gtk.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=f"{fix_name} Fix Failed"
            )
            error_dialog.set_secondary_text(f"Error: {stderr[:200]}")
            error_dialog.connect("response", lambda d, r: d.destroy())
            error_dialog.present()

        return False
