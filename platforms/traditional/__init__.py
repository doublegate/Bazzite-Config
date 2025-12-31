# TEAM_005: Traditional system implementations (GRUB + dnf/apt)
"""Implementations for traditional Linux distributions (Fedora, Ultramarine, Ubuntu)."""

from .grub import GrubKernelParams
from .rpm import DnfPackageManager

__all__ = ["GrubKernelParams", "DnfPackageManager"]
