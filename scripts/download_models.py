import os
import torch
import torchvision.models as models

def main():
    print("Initializing model caching directory...")
    cache_dir = "data/models"
    os.makedirs(cache_dir, exist_ok=True)

    # 1. Healthcare: ResNet18 (Pre-trained weights for feature extraction)
    print("Downloading ResNet18 for Healthcare Chest X-Ray...")
    resnet18 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    torch.save(resnet18.state_dict(), os.path.join(cache_dir, "resnet18_baseline.pt"))

    # 2. Image Classification: MobileNetV3-Small (Lightweight client-side model)
    print("Downloading MobileNetV3-Small for Image Classification (CIFAR)...")
    mobilenet = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
    torch.save(mobilenet.state_dict(), os.path.join(cache_dir, "mobilenet_v3_small.pt"))

    # 3. Finance & IoT: Custom MLP & 1D-CNN Architectures (blueprints saved as state)
    print("Creating blueprints for custom MLP and 1D-CNN...")
    mlp_model = torch.nn.Sequential(
        torch.nn.Linear(30, 64),
        torch.nn.ReLU(),
        torch.nn.Dropout(0.2),
        torch.nn.Linear(64, 32),
        torch.nn.ReLU(),
        torch.nn.Linear(32, 2)
    )
    torch.save(mlp_model.state_dict(), os.path.join(cache_dir, "mlp_finance.pt"))

    cnn1d_model = torch.nn.Sequential(
        torch.nn.Conv1d(in_channels=1, out_channels=16, kernel_size=3, padding=1),
        torch.nn.ReLU(),
        torch.nn.MaxPool1d(kernel_size=2),
        torch.nn.Flatten(),
        torch.nn.Linear(16 * 14, 32), # Assuming input length 30 features
        torch.nn.ReLU(),
        torch.nn.Linear(32, 2)
    )
    torch.save(cnn1d_model.state_dict(), os.path.join(cache_dir, "cnn1d_iot.pt"))

    print(f"All model checkpoints successfully cached to: {os.path.abspath(cache_dir)}")

if __name__ == "__main__":
    main()
