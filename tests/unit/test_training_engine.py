import pytest

# Import providers to trigger registration
from packages.training.domain.exceptions import TrainingConfigurationError
from packages.training.domain.policies import DevicePolicy, PrecisionPolicy
from packages.training.services.registries import model_registry, provider_registry
from packages.training.services.seed import SeedManager

import packages.training.providers.pytorch.model  # noqa: F401
import packages.training.providers.pytorch.trainer  # noqa: F401


def test_precision_policy_validation() -> None:
    # Valid
    p = PrecisionPolicy(mode="amp")
    assert p.mode == "AMP"

    # Invalid
    with pytest.raises(TrainingConfigurationError):
        PrecisionPolicy(mode="INVALID")


def test_device_policy_validation() -> None:
    # Valid
    d = DevicePolicy(preferred_device="mps")
    assert d.preferred_device == "MPS"

    # Invalid
    with pytest.raises(TrainingConfigurationError):
        DevicePolicy(preferred_device="TPU")


def test_registry_lookup() -> None:
    # Should raise error if not found
    with pytest.raises(Exception):
        provider_registry.get_trainer("non_existent", config=None, callbacks=None)

    assert "pytorch" in provider_registry._registry
    assert "SimpleMLP" in model_registry._registry


def test_seed_reproducibility() -> None:
    import torch

    SeedManager.set_seed(42)
    val1 = torch.rand(1).item()
    SeedManager.set_seed(42)
    val2 = torch.rand(1).item()
    assert val1 == val2
