# Laura Image Studio - Complete Project Plan (v0.5+)

## Executive Summary

**Project Name:** Laura's Complete Image Studio (Best_Real_Image_Gen)
**Type:** ComfyUI Custom Nodes Package + Workflow Templates
**Purpose:** Truly all-in-one AI image generation, editing, virtual dressing, face manipulation, upscaling, and video creation system supporting ALL open-weight AI models with VRAM optimization for all hardware configurations
**Target Users:** Content creators, fashion designers, digital artists, AI enthusiasts with any GPU (2GB to 80GB+ VRAM)

---

## 1. Complete Model Support Matrix (Latest Open Weights - 2025/2026)

### 1.1 Image Generation Models

| Model | Type | Parameters | VRAM (FP16) | VRAM (INT8/Quantized) | Status | Source |
|-------|------|------------|-------------|----------------------|--------|--------|
| **SDXL 1.0** | Latent Diffusion | ~6.6B | 8-10GB | 4-5GB | ✅ Supported | Stability AI |
| **SD 1.5** | Latent Diffusion | ~860M | 4GB | 2GB | ✅ Supported | CompVis |
| **SD 2.1** | Latent Diffusion | ~1B | 5GB | 2.5GB | ✅ Supported | Stability AI |
| **SD 3.0** | Latent Diffusion | ~2B | 10GB | 5GB | ✅ Supported | Stability AI |
| **SD 3.5 Medium** | Latent Diffusion | ~2B | 6GB | 3GB | ✅ Supported | Stability AI |
| **FLUX.1 Schnell** | Rectified Flow | 12B | 16GB | 8GB | ✅ Supported | Black Forest Labs |
| **FLUX.1 Dev** | Rectified Flow | 12B | 16GB | 8GB | ✅ Supported | Black Forest Labs |
| **FLUX.2 Schnell** | Rectified Flow | 12B | 16GB | 8GB | ✅ Supported | Black Forest Labs |
| **FLUX.2 Dev** | Rectified Flow | 12B | 16GB | 8GB | ✅ Supported | Black Forest Labs |
| **Wan 2.1 T2V-14B** | Diffusion Transformer | 14B | 28GB | 14GB | ✅ Supported | Wan AI |
| **Wan 2.1 T2V-1.3B** | Diffusion Transformer | 1.3B | 8GB | 4GB | ✅ Supported | Wan AI |
| **Wan 2.2 T2V-A14B** | MoE Transformer | ~27B (14B active) | 24GB | 12GB | ✅ Supported | Wan AI |
| **Wan 2.2 I2V-A14B** | MoE Transformer | ~27B (14B active) | 24GB | 12GB | ✅ Supported | Wan AI |
| **HunyuanDiT-v1.2** | DiT | 1.5B | 11GB | 5GB | ✅ Supported | Tencent |
| **HunyuanImage-3.0** | MoE | 80B (13B active) | 240GB | 80GB+ | ✅ Supported | Tencent |
| **Kolors** | Latent Diffusion | ~5B | 10GB | 5GB | ✅ Supported | Kuaishou |
| **Pixart Sigma** | DiT | ~300M | 4GB | 2GB | ✅ Supported | Pixart |
| **Aura Flow** | Flow Matching | ~5B | 10GB | 5GB | ✅ Supported | Aura |
| **Playground v2.5** | Latent Diffusion | ~2B | 8GB | 4GB | ✅ Supported | Playground |
| **Lumina 3** | DiT | ~2B | 8GB | 4GB | ✅ Supported | Lumina |
| **Z-Image** | Diffusion | ~5B | 12GB | 6GB | ✅ Supported | Alibaba |
| **Qwen-Image** | Diffusion | ~5B | 12GB | 6GB | ✅ Supported | Alibaba |

### 1.2 Video Generation Models

