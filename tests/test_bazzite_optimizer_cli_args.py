import importlib.util
import sys
from pathlib import Path


def load_bazzite_optimizer():
    spec = importlib.util.spec_from_file_location(
        "bazzite_optimizer", str(Path(__file__).resolve().parent.parent / "bazzite-optimizer.py")
    )
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def test_list_profiles_exits_early(monkeypatch, capsys):
    m = load_bazzite_optimizer()

    # Avoid heavy IO/commands during banner/system info and logging
    import logging
    monkeypatch.setattr(m, "setup_logging", lambda: logging.getLogger("noop"))
    monkeypatch.setattr(m, "get_system_info", lambda: {
        "kernel": "6.8.0",
        "kernel_version": (6, 8, 0),
        "distribution": "Bazzite",
        "cpu_model": "",
        "cpu_cores": 8,
        "cpu_threads": 16,
        "ram_gb": 32,
        "gpus": [],
        "network_interfaces": [],
        "nvme_devices": [],
        "free_disk_gb": 500,
        "form_factor": "desktop",
        "display_server": "wayland",
    })
    # Avoid IO during banner/system info
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_banner", lambda self: None)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_system_info", lambda self: None)

    # Run with --list-profiles
    monkeypatch.setenv("PYTHONUNBUFFERED", "1")
    monkeypatch.setattr(sys, "argv", ["bazzite-optimizer.py", "--list-profiles"])  # type: ignore[attr-defined]

    opt = m.BazziteGamingOptimizer()
    rc = opt.run()
    captured = capsys.readouterr().out

    assert rc == 0
    # Expect profile names in output
    assert "balanced" in captured
    assert "competitive" in captured


def test_verify_calls_printer_and_returns_zero(monkeypatch):
    m = load_bazzite_optimizer()

    # Avoid heavy IO/commands during banner/system info and logging
    import logging
    monkeypatch.setattr(m, "setup_logging", lambda: logging.getLogger("noop"))
    monkeypatch.setattr(m, "get_system_info", lambda: {
        "kernel": "6.8.0",
        "kernel_version": (6, 8, 0),
        "distribution": "Bazzite",
        "cpu_model": "",
        "cpu_cores": 8,
        "cpu_threads": 16,
        "ram_gb": 32,
        "gpus": [],
        "network_interfaces": [],
        "nvme_devices": [],
        "free_disk_gb": 500,
        "form_factor": "desktop",
        "display_server": "wayland",
    })
    # Avoid IO during banner/system info
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_banner", lambda self: None)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_system_info", lambda self: None)

    called = {"verify": False}

    def fake_print_verification_commands(self):
        called["verify"] = True

    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_verification_commands", fake_print_verification_commands)

    monkeypatch.setattr(sys, "argv", ["bazzite-optimizer.py", "--verify"])  # type: ignore[attr-defined]

    opt = m.BazziteGamingOptimizer()
    rc = opt.run()

    assert rc == 0
    assert called["verify"] is True


def test_validate_prints_results_and_returns_zero(monkeypatch, capsys):
    m = load_bazzite_optimizer()

    # Avoid heavy IO/commands during banner/system info and logging
    import logging
    monkeypatch.setattr(m, "setup_logging", lambda: logging.getLogger("noop"))
    monkeypatch.setattr(m, "get_system_info", lambda: {
        "kernel": "6.8.0",
        "kernel_version": (6, 8, 0),
        "distribution": "Bazzite",
        "cpu_model": "",
        "cpu_cores": 8,
        "cpu_threads": 16,
        "ram_gb": 32,
        "gpus": [],
        "network_interfaces": [],
        "nvme_devices": [],
        "free_disk_gb": 500,
        "form_factor": "desktop",
        "display_server": "wayland",
    })
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_banner", lambda self: None)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_system_info", lambda self: None)

    # Stub validate_all_optimizations to deterministic content
    def fake_validate(self):
        return {
            "Kernel": {"mitigations_disabled": True, "modules_loaded": False},
            "CPU": {"cpu_governor": True},
        }

    monkeypatch.setattr(m.BazziteGamingOptimizer, "validate_all_optimizations", fake_validate)

    # Run with --validate
    monkeypatch.setattr(sys, "argv", ["bazzite-optimizer.py", "--validate", "--profile", "balanced"])  # type: ignore[attr-defined]

    opt = m.BazziteGamingOptimizer()
    rc = opt.run()
    out = capsys.readouterr().out

    assert rc == 0
    assert "Validation Results:" in out
    assert "Kernel:" in out and "CPU:" in out
    assert "mitigations_disabled" in out and "modules_loaded" in out
    # Expect both pass and fail markers
    assert "✓" in out and "✗" in out


