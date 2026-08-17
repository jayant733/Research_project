"""
Dynamic plugin registries avoiding hardcoded switch statements.
"""

from typing import Any, Dict

from packages.training.domain.exceptions import ModelInitializationError
from packages.training.domain.interfaces import BaseTrainer, IModel


class Registry:
    """Generic base registry."""

    def __init__(self):
        self._registry: Dict[str, Any] = {}

    def register(self, name: str, item: Any) -> None:
        self._registry[name] = item

    def get(self, name: str) -> Any:
        if name not in self._registry:
            raise KeyError(f"'{name}' not found in registry.")
        return self._registry[name]


class ModelRegistry(Registry):
    """Dynamic registry for model architectures."""

    def get(self, name: str, **kwargs) -> IModel:
        try:
            model_class = super().get(name)
            return model_class(**kwargs)
        except KeyError as e:
            raise ModelInitializationError(str(e))


class ProviderRegistry(Registry):
    """Dynamic registry for training providers (e.g. PyTorch, JAX)."""

    def get_trainer(self, name: str, **kwargs) -> BaseTrainer:
        provider_class = self.get(name)
        return provider_class(**kwargs)


class CallbackRegistry(Registry):
    """Dynamic registry for available callbacks."""

    pass


# Global singletons
model_registry = ModelRegistry()
provider_registry = ProviderRegistry()
callback_registry = CallbackRegistry()
