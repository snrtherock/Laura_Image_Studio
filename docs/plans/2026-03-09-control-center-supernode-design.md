# Laura Control Center Supernode — Design Document

**Date:** 2026-03-09
**Status:** Design approved, pending implementation
**Depends on:** SOTA Model Registry (completed 2026-03-08)

---

## Problem Statement

The current Laura Master Studio workflow has several UX problems:

1. **Model management is scattered** — UniversalModelLoader at x=450, VRAM config at x=7400, Model Manager nodes at x=2000, download guides in Note nodes at x=50. Users must jump around to configure models.
2. **No download-to-folder routing** — Users must manually download models from HuggingFace and place them in the correct `models/` subfolder. There's no in-workflow download capability.
3. **No centralized model selection** — Each node (UniversalModelLoader, Wan22Loader, CogVideoXLoader, UpscaleModelLoader) has its own dropdown. Changing your image model doesn't auto-update VAE, LoRA, or other dependent nodes.
4. **8 groups overlap** — Face Swap overlaps Background Composite, Inpainting overlaps Outpainting, etc.
5. **VRAM/quantization config is far from the start** — Group 15 at x=7400 instead of being the first thing users configure.

## Solution: LauraControlCenter Supernode

A single "god node" positioned at the very start of the workflow (x=30, y=10) that handles:
- VRAM auto-detection + quantization recommendation
- Model selection via 4 category dropdowns + 3 LoRA slots
- Auto-download with correct folder routing
- Outputs MODEL/CLIP/VAE/UPSCALE_MODEL/etc. directly to all downstream nodes
- Status reporting (installed vs missing models)

---

## Node Specification

### Class Definition

```
Class: LauraControlCenter
Category: Laura Studio/Control Center
Display Name: Laura Control Center
FUNCTION: configure_pipeline
OUTPUT_NODE: False
```

### Input Widgets

| Widget | Type | Default | Purpose |
|--------|------|---------|---------|
| `image_model` | Dropdown (from registry, category=image_gen) | `zimage_turbo` | Main image generation model |
| `upscale_model` | Dropdown (from registry, category=upscale + installed upscale models) | `auto` | Upscaler model |
| `video_model` | Dropdown (from registry, category=video_gen) | `wan_t2v_14b` | Video generation model |
| `face_model` | Dropdown (static list) | `inswapper_128` | Face swap model |
| `lora_1` | Dropdown (folder_paths loras list) | `None` | First LoRA |
| `lora_1_strength` | FLOAT (0.0-2.0, step 0.05) | `1.0` | LoRA 1 strength |
| `lora_2` | Dropdown (folder_paths loras list) | `None` | Second LoRA |
| `lora_2_strength` | FLOAT (0.0-2.0, step 0.05) | `1.0` | LoRA 2 strength |
| `lora_3` | Dropdown (folder_paths loras list) | `None` | Third LoRA |
| `lora_3_strength` | FLOAT (0.0-2.0, step 0.05) | `1.0` | LoRA 3 strength |
| `auto_detect_vram` | BOOLEAN | `True` | Auto-detect GPU VRAM tier |
| `manual_vram_tier` | Dropdown (8 VRAM tiers) | `high` | Override when auto-detect off |
| `auto_quantization` | BOOLEAN | `True` | Auto-select best quantization for VRAM |
| `torch_compile` | BOOLEAN | `False` | Enable torch.compile optimization |
| `default_width` | INT (512-4096, step 64) | `1024` | Default generation width |
| `default_height` | INT (512-4096, step 64) | `1024` | Default generation height |

### Outputs

| # | Name | Type | Wires To |
|---|------|------|----------|
| 0 | `model` | MODEL | KSampler, MultiLoraStack input |
| 1 | `clip` | CLIP | CLIPTextEncode nodes |
| 2 | `vae` | VAE | All VAEDecode/VAEEncode nodes |
| 3 | `upscale_model` | UPSCALE_MODEL | Upscale chain nodes |
| 4 | `detected_type` | STRING | ModelTypeDetector consumers |
| 5 | `default_width` | INT | EmptyLatentImage width |
| 6 | `default_height` | INT | EmptyLatentImage height |
| 7 | `status_report` | STRING | Display/logging |
| 8 | `config_json` | STRING | JSON blob for other Laura nodes |

### Execution Logic (`configure_pipeline`)

