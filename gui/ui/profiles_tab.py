#!/usr/bin/env python3
"""
Profiles Tab for Bazzite Optimizer GUI

Visual profile selection and management interface.
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from models.profile_model import ProfileType


class ProfilesTab(Gtk.Box):
    """Profiles tab for selecting gaming profiles"""

    def __init__(self, profile_model, backend):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_start(20)
        self.set_margin_end(20)
        self.set_margin_top(20)
        self.set_margin_bottom(20)

        self.profile_model = profile_model
        self.backend = backend

        self._create_ui()

    def _create_ui(self):
        """Create profiles UI"""
        # Title
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>Gaming Profiles</span>")
        title.set_xalign(0)
        self.append(title)

        subtitle = Gtk.Label(label="Select a gaming profile to optimize your system")
        subtitle.set_xalign(0)
        subtitle.set_margin_bottom(10)
        self.append(subtitle)

        # Profile cards grid
        grid = Gtk.Grid()
        grid.set_column_spacing(15)
        grid.set_row_spacing(15)
        grid.set_column_homogeneous(True)
        self.append(grid)

        # Create profile cards
        profiles = self.profile_model.get_all_profiles()
        for idx, profile in enumerate(profiles):
            card = self._create_profile_card(profile)
            row = idx // 2
            col = idx % 2
            grid.attach(card, col, row, 1, 1)

        # Details section
        self.details_frame = Gtk.Frame(label="Profile Details")
        self.details_frame.set_margin_top(20)
        details_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        details_box.set_margin_start(10)
        details_box.set_margin_end(10)
        details_box.set_margin_top(10)
        details_box.set_margin_bottom(10)
        self.details_frame.set_child(details_box)
        self.append(self.details_frame)

        self.details_label = Gtk.Label(label="Select a profile to view details")
        self.details_label.set_xalign(0)
        self.details_label.set_wrap(True)
        details_box.append(self.details_label)

        self.features_label = Gtk.Label()
        self.features_label.set_xalign(0)
        self.features_label.set_wrap(True)
        details_box.append(self.features_label)

        # Action buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_margin_top(10)
        self.append(button_box)

        self.apply_profile_button = Gtk.Button(label="Apply Selected Profile")
        self.apply_profile_button.connect("clicked", self._on_apply_profile)
        self.apply_profile_button.set_sensitive(False)
        button_box.append(self.apply_profile_button)

        benchmark_button = Gtk.Button(label="Run Benchmark")
        benchmark_button.connect("clicked", self._on_benchmark)
        button_box.append(benchmark_button)

        self.selected_profile = None

    def _create_profile_card(self, profile):
        """Create a profile card"""
        frame = Gtk.Frame()
        frame.add_css_class("profile-card")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_start(15)
        box.set_margin_end(15)
        box.set_margin_top(15)
        box.set_margin_bottom(15)
        frame.set_child(box)

        # Icon and name
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.append(header_box)

        icon_label = Gtk.Label()
        icon_label.set_markup(f"<span size='xx-large'>{profile.icon_name}</span>")
        header_box.append(icon_label)

        name_label = Gtk.Label()
        name_label.set_markup(f"<span size='large' weight='bold'>{profile.display_name}</span>")
        name_label.set_xalign(0)
        name_label.set_hexpand(True)
        header_box.append(name_label)

        # Description
        desc_label = Gtk.Label(label=profile.description)
        desc_label.set_xalign(0)
        desc_label.set_wrap(True)
        desc_label.set_max_width_chars(40)
        box.append(desc_label)

        # Features (first 3)
        features_text = "\n".join(f"• {feat}" for feat in profile.features[:3])
        features_label = Gtk.Label(label=features_text)
        features_label.set_xalign(0)
        features_label.set_margin_top(5)
        box.append(features_label)

        # Select button
        select_button = Gtk.Button(label="Select")
        select_button.connect("clicked", self._on_profile_selected, profile)
        box.append(select_button)

        return frame

    def _on_profile_selected(self, button, profile):
        """Handle profile selection"""
        self.selected_profile = profile

        # Update details
        self.details_label.set_markup(f"<b>{profile.display_name}</b>\n\n{profile.description}")

        features_text = "<b>Features:</b>\n" + "\n".join(f"• {feat}" for feat in profile.features)
        self.features_label.set_markup(features_text)

        recommended = ", ".join(profile.recommended_for)
        self.features_label.set_label(
            self.features_label.get_label() + f"\n\n<b>Recommended for:</b> {recommended}"
        )

        self.apply_profile_button.set_sensitive(True)

    def _on_apply_profile(self, button):
        """Apply selected profile"""
        if not self.selected_profile or not self.backend:
            return

        # Show confirmation dialog
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Apply {self.selected_profile.display_name} Profile?"
        )
        dialog.set_secondary_text(
            f"This will optimize your system for:\n{', '.join(self.selected_profile.recommended_for)}"
        )
        dialog.connect("response", self._on_apply_confirm)
        dialog.present()

    def _on_apply_confirm(self, dialog, response):
        """Handle apply confirmation"""
        dialog.destroy()
        if response == Gtk.ResponseType.YES and self.backend:
            profile_name = self.selected_profile.name

            # Show progress
            progress_dialog = Gtk.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.NONE,
                text="Applying Profile"
            )
            progress_dialog.set_secondary_text(f"Applying {self.selected_profile.display_name} profile...")
            progress_dialog.present()

            def callback(returncode, stdout, stderr):
                GLib.idle_add(self._on_apply_complete, progress_dialog, returncode, stdout, stderr)

            self.backend.apply_profile(profile_name, callback)

    def _on_apply_complete(self, progress_dialog, returncode, stdout, stderr):
        """Handle profile apply completion"""
        progress_dialog.destroy()

        if returncode == 0:
            success_dialog = Gtk.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Profile Applied Successfully"
            )
            success_dialog.set_secondary_text(
                f"{self.selected_profile.display_name} profile has been applied.\n"
                "Your system has been optimized for peak performance."
            )
            success_dialog.connect("response", lambda d, r: d.destroy())
            success_dialog.present()
        else:
            error_dialog = Gtk.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Failed to Apply Profile"
            )
            error_dialog.set_secondary_text(f"Error: {stderr}")
            error_dialog.connect("response", lambda d, r: d.destroy())
            error_dialog.present()

        return False

    def _on_benchmark(self, button):
        """Run benchmark"""
        if not self.backend:
            return

        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Benchmark Starting"
        )
        dialog.set_secondary_text(
            "Benchmark will run in the background.\n"
            "This may take several minutes."
        )
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()

        def callback(returncode, stdout, stderr):
            GLib.idle_add(self._show_benchmark_result, returncode, stdout)

        self.backend.run_benchmark(callback)

    def _show_benchmark_result(self, returncode, stdout):
        """Show benchmark results"""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Benchmark Complete"
        )

        if returncode == 0:
            dialog.set_secondary_text(f"Benchmark results:\n\n{stdout[:500]}")
        else:
            dialog.set_secondary_text("Benchmark failed or was cancelled.")

        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()
        return False
