# Workspace Analysis & Future Planning

## Best Open-Source Models (2025-2026)

### Image Generation
- **FLUX.1 Family (Black Forest Labs):** Schnell (Distilled), Dev (Guidance-distilled), Pro (API-only). Top quality in 2025.
- **SD3.5 Medium/Large:** Stability AI's latest. High prompt adherence.
- **HunyuanImage-3.0:** Tencent's 80GB model, SOTA quality.
- **Kolors:** XL-sized Chinese model with excellent detail.
- **Z-Image:** Emerging open-weight model specialized in photorealism.
- **Pixart Sigma:** Efficient 4K generation.

### Image Editing
- **Qwen2-VL:** Multimodal editing and understanding.
- **InstructPix2Pix (Updated variants):** Direct instruction-based editing.
- **SAM 2 (Segment Anything):** For mask-based selective editing.

### Video Generation & Editing
- **Wan 2.2:** Currently SOTA for open video (14B, 1.3B variants).
- **HunyuanVideo:** Tencent's video DiT, high temporal consistency.
- **CogVideoX-5B/2B:** Optimized for local GPUs.
- **NVIDIA Cosmos-Predict 2.5:** World-model based cinematic video.
- **AnimateDiff (SDXL variants):** Continued community SOTA for stylized video.

## Official Model Links & Resources

| Model | Repository / Official Link | VAE / Specialized Assets |
|-------|----------------------------|--------------------------|
| FLUX.1 Dev | [HF/black-forest-labs/FLUX.1-dev](https://huggingface.co/black-forest-labs/FLUX.1-dev) | ae.safetensors |
| FLUX.1 Schnell | [HF/black-forest-labs/FLUX.1-schnell](https://huggingface.co/black-forest-labs/FLUX.1-schnell) | ae.safetensors |
| Wan 2.2 | [HF/Wan-AI/Wan2.2-14B-T2V](https://huggingface.co/Wan-AI/Wan2.2-14B-T2V) | wan_vae.safetensors |
| CogVideoX | [HF/THUDM/CogVideoX-5b](https://huggingface.co/THUDM/CogVideoX-5b) | Built-in |
| SD 3.5 Medium | [HF/stabilityai/stable-diffusion-3.5-medium](https://huggingface.co/stabilityai/stable-diffusion-3.5-medium) | sd3_vae.safetensors |
| HunyuanImage | [HF/Tencent-Hunyuan/HunyuanImage-v3.0](https://huggingface.co/Tencent-Hunyuan/HunyuanImage-v3.0) | Multi-stage assets |
| NVIDIA Cosmos | [HF/nvidia/Cosmos-1.0-Predict-Diffusion-7B-Video2World](https://huggingface.co/nvidia) | Cosmos VAE |

## Recommendation for UX Improvement

1. **Auto VRAM Tiers:** Enhance the existing `quantization.py` to not just detect, but *automatically* apply `load_device="offload"` and `precision="fp8"` if VRAM < 12GB for Flux/Wan models.
2. **Model Sync Script:** A Python script in the `scripts/` directory that uses `huggingface_hub` to download/update all required VAEs and model weights to the correct `ComfyUI/models/` paths.
3. **Character LoRA Uploader:** A dedicated node that takes a local path or HF URL, downloads the LoRA, and applies it to the current model pipeline with a single click.

## LoRA Influencer Support
- **CharacterLoRALoader:** (To be implemented) Node for users to load their trained character models easily.
- **TriggerWordDetection:** Auto-extracting trigger words from LoRA metadata to append to the prompt builder.
