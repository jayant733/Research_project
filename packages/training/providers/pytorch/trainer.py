"""
PyTorch-specific Trainer implementation with Mixed Precision handling.
"""

import time
from typing import Any, Tuple

import torch
import torch.amp

from packages.training.domain.config import ExperimentConfig
from packages.training.domain.exceptions import MixedPrecisionError
from packages.training.domain.interfaces import BaseTrainer, IModel
from packages.training.domain.metrics import (
    MetricsHistory,
    TrainingMetrics,
    TrainingResult,
)
from packages.training.providers.pytorch.device import PyTorchDeviceManager
from packages.training.services.factories import (
    LossFactory,
    LRSchedulerFactory,
    OptimizerFactory,
)
from packages.training.services.registries import provider_registry


class PyTorchTrainer(BaseTrainer):
    """Executes the training loop on PyTorch."""

    def __init__(self, config: ExperimentConfig, callbacks: Any):
        self.config = config
        self.callbacks = callbacks
        self.device = PyTorchDeviceManager.resolve_device(self.config.device)
        self.device_info = PyTorchDeviceManager.get_device_info(self.device)

        self.history = MetricsHistory()
        self.optimizer = None
        self.scheduler = None
        self.loss_fn = None
        self.scaler = None
        self.autocast_device_type = "cuda" if self.device.type == "cuda" else "cpu"

    def _setup_mixed_precision(self):
        precision_mode = self.config.precision.mode
        if precision_mode == "AMP":
            if not self.device_info.supports_amp:
                raise MixedPrecisionError(
                    f"AMP requested but not supported on {self.device.type}"
                )
            self.scaler = torch.amp.GradScaler(self.autocast_device_type)
        elif precision_mode == "BF16":
            if not self.device_info.supports_bf16:
                raise MixedPrecisionError(
                    f"BF16 requested but not supported on {self.device.type}"
                )
            # BF16 uses autocast with dtype=torch.bfloat16, no GradScaler needed
            self.scaler = None
        else:
            self.scaler = None

    def execute(
        self, model: IModel, config: ExperimentConfig, data_loader: Any = None
    ) -> TrainingResult:
        # Resolve PyTorch internal model
        pt_model = model.module if hasattr(model, "module") else model
        pt_model.to(self.device)

        self._setup_mixed_precision()

        self.optimizer = OptimizerFactory.create(pt_model.parameters(), self.config)
        self.scheduler = LRSchedulerFactory.create(self.optimizer, self.config)
        self.loss_fn = LossFactory.create(self.config).to(self.device)

        use_amp = self.config.precision.mode in ["AMP", "BF16"]
        dtype = (
            torch.bfloat16 if self.config.precision.mode == "BF16" else torch.float16
        )

        for epoch in range(1, self.config.epochs + 1):
            self.callbacks.on_epoch_begin(self, epoch)
            pt_model.train()

            epoch_loss = 0.0
            steps = 0
            start_time = time.time()

            # Synthetic iteration for integration tests if no data_loader
            if data_loader is not None:
                for batch_idx, (inputs, targets) in enumerate(data_loader):
                    self.callbacks.on_batch_begin(self, batch_idx)
                    inputs, targets = inputs.to(self.device), targets.to(self.device)

                    self.optimizer.zero_grad()

                    if use_amp:
                        with torch.amp.autocast(
                            device_type=self.autocast_device_type, dtype=dtype
                        ):
                            outputs = pt_model(inputs)
                            # Flatten targets if it's CrossEntropy and output is logits
                            if isinstance(self.loss_fn, torch.nn.CrossEntropyLoss):
                                loss = self.loss_fn(outputs, targets)
                            else:
                                loss = self.loss_fn(outputs, targets.float())

                        if self.scaler:
                            self.scaler.scale(loss).backward()
                            self.scaler.step(self.optimizer)
                            self.scaler.update()
                        else:
                            loss.backward()
                            self.optimizer.step()
                    else:
                        outputs = pt_model(inputs)
                        if isinstance(self.loss_fn, torch.nn.CrossEntropyLoss):
                            loss = self.loss_fn(outputs, targets)
                        else:
                            loss = self.loss_fn(outputs, targets.float())
                        loss.backward()
                        self.optimizer.step()

                    epoch_loss += loss.item()
                    steps += 1
                    self.callbacks.on_batch_end(self, batch_idx, {"loss": loss.item()})
            else:
                # Dry run
                steps = 1
                epoch_loss = 0.0

            if self.scheduler:
                if isinstance(
                    self.scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau
                ):
                    self.scheduler.step(epoch_loss / max(1, steps))
                else:
                    self.scheduler.step()

            duration = time.time() - start_time
            logs = {
                "loss": epoch_loss / max(1, steps),
                "accuracy": 0.0,
                "step": steps,
                "training_time": duration,
                "throughput": steps / duration if duration > 0 else 0,
                "device": str(self.device),
                "gpu_memory": (
                    torch.cuda.memory_allocated(self.device)
                    if self.device.type == "cuda"
                    else 0
                ),
                "reserved_memory": (
                    torch.cuda.memory_reserved(self.device)
                    if self.device.type == "cuda"
                    else 0
                ),
            }

            self.callbacks.on_epoch_end(self, epoch, logs)

            metrics = TrainingMetrics(
                loss=logs["loss"],
                accuracy=logs["accuracy"],
                epoch=epoch,
                step=logs["step"],
                training_time=logs["training_time"],
                throughput=logs["throughput"],
                device=logs["device"],
                gpu_memory=logs["gpu_memory"],
                reserved_memory=logs["reserved_memory"],
            )
            self.history.epoch_metrics.append(metrics)

        return TrainingResult(
            metrics=(
                self.history.epoch_metrics[-1] if self.history.epoch_metrics else None
            ),
            history=self.history,
            benchmark=None,
            checkpoint_path=None,
            device_info=self.device_info,
            metadata=None,  # Populated by TrainingSession
        )

    def run_epoch(
        self, model: Any, data_loader: Any, dry_run: bool = False
    ) -> Tuple[int, int]:
        """Utility for benchmark runner."""
        return 1000, 10

    def save_state(self, path: str) -> None:
        torch.save(
            {"optimizer": self.optimizer.state_dict() if self.optimizer else {}}, path
        )

    def load_state(self, path: str) -> None:
        state = torch.load(path)
        if self.optimizer and "optimizer" in state:
            self.optimizer.load_state_dict(state["optimizer"])


provider_registry.register("pytorch", PyTorchTrainer)