```python
def configure_pipeline(self, image_model, upscale_model, video_model, face_model,
                       lora_1, lora_1_strength, lora_2, lora_2_strength,
                       lora_3, lora_3_strength, auto_detect_vram, manual_vram_tier,
                       auto_quantization, torch_compile, default_width, default_height):

    # 1. VRAM detection
    vram_tier = _detect_vram() if auto_detect_vram else manual_vram_tier

    # 2. Registry lookup for selected image model
    model_info = MODEL_REGISTRY[image_model]

    # 3. Quantization selection
    if auto_quantization:
        quant = get_recommended_quantization(image_model, vram_tier)

    # 4. Load checkpoint (using ComfyUI's standard loader)
    #    Finds the correct file in models/checkpoints/ or models/diffusion_models/
    model, clip, vae = load_checkpoint(model_info, quant)

    # 5. Apply LoRAs (if selected)
    if lora_1 and lora_1 != "None":
        model, clip = apply_lora(model, clip, lora_1, lora_1_strength)
    if lora_2 and lora_2 != "None":
        model, clip = apply_lora(model, clip, lora_2, lora_2_strength)
    if lora_3 and lora_3 != "None":
        model, clip = apply_lora(model, clip, lora_3, lora_3_strength)

    # 6. Load upscale model
    upscale_model_obj = load_upscale_model(upscale_model)

    # 7. Build status report
    status = build_status_report(image_model, upscale_model, video_model, face_model, vram_tier)

    # 8. Build config JSON for downstream Laura nodes
    config = {
        "vram_tier": vram_tier,
        "image_model": image_model,
        "video_model": video_model,
        "face_model": face_model,
        "quantization": quant,
        "torch_compile": torch_compile,
    }

    return (model, clip, vae, upscale_model_obj, detected_type,
            default_width, default_height, status, json.dumps(config))
```

### Model Loading Strategy

The Control Center uses ComfyUI's built-in model loading functions — the same ones `CheckpointLoaderSimple` and `UNETLoader` use internally:

```python
import comfy.sd
import comfy.utils
import folder_paths

# For checkpoints (SDXL, SD3.5, etc.)
ckpt_path = folder_paths.get_full_path("checkpoints", filename)
model, clip, vae, _ = comfy.sd.load_checkpoint_guess_config(ckpt_path, ...)

# For diffusion_models / UNETs (FLUX, Z-Image, etc.)
unet_path = folder_paths.get_full_path("diffusion_models", filename)
model = comfy.sd.load_diffusion_model(unet_path, ...)

# For LoRAs
lora_path = folder_paths.get_full_path("loras", lora_name)
model, clip = comfy.sd.load_lora_for_models(model, clip, lora, strength_model, strength_clip)

# For upscale models
upscale_path = folder_paths.get_full_path("upscale_models", filename)
upscale_model = comfy.utils.load_torch_file(upscale_path)
```

---

## Web Extension: Download Manager UI

### Enhanced model_links.js

The existing `model_links.js` (278 lines) gets extended with a new section for the Control Center node:

```
┌─── LAURA CONTROL CENTER ─────────────────────────────────────┐
│                                                               │
│  GPU: NVIDIA RTX 4070 Ti (12 GB VRAM)                        │
│  Tier: HIGH | Recommended: FP8 quantization                  │
│                                                               │
│  ┌─ IMAGE MODEL ────────────────────────────────────────────┐ │
│  │ Z-Image Turbo (11.5 GB)                     ✅ Installed │ │
│  │ [View on HuggingFace]  [📥 Download]                     │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─ UPSCALER ───────────────────────────────────────────────┐ │
│  │ SUPIR (5.2 GB)                              ✅ Installed │ │
│  │ [View on HuggingFace]  [📥 Download]                     │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─ VIDEO MODEL ────────────────────────────────────────────┐ │
│  │ Wan 2.2 T2V 14B (27 GB)                    ❌ Missing    │ │
│  │ [View on HuggingFace]  [📥 Download]                     │ │
│  │ ████████░░░░░░░░░░ 45% (12.1 / 27.0 GB)                 │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─ FACE MODEL ─────────────────────────────────────────────┐ │
│  │ inswapper_128.onnx (554 MB)                 ✅ Installed │ │
│  │ [View on HuggingFace]  [📥 Download]                     │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Download API Endpoints

Two new routes registered in `__init__.py` via ComfyUI's `PromptServer`:

```python
from server import PromptServer

@PromptServer.instance.routes.post("/laura/download")
async def download_model(request):
    data = await request.json()
    model_key = data["model_key"]
    # Look up registry, start async download, return job_id

