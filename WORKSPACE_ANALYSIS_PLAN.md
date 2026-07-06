# Workspace Analysis & Future Planning v2.0

**Project:** Laura Image Studio v0.8 — Viral Video Edition
**Last Updated:** 2026-03-03
**Status:** Production Ready (107 nodes, 15 modules, 3 premium workflows)

---

## Current Architecture

### Repository Structure
- **Public GitHub Repo** (`snrtherock/Laura-Image-Studio`): Custom node source code only
- **Private/Local**: Premium workflow JSONs (Patreon/Buy Me a Coffee distribution)
- **Submodule**: Installed into ComfyUI at `custom_nodes/Laura_Image_Studio/`

### Node Suite (107 Nodes across 15 Modules)

| Module | Nodes | Focus Area |
|--------|-------|------------|
| models.py | 12 | Universal model loading, LoRA management, ControlNet |
| video_advanced.py | 11 | Wan 2.2, CogVideoX, Cosmos-Predict, HunyuanDiT, VRAM Cleaner |
| dressing.py | 10 | Virtual dressing room, IPAdapter clothing/style references |
| toggle.py | 9 | Pipeline switches (Image, Latent, Mask, Model, CLIP, VAE, Conditioning) |
| upscaling.py | 9 | 2K/4K/8K upscale, SUPIR+RIFE cinema upscale, detail enhancement |
| face.py | 9 | Detection, swapping (ReActor), IPAdapter face, LivePortrait v2 |
| video.py | 8 | I2V, V2V, frame interpolation, video face swap, video upscale |
| inpainting.py | 7 | SAM2 masks, inpainting, outpainting, object removal |
| background.py | 7 | Background removal/replacement/generation, bokeh, pro lighting |
| generation.py | 6 | SDXL generation, prompt builder, seed control, negative prompts |
| quantization.py | 5 | VRAM auto-detect, quantization config, model offloading |
| checkpoint.py | 5 | Pipeline checkpointing, auto-save, resume from checkpoint |
| batch_processing.py | 4 | Batch queues, prompt lists, batch iteration |
| tile_processing.py | 3 | Tile split/merge/inpaint for high-res processing |
| comparison.py | 2 | Multi-model comparison grid, professional background presets |

### Premium Workflow Editions

| Edition | Target | Key Differentiator |
|---------|--------|-------------------|
| **Community** | Free tier / 8GB VRAM | Wan 2.2 1.3B, open-source models only |
| **Studio** | Patreon / 12GB+ VRAM | Wan 2.2 14B, CogVideoX-5B, SUPIR cinema upscale |
| **Hybrid** | Premium / 12GB+ VRAM | Multi-engine (Wan + CogVideoX + Cosmos), LivePortrait v2 face animation |

---

## Supported Models & Frameworks (2025-2026)

### Image Generation
| Model | Source | VRAM | Notes |
|-------|--------|------|-------|
| FLUX.1 Dev | Black Forest Labs | 12GB | High-quality guidance-distilled |
| FLUX.1 Schnell | Black Forest Labs | 8GB | Fast 4-step distilled |
| SD 3.5 Medium/Large | Stability AI | 8-12GB | High prompt adherence |
| HunyuanImage 3.0 | Tencent | 80GB+ (offload OK) | SOTA quality |
| SDXL 1.0 | Stability AI | 8GB | Broad ecosystem |

### Video Generation
| Model | Source | VRAM | Notes |
|-------|--------|------|-------|
| Wan 2.2 14B (T2V/I2V) | Wan-AI | 12GB+ (FP8) | Current SOTA open-source video |
| Wan 2.2 1.3B | Wan-AI | 6GB | Low-VRAM variant |
| CogVideoX 5B/2B | THUDM | 8-12GB | Optimized for local GPUs |
| NVIDIA Cosmos-Predict 2.5 | NVIDIA | 12GB+ | World-model cinematic video |
| HunyuanVideo | Tencent | 12GB+ | High temporal consistency |
| AnimateDiff (SDXL) | Community | 8GB | Stylized video |

### Face & Enhancement
| Model | Source | VRAM | Notes |
|-------|--------|------|-------|
| LivePortrait v2 | Community | 4GB | Face animation / video driving |
| ReActor | Community | 4GB | Face swap |
| SUPIR | Community | 8GB | Cinema-grade upscaling |
| RIFE v4 | Community | 2GB | 60fps frame interpolation |
| SAM 2 | Meta | 4GB | Segment Anything for masks |
| IPAdapter Plus | Community | 4GB | Style/face/clothing reference |

### Utility
| Model | Source | Purpose |
|-------|--------|---------|
| RMBG 2.0 | BRIA AI | Background removal |
| ControlNet (multiple) | Community | Pose/depth/canny guidance |
| Various LoRAs | Community | Character/style customization |

---

## Official Model Download Links

