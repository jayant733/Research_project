"""
Checkpointing abstraction with schema versioning for backward compatibility.
"""

import json
import os
from typing import Any

from packages.training.domain.exceptions import CheckpointError


class CheckpointManager:
    """Manages saving and loading of model states, metrics, and metadata."""

    SCHEMA_VERSION = "1.0"

    def __init__(self, directory: str):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def save_checkpoint(self, trainer: Any, epoch: int, metrics: dict) -> str:
        """
        Saves a checkpoint using the provider's specific serialization logic,
        while managing domain metadata alongside it.
        """
        # trainer must implement save_state(path) returning the serialized state dict path or dict.
        path = os.path.join(self.directory, f"checkpoint_epoch_{epoch}.pt")
        metadata_path = os.path.join(
            self.directory, f"checkpoint_epoch_{epoch}_meta.json"
        )

        try:
            # Delegate raw weight/optimizer saving to the provider
            trainer.save_state(path)

            # Save domain metadata independently
            meta = {
                "schema_version": self.SCHEMA_VERSION,
                "epoch": epoch,
                "metrics": metrics,
                # Would extract tracker metadata here if injected
            }
            with open(metadata_path, "w") as f:
                json.dump(meta, f)

            return path
        except Exception as e:
            raise CheckpointError(f"Failed to save checkpoint: {str(e)}")

    def load_checkpoint(self, trainer: Any, epoch: int) -> None:
        path = os.path.join(self.directory, f"checkpoint_epoch_{epoch}.pt")
        if not os.path.exists(path):
            raise CheckpointError(f"Checkpoint not found at {path}")

        try:
            trainer.load_state(path)
        except Exception as e:
            raise CheckpointError(f"Failed to load checkpoint: {str(e)}")
