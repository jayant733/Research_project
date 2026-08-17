import os
import torch
import shutil
from packages.training.domain.config import ExperimentConfig
from packages.training.domain.policies import PrecisionPolicy, DevicePolicy
from packages.training.domain.exceptions import TrainingConfigurationError, MixedPrecisionError
from packages.training.services.trainer import TrainingSession
from packages.training.services.registries import model_registry, provider_registry, CallbackRegistry
from packages.training.services.callbacks import CallbackManager, TrainerCallback
from packages.training.services.dataset import SyntheticDatasetGenerator
from packages.training.services.checkpoint import CheckpointManager
from packages.training.services.benchmark import BenchmarkRunner
from packages.training.services.factories import OptimizerFactory, LossFactory, LRSchedulerFactory
from packages.training.services.seed import SeedManager
from packages.training.providers.pytorch.model import TorchModel
from packages.training.providers.pytorch.device import PyTorchDeviceManager
import packages.training.providers.pytorch.trainer
import packages.training.providers.pytorch.model
from torch.utils.data import DataLoader

print("="*60)
print("VERIFICATION CHECK 1 & 3: CPU TRAINING & FALLBACK")
print("="*60)

config = ExperimentConfig(
    batch_size=32,
    epochs=2,
    learning_rate=0.01,
    optimizer="Adam",
    loss_function="CrossEntropy",
    precision=PrecisionPolicy(mode="FP32"),
    device=DevicePolicy(preferred_device="CUDA"), # Request CUDA to test fallback
    random_seed=42,
    checkpoint_directory="./test_checkpoints"
)

raw_model = model_registry.get("SimpleMLP", input_dim=20, hidden_dim=32, num_classes=2)
model = TorchModel(raw_model)
dataset = SyntheticDatasetGenerator.create_classification_dataset(samples=100, features=20, classes=2)
loader = DataLoader(dataset, batch_size=config.batch_size)

class TrackingCallback(TrainerCallback):
    def __init__(self):
        self.events = []
    def on_train_start(self, trainer, **kwargs): self.events.append("on_train_start")
    def on_epoch_begin(self, trainer, epoch, **kwargs): self.events.append("on_epoch_begin")
    def on_batch_begin(self, trainer, batch, **kwargs): self.events.append("on_batch_begin")
    def on_batch_end(self, trainer, batch, logs, **kwargs): self.events.append("on_batch_end")
    def on_epoch_end(self, trainer, epoch, logs, **kwargs): self.events.append("on_epoch_end")
    def on_train_end(self, trainer, **kwargs): self.events.append("on_train_end")

tracker_cb = TrackingCallback()
callbacks = CallbackManager([tracker_cb])
session = TrainingSession(config=config, callbacks=callbacks)
result = session.execute(model, provider_name="pytorch", data_loader=loader)

print("Training finished.")
print(f"Final Epoch: {result.metrics.epoch}")
print(f"Final Loss: {result.metrics.loss}")
print(f"Device used: {result.metrics.device}")
print("CPU Fallback successful: True" if "cpu" in str(result.metrics.device) else "False")

print("\n" + "="*60)
print("VERIFICATION CHECK 4: MIXED PRECISION")
print("="*60)
config_amp = ExperimentConfig(
    batch_size=32, epochs=1, learning_rate=0.01, precision=PrecisionPolicy(mode="AMP"), device=DevicePolicy(preferred_device="CPU")
)
try:
    session_amp = TrainingSession(config=config_amp, callbacks=CallbackManager([]))
    session_amp.execute(TorchModel(model_registry.get("SimpleMLP")), provider_name="pytorch", data_loader=loader)
    print("AMP executed (or raised expected error if unsupported)")
except MixedPrecisionError as e:
    print(f"AMP fallback handled correctly: {e}")

print("\n" + "="*60)
print("VERIFICATION CHECK 5: CHECKPOINT SYSTEM")
print("="*60)
ckpt_manager = CheckpointManager(config.checkpoint_directory)
trainer_impl = provider_registry.get_trainer("pytorch", config=config, callbacks=callbacks)
trainer_impl.optimizer = torch.optim.Adam(model.module.parameters())
path = ckpt_manager.save_checkpoint(trainer_impl, epoch=2, metrics={"loss": result.metrics.loss})
print(f"Checkpoint saved at: {path}")
assert os.path.exists(path)

# Load Checkpoint
trainer_impl.load_state(path)
print("Checkpoint loaded successfully")
shutil.rmtree(config.checkpoint_directory)

print("\n" + "="*60)
print("VERIFICATION CHECK 6: REPRODUCIBILITY")
print("="*60)
def run_seed(seed):
    SeedManager.set_seed(seed)
    c = ExperimentConfig(batch_size=32, epochs=1, learning_rate=0.01, random_seed=seed)
    m = TorchModel(model_registry.get("SimpleMLP"))
    d = SyntheticDatasetGenerator.create_classification_dataset(samples=100, features=20, classes=2, seed=seed)
    l = DataLoader(d, batch_size=c.batch_size)
    s = TrainingSession(config=c, callbacks=CallbackManager([]))
    return s.execute(m, provider_name="pytorch", data_loader=l).metrics.loss

loss_42_a = run_seed(42)
loss_42_b = run_seed(42)
loss_99 = run_seed(99)
print(f"Seed 42 Loss A: {loss_42_a}")
print(f"Seed 42 Loss B: {loss_42_b}")
print(f"Seed 99 Loss:   {loss_99}")
assert loss_42_a == loss_42_b
assert loss_42_a != loss_99
print("Reproducibility verified.")

print("\n" + "="*60)
print("VERIFICATION CHECK 7: BENCHMARK ENGINE")
print("="*60)
bench_res = BenchmarkRunner.measure(trainer_impl, model, loader, num_epochs=1)
print(f"Samples/sec: {bench_res.samples_per_sec:.2f}")
print(f"Batches/sec: {bench_res.batches_per_sec:.2f}")

print("\n" + "="*60)
print("VERIFICATION CHECK 8: CALLBACK SYSTEM")
print("="*60)
expected_events = ['on_train_start', 'on_epoch_begin', 'on_batch_begin', 'on_batch_end', 'on_batch_begin', 'on_batch_end', 'on_batch_begin', 'on_batch_end', 'on_batch_begin', 'on_batch_end', 'on_epoch_end', 'on_epoch_begin', 'on_batch_begin', 'on_batch_end', 'on_batch_begin', 'on_batch_end', 'on_batch_begin', 'on_batch_end', 'on_batch_begin', 'on_batch_end', 'on_epoch_end', 'on_train_end']
print("Expected:", expected_events)
print("Actual  :", tracker_cb.events[:22])
print("Execution order matches expected:", tracker_cb.events[:22] == expected_events)

print("\n" + "="*60)
print("VERIFICATION CHECK 9: FACTORIES")
print("="*60)
try:
    OptimizerFactory.create(model.module.parameters(), ExperimentConfig(batch_size=1, epochs=1, learning_rate=0.1, optimizer="INVALID"))
except TrainingConfigurationError:
    print("Invalid optimizer raised TrainingConfigurationError")

print("\n" + "="*60)
print("VERIFICATION CHECK 10 & 11: REGISTRIES & DEVICE MANAGER")
print("="*60)
cb_reg = CallbackRegistry()
cb_reg.register("test", "test_item")
try:
    cb_reg.get("invalid")
except KeyError:
    print("Invalid lookup raised KeyError")

info_cpu = PyTorchDeviceManager.get_device_info(torch.device("cpu"))
print(f"Device Info (CPU): {info_cpu.device_name}, Memory: {info_cpu.total_memory}")
