import argparse
import os

import numpy as np
import torch
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split


def generate_healthcare_data(num_samples: int = 10000, num_features: int = 15):
    """Generates synthetic healthcare data for binary classification."""
    X, y = make_classification(
        n_samples=num_samples,
        n_features=num_features,
        n_informative=10,
        n_redundant=2,
        n_classes=2,
        random_state=42,
        shuffle=True
    )
    return X.astype(np.float32), y.astype(np.int64)

def partition_data_dirichlet(X: np.ndarray, y: np.ndarray, num_clients: int, alpha: float = 0.5):
    """Partitions data across clients using a Dirichlet distribution for non-IID data."""
    num_classes = len(np.unique(y))
    client_indices = {i: [] for i in range(num_clients)}
    
    for c in range(num_classes):
        idx_c = np.where(y == c)[0]
        np.random.shuffle(idx_c)
        
        # Draw proportions for each client from Dirichlet
        proportions = np.random.dirichlet(np.repeat(alpha, num_clients))
        
        # Scale proportions to actual number of elements
        splits = (proportions * len(idx_c)).astype(int)
        
        # Handle rounding errors by adjusting the last split
        splits[-1] = len(idx_c) - splits[:-1].sum()
        
        # Split the indices for this class
        split_indices = np.split(idx_c, np.cumsum(splits)[:-1])
        
        for i in range(num_clients):
            client_indices[i].extend(split_indices[i])
            
    # Compile final datasets
    client_data = {}
    for i in range(num_clients):
        indices = client_indices[i]
        np.random.shuffle(indices) # Shuffle each client's data
        X_client = X[indices]
        y_client = y[indices]
        client_data[i] = (X_client, y_client)
        
    return client_data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clients", type=int, default=3, help="Number of clients to partition for")
    parser.add_argument("--samples", type=int, default=10000, help="Total number of samples")
    parser.add_argument("--outdir", type=str, default="data/healthcare", help="Output directory")
    args = parser.parse_args()
    
    os.makedirs(args.outdir, exist_ok=True)
    
    print(f"Generating {args.samples} synthetic healthcare samples...")
    X, y = generate_healthcare_data(num_samples=args.samples)
    
    print(f"Partitioning across {args.clients} clients (non-IID Dirichlet)...")
    client_data = partition_data_dirichlet(X, y, args.clients)
    
    for i in range(args.clients):
        X_c, y_c = client_data[i]
        # Split into train/test
        X_train, X_test, y_train, y_test = train_test_split(X_c, y_c, test_size=0.2, random_state=42)
        
        data_dict = {
            "x_train": torch.tensor(X_train),
            "y_train": torch.tensor(y_train),
            "x_test": torch.tensor(X_test),
            "y_test": torch.tensor(y_test)
        }
        
        filepath = os.path.join(args.outdir, f"client_{i}.pt")
        torch.save(data_dict, filepath)
        print(f"Client {i} data saved to {filepath} | Train: {len(X_train)}, Test: {len(X_test)}")
        
    # Save a global test set (e.g. for server-side evaluation if needed)
    X_train_g, X_test_g, y_train_g, y_test_g = train_test_split(X, y, test_size=0.1, random_state=42)
    global_dict = {
        "x_test": torch.tensor(X_test_g),
        "y_test": torch.tensor(y_test_g)
    }
    torch.save(global_dict, os.path.join(args.outdir, "global_test.pt"))
    print(f"Global test set saved. Total test samples: {len(X_test_g)}")
    
if __name__ == "__main__":
    main()
