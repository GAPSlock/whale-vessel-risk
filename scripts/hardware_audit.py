import os
import sys
import yaml
import torch

def get_gpu_info():
    if not torch.cuda.is_available():
        print("CUDA is not available.")
        sys.exit(1)
    
    device = torch.device('cuda')
    props = torch.cuda.get_device_properties(device)
    vram_gb = props.total_memory / (1024**3)
    
    print(f"Detected GPU: {props.name}")
    print(f"Total VRAM: {vram_gb:.2f} GB")
    print(f"Compute Capability: {props.major}.{props.minor}")
    
    return {
        "name": props.name,
        "vram_gb": vram_gb,
        "compute_capability": f"{props.major}.{props.minor}"
    }

def benchmark_tfno(batch_size, tile_size, hidden_channels=32, n_modes=(16, 16), n_layers=4):
    try:
        from neuralop.models import TFNO
    except ImportError:
        print("neuraloperator is not installed. Please install it first.")
        sys.exit(1)
        
    device = torch.device('cuda')
    
    in_channels = 9 * 4 # 9 features * 4 time steps
    out_channels = 12 # 12 future time steps
    
    try:
        model = TFNO(
            n_modes=n_modes,
            hidden_channels=hidden_channels,
            in_channels=in_channels,
            out_channels=out_channels,
            n_layers=n_layers,
            factorization='tucker',
            rank=0.1
        ).to(device)
        
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
        
        x = torch.randn(batch_size, in_channels, tile_size, tile_size, device=device)
        y = torch.randn(batch_size, out_channels, tile_size, tile_size, device=device)
        
        print(f"Testing config: batch_size={batch_size}, tile_size={tile_size}")
        
        for _ in range(3):
            optimizer.zero_grad()
            with torch.amp.autocast('cuda'):
                out = model(x)
                loss = torch.nn.functional.mse_loss(out, y)
            
            # Using standard backward instead of GradScaler to avoid ComplexFloat error
            loss.backward()
            optimizer.step()
            
        torch.cuda.empty_cache()
        return True
    except RuntimeError as e:
        if "out of memory" in str(e).lower():
            print(f"OOM at batch_size={batch_size}, tile_size={tile_size}")
            torch.cuda.empty_cache()
            return False
        else:
            raise e
            
def find_best_config():
    # Target configurations
    configs = [
        {"batch_size": 16, "tile_size": 64},
        {"batch_size": 8, "tile_size": 64},
        {"batch_size": 4, "tile_size": 64},
        {"batch_size": 2, "tile_size": 64},
        {"batch_size": 1, "tile_size": 64},
        {"batch_size": 8, "tile_size": 32},
        {"batch_size": 4, "tile_size": 32},
    ]
    
    for conf in configs:
        success = benchmark_tfno(**conf)
        if success:
            print(f"Found valid configuration: {conf}")
            return conf
            
    print("Could not find a configuration that fits in memory.")
    sys.exit(1)

def main():
    print("Starting Hardware Audit...")
    gpu_info = get_gpu_info()
    
    valid_config = find_best_config()
    
    config_data = {
        "hardware": gpu_info,
        "training": {
            "batch_size": valid_config["batch_size"],
            "tile_size": valid_config["tile_size"],
            "hidden_channels": 32,
            "n_modes": [16, 16],
            "n_layers": 4,
            "gradient_accumulation_steps": max(1, 32 // valid_config["batch_size"])
        }
    }
    
    os.makedirs('configs', exist_ok=True)
    with open('configs/hardware.yaml', 'w') as f:
        yaml.dump(config_data, f, default_flow_style=False)
        
    print("Hardware audit complete. Configuration saved to configs/hardware.yaml")

if __name__ == "__main__":
    main()
