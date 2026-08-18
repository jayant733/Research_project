from typing import Any, List, Optional

import numpy as np
import torch
from torch.utils.data import DataLoader

from packages.common.model_interface import IModel


class RealModel(IModel):
    """A concrete implementation of IModel that wraps a PyTorch nn.Module."""

    def __init__(self, model: torch.nn.Module, device: str = "cpu"):
        self.model = model
        self.device = torch.device(device)
        self.model.to(self.device)
        
    def get_weights(self) -> List[np.ndarray]:
        """Returns the current model weights as a list of NumPy arrays."""
        return [val.cpu().numpy() for _, val in self.model.state_dict().items()]

    def set_weights(self, weights: List[np.ndarray]) -> None:
        """Sets the model weights from a list of NumPy arrays."""
        import collections
        state_dict = collections.OrderedDict(
            {k: torch.tensor(v) for k, v in zip(self.model.state_dict().keys(), weights)}
        )
        self.model.load_state_dict(state_dict, strict=True)

    def train(self, data: Any = None, epochs: int = 1, lr: float = 0.01) -> float:
        """
        Trains the model locally.
        
        Args:
            data: A PyTorch DataLoader containing the training data.
            epochs: Number of local epochs.
            lr: Learning rate.
            
        Returns:
            The average training loss over the last epoch.
        """
        if not isinstance(data, DataLoader):
            raise ValueError("RealModel requires a PyTorch DataLoader for training data.")
            
        criterion = torch.nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(self.model.parameters(), lr=lr, momentum=0.9)
        
        self.model.train()
        avg_loss = 0.0
        
        for _ in range(epochs):
            total_loss = 0.0
            num_batches = 0
            
            for batch_x, batch_y in data:
                batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                num_batches += 1
                
            if num_batches > 0:
                avg_loss = total_loss / num_batches
                
        return avg_loss

    def evaluate(self, data: Any = None) -> float:
        """
        Evaluates the model.
        
        Args:
            data: A PyTorch DataLoader containing the test data.
            
        Returns:
            The accuracy [0.0, 1.0].
        """
        if not isinstance(data, DataLoader):
            raise ValueError("RealModel requires a PyTorch DataLoader for evaluation data.")
            
        self.model.eval()
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch_x, batch_y in data:
                batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)
                outputs = self.model(batch_x)
                _, predicted = torch.max(outputs.data, 1)
                total += batch_y.size(0)
                correct += (predicted == batch_y).sum().item()
                
        if total == 0:
            return 0.0
        return float(correct / total)