def test_rollback_success_path(monkeypatch, capsys):
    m = load_bazzite_optimizer()

    # Avoid heavy IO & logging; stub prerequisites
    import logging
    monkeypatch.setattr(m, "setup_logging", lambda: logging.getLogger("noop"))
    monkeypatch.setattr(m, "get_system_info", lambda: {
        "kernel": "6.8.0",
        "kernel_version": (6, 8, 0),
        "distribution": "Bazzite",
        "cpu_model": "",
        "cpu_cores": 8,
        "cpu_threads": 16,
        "ram_gb": 32,
        "gpus": [],
        "network_interfaces": [],
        "nvme_devices": [],
        "free_disk_gb": 500,
        "form_factor": "desktop",
        "display_server": "wayland",
    })
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_banner", lambda self: None)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_system_info", lambda self: None)

    # Force prerequisites pass and rollback script presence
    monkeypatch.setattr(m.BazziteGamingOptimizer, "check_prerequisites", lambda self: True)

    # Patch Path.exists to return True for the rollback script
    from pathlib import Path as _Path

    real_exists = _Path.exists

    def fake_exists(p: _Path):
        if str(p) == "/usr/local/bin/rollback-gaming-optimizations.sh":
            return True
        return real_exists(p)

    monkeypatch.setattr(m.Path, "exists", fake_exists)

    # Stub run_command to succeed
    monkeypatch.setattr(m, "run_command", lambda cmd, **kw: (0, "", ""))

    monkeypatch.setattr(sys, "argv", ["bazzite-optimizer.py", "--rollback"])  # type: ignore[attr-defined]
    opt = m.BazziteGamingOptimizer()
    rc = opt.run()
    out = capsys.readouterr().out

    assert rc == 0
    assert "Executing rollback" in out
    assert "Rollback completed successfully" in out


def test_rollback_failure_path(monkeypatch, capsys):
    m = load_bazzite_optimizer()

    # Avoid heavy IO & logging; stub prerequisites
    import logging
    monkeypatch.setattr(m, "setup_logging", lambda: logging.getLogger("noop"))
    monkeypatch.setattr(m, "get_system_info", lambda: {
        "kernel": "6.8.0",
        "kernel_version": (6, 8, 0),
        "distribution": "Bazzite",
        "cpu_model": "",
        "cpu_cores": 8,
        "cpu_threads": 16,
        "ram_gb": 32,
        "gpus": [],
        "network_interfaces": [],
        "nvme_devices": [],
        "free_disk_gb": 500,
        "form_factor": "desktop",
        "display_server": "wayland",
    })
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_banner", lambda self: None)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_system_info", lambda self: None)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "check_prerequisites", lambda self: True)

    # Patch Path.exists to return True for the rollback script
    from pathlib import Path as _Path
    real_exists = _Path.exists

    def fake_exists(p: _Path):
        if str(p) == "/usr/local/bin/rollback-gaming-optimizations.sh":
            return True
        return real_exists(p)

    monkeypatch.setattr(m.Path, "exists", fake_exists)

    # Stub run_command to fail
    monkeypatch.setattr(m, "run_command", lambda cmd, **kw: (1, "", "err"))

    monkeypatch.setattr(sys, "argv", ["bazzite-optimizer.py", "--rollback"])  # type: ignore[attr-defined]
    opt = m.BazziteGamingOptimizer()
    rc = opt.run()
    out = capsys.readouterr().out

    assert rc == 1
    assert "Executing rollback" in out
    assert "Rollback encountered errors" in out


def test_skip_packages_flag_is_passed(monkeypatch):
    m = load_bazzite_optimizer()

    # Quiet logging/system info
    import logging
    monkeypatch.setattr(m, "setup_logging", lambda: logging.getLogger("noop"))
    monkeypatch.setattr(m, "get_system_info", lambda: {
        "kernel": "6.8.0",
        "kernel_version": (6, 8, 0),
        "distribution": "Bazzite",
        "cpu_model": "",
        "cpu_cores": 8,
        "cpu_threads": 16,
        "ram_gb": 32,
        "gpus": [],
        "network_interfaces": [],
        "nvme_devices": [],
        "free_disk_gb": 500,
        "form_factor": "desktop",
        "display_server": "wayland",
    })
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_banner", lambda self: None)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_system_info", lambda self: None)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "check_prerequisites", lambda self: True)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "initialize_optimizers", lambda self: None)
    # Avoid file writes and large prints
    monkeypatch.setattr(m.BazziteGamingOptimizer, "create_rollback_script", lambda self: None)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_verification_commands", lambda self: None)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_usage_instructions", lambda self: None)
    # Avoid profile file writes
    monkeypatch.setattr(m.ProfileManager, "export_profile_env", lambda self, profile: None)

    seen = {"args": None}

    def fake_apply(self, skip_packages=False, run_benchmarks=False):
        seen["args"] = (skip_packages, run_benchmarks)
        return True

    monkeypatch.setattr(m.BazziteGamingOptimizer, "apply_optimizations", fake_apply)

    monkeypatch.setattr(sys, "argv", ["bazzite-optimizer.py", "--skip-packages"])  # type: ignore[attr-defined]
    opt = m.BazziteGamingOptimizer()
    rc = opt.run()

    assert rc == 0
    assert seen["args"] == (True, False)


