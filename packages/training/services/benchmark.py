"""
Utilities for performance benchmarking and hardware throughput measurement.
"""

import time
from typing import Any

from packages.training.domain.metrics import BenchmarkResult


class BenchmarkRunner:
    """Independent utility to measure training engine throughput."""

    @staticmethod
    def measure(
        trainer: Any, model: Any, data_loader: Any, num_epochs: int = 1
    ) -> BenchmarkResult:
        """
        Executes a dry-run training loop to collect throughput metrics.
        """
        # Start tracking time
        start_time = time.time()

        # Temporarily override config to run for num_epochs
        original_epochs = trainer.config.epochs
        trainer.config.epochs = num_epochs
        
        try:
            result = trainer.execute(model, trainer.config, data_loader=data_loader)
        finally:
            trainer.config.epochs = original_epochs
            
        end_time = time.time()
        training_duration = end_time - start_time
        
        total_samples = 0
        total_batches = 0
        if result and result.metrics:
            # Approx calculation from final step count
            total_batches = result.metrics.step * num_epochs
            total_samples = total_batches * trainer.config.batch_size

        epoch_duration = training_duration / num_epochs if num_epochs > 0 else 0

        samples_per_sec = (
            total_samples / training_duration if training_duration > 0 else 0
        )
        batches_per_sec = (
            total_batches / training_duration if training_duration > 0 else 0
        )

        # Attempt to gather hardware metrics if available (e.g., via PyTorch CUDA functions)
        gpu_utilization = 0.0
        allocated_memory = 0.0
        reserved_memory = 0.0
        peak_memory = 0.0

        try:
            import torch

            if torch.cuda.is_available():
                allocated_memory = torch.cuda.memory_allocated() / (1024**2)
                reserved_memory = torch.cuda.memory_reserved() / (1024**2)
                peak_memory = torch.cuda.max_memory_allocated() / (1024**2)
                # gpu_utilization requires pynvml, stubbed out for now
        except ImportError:
            pass

        return BenchmarkResult(
            samples_per_sec=samples_per_sec,
            batches_per_sec=batches_per_sec,
            epoch_duration=epoch_duration,
            training_duration=training_duration,
            gpu_utilization=gpu_utilization,
            allocated_memory=allocated_memory,
            reserved_memory=reserved_memory,
            peak_memory=peak_memory,
            cpu_utilization=0.0,  # Placeholder, requires psutil
            ram_utilization=0.0,  # Placeholder, requires psutil
        )
