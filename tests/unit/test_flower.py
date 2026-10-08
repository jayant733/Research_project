# tests/unit/test_flower.py
# Technical Explanation: Verifies decoupled model training, client state,
# and parameter aggregation algorithms.

import numpy as np

from packages.common.client import GenericClient
from packages.common.context import RoundContext
from packages.common.fedavg_aggregator import FedAvgAggregator
from packages.common.mock_model import MockModel


def test_mock_model_train() -> None:
    """Verifies that MockModel increments parameters during train calls."""
    model = MockModel()
    weights = model.get_weights()
    assert len(weights) == 1
    np.testing.assert_array_almost_equal(
        weights[0], np.array([1.0, 2.0, 3.0], dtype=np.float32)
    )

    model.train()
    updated_weights = model.get_weights()
    np.testing.assert_array_almost_equal(
        updated_weights[0], np.array([2.0, 3.0, 4.0], dtype=np.float32)
    )


def test_generic_client_fit() -> None:
    """Verifies that GenericClient updates parameters using RoundContext."""
    model = MockModel()
    client = GenericClient(model=model)
    context = RoundContext(current_round=1, config={})

    input_params = [np.array([1.0, 2.0, 3.0], dtype=np.float32)]
    updated_params, num_samples, metrics = client.fit(input_params, context=context)

    assert num_samples == 10
    np.testing.assert_array_almost_equal(
        updated_params[0], np.array([2.0, 3.0, 4.0], dtype=np.float32)
    )


def test_fedavg_aggregator() -> None:
    """Verifies weighted averaging calculation."""
    aggregator = FedAvgAggregator()

    # 2 clients returning [2,3,4] and [4,5,6] with equal samples (10 each)
    updates = [
        ([np.array([2.0, 3.0, 4.0], dtype=np.float32)], 10),
        ([np.array([4.0, 5.0, 6.0], dtype=np.float32)], 10),
    ]

    aggregated = aggregator.aggregate(updates)
    assert len(aggregated) == 1
    np.testing.assert_array_almost_equal(
        aggregated[0], np.array([3.0, 4.0, 5.0], dtype=np.float32)
    )


def test_fedavg_aggregates_every_tensor() -> None:
    """Verifies multi-layer updates are all included in the average."""
    aggregator = FedAvgAggregator()
    updates = [
        (
            [
                np.array([[1.0, 2.0]], dtype=np.float32),
                np.array([4.0], dtype=np.float32),
            ],
            1,
        ),
        (
            [
                np.array([[3.0, 6.0]], dtype=np.float32),
                np.array([8.0], dtype=np.float32),
            ],
            1,
        ),
    ]
    aggregated = aggregator.aggregate(updates)
    np.testing.assert_allclose(aggregated[0], np.array([[2.0, 4.0]], dtype=np.float32))
    np.testing.assert_allclose(aggregated[1], np.array([6.0], dtype=np.float32))