| Model | Type | Parameters | VRAM (FP16) | VRAM (Quantized) | Status | Source |
|-------|------|------------|-------------|------------------|--------|--------|
| **CogVideoX-2B** | Diffusion Transformer | 2B | 12GB | 6GB | ✅ Supported | THUDM/Z.ai |
| **CogVideoX1.5-5B** | Diffusion Transformer | 5B | 20GB | 10GB | ✅ Supported | THUDM/Z.ai |
| **CogVideoX1.5-5B-I2V** | Diffusion Transformer | 5B | 16GB | 8GB | ✅ Supported | THUDM/Z.ai |
| **Wan 2.1 T2V** | Diffusion Transformer | 14B | 28GB | 14GB | ✅ Supported | Wan AI |
| **Wan 2.1 I2V** | Diffusion Transformer | 14B | 28GB | 14GB | ✅ Supported | Wan AI |
| **Wan 2.2 T2V-A14B** | MoE Transformer | ~27B | 24GB | 12GB | ✅ Supported | Wan AI |
| **Wan 2.2 I2V-A14B** | MoE Transformer | ~27B | 24GB | 12GB | ✅ Supported | Wan AI |
| **Wan 2.2 TI2V-5B** | Dense Transformer | 5B | 16GB | 8GB | ✅ Supported | Wan AI |
| **Cosmos-Predict2.5-14B** | World Model | 14B | 28GB | 14GB | ✅ Supported | NVIDIA |
| **LivePortrait v2** | Temporal Mesh | ~500M | 6GB | 4GB | 🔄 Add to Plan | Kuaishou |

### 1.3 Upscaling/Enhancement Models

| Model | Type | Parameters | VRAM | Status |
|-------|------|------------|------|--------|
| **4X-UltraSharp** | ESRGAN | ~2.5M | 2GB | ✅ Supported |
| **RealESRGAN_x4plus** | ESRGAN | ~1.5M | 2GB | ✅ Supported |
| **ScuNet** | CNN | ~10M | 2GB | ✅ Supported |
| **SUPIR-Video** | Diffusion Refiner | ~2B | 16GB | 🔄 Add to Plan |
| **RIFE v4** | Interpolation | ~50M | 4GB | 🔄 Add to Plan |

### 1.4 Face/Identity Models

| Model | Type | Purpose | VRAM | Status |
|-------|------|---------|------|--------|
| **inswapper_128.onnx** | ONNX | Face Swap | 1GB | ✅ Required |
| **IPAdapter FaceID** | IPAdapter | Face Embedding | 2GB | ✅ Required |
| **CodeFormer** | Face Restoration | Face Enhancement | 1GB | ✅ Required |
| **GFPGAN** | Face Restoration | Face Enhancement | 1GB | ✅ Required |

---

## 2. VRAM Optimization System

### 2.1 VRAM Tiers & Configuration

| VRAM Tier | Model Category | Optimization Strategy | Max Resolution |
|-----------|---------------|---------------------|---------------|
| **Ultra Low (2-4GB)** | SD 1.5, Pixart | INT8 quantization, tile processing | 512x512 |
| **Low (4-6GB)** | SDXL Refiner, SD 3.5 Medium | FP16, model offloading | 768x768 |
| **Medium (6-8GB)** | SDXL, Kolors, Playground | FP16, full resolution | 1024x1024 |
| **High (8-12GB)** | FLUX, Wan 1.3B, SD 3 | FP16, full resolution | 1024x1024 |
| **Very High (12-16GB)** | FLUX 2x, Wan 2.1 14B | FP16, batch 2 | 1024x1024 |
| **Ultra (16-24GB)** | All models | FP16, batch 4 | 1024x1024 |
| **Extreme (24GB+)** | Wan 2.2, CogVideoX | Full precision, batch 8 | 1024-1536 |
| **HPC (80GB+)** | HunyuanImage-3.0 | Full precision | 2048x2048 |

### 2.2 Optimization Techniques

1. **Quantization Support**
   - FP32 → FP16 → BF16 → INT8 → INT4
   - Automatic detection based on model metadata

2. **Memory Management**
   - Model offloading (CPU/GPU swap)
   - VAE tiling for large images
   - Gradient checkpointing for training
   - Lazy loading of models

