import importlib.util
import logging
from pathlib import Path


def load_bazzite_optimizer():
    """Dynamically load the bazzite-optimizer.py as a module."""
    spec = importlib.util.spec_from_file_location(
        "bazzite_optimizer", str(Path(__file__).resolve().parent.parent / "bazzite-optimizer.py")
    )
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def make_kernel_optimizer(module):
    logger = logging.getLogger("test-kernel-opt")
    logger.setLevel(logging.CRITICAL)
    return module.KernelOptimizer(logger)


def test_clean_kernel_params_boot_log_duplication():
    m = load_bazzite_optimizer()
    opt = make_kernel_optimizer(m)

    current = "quiet splash mitigations=auto mitigations=off mitigations=off processor.max_cstate=3 processor.max_cstate=3"
    new_params = ["mitigations=off", "processor.max_cstate=3"]

    result = opt._clean_kernel_params(current, new_params)
    # Expect deduped values with last value prevailing
    assert result == "quiet splash mitigations=off processor.max_cstate=3"


def test_clean_kernel_params_add_new_values():
    m = load_bazzite_optimizer()
    opt = make_kernel_optimizer(m)

    current = "quiet splash"
    new_params = ["mitigations=off", "processor.max_cstate=1"]
    result = opt._clean_kernel_params(current, new_params)
    assert result == "quiet splash mitigations=off processor.max_cstate=1"


def test_clean_kernel_params_value_replacement():
    m = load_bazzite_optimizer()
    opt = make_kernel_optimizer(m)

    current = "quiet splash mitigations=auto processor.max_cstate=3"
    new_params = ["mitigations=off", "processor.max_cstate=1"]
    result = opt._clean_kernel_params(current, new_params)
    assert result == "quiet splash mitigations=off processor.max_cstate=1"


def test_clean_kernel_params_handles_quoted_values():
    m = load_bazzite_optimizer()
    opt = make_kernel_optimizer(m)

    current = 'quiet splash root="UUID=12345" mitigations=auto'
    new_params = ["mitigations=off", "intel_idle.max_cstate=1"]
    result = opt._clean_kernel_params(current, new_params)
    # Quotes removed from value, dedup applied
    assert result == 'quiet splash root=UUID=12345 mitigations=off intel_idle.max_cstate=1'
