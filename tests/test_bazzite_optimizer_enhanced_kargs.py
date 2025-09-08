import importlib.util
from pathlib import Path


def load_bazzite_optimizer():
    spec = importlib.util.spec_from_file_location(
        "bazzite_optimizer", str(Path(__file__).resolve().parent.parent / "bazzite-optimizer.py")
    )
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def test_enhanced_rpm_ostree_kargs_direct(monkeypatch):
    m = load_bazzite_optimizer()

    # Simulate modern rpm-ostree kargs returning arguments
    def fake_run_command(cmd, check=True, shell=True, timeout=30):
        assert "rpm-ostree kargs" in cmd
        return 0, "mitigations=off threadirqs", ""

    monkeypatch.setattr(m, "run_command", fake_run_command)
    out = m.enhanced_rpm_ostree_kargs()
    assert out == "mitigations=off threadirqs"


def test_enhanced_rpm_ostree_kargs_fallback(monkeypatch):
    m = load_bazzite_optimizer()

    calls = {"n": 0}

    def fake_run_command(cmd, check=True, shell=True, timeout=30):
        # First call: simulate kargs failure
        if calls["n"] == 0:
            calls["n"] += 1
            return 1, "", "error"
        # Second call: status output including Kernel arguments
        return (
            0,
            "Some text\nKernel arguments: mitigations=off preempt=full\nOther text\n",
            "",
        )

    monkeypatch.setattr(m, "run_command", fake_run_command)
    out = m.enhanced_rpm_ostree_kargs()
    assert out == "mitigations=off preempt=full"


def test_enhanced_rpm_ostree_kargs_empty_when_unavailable(monkeypatch):
    m = load_bazzite_optimizer()

    def fake_run_command(cmd, check=True, shell=True, timeout=30):
        return 1, "", "nope"

    monkeypatch.setattr(m, "run_command", fake_run_command)
    out = m.enhanced_rpm_ostree_kargs()
    assert out == ""

