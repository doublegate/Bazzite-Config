import importlib.util
import subprocess
from pathlib import Path


def load_bazzite_optimizer():
    spec = importlib.util.spec_from_file_location(
        "bazzite_optimizer", str(Path(__file__).resolve().parent.parent / "bazzite-optimizer.py")
    )
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def test_run_command_success(monkeypatch):
    m = load_bazzite_optimizer()

    class DummyCompleted:
        def __init__(self):
            self.returncode = 0
            self.stdout = "ok"
            self.stderr = ""

    def fake_subprocess_run(*args, **kwargs):
        return DummyCompleted()

    monkeypatch.setattr(subprocess, "run", fake_subprocess_run)
    code, out, err = m.run_command("echo ok")
    assert code == 0 and out == "ok" and err == ""


def test_run_command_timeout(monkeypatch):
    m = load_bazzite_optimizer()

    def fake_subprocess_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="sleep 2", timeout=1)

    monkeypatch.setattr(subprocess, "run", fake_subprocess_run)
    code, out, err = m.run_command("sleep 2", timeout=1)
    assert code == -1 and out == "" and "timed out" in err.lower()


def test_check_kernel_version(monkeypatch):
    m = load_bazzite_optimizer()

    def fake_info_ok():
        return {"kernel_version": m.MIN_KERNEL_VERSION}

    def fake_info_old():
        major, minor, patch = m.MIN_KERNEL_VERSION
        return {"kernel_version": (major, max(0, minor - 1), patch)}

    monkeypatch.setattr(m, "get_system_info", fake_info_ok)
    assert m.check_kernel_version() is True

    monkeypatch.setattr(m, "get_system_info", fake_info_old)
    assert m.check_kernel_version() is False


def test_validate_file_exists(tmp_path, monkeypatch):
    m = load_bazzite_optimizer()

    # Build a minimal BaseOptimizer instance with a dummy logger
    import logging

    opt = m.BaseOptimizer(logging.getLogger("test"))
    existing = tmp_path / "exists.txt"
    existing.write_text("x")

    assert opt._validate_file_exists("exists", str(existing)) is True
    assert opt._validate_file_exists("missing", str(tmp_path / "missing.txt")) is False