| Model | Repository | Primary Asset |
|-------|------------|---------------|
| FLUX.1 Dev | [black-forest-labs/FLUX.1-dev](https://huggingface.co/black-forest-labs/FLUX.1-dev) | flux1-dev.safetensors |
| FLUX.1 Schnell | [black-forest-labs/FLUX.1-schnell](https://huggingface.co/black-forest-labs/FLUX.1-schnell) | flux1-schnell.safetensors |
| Wan 2.2 14B T2V | [Wan-AI/Wan2.2-T2V-14B](https://huggingface.co/Wan-AI/Wan2.2-T2V-14B) | wan2.2_t2v_14b.safetensors |
| Wan 2.2 14B I2V | [Wan-AI/Wan2.2-I2V-14B-720P](https://huggingface.co/Wan-AI/Wan2.2-I2V-14B-720P) | wan2.2_i2v_14b_720p.safetensors |
| Wan 2.2 1.3B T2V | [Wan-AI/Wan2.2-T2V-1.3B](https://huggingface.co/Wan-AI/Wan2.2-T2V-1.3B) | wan2.2_t2v_1.3b_480p.safetensors |
| CogVideoX 5B | [THUDM/CogVideoX-5b](https://huggingface.co/THUDM/CogVideoX-5b) | Built-in VAE |
| SD 3.5 Medium | [stabilityai/stable-diffusion-3.5-medium](https://huggingface.co/stabilityai/stable-diffusion-3.5-medium) | sd3.5_medium.safetensors |
| NVIDIA Cosmos | [nvidia/Cosmos-1.0-Predict-Diffusion-7B](https://huggingface.co/nvidia) | Cosmos model + VAE |
| LivePortrait | [Kijai/LivePortrait_safetensors](https://huggingface.co/Kijai/LivePortrait_safetensors) | liveportrait_model.safetensors |
| SUPIR | [Kijai/SUPIR_safetensors](https://huggingface.co/Kijai/SUPIR_safetensors) | SUPIR_v0.safetensors |

---

## VRAM Tier Strategy (8 Tiers — Matches quantization.py Code)

| Tier | VRAM | Quantization | CPU Offload | Max Resolution | Best Models |
|------|------|-------------|-------------|---------------|-------------|
| Ultra Low | 2-4GB | INT8 | Yes (Sequential) | 512x512 | SD 1.5, Pixart |
| Low | 4-6GB | FP16 | Yes | 768x768 | SD 3.5 Medium |
| Medium | 6-8GB | FP16 | Optional | 1024x1024 | SDXL, Kolors |
| High | 8-12GB | FP16 | No | 1024x1024 | FLUX, Wan 1.3B |
| Very High | 12-16GB | FP16 | No | 1024x1024 | FLUX 2x, Wan 14B (FP8) |
| Ultra | 16-24GB | FP16 | No | 1024x1024 | All models |
| Extreme | 24GB+ | Full | No | 1536x1536 | Wan 2.2, CogVideoX |
| HPC | 80GB+ | Full | No | 2048x2048 | HunyuanImage-3.0 |

The `VRAMAutoDetector` node automatically selects the appropriate tier and configures:
- `load_device`: GPU vs CPU offload
- `precision`: FP32 / FP16 / BF16 / FP8
- `resolution`: Capped per available memory
- Model variant selection (14B vs 1.3B)

---

## Future Roadmap (v0.9 and beyond)

### v0.9 — Polish & Community Launch
- [ ] ComfyUI-Manager full compatibility (node_config.json + model-list.json)
- [ ] End-to-end workflow testing on 8GB / 12GB / 24GB GPUs
- [ ] Video tutorial for each workflow edition
- [ ] Patreon / Buy Me a Coffee storefront setup
- [ ] Community feedback integration

### v1.0 — Stable Release
- [ ] Character LoRA training pipeline node
- [ ] Trigger word auto-detection from LoRA metadata
- [ ] Model sync script (auto-download all required models)
- [ ] Web UI dashboard for workflow management
- [ ] Multi-language prompt support

### v1.1+ — Advanced Features
- [ ] Real-time preview node (streaming inference)
- [ ] Cloud GPU offload support (RunPod / Vast.ai integration)
- [ ] A/B testing node for comparing generation parameters
- [ ] Audio-driven lip sync (WAV2Lip / SadTalker integration)
- [ ] Automated social media posting pipeline

---

## UX Improvement Recommendations

1. **Auto VRAM Tiers**: The `quantization.py` module already detects VRAM and applies appropriate precision/offload settings automatically.
2. **Model Sync Script**: A `scripts/model_downloader.py` using `huggingface_hub` to download all required models to correct ComfyUI paths (implemented but needs testing).
3. **Character LoRA Uploader**: `CharacterLoRALoader` node supports loading from local path or HF URL with single-click application.
4. **Trigger Word Detection**: Future feature to auto-extract trigger words from LoRA metadata and append to prompt builder.
5. **Crash Recovery**: `ResumeFromCheckpoint` node allows recovering interrupted pipelines from the last saved stage.

---

*Document version: 2.0*
*Previous version: 1.0 (v0.5 era, 45 lines)*
*Maintained by: snrtherock*
