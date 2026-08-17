from packages.training.domain.config import ExperimentConfig
from packages.training.domain.policies import DevicePolicy, PrecisionPolicy
from packages.training.providers.pytorch.model import TorchModel
from packages.training.services.callbacks import CallbackManager
from packages.training.services.dataset import SyntheticDatasetGenerator

import packages.training.providers.pytorch.trainer  # noqa: F401
from packages.training.services.registries import model_registry
from packages.training.services.trainer import TrainingSession


def test_end_to_end_training() -> None:
    # 1. Setup Configuration
    config = ExperimentConfig(
        batch_size=32,
        epochs=3,
        learning_rate=0.01,
        optimizer="Adam",
        loss_function="CrossEntropy",
        precision=PrecisionPolicy(mode="FP32"),
        device=DevicePolicy(preferred_device="CPU"),  # Use CPU for CI reliability
        random_seed=42,
    )

    # 2. Get Model from Registry
    raw_model = model_registry.get(
        "SimpleMLP", input_dim=20, hidden_dim=32, num_classes=2
    )
    model = TorchModel(raw_model)  # type: ignore

    # 3. Create Dataset
    dataset = SyntheticDatasetGenerator.create_classification_dataset(
        samples=100, features=20, classes=2
    )
    from torch.utils.data import DataLoader

    loader = DataLoader(dataset, batch_size=config.batch_size)

    # 4. Initialize Session
    callbacks = CallbackManager([])
    session = TrainingSession(config=config, callbacks=callbacks)

    # 5. Execute Training
    result = session.execute(model, provider_name="pytorch", data_loader=loader)

    # 6. Verify Results
    assert result is not None
    assert result.metrics is not None
    assert result.metrics.epoch == 3
    assert result.metrics.loss > 0
    assert len(result.history.epoch_metrics) == 3