3. **VRAM Auto-Detection System**
   ```python
   def get_vram_tier():
       vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
       if vram_gb < 4: return "ultra_low"
       elif vram_gb < 6: return "low"
       elif vram_gb < 8: return "medium"
       elif vram_gb < 12: return "high"
       elif vram_gb < 16: return "very_high"
       elif vram_gb < 24: return "ultra"
       else: return "extreme"
   ```

---

## 3. Workflow Architecture

### 3.1 Universal Pipeline Stages (6 Toggleable Stages)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TRULY ALL-IN-ONE WORKFLOW                           │
├─────────────────────────────────────────────────────────────────────────┤
│  Stage 1: MODEL SELECTION & LOADING (Auto-detect)                      │
│  ├── Universal Model Loader (20+ models)                              │
│  ├── Model Type Auto-Detection                                         │
│  ├── LoRA Manager (Character: Laura/Zoriana)                          │
│  ├── Multi-LoRA Stack (3 Loras)                                        │
│  ├── ControlNet Loader                                                 │
│  └── VRAM Auto-Optimization                                           │
├─────────────────────────────────────────────────────────────────────────┤
│  Stage 2: IMAGE GENERATION                                             │
│  ├── Text-to-Image                                                    │
│  ├── Image-to-Image                                                   │
│  ├── Prompt Builder (Quality presets)                                 │
│  ├── Seed Control                                                     │
│  └── Reference Image Input (IPAdapter) ◄ NEW                        │
├─────────────────────────────────────────────────────────────────────────┤
│  Stage 3: VIRTUAL DRESSING                                             │
│  ├── Clothing Segmentor (18 categories)                               │
│  ├── Accessory Detector                                               │
│  ├── Virtual Dresser                                                  │
│  ├── Dressing Room Compositor (6 items)                             │
│  ├── Hair Stylist                                                     │
│  ├── Makeup Artist                                                    │
│  └── Reference Image Support ◄ NEW                                   │
├─────────────────────────────────────────────────────────────────────────┤
│  Stage 4: FACE & IDENTITY                                             │
│  ├── Face Detector (19 features)                                      │
│  ├── Face Swapper (ReActor)                                          │
│  ├── IPAdapter Face Embedding                                         │
│  ├── Face Enhancer (CodeFormer/GFPGAN)                               │
│  ├── Multi-Face Handler                                               │
│  └── Expression Transfer                                              │
├─────────────────────────────────────────────────────────────────────────┤
│  Stage 5: BACKGROUND                                                  │
│  ├── Background Remover (4 models)                                    │
│  ├── Background Replacer                                              │
│  ├── Portrait Bokeh                                                   │
│  ├── Pro Lighting (8 presets)                                        │
│  ├── Background Generator                                             │
│  └── Seamless Tile                                                   │
├─────────────────────────────────────────────────────────────────────────┤
│  Stage 6: UPSCALING & OUTPUT                                          │
│  ├── 2K Upscale (4X)                                                 │
│  ├── 4K Upscale (4X)                                                 │
│  ├── 8K Upscale (4X)                                                 │
│  ├── Custom Resolution                                               │
│  ├── Detail Enhancer                                                 │
│  └── Tile-based Processing ◄ NEW                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Video Branch (Toggleable)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  VIDEO GENERATION STAGE (Optional Toggle)                              │
├─────────────────────────────────────────────────────────────────────────┤
│  ├── Image-to-Video (Wan 2.1/2.2, CogVideoX)                         │
│  ├── Video-to-Video (Style Transfer)                                  │
│  ├── Frame Interpolation (2x/4x/8x)                                   │
│  ├── Video Face Swap                                                  │
│  ├── Video Upscale                                                   │
│  └── Video Saver (MP4/GIF/WebM/PNG)                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Feature Enhancement Plan

### 4.1 High Priority Features

| Feature | Description | Status | Priority |
|---------|-------------|--------|----------|
| **VRAM Auto-Detection** | Auto-select quantization/resolution based on GPU | 🔄 In Progress | Critical |
| **Reference Image Support** | IPAdapter-based clothing reference input | 🔄 In Progress | High |
| **Model Type Auto-Detection** | Detect model from filename + metadata | ✅ Complete | Complete |
| **Universal Model Loader** | Single node for all model types | ✅ Complete | Complete |
| **Toggle System** | Enable/disable workflow stages | ✅ Complete | Complete |
| **Crash Recovery** | Checkpoint save/load system | ✅ Complete | Complete |

