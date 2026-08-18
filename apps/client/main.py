# apps/client/main.py
import argparse
import sys

import torch
from torch.utils.data import DataLoader, TensorDataset

from packages.common.client import GenericClient
from packages.common.real_model import RealModel
from packages.flower.client_adapter import FlowerClientAdapter
from packages.privacy.engine import PrivacyEngine
from packages.telemetry.simulator import SimulatedTelemetryProvider
from packages.training.providers.pytorch.healthcare_model import HealthcareMLP


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-id", type=str, required=True)
    parser.add_argument("--profile", type=str, default="mobile")
    parser.add_argument("--data", type=str, required=True, help="Path to .pt data file")
    parser.add_argument("--tier", type=str, default="TIER_3_DP_PLAIN")
    args = parser.parse_args()

    print(f"Starting Client Node {args.client_id}...", flush=True)

    # 1. Load Data
    try:
        data_dict = torch.load(args.data)
        train_dataset = TensorDataset(data_dict["x_train"], data_dict["y_train"])
        test_dataset = TensorDataset(data_dict["x_test"], data_dict["y_test"])
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=32)
    except Exception as e:
        print(f"Error loading data from {args.data}: {e}", file=sys.stderr)
        sys.exit(1)

    # 2. Initialize Model
    torch_model = HealthcareMLP(input_dim=15)
    model = RealModel(torch_model, device="cpu")

    # 3. Initialize Telemetry & Privacy
    telemetry = SimulatedTelemetryProvider(profile_name=args.profile, profiles_config=[])
    privacy = PrivacyEngine(tier_name=args.tier)

    # 4. Initialize Core Client logic
    generic_client = GenericClient(model=model, data=train_loader)

    # 5. Initialize Flower Adapter
    flower_adapter = FlowerClientAdapter(generic_client)

    print(f"Client {args.client_id} (Profile: {args.profile}, Tier: {args.tier}) initialized.", flush=True)
    
    # Normally we'd start flwr.client.start_client here.
    # For script testing, we leave it to the runner.
    import flwr as fl
    try:
        fl.client.start_client(server_address="127.0.0.1:8081", client=flower_adapter)
    except Exception as e:
        print(f"Client {args.client_id} stopped: {e}")


if __name__ == "__main__":
    main()
