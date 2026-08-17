"""
Strongly typed domain objects for metrics, benchmarking, and device info.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from packages.training.domain.metadata import ExperimentMetadata


@dataclass
class DeviceInfo:
    """Detailed hardware profiling snapshot."""

    device_name: str
    device_type: str
    cuda_version: Optional[str]
    cudnn_version: Optional[str]
    compute_capability: Optional[str]
    total_memory: int
    free_memory: int
    supports_amp: bool
    supports_bf16: bool
    tensor_core_support: bool
    num_sms: Optional[int]
    driver_version: Optional[str]


@dataclass
class TrainingMetrics:
    """Represents one snapshot of training metrics for an epoch or step."""

    loss: float
    accuracy: float
    epoch: int
    step: int
    training_time: float
    throughput: float
    device: str
    gpu_memory: int
    reserved_memory: int


@dataclass
class MetricsHistory:
    """Stores the full history of metrics for plotting and checkpointing."""

    epoch_metrics: List[TrainingMetrics] = field(default_factory=list)
    validation_metrics: List[TrainingMetrics] = field(default_factory=list)
    learning_rate_history: List[float] = field(default_factory=list)
    throughput_history: List[float] = field(default_factory=list)
    gpu_memory_history: List[int] = field(default_factory=list)


@dataclass
class BenchmarkResult:
    """Strongly typed output from the BenchmarkRunner."""

    samples_per_sec: float
    batches_per_sec: float
    epoch_duration: float
    training_duration: float
    gpu_utilization: float
    allocated_memory: float
    reserved_memory: float
    peak_memory: float
    cpu_utilization: float
    ram_utilization: float


@dataclass
class TrainingResult:
    """Complete output of a TrainingSession."""

    metrics: TrainingMetrics
    history: MetricsHistory
    benchmark: Optional[BenchmarkResult]
    checkpoint_path: Optional[str]
    device_info: DeviceInfo
    metadata: Optional[ExperimentMetadata]