def test_benchmark_flag_is_passed(monkeypatch):
    m = load_bazzite_optimizer()

    import logging
    monkeypatch.setattr(m, "setup_logging", lambda: logging.getLogger("noop"))
    monkeypatch.setattr(m, "get_system_info", lambda: {
        "kernel": "6.8.0",
        "kernel_version": (6, 8, 0),
        "distribution": "Bazzite",
        "cpu_model": "",
        "cpu_cores": 8,
        "cpu_threads": 16,
        "ram_gb": 32,
        "gpus": [],
        "network_interfaces": [],
        "nvme_devices": [],
        "free_disk_gb": 500,
        "form_factor": "desktop",
        "display_server": "wayland",
    })
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_banner", lambda self: None)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_system_info", lambda self: None)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "check_prerequisites", lambda self: True)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "initialize_optimizers", lambda self: None)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "create_rollback_script", lambda self: None)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_verification_commands", lambda self: None)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_usage_instructions", lambda self: None)
    monkeypatch.setattr(m.ProfileManager, "export_profile_env", lambda self, profile: None)

    seen = {"args": None}

    def fake_apply(self, skip_packages=False, run_benchmarks=False):
        seen["args"] = (skip_packages, run_benchmarks)
        return True

    monkeypatch.setattr(m.BazziteGamingOptimizer, "apply_optimizations", fake_apply)

    monkeypatch.setattr(sys, "argv", ["bazzite-optimizer.py", "--benchmark"])  # type: ignore[attr-defined]
    opt = m.BazziteGamingOptimizer()
    rc = opt.run()

    assert rc == 0
    assert seen["args"] == (False, True)


def test_profile_selection_passed_to_export(monkeypatch):
    m = load_bazzite_optimizer()

    import logging
    monkeypatch.setattr(m, "setup_logging", lambda: logging.getLogger("noop"))
    monkeypatch.setattr(m, "get_system_info", lambda: {
        "kernel": "6.8.0",
        "kernel_version": (6, 8, 0),
        "distribution": "Bazzite",
        "cpu_model": "",
        "cpu_cores": 8,
        "cpu_threads": 16,
        "ram_gb": 32,
        "gpus": [],
        "network_interfaces": [],
        "nvme_devices": [],
        "free_disk_gb": 500,
        "form_factor": "desktop",
        "display_server": "wayland",
    })
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_banner", lambda self: None)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_system_info", lambda self: None)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "check_prerequisites", lambda self: True)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "initialize_optimizers", lambda self: None)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "create_rollback_script", lambda self: None)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_verification_commands", lambda self: None)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "print_usage_instructions", lambda self: None)

    seen = {"profile": None}

    def fake_export(self, profile):
        seen["profile"] = profile

    monkeypatch.setattr(m.ProfileManager, "export_profile_env", fake_export)

    # Ensure we proceed to export step (apply_optimizations returns True)
    monkeypatch.setattr(m.BazziteGamingOptimizer, "apply_optimizations", lambda self, skip_packages=False, run_benchmarks=False: True)

    monkeypatch.setattr(sys, "argv", ["bazzite-optimizer.py", "--profile", "competitive"])  # type: ignore[attr-defined]
    opt = m.BazziteGamingOptimizer()
    rc = opt.run()

    assert rc == 0
    assert seen["profile"] == "competitive"


def test_print_validation_summary_formats_output(monkeypatch, capsys):
    m = load_bazzite_optimizer()

    import logging
    monkeypatch.setattr(m, "setup_logging", lambda: logging.getLogger("noop"))
    monkeypatch.setattr(m, "get_system_info", lambda: {
        "kernel": "6.8.0",
        "kernel_version": (6, 8, 0),
        "distribution": "Bazzite",
        "cpu_model": "",
        "cpu_cores": 8,
        "cpu_threads": 16,
        "ram_gb": 32,
        "gpus": [],
        "network_interfaces": [],
        "nvme_devices": [],
        "free_disk_gb": 500,
        "form_factor": "desktop",
        "display_server": "wayland",
    })

    opt = m.BazziteGamingOptimizer()
    opt.profile = "balanced"
    # Two modules: one fully passing, one mixed
    opt.validation_results = {
        "Kernel & Boot": {"mitigations_disabled": True, "modules_loaded": True},
        "Audio System": {"audio_config": True, "latency_tuned": False},
    }

    opt.print_validation_summary()
    out = capsys.readouterr().out

    # Header and profile line present
    assert "VALIDATION SUMMARY" in out
    assert "Profile: Balanced Gaming (balanced)" in out

    # Module status lines
    assert "✓ Kernel & Boot: 2/2 checks passed" in out
    assert "⚠ Audio System: 1/2 checks passed" in out
    # Failed check line printed
    assert "✗ latency_tuned" in out

    # Overall percentage: 3/4 = 75.0%
    assert "Overall: 3/4 (75.0%) validations passed" in out
