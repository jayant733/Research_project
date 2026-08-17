"""
PyTorch-specific device resolution and hardware telemetry mapping.
"""

import torch

from packages.training.domain.exceptions import DeviceInitializationError
from packages.training.domain.metrics import DeviceInfo
from packages.training.domain.policies import DevicePolicy


class PyTorchDeviceManager:
    """Resolves PyTorch devices based on the policy and collects hardware metrics."""

    @staticmethod
    def resolve_device(policy: DevicePolicy) -> torch.device:
        target = policy.preferred_device

        if target == "CUDA" and torch.cuda.is_available():
            return torch.device("cuda")
        elif target == "MPS" and torch.backends.mps.is_available():
            return torch.device("mps")
        elif target == "CPU":
            return torch.device("cpu")

        # Fallback logic
        for fallback in policy.fallback_order:
            if fallback == "CUDA" and torch.cuda.is_available():
                return torch.device("cuda")
            if fallback == "MPS" and torch.backends.mps.is_available():
                return torch.device("mps")
            if fallback == "CPU":
                return torch.device("cpu")

        raise DeviceInitializationError(
            f"Could not resolve any device from policy: {policy}"
        )

    @staticmethod
    def get_device_info(device: torch.device) -> DeviceInfo:
        device_type = device.type
        if device_type == "cuda":
            props = torch.cuda.get_device_properties(device)
            return DeviceInfo(
                device_name=props.name,
                device_type="CUDA",
                cuda_version=torch.version.cuda,
                cudnn_version=str(torch.backends.cudnn.version()),
                compute_capability=f"{props.major}.{props.minor}",
                total_memory=props.total_memory,
                free_memory=props.total_memory - torch.cuda.memory_reserved(device),
                supports_amp=True,
                supports_bf16=torch.cuda.is_bf16_supported(),
                tensor_core_support=(props.major >= 7),
                num_sms=props.multi_processor_count,
                driver_version=None,
            )
        elif device_type == "mps":
            return DeviceInfo(
                device_name="Apple Silicon",
                device_type="MPS",
                cuda_version=None,
                cudnn_version=None,
                compute_capability=None,
                total_memory=0,  # MPS doesn't easily expose this
                free_memory=0,
                supports_amp=True,
                supports_bf16=False,
                tensor_core_support=False,
                num_sms=None,
                driver_version=None,
            )
        else:
            return DeviceInfo(
                device_name="CPU",
                device_type="CPU",
                cuda_version=None,
                cudnn_version=None,
                compute_capability=None,
                total_memory=0,
                free_memory=0,
                supports_amp=False,
                supports_bf16=False,
                tensor_core_support=False,
                num_sms=None,
                driver_version=None,
            )
