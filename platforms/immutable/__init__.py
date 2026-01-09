# TEAM_005: Immutable system implementations (rpm-ostree based)
"""Implementations for immutable Linux distributions (Bazzite, Silverblue, Kinoite, Aurora)."""

from .rpm_ostree import RpmOstreeKernelParams, RpmOstreePackageManager

__all__ = ["RpmOstreeKernelParams", "RpmOstreePackageManager"]