### 4.2 Medium Priority Features

| Feature | Description | Status | Priority |
|---------|-------------|--------|----------|
| **Batch Processing** | Queue multiple images | 🔄 Not Started | Medium |
| **Tile-based Upscaling** | Process large images in tiles | 🔄 Not Started | Medium |
| **Preset Backgrounds** | Library of backgrounds | 🔄 Not Started | Medium |
| **UI Improvements** | Preview nodes, better layouts | 🔄 Not Started | Medium |
| **Multi-Model Comparison** | Generate with multiple models at once | 🔄 Not Started | Medium |

### 4.3 Low Priority Features

| Feature | Description | Status | Priority |
|---------|-------------|--------|----------|
| **Character Presets** | Multiple saved characters | 🔄 Not Started | Low |
| **Style Presets** | Saved style configurations | 🔄 Not Started | Low |
| **Workflow Templates** | Community workflow sharing | 🔄 Not Started | Low |
| **API Integration** | External service integration | 🔄 Not Started | Low |

---

## 5. Node Implementation Status

### 5.1 Core Nodes (74+)

| Module | Nodes | Status | Notes |
|--------|-------|--------|-------|
| `models.py` | 9 | ✅ Complete | 20 model types |
| `dressing.py` | 8 | ✅ Complete | 18 clothing categories |
| `face.py` | 8 | ✅ Complete | ReActor/IPAdapter delegation |
| `inpainting.py` | 7 | ✅ Complete | SAM2 + GroundingDINO |
| `upscaling.py` | 6 | ✅ Complete | 2K/4K/8K |
| `background.py` | 7 | ✅ Complete | 4 RMBG models |
| `video.py` | 8 | ✅ Complete | Wan/AnimateDiff |
| `toggle.py` | 10 | ✅ Complete | 10 outputs |
| `checkpoint.py` | 5 | ✅ Complete | Save/Load/Resume |
| `generation.py` | 4 | ✅ Complete | SDXL-focused |

### 5.2 New Nodes to Add

| Module | Nodes | Purpose |
|--------|-------|---------|
| `quantization.py` | 5 | INT8/INT4 quantization, VRAM detection |
| `tile_processing.py` | 4 | Tile-based generation for large images |
| `batch_processing.py` | 6 | Queue management, batch generation |
| `video_advanced.py` | 6 | CogVideoX, Cosmos support |
| `comparison.py` | 4 | Multi-model comparison outputs |

---

## 6. User Experience Enhancements

### 6.1 Workflow Improvements

1. **Smart Default Settings**
   - Auto-configure CFG, steps, resolution per model
   - One-click optimal settings

2. **Preset System**
   - Model presets with optimal settings
   - Style presets (photorealistic, anime, artistic)
   - Quality presets (fast, balanced, quality)

3. **Visual Feedback**
   - Progress indicators per stage
   - VRAM usage display
   - Stage completion checkmarks

4. **Error Handling**
   - Graceful fallbacks for missing models
   - Clear error messages
   - Recovery suggestions

### 6.2 Installation & Setup

1. **One-Click Install**
   - Auto-install all dependencies
   - Auto-download required models
   - Auto-configure paths

2. **Model Manager**
   - Browse available models
   - Download from UI
   - Track disk space

---

## 7. External Dependencies

### 7.1 Required ComfyUI Nodes

| Package | Purpose | Required |
|---------|---------|----------|
| ComfyUI-ReActor | Face swap, face boost | Yes |
| ComfyUI_IPAdapter_plus | Face embedding | Yes |
| ComfyUI-RMBG | Background removal, segmentation | Yes |
| ComfyUI-AdvancedUpscripts | Professional upscaling | Yes |
| ComfyUI-Inpaint-Anything | Smart masking | Yes |
| ComfyUI-Manager | Package management | Recommended |

