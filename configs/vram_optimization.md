# VRAM Optimization Configuration

## Model Settings

### Low VRAM (<=4GB)
- Use 4-bit/8-bit quantized models (.safetensors)
- Enable model offloading
- Use tile-based processing

### Standard VRAM (8-16GB)
- Use optimized .ckpt files
- Enable VRAM-aware checkpoint saving
- Use progressive upscaling

### High VRAM (>16GB)
- Use full-precision .pth files
- Disable model offloading
- Enable multi-resolution processing

## Workflow Settings
- Add VRAM mode selector (dropdown)
- Include VRAM requirements in model metadata
- Add progress tracking for memory usage
- Enable automatic model optimization based on system specs