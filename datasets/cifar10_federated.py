import argparse
import os

import numpy as np
import torch
import torchvision
import torchvision.transforms as transforms


def get_cifar10(root: str = "data/cifar10"):
    """Downloads and loads CIFAR-10."""
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    trainset = torchvision.datasets.CIFAR10(root=root, train=True, download=True, transform=transform)
    testset = torchvision.datasets.CIFAR10(root=root, train=False, download=True, transform=transform)
    
    return trainset, testset

def partition_cifar10(trainset, num_clients: int, alpha: float = 0.5):
    """Partitions CIFAR-10 training set using Dirichlet distribution."""
    # CIFAR-10 has 50000 training images, 10 classes.
    y_train = np.array(trainset.targets)
    num_classes = 10
    
    client_indices = {i: [] for i in range(num_clients)}
    
    for c in range(num_classes):
        idx_c = np.where(y_train == c)[0]
        np.random.shuffle(idx_c)
        
        proportions = np.random.dirichlet(np.repeat(alpha, num_clients))
        splits = (proportions * len(idx_c)).astype(int)
        splits[-1] = len(idx_c) - splits[:-1].sum()
        
        split_indices = np.split(idx_c, np.cumsum(splits)[:-1])
        
        for i in range(num_clients):
            client_indices[i].extend(split_indices[i])
            
    return client_indices

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clients", type=int, default=3)
    parser.add_argument("--outdir", type=str, default="data/cifar10_partitions")
    args = parser.parse_args()
    
    os.makedirs(args.outdir, exist_ok=True)
    
    print("Downloading CIFAR-10...")
    trainset, testset = get_cifar10()
    
    print(f"Partitioning across {args.clients} clients...")
    client_indices = partition_cifar10(trainset, args.clients)
    
    # We save the indices instead of the full tensors to save space.
    # The client can load CIFAR-10 and use a Subset.
    for i in range(args.clients):
        indices = client_indices[i]
        np.random.shuffle(indices)
        
        filepath = os.path.join(args.outdir, f"client_{i}_indices.pt")
        torch.save({"indices": indices}, filepath)
        print(f"Client {i} allocated {len(indices)} samples.")
        
if __name__ == "__main__":
    main()
