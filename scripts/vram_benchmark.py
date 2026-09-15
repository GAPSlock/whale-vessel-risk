import torch
import gc
from neuralop.models import TFNO
import traceback

def print_mem(prefix):
    allocated = torch.cuda.memory_allocated() / (1024**2)
    reserved = torch.cuda.memory_reserved() / (1024**2)
    print(f"{prefix} - Allocated: {allocated:.2f} MB, Reserved: {reserved:.2f} MB")

def test_gradscaler_error():
    print("--- Testing GradScaler with ComplexFloat ---")
    device = 'cuda'
    model = TFNO(n_modes=(16, 16), hidden_channels=32, in_channels=36, out_channels=12, n_layers=4, factorization='tucker', rank=0.1).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    scaler = torch.amp.GradScaler('cuda')
    
    x = torch.randn(2, 36, 64, 64, device=device)
    y = torch.randn(2, 12, 64, 64, device=device)
    
    try:
        with torch.amp.autocast('cuda'):
            out = model(x)
            loss = torch.nn.functional.mse_loss(out, y)
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        print("GradScaler succeeded (unexpected).")
    except Exception as e:
        print("GradScaler failed as expected:")
        traceback.print_exc()
    
    del model, optimizer, scaler, x, y
    torch.cuda.empty_cache()
    gc.collect()

def run_benchmark(batch_size, tile_size=64, mode='fp32'):
    device = 'cuda'
    in_channels = 36
    out_channels = 12
    
    model = TFNO(n_modes=(16, 16), hidden_channels=32, in_channels=in_channels, out_channels=out_channels, n_layers=4, factorization='tucker', rank=0.1).to(device)
    
    # Force gradient checkpointing if available in neuralop, though TFNO might not expose it easily directly. 
    # We will just test baseline memory.
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    
    x = torch.randn(batch_size, in_channels, tile_size, tile_size, device=device)
    y = torch.randn(batch_size, out_channels, tile_size, tile_size, device=device)
    
    torch.cuda.reset_peak_memory_stats()
    
    try:
        for _ in range(3):
            optimizer.zero_grad()
            if mode == 'autocast':
                with torch.amp.autocast('cuda'):
                    out = model(x)
                    loss = torch.nn.functional.mse_loss(out, y)
                loss.backward() # NO GradScaler due to complexfloat bug
            else:
                out = model(x)
                loss = torch.nn.functional.mse_loss(out, y)
                loss.backward()
            optimizer.step()
            
        peak_alloc = torch.cuda.max_memory_allocated() / (1024**2)
        peak_res = torch.cuda.max_memory_reserved() / (1024**2)
        print(f"Batch {batch_size:2d} | Mode: {mode:8s} | Peak Alloc: {peak_alloc:7.2f} MB | Peak Rsvd: {peak_res:7.2f} MB")
        success = True
    except RuntimeError as e:
        if "out of memory" in str(e).lower():
            print(f"Batch {batch_size:2d} | Mode: {mode:8s} | OOM ERROR")
            success = False
        else:
            raise e
            
    del model, optimizer, x, y
    torch.cuda.empty_cache()
    gc.collect()
    return success

if __name__ == "__main__":
    print(f"PyTorch Version: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA Device Name: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Total Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**2):.2f} MB")
        
    test_gradscaler_error()
    
    print("\n--- Running Memory Benchmarks ---")
    for b in [4, 8, 12, 16, 20]:
        for mode in ['fp32', 'autocast']:
            run_benchmark(b, mode=mode)
