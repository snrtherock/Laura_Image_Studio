# VRAM Optimization Configuration

> **DEPRECATED:** This file is superseded by the 8-tier auto-detection system in
> `custom_nodes/Laura_Image_Studio/nodes/quantization.py`.
> See `PLAN.md` Section 2 for the current VRAM tier matrix.

## Current VRAM Tiers (8 tiers + auto)

| Tier | VRAM Range | Quantization | CPU Offload | Max Resolution |
|------|-----------|-------------|-------------|---------------|
| ultra_low | 2-4GB | INT8 | Sequential | 512x512 |
| low | 4-6GB | FP16 | Yes | 768x768 |
| medium | 6-8GB | FP16 | Optional | 1024x1024 |
| high | 8-12GB | FP16 | No | 1024x1024 |
| very_high | 12-16GB | FP16 | No | 1024x1024 |
| ultra | 16-24GB | FP16 | No | 1024x1024 |
| extreme | 24-80GB | Full | No | 1536x1536 |
| hpc | 80GB+ | Full | No | 2048x2048 |

Managed by nodes: `VRAMAutoDetector`, `QuantizationSelector`, `ResolutionScaler`,
`ModelOffloadConfig`, `QuantizationConfig`.
