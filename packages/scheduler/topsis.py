from typing import Dict, List, Tuple

import numpy as np

from packages.telemetry.vectors import TelemetryVector


class TOPSISEngine:
    """Implementation of the TOPSIS multi-criteria decision algorithm for scoring clients."""

    def __init__(self, weights: Dict[str, float]):
        """
        Args:
            weights: Dictionary containing weights for each criteria. Must sum to 1.0.
                     Expected keys: w_cpu, w_memory, w_bandwidth, w_battery, w_sensitivity.
        """
        self.weights = np.array([
            weights.get("w_cpu", 0.2),
            weights.get("w_memory", 0.2),
            weights.get("w_bandwidth", 0.2),
            weights.get("w_battery", 0.2),
            weights.get("w_sensitivity", 0.2)
        ])
        
        # Normalize weights just in case
        weight_sum = np.sum(self.weights)
        if weight_sum > 0:
            self.weights = self.weights / weight_sum

    def compute_scores(self, clients_data: Dict[str, Tuple[TelemetryVector, float]]) -> Dict[str, float]:
        """
        Computes TOPSIS relative closeness scores for each client.
        
        Args:
            clients_data: Mapping from client_id to a tuple of (TelemetryVector, sensitivity_score).
            
        Returns:
            Dictionary mapping client_id to their computed TOPSIS score [0.0, 1.0].
        """
        if not clients_data:
            return {}

        client_ids = list(clients_data.keys())
        num_clients = len(client_ids)
        
        # 1. Build Decision Matrix (rows: clients, cols: criteria)
        # Criteria: [cpu (max), memory (max), bandwidth (max), battery (max), sensitivity (min)]
        # We want to maximize resource availability, but minimize sensitivity for generic high-tier placement.
        # Actually, for RATC, high score = capable of doing FHE.
        # So we want MAX: cpu, memory, bandwidth, battery.
        # And we want MAX sensitivity to route highly sensitive data to FHE.
        # Thus, all criteria are "benefit" criteria for the purpose of getting a high score = FHE tier.
        
        matrix = np.zeros((num_clients, 5))
        for i, cid in enumerate(client_ids):
            telemetry, sensitivity = clients_data[cid]
            # Invert CPU/Mem/Net/Disk usages from TelemetryVector? 
            # TelemetryVector gives usages (0=idle, 1=full load).
            # To be capable of FHE, we want HIGH available resources, so we want LOW usage.
            # So available = 1.0 - usage
            matrix[i, 0] = max(0.0, 1.0 - telemetry.cpu_usage)
            matrix[i, 1] = max(0.0, 1.0 - telemetry.memory_usage)
            matrix[i, 2] = telemetry.network_bandwidth # Assuming this is available bandwidth
            matrix[i, 3] = telemetry.battery_level
            matrix[i, 4] = sensitivity
            
        # 2. Vector Normalization
        norm_matrix = np.zeros_like(matrix)
        for j in range(5):
            col_norm = np.linalg.norm(matrix[:, j])
            if col_norm == 0:
                norm_matrix[:, j] = 0
            else:
                norm_matrix[:, j] = matrix[:, j] / col_norm
                
        # 3. Apply Weights
        weighted_matrix = norm_matrix * self.weights
        
        # 4. Determine Ideal Best (V+) and Ideal Worst (V-)
        # All criteria are benefits in our formulation.
        v_plus = np.max(weighted_matrix, axis=0)
        v_minus = np.min(weighted_matrix, axis=0)
        
        # 5. Calculate Distances
        scores = {}
        for i, cid in enumerate(client_ids):
            d_plus = np.linalg.norm(weighted_matrix[i] - v_plus)
            d_minus = np.linalg.norm(weighted_matrix[i] - v_minus)
            
            # 6. Calculate Relative Closeness
            if d_plus + d_minus == 0:
                scores[cid] = 0.0
            else:
                scores[cid] = float(d_minus / (d_plus + d_minus))
                
        return scores