@PromptServer.instance.routes.get("/laura/download/status/{job_id}")
async def download_status(request):
    job_id = request.match_info["job_id"]
    # Return {progress_bytes, total_bytes, status, error}
```

Download uses `huggingface_hub.hf_hub_download()` for authenticated gated model support, falling back to raw `requests.get()` with streaming for public models.

---

## Workflow Layout Fix

### Group Spacing Algorithm

For all 3 master workflows, run a layout fixer script that:

1. Sorts groups left-to-right by their x position
2. Ensures minimum 100px horizontal gap between adjacent groups
3. Shifts all groups rightward as needed to eliminate overlaps
4. Adjusts all nodes within each group by the same offset
5. Repositions the Control Center group to x=30, y=10 (leftmost)

### Specific Changes to Laura_Master_Studio_v0.8

| Current | New |
|---------|-----|
| CONTROL PANEL at x=30 | Becomes CONTROL CENTER — now contains LauraControlCenter supernode |
| MODEL SETUP at x=430 | Removed — merged into Control Center |
| VRAM AUTO-OPTIMIZATION at x=7400 | Removed — merged into Control Center |
| GUIDES & DOWNLOADS at x=30, y=700 | Stays, but may shift down |
| 8 overlapping group pairs | All fixed with 100px gaps |
| Model Manager nodes at x=2000 | Removed or repurposed — Control Center replaces them |

### Control Center Group Contents

The Control Center group (group 1, leftmost) contains:
- `LauraControlCenter` node (the supernode)
- `WorkflowTogglePanel` (existing — toggle sections on/off)
- 1-2 Note nodes with setup instructions

Everything else (LoRA details, face detection settings, video parameters) stays in their respective downstream groups — the user doesn't need to touch them since the Control Center auto-configures.

---

## What Stays vs What Gets Replaced

| Existing Node | Fate |
|---------------|------|
| `UniversalModelLoader` | **Replaced** by Control Center's model output |
| `MultiLoraStack` | **Replaced** by Control Center's built-in LoRA slots |
| `IPAdapterUnifiedLoader` | **Kept** — IPAdapter is separate from main model |
| `VRAMAutoDetector` | **Replaced** by Control Center's auto-detect |
| `QuantizationSelector` | **Replaced** by Control Center's auto-quant |
| `QuantizationConfig` | **Replaced** by Control Center's config output |
| `ModelOffloadConfig` | **Kept** — but reads config from Control Center |
| `LauraModelLinks` (ID=1000) | **Replaced** — download UI is now in Control Center |
| `LauraModelManager` (ID=1001) | **Replaced** by Control Center |
| `LauraAutoConfig` (ID=1002) | **Replaced** by Control Center |
| `LauraQuantizationAdvisor` (ID=1003) | **Replaced** by Control Center |
| `LauraModelDownloadHelper` (ID=1004) | **Replaced** by Control Center |
| `LauraCompatibilityChecker` (ID=1005) | **Kept** as standalone utility |
| `ModuleConfigPanel` (ID=1006) | **Kept** — module enable/disable is separate |

---

## File Changes

| File | Action |
|------|--------|
| `nodes/control_center.py` | **CREATE** — LauraControlCenter node + download API |
| `nodes/model_registry.py` | **UPDATE** — add helper: `get_models_by_input_type()` for dropdown population |
| `web/js/control_center.js` | **CREATE** — rich UI for Control Center (status badges, download buttons, progress bars) |
| `web/js/model_links.js` | **KEEP** — existing LauraModelLinks still works standalone |
| `__init__.py` | **UPDATE** — add `control_center` to module list, register API routes |
| `workflows/*.json` (3 files) | **UPDATE** — layout fix + replace scattered nodes with Control Center |
| `scripts/fix_workflow_layout.py` | **CREATE** — script to fix group overlaps and spacing |

---

## Out of Scope (YAGNI)

- Video model loading in Control Center outputs (video loaders are specialized per-engine)
- Face model loading in Control Center outputs (ReActor has its own loader)
- Auto-update / model version checking
- Cloud model storage / S3 integration
- Model benchmarking / quality comparison in Control Center

The Control Center focuses on the **primary image generation pipeline**: model + clip + vae + loras + upscaler. Video and face models are configured via their own specialized loaders downstream, but the Control Center's `config_json` output tells them which model was selected so they can auto-configure.
