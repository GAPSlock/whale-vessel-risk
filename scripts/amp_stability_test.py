import torch
import gc
import math
from neuralop.models import TFNO

def check_amp_stability(mode='fp32', steps=20, batch_size=4, tile_size=64):
    device = 'cuda'
    in_channels = 36
    out_channels = 12
    
    model = TFNO(n_modes=(16, 16), hidden_channels=32, in_channels=in_channels, 
                 out_channels=out_channels, n_layers=4, factorization='tucker', rank=0.1).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    
    x = torch.randn(batch_size, in_channels, tile_size, tile_size, device=device)
    y = torch.randn(batch_size, out_channels, tile_size, tile_size, device=device)
    
    torch.cuda.reset_peak_memory_stats()
    
    print(f"--- Running Stability Test: {mode.upper()} ---")
    for step in range(steps):
        optimizer.zero_grad()
        
        if mode == 'autocast_fp16':
            with torch.amp.autocast('cuda', dtype=torch.float16):
                out = model(x)
                loss = torch.nn.functional.mse_loss(out, y)
            loss.backward()
        elif mode == 'autocast_bf16':
            with torch.amp.autocast('cuda', dtype=torch.bfloat16):
                out = model(x)
                loss = torch.nn.functional.mse_loss(out, y)
            loss.backward()
        else:
            out = model(x)
            loss = torch.nn.functional.mse_loss(out, y)
            loss.backward()
            
        # Compute grad norm
        grad_norm = 0.0
        has_nan = False
        for p in model.parameters():
            if p.grad is not None:
                if torch.isnan(p.grad).any() or torch.isinf(p.grad).any():
                    has_nan = True
                
                # Handling complex types for norm
                if p.grad.is_complex():
                    grad_norm += p.grad.abs().detach().norm(2).item() ** 2
                else:
                    grad_norm += p.grad.detach().norm(2).item() ** 2
        grad_norm = math.sqrt(grad_norm)
        
        if has_nan or math.isnan(loss.item()) or math.isinf(loss.item()):
            print(f"Step {step}: Loss = {loss.item():.4f}, GradNorm = {grad_norm:.4f} -> NaN/Inf DETECTED. Instability found.")
            break
            
        optimizer.step()
        if step % 5 == 0 or step == steps - 1:
            print(f"Step {step}: Loss = {loss.item():.4f}, GradNorm = {grad_norm:.4f}")
            
    peak_alloc = torch.cuda.max_memory_allocated() / (1024**2)
    print(f"Peak VRAM Allocated: {peak_alloc:.2f} MB\n")
    
    del model, optimizer, x, y
    torch.cuda.empty_cache()
    gc.collect()

if __name__ == "__main__":
    check_amp_stability('fp32')
    check_amp_stability('autocast_fp16')
    if torch.cuda.is_bf16_supported():
        check_amp_stability('autocast_bf16')
    else:
        print("BF16 not supported on this device.")