### 7.2 Model Files Required

| Model | Size | Purpose |
|-------|------|---------|
| inswapper_128.onnx | ~500MB | Face swap |
| ip-adapter-faceid-plus | ~1GB | Face embedding |
| RMBG-2.0 | ~100MB | Background removal |
| 4X-UltraSharp | ~50MB | Upscaling |
| RealESRGAN_x4plus | ~20MB | Upscaling |

---

## 8. File Structure

```
Best_Real_Image_Gen/
├── custom_nodes/
│   └── Laura_Image_Studio/
│       ├── __init__.py                    # Entry point
│       ├── nodes/
│       │   ├── __init__.py
│       │   ├── generation.py              # Image generation
│       │   ├── models.py                 # Model loading (20+ models)
│       │   ├── dressing.py                # Virtual dressing
│       │   ├── face.py                   # Face manipulation
│       │   ├── inpainting.py             # Inpainting/outpainting
│       │   ├── upscaling.py              # Resolution scaling
│       │   ├── background.py             # Background editing
│       │   ├── video.py                  # Video generation
│       │   ├── toggle.py                 # Workflow toggles
│       │   ├── checkpoint.py             # Crash recovery
│       │   ├── quantization.py           # NEW: VRAM optimization
│       │   ├── tile_processing.py        # NEW: Large image handling
│       │   ├── batch_processing.py       # NEW: Batch queue
│       │   └── video_advanced.py         # NEW: CogVideoX, Cosmos
│       └── workflows/
│           ├── truly_all_in_one.json     # Master workflow
│           ├── virtual_dressing_room.json
│           └── ...
├── scripts/
│   ├── install_dependencies.py
│   ├── civitai_integration.py
│   ├── download_models.py                # NEW
│   └── vram_optimization_config.md
├── configs/
│   ├── vram_optimization.md
│   └── vram_optimization_config.yaml
├── docs/
│   ├── installation.md
│   ├── quickstart.md
│   └── troubleshooting.md
├── PLAN.md                                # This file
├── PROGRESS.md                            # Task progress tracking
├── WORKSPACE_ANALYSIS_PLAN.md
└── TASK_TRACKING.md                       # Detailed task status
```

---

## 9. Implementation Roadmap

### Phase 1: Foundation (v0.5)
- [x] 82+ nodes implemented
- [x] 23+ model types supported
- [x] Toggle system
- [x] Crash recovery
- [x] VRAM auto-detection system
- [x] Reference image support for dressing
- [x] Test with real models (Delegation validation)
- [x] Advanced Model Loader (Optimized)
- [x] CogVideoX support

### Phase 2: Expansion (v0.6)
- [x] Add HunyuanDiT support
- [x] Add Cosmos-Predict support
- [x] Implement batch processing
- [x] Implement tile-based processing
- [x] UI/UX improvements (ModelTypeDetector, CharacterLoRA)

### Phase 4: Viral Social Media Production (v0.8+) - NEW
- [x] Implement **LauraVideoFaceDrive** (Temporal-Mesh Face Swap/Drive)
- [x] Implement **LauraVideoCinemaUpscale** (SUPIR-Video + RIFE v4 Integration)
- [x] Implement **LauraWanDirectedVideo** (Prompt-based Motion Control)
- [x] Create **viral_video_production_v1.json** master workflow
- [ ] Add **Motion-Control-Net** support to video pipeline

---

## 10. Summary

This project aims to be the **truly all-in-one solution** for:

- ✅ **All Open Weight Models** (30+ and growing)
- ✅ **All VRAM Configurations** (2GB to 80GB+)
- ✅ **Image Generation & Editing** (full pipeline)
- ✅ **Video Generation** (T2V, I2V, V2V)
- ✅ **Virtual Dressing** (18 categories)
- ✅ **Face Manipulation** (swap, embed, enhance)
- ✅ **Professional Upscaling** (2K, 4K, 8K)
- ✅ **Universal Workflow** (single workflow for everything)

---

*Document Version: 1.1*
*Last Updated: 2026-03-02*
*Based on: Web research, user requirements, workspace analysis*
