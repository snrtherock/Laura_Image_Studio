# SOTA Model Registry + Auto-Config Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a centralized model registry covering all March 2026 SOTA open-source models, with auto-config detection, module enable/disable, and download management nodes for Laura Image Studio v1.0.

**Architecture:** A single `MODEL_REGISTRY` dict in `nodes/model_registry.py` serves as the source of truth. New `nodes/model_manager.py` provides 7 ComfyUI nodes for model health checking, download guidance, module configuration, quantization advice, and model download links. `__init__.py` reads a `laura_config.json` to conditionally load modules. All workflow JSONs are updated with `models` metadata for ComfyUI's native missing-models popup.

**Tech Stack:** Python 3.10+, ComfyUI custom nodes API (`folder_paths`, `NODE_CLASS_MAPPINGS`), PyTorch (CUDA introspection), JSON config files, HuggingFace Hub URLs.

**Design Doc:** `docs/plans/2026-03-08-sota-model-registry-design.md`

---

## Implementation Status

| Task | Description | Status | Notes |
|------|-------------|--------|-------|
| 1 | Create `model_registry.py` | **COMPLETED** | 20 models, 7 categories, 8 VRAM tiers, 7 helper functions |
| 2 | Create `model_manager.py` (7 nodes) | **COMPLETED** | LauraModelManager, ModuleConfigPanel, LauraQuantizationAdvisor, LauraModelDownloadHelper, LauraCompatibilityChecker, LauraAutoConfig, LauraModelLinks |
| 2b | Create web extension `model_links.js` | **COMPLETED** | 278 lines, parses [LINK:] markers into clickable hyperlinks, tab UI |
| 3 | Update `__init__.py` | **COMPLETED** | WEB_DIRECTORY='./web', config-aware module loading, 128 total nodes |
| 4 | Update `models.py` | **COMPLETED** | Registry-based type detection, 4 new model types in dropdowns, dynamic health check |
| 5 | Update `quantization.py` | **COMPLETED** | Registry-based quant lookup, expanded dropdown with 8 new model types |
| 6 | Rewrite `model_downloader.py` | **COMPLETED** | Uses centralized registry, --recommend and --category flags |
| 7 | Create `inject_workflow_models.py` | **COMPLETED** | Processed 33 workflows, injected metadata into 3 (matching filenames) |
| 8 | Final integration test | **COMPLETED** | 128 nodes verified, all 13 LauraModelLinks dropdown choices work |

### Remaining / Not Yet Done

1. **Workflow node placement** — The 7 new nodes (LauraModelLinks, LauraModelManager, LauraAutoConfig, etc.) are NOT yet added to any workflow JSON files. Need to programmatically inject them into master workflows (enhanced_master_workflow.json, master_all_in_one.json, etc.) with correct ComfyUI node format (positions, IDs, widget defaults, connections).
2. **9 registry entries have TBD/placeholder files** — z_image_edit, qwen_image_2512, glm_image, firered_edit_1_1, helios_distilled, helios_base, ltx_2_3, cogvideox_5b, seedvr2 — download URLs/filenames to be added when HuggingFace repos are confirmed.
3. **Live ComfyUI test** — All verification was done with mocked `folder_paths` outside ComfyUI. Need to load in actual ComfyUI to confirm all 128 nodes register and the web extension renders correctly.
4. **Git committed** ✅ — Submodule: `0e4bf20`, Parent: `4eae4bb` (2026-03-09)

### Key Bug Fixes Applied During Implementation

1. **Registry data shape mismatch**: Task 1 created files as `{role: dict}` but Task 2 expected `{folder: [list]}` — fixed in `_gather_model_files`, `LauraModelManager.manage()`, `LauraAutoConfig.auto_configure()`
2. **`total_mem` vs `total_memory`**: Fixed in `_detect_vram()`

---

## Task 1: Create Model Registry (`nodes/model_registry.py`)

**Files:**
- Create: `custom_nodes/Laura_Image_Studio/nodes/model_registry.py`

**Step 1: Create the registry module with all models**

Create `custom_nodes/Laura_Image_Studio/nodes/model_registry.py` with the complete `MODEL_REGISTRY` dict. This file has NO ComfyUI nodes — it's pure data + helper functions.

```python
"""
Laura Image Studio - Centralized Model Registry
Single source of truth for all supported models, their HuggingFace repos,
file sizes, VRAM requirements, quantization recommendations, and compatibility.

v1.0 — March 2026 SOTA Edition
"""

import os

# ============== VRAM TIER DEFINITIONS ==============
VRAM_TIERS = {
    "ultra_low": {"min_gb": 0, "max_gb": 4.5, "label": "Ultra Low (< 4.5GB)"},
    "low": {"min_gb": 4.5, "max_gb": 6.5, "label": "Low (4.5-6.5GB)"},
    "medium": {"min_gb": 6.5, "max_gb": 8.5, "label": "Medium (6.5-8.5GB)"},
    "high": {"min_gb": 8.5, "max_gb": 12.5, "label": "High (8.5-12.5GB)"},
    "very_high": {"min_gb": 12.5, "max_gb": 16.5, "label": "Very High (12.5-16.5GB)"},
    "ultra": {"min_gb": 16.5, "max_gb": 24.5, "label": "Ultra (16.5-24.5GB)"},
    "extreme": {"min_gb": 24.5, "max_gb": 48.5, "label": "Extreme (24.5-48.5GB)"},
    "hpc": {"min_gb": 48.5, "max_gb": 999, "label": "HPC (48.5GB+)"},
}

# ============== MODEL CATEGORIES ==============
CATEGORIES = {
    "image_gen": "Image Generation",
    "image_edit": "Image Editing",
    "video_gen": "Video Generation",
    "upscale": "Upscaling",
    "vae": "VAE",
    "text_encoder": "Text Encoder",
    "controlnet": "ControlNet",
}

# ============== COMPLETE MODEL REGISTRY ==============
MODEL_REGISTRY = {
    # --- IMAGE GENERATION ---
    "z_image_turbo": {
        "display_name": "Z-Image Turbo",
        "family": "zimage",
        "category": "image_gen",
        "repo": "Tongyi-MAI/Z-Image-Turbo",
        "homepage": "https://tongyi-mai.github.io/Z-Image-blog/",
        "license": "Apache-2.0",
        "params": "6B",
        "architecture": "S3-DiT (Single-Stream DiT)",
        "status": "released",
        "files": {
            "diffusion_models": [
                {"filename": "z_image_turbo_bf16.safetensors", "size_gb": 11.46, "precision": "bf16", "required": True},
            ],
            "text_encoders": [
                {"filename": "qwen_3_4b.safetensors", "size_gb": 7.49, "precision": "bf16", "required": True},
            ],
            "vae": [
                {"filename": "ae.safetensors", "size_gb": 0.31, "precision": "bf16", "required": True},
            ],
        },
        "total_size_gb": 19.26,
        "quantization_variants": {
            "bf16": {"vram_gb": 16, "quality": "best", "speed": "fast (8 steps)"},
            "fp8": {"vram_gb": 10, "quality": "near-best", "speed": "fast"},
            "gguf_q8": {"vram_gb": 8, "quality": "good", "speed": "medium"},
            "gguf_q4": {"vram_gb": 6, "quality": "acceptable", "speed": "medium"},
            "nvfp4": {"vram_gb": 6, "quality": "good", "speed": "fast (Ada Lovelace+)"},
        },
        "quantization_recommendation": {
            "ultra_low": "gguf_q4", "low": "gguf_q8", "medium": "fp8",
            "high": "bf16", "very_high": "bf16", "ultra": "bf16",
            "extreme": "bf16", "hpc": "bf16",
        },
        "inference": {"steps": 8, "cfg": False, "resolution_range": [512, 2048], "default_resolution": [1024, 1024]},
        "compatibility": {
            "lora": False, "controlnet": True,
            "controlnet_models": ["ControlNet Union 2.1"],
            "ipadapter": True, "negative_prompt": False,
        },
        "quality_score": {"elo_rank": "#1 open-source (Alibaba AI Arena)", "strengths": ["photorealism", "bilingual text rendering", "prompt adherence"], "weaknesses": ["low diversity", "no LoRA", "no negative prompt"]},
        "module_dependency": "generation",
        "comfyui_type": "diffusion_models",
    },
    "z_image_base": {
        "display_name": "Z-Image (Base)",
        "family": "zimage",
        "category": "image_gen",
        "repo": "Tongyi-MAI/Z-Image",
        "license": "Apache-2.0",
        "params": "6B",
        "architecture": "S3-DiT",
        "status": "released",
        "files": {
            "diffusion_models": [
                {"filename": "z_image_bf16.safetensors", "size_gb": 11.46, "precision": "bf16", "required": True},
            ],
            "text_encoders": [
                {"filename": "qwen_3_4b.safetensors", "size_gb": 7.49, "precision": "bf16", "required": True, "shared_with": ["z_image_turbo"]},
            ],
            "vae": [
                {"filename": "ae.safetensors", "size_gb": 0.31, "precision": "bf16", "required": True, "shared_with": ["z_image_turbo"]},
            ],
        },
        "total_size_gb": 19.26,
        "quantization_variants": {
            "bf16": {"vram_gb": 16, "quality": "best", "speed": "slow (28-50 steps)"},
            "fp8": {"vram_gb": 10, "quality": "near-best", "speed": "medium"},
            "gguf_q8": {"vram_gb": 8, "quality": "good", "speed": "medium"},
            "gguf_q4": {"vram_gb": 6, "quality": "acceptable", "speed": "medium"},
        },
        "quantization_recommendation": {
            "ultra_low": "gguf_q4", "low": "gguf_q8", "medium": "fp8",
            "high": "bf16", "very_high": "bf16", "ultra": "bf16",
            "extreme": "bf16", "hpc": "bf16",
        },
        "inference": {"steps": 50, "cfg": True, "cfg_scale": [3.0, 5.0], "resolution_range": [512, 2048], "default_resolution": [1024, 1024]},
        "compatibility": {"lora": True, "controlnet": True, "controlnet_models": ["ControlNet Union 2.1"], "ipadapter": True, "negative_prompt": True},
        "quality_score": {"strengths": ["high diversity", "LoRA training", "negative prompting", "fine-tunability"], "weaknesses": ["slower than Turbo (28-50 steps)"]},
        "module_dependency": "generation",
        "comfyui_type": "diffusion_models",
    },
    "z_image_edit": {
        "display_name": "Z-Image Edit",
        "family": "zimage",
        "category": "image_edit",
        "repo": "Tongyi-MAI/Z-Image-Edit",
        "license": "Apache-2.0",
        "params": "6B",
        "status": "pending_release",
        "files": {},
        "total_size_gb": 0,
        "quantization_recommendation": {"ultra_low": "gguf_q4", "low": "gguf_q8", "medium": "fp8", "high": "bf16", "very_high": "bf16", "ultra": "bf16", "extreme": "bf16", "hpc": "bf16"},
        "inference": {"steps": 50, "cfg": True},
        "compatibility": {"lora": True},
        "module_dependency": "inpainting",
    },
    "flux2_dev": {
        "display_name": "Flux 2 Dev",
        "family": "flux",
        "category": "image_gen",
        "repo": "black-forest-labs/FLUX.2-dev",
        "homepage": "https://bfl.ai/flux2",
        "license": "FLUX Non-Commercial License",
        "params": "32B",
        "architecture": "Rectified Flow Transformer",
        "status": "released",
        "files": {
            "checkpoints": [
                {"filename": "flux2-dev.safetensors", "size_gb": 24.0, "precision": "bf16", "required": True},
            ],
        },
        "total_size_gb": 24.0,
        "quantization_variants": {
            "bf16": {"vram_gb": 48, "quality": "best", "speed": "medium"},
            "fp8": {"vram_gb": 24, "quality": "near-best", "speed": "medium"},
            "bnb_4bit": {"vram_gb": 8, "quality": "good", "speed": "medium", "alt_repo": "diffusers/FLUX.2-dev-bnb-4bit"},
            "nvfp4": {"vram_gb": 10, "quality": "good", "speed": "fast (Ada+)", "alt_repo": "black-forest-labs/FLUX.2-dev-NVFP4"},
        },
        "quantization_recommendation": {
            "ultra_low": None, "low": "bnb_4bit", "medium": "bnb_4bit",
            "high": "fp8", "very_high": "fp8", "ultra": "bf16",
            "extreme": "bf16", "hpc": "bf16",
        },
        "inference": {"steps": 50, "cfg": True, "cfg_scale": 4.0, "resolution_range": [512, 2048], "default_resolution": [1024, 1024]},
        "compatibility": {"lora": True, "controlnet": True, "ipadapter": True, "negative_prompt": True, "multi_reference": True, "image_editing": True},
        "quality_score": {"strengths": ["SOTA multi-reference", "generation + editing in one model", "32B parameters"], "weaknesses": ["very large", "requires HF agreement"]},
        "module_dependency": "generation",
        "comfyui_type": "checkpoints",
    },
    "flux1_dev": {
        "display_name": "Flux 1 Dev",
        "family": "flux",
        "category": "image_gen",
        "repo": "black-forest-labs/FLUX.1-dev",
        "license": "FLUX Non-Commercial License",
        "params": "12B",
        "status": "released",
        "files": {"checkpoints": [{"filename": "flux1-dev.safetensors", "size_gb": 24.0, "precision": "bf16", "required": True}]},
        "total_size_gb": 24.0,
        "quantization_variants": {"bf16": {"vram_gb": 24}, "fp8": {"vram_gb": 12}, "gguf_q8": {"vram_gb": 8}},
        "quantization_recommendation": {"ultra_low": "gguf_q4", "low": "gguf_q8", "medium": "fp8", "high": "bf16", "very_high": "bf16", "ultra": "bf16", "extreme": "bf16", "hpc": "bf16"},
        "compatibility": {"lora": True, "controlnet": True, "ipadapter": True},
        "module_dependency": "generation",
        "comfyui_type": "checkpoints",
    },
    "flux1_schnell": {
        "display_name": "Flux 1 Schnell",
        "family": "flux",
        "category": "image_gen",
        "repo": "black-forest-labs/FLUX.1-schnell",
        "license": "Apache-2.0",
        "params": "12B",
        "status": "released",
        "files": {"checkpoints": [{"filename": "flux1-schnell.safetensors", "size_gb": 24.0, "precision": "bf16", "required": True}]},
        "total_size_gb": 24.0,
        "quantization_recommendation": {"ultra_low": "gguf_q4", "low": "gguf_q8", "medium": "fp8", "high": "bf16", "very_high": "bf16", "ultra": "bf16", "extreme": "bf16", "hpc": "bf16"},
        "compatibility": {"lora": False, "controlnet": True, "ipadapter": True},
        "module_dependency": "generation",
        "comfyui_type": "checkpoints",
    },
    "qwen_image_2512": {
        "display_name": "Qwen-Image-2512",
        "family": "qwen",
        "category": "image_gen",
        "repo": "QwenLM/Qwen-Image-2512",
        "homepage": "https://qwen.ai/blog?id=qwen-image-2512",
        "license": "Apache-2.0",
        "params": "~7B",
        "architecture": "Unified Vision-Language",
        "status": "released",
        "files": {},
        "total_size_gb": 16.0,
        "quantization_variants": {"bf16": {"vram_gb": 16}, "fp8": {"vram_gb": 10}},
        "quantization_recommendation": {"ultra_low": None, "low": "fp8", "medium": "fp8", "high": "bf16", "very_high": "bf16", "ultra": "bf16", "extreme": "bf16", "hpc": "bf16"},
        "compatibility": {"lora": True, "controlnet": False, "ipadapter": False},
        "quality_score": {"strengths": ["enterprise workflows", "precise detail", "realism"]},
        "module_dependency": "generation",
    },
    "glm_image": {
        "display_name": "GLM-Image",
        "family": "glm",
        "category": "image_gen",
        "repo": "zai-org/GLM-Image",
        "homepage": "https://z.ai/blog/glm-image",
        "license": "Open Source",
        "params": "16B",
        "architecture": "Auto-regressive Dense-knowledge",
        "status": "released",
        "files": {},
        "total_size_gb": 32.0,
        "quantization_variants": {"bf16": {"vram_gb": 32}, "fp8": {"vram_gb": 16}, "gguf_q8": {"vram_gb": 12}},
        "quantization_recommendation": {"ultra_low": None, "low": None, "medium": "gguf_q8", "high": "fp8", "very_high": "fp8", "ultra": "bf16", "extreme": "bf16", "hpc": "bf16"},
        "compatibility": {"lora": False, "controlnet": False, "ipadapter": False},
        "quality_score": {"strengths": ["beats Nano Banana Pro at text-heavy images", "high fidelity"]},
        "module_dependency": "generation",
    },
    "sd35_medium": {
        "display_name": "SD 3.5 Medium",
        "family": "sd3",
        "category": "image_gen",
        "repo": "stabilityai/stable-diffusion-3.5-medium",
        "license": "Stability Community License",
        "params": "2.5B",
        "status": "released",
        "files": {"checkpoints": [{"filename": "sd3.5_medium.safetensors", "size_gb": 6.0, "required": True}]},
        "total_size_gb": 6.0,
        "quantization_recommendation": {"ultra_low": "fp8", "low": "fp16", "medium": "fp16", "high": "fp16", "very_high": "fp16", "ultra": "fp16", "extreme": "fp16", "hpc": "fp16"},
        "compatibility": {"lora": True, "controlnet": True, "ipadapter": True},
        "module_dependency": "generation",
        "comfyui_type": "checkpoints",
    },

    # --- IMAGE EDITING ---
    "firered_edit_1_1": {
        "display_name": "FireRed-Image-Edit 1.1",
        "family": "firered",
        "category": "image_edit",
        "repo": "FireRedTeam/FireRed-Image-Edit-1.1",
        "homepage": "https://github.com/FireRedTeam/FireRed-Image-Edit",
        "license": "Apache-2.0",
        "params": "~12B",
        "status": "released",
        "files": {},
        "total_size_gb": 24.0,
        "quantization_variants": {
            "bf16": {"vram_gb": 30, "quality": "best", "speed": "4.5s end-to-end"},
            "gguf_q8": {"vram_gb": 10, "quality": "good", "alt_repo": "drbaph/FireRed-Image-Edit-1.0_ComfyUI_Quants"},
        },
        "quantization_recommendation": {"ultra_low": None, "low": None, "medium": "gguf_q8", "high": "gguf_q8", "very_high": "bf16", "ultra": "bf16", "extreme": "bf16", "hpc": "bf16"},
        "compatibility": {
            "lora": True, "lora_zoo": "FireRedTeam/FireRed-Image-Edit-LoRA-Zoo",
            "lora_zoo_models": ["Makeup", "Covercraft", "Style"],
            "comfyui_native": True,
        },
        "quality_score": {"elo_rank": "SOTA open-source image editing", "strengths": ["identity consistency", "multi-element fusion", "portrait makeup", "text style reference", "photo restoration"]},
        "module_dependency": "inpainting",
    },

    # --- VIDEO GENERATION ---
    "helios_distilled": {
        "display_name": "Helios (Distilled)",
        "family": "helios",
        "category": "video_gen",
        "repo": "BestWishYsh/Helios-Distilled",
        "homepage": "https://github.com/PKU-YuanGroup/Helios",
        "license": "Open Source",
        "params": "14B distilled",
        "status": "released",
        "released": "2026-03-04",
        "files": {},
        "total_size_gb": 14.0,
        "quantization_recommendation": {},
        "quality_score": {"strengths": ["real-time generation", "long video", "cheaper than 1.3B models"]},
        "module_dependency": "video_advanced",
    },
    "helios_base": {
        "display_name": "Helios (Base)",
        "family": "helios",
        "category": "video_gen",
        "repo": "BestWishYsh/Helios-Base",
        "license": "Open Source",
        "params": "14B",
        "status": "released",
        "released": "2026-03-04",
        "files": {},
        "total_size_gb": 28.0,
        "module_dependency": "video_advanced",
    },
    "ltx_2_3": {
        "display_name": "LTX-2.3",
        "family": "ltx",
        "category": "video_gen",
        "repo": "Lightricks/LTX-2.3",
        "homepage": "https://ltx.io/model/ltx-2-3",
        "license": "Open Source",
        "params": "~2B",
        "status": "released",
        "files": {},
        "total_size_gb": 6.0,
        "quantization_variants": {"bf16": {"vram_gb": 12}, "fp8": {"vram_gb": 8}},
        "quantization_recommendation": {"ultra_low": None, "low": "fp8", "medium": "fp8", "high": "bf16", "very_high": "bf16", "ultra": "bf16", "extreme": "bf16", "hpc": "bf16"},
        "quality_score": {"strengths": ["audio support", "portrait video", "sharper detail", "vertical format"]},
        "module_dependency": "video_advanced",
    },
    "wan22_14b": {
        "display_name": "Wan 2.2 14B",
        "family": "wan",
        "category": "video_gen",
        "repo": "Wan-AI/Wan2.2-14B-T2V",
        "params": "14B",
        "status": "released",
        "files": {"checkpoints": [{"filename": "diffusion_pytorch_model.safetensors", "size_gb": 28.0, "required": True}]},
        "total_size_gb": 28.0,
        "quantization_recommendation": {"ultra_low": None, "low": None, "medium": None, "high": "fp8", "very_high": "fp8", "ultra": "bf16", "extreme": "bf16", "hpc": "bf16"},
        "compatibility": {"motion_control": True, "i2v": True, "t2v": True},
        "module_dependency": "video_advanced",
        "comfyui_type": "checkpoints",
    },
    "hunyuan_video": {
        "display_name": "HunyuanVideo 2.0",
        "family": "hunyuan",
        "category": "video_gen",
        "repo": "tencent/HunyuanVideo",
        "params": "~13B",
        "status": "released",
        "files": {"checkpoints": [{"filename": "hunyuan_video_v1.0.safetensors", "size_gb": 24.0, "required": True}]},
        "total_size_gb": 24.0,
        "quantization_recommendation": {"ultra_low": None, "low": None, "medium": "fp8", "high": "fp8", "very_high": "bf16", "ultra": "bf16", "extreme": "bf16", "hpc": "bf16"},
        "module_dependency": "video_advanced",
        "comfyui_type": "checkpoints",
    },
    "cogvideox_5b": {
        "display_name": "CogVideoX 5B",
        "family": "cogvideo",
        "category": "video_gen",
        "repo": "THUDM/CogVideoX-5b",
        "params": "5B",
        "status": "released",
        "files": {},
        "total_size_gb": 10.0,
        "quantization_recommendation": {"ultra_low": None, "low": None, "medium": "fp8", "high": "bf16", "very_high": "bf16", "ultra": "bf16", "extreme": "bf16", "hpc": "bf16"},
        "module_dependency": "video_advanced",
    },

    # --- UPSCALE ---
    "seedvr2": {
        "display_name": "SeedVR2",
        "family": "seedvr",
        "category": "upscale",
        "repo": "TBD",
        "status": "community",
        "files": {},
        "total_size_gb": 2.0,
        "quality_score": {"strengths": ["best i2i upscale (community consensus March 2026)"]},
        "module_dependency": "upscaling",
    },

    # --- SHARED COMPONENTS ---
    "flux_vae": {
        "display_name": "Flux VAE (ae.safetensors)",
        "family": "flux",
        "category": "vae",
        "repo": "black-forest-labs/FLUX.1-dev",
        "status": "released",
        "files": {"vae": [{"filename": "ae.safetensors", "size_gb": 0.31, "required": True, "shared_with": ["flux1_dev", "flux1_schnell", "z_image_turbo", "z_image_base"]}]},
        "total_size_gb": 0.31,
    },
    "cosmos_vae": {
        "display_name": "Cosmos VAE",
        "family": "cosmos",
        "category": "vae",
        "repo": "nvidia/Cosmos-1.0-VAE",
        "status": "released",
        "files": {"vae": [{"filename": "cosmos_vae.safetensors", "size_gb": 0.5, "required": False}]},
        "total_size_gb": 0.5,
    },
}


# ============== HELPER FUNCTIONS ==============

def get_models_by_category(category):
    """Return all models in a given category."""
    return {k: v for k, v in MODEL_REGISTRY.items() if v.get("category") == category}


def get_models_by_family(family):
    """Return all models in a given family (e.g., 'zimage', 'flux')."""
    return {k: v for k, v in MODEL_REGISTRY.items() if v.get("family") == family}


def get_recommended_quantization(model_key, vram_tier):
    """Get the recommended quantization for a model at a given VRAM tier."""
    model = MODEL_REGISTRY.get(model_key)
    if not model:
        return None
    rec = model.get("quantization_recommendation", {})
    return rec.get(vram_tier)


def get_download_url(model_key):
    """Generate the HuggingFace download URL for a model."""
    model = MODEL_REGISTRY.get(model_key)
    if not model or not model.get("repo"):
        return None
    return f"https://huggingface.co/{model['repo']}"


def get_all_required_files(model_key):
    """Return a flat list of all required files for a model with their folder targets."""
    model = MODEL_REGISTRY.get(model_key)
    if not model:
        return []
    result = []
    for folder, files in model.get("files", {}).items():
        for f in files:
            if f.get("required", False):
                result.append({
                    "folder": folder,
                    "filename": f["filename"],
                    "size_gb": f.get("size_gb", 0),
                    "url": f"https://huggingface.co/{model['repo']}/resolve/main/{f['filename']}",
                })
    return result


def detect_model_key_from_filename(filename):
    """Auto-detect which model a filename belongs to."""
    filename_lower = filename.lower()

    detection_patterns = [
        ("z_image_turbo", ["z_image_turbo", "z-image-turbo", "zimage_turbo", "zimagturbo"]),
        ("z_image_base", ["z_image_bf16", "z-image_bf16", "z_image.", "z-image."]),
        ("flux2_dev", ["flux2-dev", "flux2_dev", "flux.2"]),
        ("flux1_dev", ["flux1-dev", "flux1_dev", "flux.1-dev", "flux1-dev"]),
        ("flux1_schnell", ["flux1-schnell", "schnell"]),
        ("qwen_image_2512", ["qwen-image", "qwen_image"]),
        ("glm_image", ["glm-image", "glm_image"]),
        ("firered_edit_1_1", ["firered", "fire-red", "fire_red"]),
        ("helios_distilled", ["helios-distilled", "helios_distilled"]),
        ("helios_base", ["helios-base", "helios_base", "helios"]),
        ("ltx_2_3", ["ltx-2.3", "ltx_2_3", "ltx-video"]),
        ("wan22_14b", ["wan2.2", "wan22", "wan-2.2"]),
        ("hunyuan_video", ["hunyuan"]),
        ("cogvideox_5b", ["cogvideo"]),
        ("sd35_medium", ["sd3.5", "sd35"]),
        ("seedvr2", ["seedvr"]),
    ]

    for model_key, patterns in detection_patterns:
        for pattern in patterns:
            if pattern in filename_lower:
                return model_key
    return None


def get_registry_version():
    """Return the registry version string."""
    return "1.0.0-2026.03.08"
```

**Step 2: Verify the module imports cleanly**

Run: `python -c "import sys; sys.path.insert(0, 'custom_nodes'); from Laura_Image_Studio.nodes.model_registry import MODEL_REGISTRY, get_models_by_category; print(f'Registry loaded: {len(MODEL_REGISTRY)} models'); print('Image gen:', len(get_models_by_category(\"image_gen\")))"`

Expected output: `Registry loaded: 20 models` and `Image gen: 9`

**Step 3: Commit**

```bash
git add custom_nodes/Laura_Image_Studio/nodes/model_registry.py
git commit -m "feat: add centralized model registry with 20+ SOTA models

Covers Z-Image family, Flux 1/2, Qwen-Image, GLM-Image, FireRed,
Helios, LTX-2.3, Wan 2.2, HunyuanVideo, CogVideoX, SeedVR2.
Includes quantization recommendations per VRAM tier, compatibility
matrices (LoRA/ControlNet/IPAdapter), and download URLs."
```

---

## Task 2: Create Model Manager Nodes (`nodes/model_manager.py`)

**Files:**
- Create: `custom_nodes/Laura_Image_Studio/nodes/model_manager.py`

**Step 1: Create the model manager module with 6 nodes**

Create `custom_nodes/Laura_Image_Studio/nodes/model_manager.py`:

```python
"""
Laura Image Studio - Model Manager Nodes
Provides model health checking, download guidance, module configuration,
quantization advice, and compatibility checking.

v1.0 — March 2026 SOTA Edition
"""

import json
import os
import torch

import folder_paths

from .model_registry import (
    MODEL_REGISTRY,
    VRAM_TIERS,
    CATEGORIES,
    get_models_by_category,
    get_recommended_quantization,
    get_download_url,
    get_all_required_files,
    get_registry_version,
)

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Path to the config file (next to the package root)
_PACKAGE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CONFIG_PATH = os.path.join(_PACKAGE_DIR, "laura_config.json")


def _detect_vram():
    """Detect VRAM and return (tier, gb, gpu_name, fp8_capable, compute_cap)."""
    if not torch.cuda.is_available():
        return "medium", 8.0, "CPU", False, None
    try:
        props = torch.cuda.get_device_properties(0)
        gb = props.total_memory / (1024**3)
        gpu_name = props.name
        cc = (props.major, props.minor)
        fp8 = cc >= (8, 9)
    except (RuntimeError, AssertionError):
        return "medium", 8.0, "Unknown GPU", False, None

    # Determine tier
    tier = "medium"
    for tier_name, tier_info in VRAM_TIERS.items():
        if tier_info["min_gb"] <= gb < tier_info["max_gb"]:
            tier = tier_name
            break

    return tier, round(gb, 2), gpu_name, fp8, cc


def _scan_installed_models():
    """Scan ComfyUI model folders and return dict of {model_key: [found_files]}."""
    installed = {}
    folder_types = ["checkpoints", "diffusion_models", "vae", "text_encoders",
                    "unet", "clip", "controlnet", "loras", "upscale_models"]

    available_files = {}
    for ft in folder_types:
        try:
            available_files[ft] = [f.lower() for f in folder_paths.get_filename_list(ft)]
        except Exception:
            available_files[ft] = []

    for model_key, model_info in MODEL_REGISTRY.items():
        found = []
        missing = []
        for folder, files in model_info.get("files", {}).items():
            folder_files = available_files.get(folder, [])
            for f_info in files:
                fname = f_info["filename"].lower()
                if any(fname in ff for ff in folder_files):
                    found.append(f_info["filename"])
                else:
                    if f_info.get("required", False):
                        missing.append(f_info["filename"])
        installed[model_key] = {"found": found, "missing": missing}

    return installed


def _load_config():
    """Load laura_config.json or return None."""
    if os.path.exists(_CONFIG_PATH):
        try:
            with open(_CONFIG_PATH, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
    return None


def _save_config(config):
    """Save laura_config.json."""
    try:
        with open(_CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except OSError:
        return False


# ============== NODE 1: LAURA MODEL MANAGER ==============
class LauraModelManager:
    """Comprehensive model health check with download guidance and VRAM-aware recommendations."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scan_now": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "show_category": (["all", "image_gen", "image_edit", "video_gen", "upscale", "vae"], {"default": "all"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("status_report", "download_urls", "recommended_config")
    FUNCTION = "scan_models"
    CATEGORY = "Laura Studio/Model Manager"
    DESCRIPTION = "Scan all supported SOTA models, show install status, VRAM-aware quantization recommendations, and download URLs."

    def scan_models(self, scan_now=True, show_category="all"):
        if not scan_now:
            return ("Scan skipped.", "{}", "")

        tier, vram_gb, gpu_name, fp8, cc = _detect_vram()
        installed = _scan_installed_models()

        cc_str = f"SM {cc[0]}.{cc[1]}" if cc else "N/A"
        lines = [
            f"{'='*60}",
            f"  LAURA STUDIO MODEL MANAGER v{get_registry_version()}",
            f"{'='*60}",
            f"  GPU: {gpu_name} ({vram_gb}GB)",
            f"  VRAM Tier: {tier.upper()} | FP8: {'Yes' if fp8 else 'No'} ({cc_str})",
            f"{'='*60}",
            "",
        ]

        download_links = {}
        total_installed = 0
        total_models = 0

        for cat_key, cat_label in CATEGORIES.items():
            if show_category != "all" and show_category != cat_key:
                continue

            cat_models = get_models_by_category(cat_key)
            if not cat_models:
                continue

            lines.append(f"  {cat_label.upper()}")
            lines.append(f"  {'-'*40}")

            for model_key, model_info in cat_models.items():
                total_models += 1
                status_info = installed.get(model_key, {"found": [], "missing": []})
                has_files = len(model_info.get("files", {})) > 0
                is_pending = model_info.get("status") == "pending_release"

                if is_pending:
                    icon = "⏳"
                    status_text = "PENDING RELEASE"
                elif not has_files:
                    icon = "❓"
                    status_text = "FILES TBD"
                elif len(status_info["missing"]) == 0 and len(status_info["found"]) > 0:
                    icon = "✅"
                    status_text = "INSTALLED"
                    total_installed += 1
                elif len(status_info["found"]) > 0:
                    icon = "⚠️"
                    status_text = "PARTIAL"
                else:
                    icon = "❌"
                    status_text = "MISSING"

                size_str = f"{model_info.get('total_size_gb', 0):.1f}GB" if model_info.get('total_size_gb') else "TBD"
                rec_quant = get_recommended_quantization(model_key, tier) or "N/A"

                lines.append(f"    {icon} {model_info['display_name']:<30} [{size_str}]")
                lines.append(f"       Status: {status_text} | Recommended: {rec_quant}")

                if status_text in ("MISSING", "PARTIAL") and model_info.get("repo"):
                    url = get_download_url(model_key)
                    lines.append(f"       Download: {url}")
                    download_links[model_key] = {
                        "name": model_info["display_name"],
                        "url": url,
                        "size_gb": model_info.get("total_size_gb", 0),
                        "recommended_quant": rec_quant,
                        "files": get_all_required_files(model_key),
                    }

                if status_info["missing"]:
                    for mf in status_info["missing"]:
                        lines.append(f"       Missing: {mf}")

                lines.append("")

        lines.append(f"{'='*60}")
        lines.append(f"  TOTAL: {total_installed}/{total_models} installed")
        if download_links:
            lines.append(f"  {len(download_links)} models available to download")
        lines.append(f"{'='*60}")

        report = "\n".join(lines)
        urls_json = json.dumps(download_links, indent=2)
        config_rec = f"VRAM Tier: {tier}, FP8: {fp8}, Recommended models for your GPU: "
        config_rec += ", ".join([
            m["display_name"] for k, m in MODEL_REGISTRY.items()
            if get_recommended_quantization(k, tier) is not None
            and m.get("status") != "pending_release"
        ][:5]) + "..."

        return (report, urls_json, config_rec)


# ============== NODE 2: MODULE CONFIG PANEL ==============
class ModuleConfigPanel:
    """Toggle Laura Studio modules on/off with smart defaults based on detected hardware and installed models."""

    CORE_MODULES = ["models", "toggle", "quantization", "checkpoint", "batch_processing", "tile_processing", "comparison"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "action": (["show_status", "auto_detect", "save_config"], {"default": "show_status"}),
            },
            "optional": {
                "generation": ("BOOLEAN", {"default": True}),
                "video": ("BOOLEAN", {"default": True}),
                "video_advanced": ("BOOLEAN", {"default": True}),
                "flux_tools": ("BOOLEAN", {"default": True}),
                "upscaling": ("BOOLEAN", {"default": True}),
                "face": ("BOOLEAN", {"default": True}),
                "dressing": ("BOOLEAN", {"default": True}),
                "inpainting": ("BOOLEAN", {"default": True}),
                "background": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("config_status", "active_modules")
    FUNCTION = "manage_config"
    CATEGORY = "Laura Studio/Model Manager"
    DESCRIPTION = "Toggle Laura Studio modules on/off. Core modules are always enabled. Use 'auto_detect' for smart defaults."

    def manage_config(self, action="show_status", **module_toggles):
        config = _load_config() or {}

        if action == "auto_detect":
            tier, vram_gb, gpu_name, fp8, cc = _detect_vram()
            installed = _scan_installed_models()

            config["version"] = "1.0"
            config["auto_detected"] = {
                "vram_tier": tier,
                "vram_gb": vram_gb,
                "gpu_name": gpu_name,
                "fp8_capable": fp8,
                "compute_capability": list(cc) if cc else None,
            }

            modules = {}
            for mod in self.CORE_MODULES:
                modules[mod] = {"enabled": True, "reason": "core module, always enabled"}

            # Smart defaults for optional modules
            optional_module_checks = {
                "generation": lambda: True,
                "video": lambda: True,
                "video_advanced": lambda: any(
                    len(installed.get(k, {}).get("found", [])) > 0
                    for k in ["wan22_14b", "hunyuan_video", "cogvideox_5b", "helios_distilled", "ltx_2_3"]
                ) or vram_gb >= 12,
                "flux_tools": lambda: any(
                    "flux" in f.lower()
                    for f in folder_paths.get_filename_list("checkpoints")
                ) if hasattr(folder_paths, 'get_filename_list') else False,
                "upscaling": lambda: True,
                "face": lambda: True,
                "dressing": lambda: True,
                "inpainting": lambda: True,
                "background": lambda: True,
            }

            for mod, check_fn in optional_module_checks.items():
                try:
                    enabled = check_fn()
                except Exception:
                    enabled = True
                reason = "auto: enabled by detection" if enabled else "auto: disabled (models/VRAM insufficient)"
                modules[mod] = {"enabled": enabled, "reason": reason}

            config["modules"] = modules
            config["user_overrides"] = {}
            _save_config(config)

        elif action == "save_config":
            if "modules" not in config:
                config["modules"] = {}
            for mod_name, enabled in module_toggles.items():
                if mod_name in config.get("modules", {}):
                    config["modules"][mod_name]["enabled"] = enabled
                    config["modules"][mod_name]["reason"] = "user override"
                else:
                    config["modules"][mod_name] = {"enabled": enabled, "reason": "user override"}
                config.setdefault("user_overrides", {})[mod_name] = enabled
            _save_config(config)

        # Build status report
        modules = config.get("modules", {})
        lines = ["=== MODULE CONFIGURATION ===", ""]
        active = []
        for mod_name, mod_info in modules.items():
            if isinstance(mod_info, dict):
                enabled = mod_info.get("enabled", True)
                reason = mod_info.get("reason", "")
            else:
                enabled = bool(mod_info)
                reason = ""
            icon = "✅" if enabled else "❌"
            lines.append(f"  {icon} {mod_name:<20} — {reason}")
            if enabled:
                active.append(mod_name)

        status = "\n".join(lines)
        return (status, ", ".join(active))


# ============== NODE 3: QUANTIZATION ADVISOR ==============
class LauraQuantizationAdvisor:
    """Get VRAM-aware quantization recommendation for any supported model."""

    @classmethod
    def INPUT_TYPES(cls):
        model_choices = sorted(MODEL_REGISTRY.keys())
        return {
            "required": {
                "model": (model_choices, {"default": model_choices[0] if model_choices else "z_image_turbo"}),
            },
            "optional": {
                "override_vram_tier": (["auto", "ultra_low", "low", "medium", "high", "very_high", "ultra", "extreme", "hpc"], {"default": "auto"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "FLOAT")
    RETURN_NAMES = ("recommendation", "download_url", "estimated_vram_gb")
    FUNCTION = "advise"
    CATEGORY = "Laura Studio/Model Manager"
    DESCRIPTION = "Get the optimal quantization format for a model based on your GPU's VRAM."

    def advise(self, model, override_vram_tier="auto"):
        if override_vram_tier == "auto":
            tier, vram_gb, gpu_name, fp8, _ = _detect_vram()
        else:
            tier = override_vram_tier
            vram_gb = VRAM_TIERS.get(tier, {}).get("min_gb", 8.0)
            gpu_name = "Manual"
            fp8 = False

        model_info = MODEL_REGISTRY.get(model, {})
        rec_quant = get_recommended_quantization(model, tier)
        url = get_download_url(model) or "N/A"

        if rec_quant is None:
            return (
                f"Model '{model_info.get('display_name', model)}' is NOT recommended for your VRAM tier ({tier}, {vram_gb}GB). "
                f"This model requires more VRAM than available.",
                url,
                0.0,
            )

        variants = model_info.get("quantization_variants", {})
        variant_info = variants.get(rec_quant, {})
        est_vram = variant_info.get("vram_gb", 0)
        quality = variant_info.get("quality", "unknown")
        speed = variant_info.get("speed", "unknown")
        alt_repo = variant_info.get("alt_repo")

        rec_text = (
            f"Model: {model_info.get('display_name', model)}\n"
            f"Your GPU: {gpu_name} ({vram_gb}GB, {tier})\n"
            f"Recommended: {rec_quant}\n"
            f"  VRAM Usage: ~{est_vram}GB\n"
            f"  Quality: {quality}\n"
            f"  Speed: {speed}\n"
        )
        if alt_repo:
            rec_text += f"  Quantized Repo: https://huggingface.co/{alt_repo}\n"
            url = f"https://huggingface.co/{alt_repo}"
        if fp8 and rec_quant.startswith("fp8"):
            rec_text += f"  Native FP8 acceleration available on your GPU!\n"

        return (rec_text, url, float(est_vram))


# ============== NODE 4: MODEL DOWNLOAD HELPER ==============
class LauraModelDownloadHelper:
    """Generate download commands and URLs for any model in the registry."""

    @classmethod
    def INPUT_TYPES(cls):
        model_choices = sorted(MODEL_REGISTRY.keys())
        return {
            "required": {
                "model": (model_choices,),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "FLOAT")
    RETURN_NAMES = ("download_info", "hf_url", "size_gb")
    FUNCTION = "get_download_info"
    CATEGORY = "Laura Studio/Model Manager"
    DESCRIPTION = "Get download URLs and commands for any supported model."

    def get_download_info(self, model):
        model_info = MODEL_REGISTRY.get(model, {})
        if not model_info:
            return ("Model not found in registry.", "", 0.0)

        url = get_download_url(model) or "N/A"
        size = model_info.get("total_size_gb", 0)
        files = get_all_required_files(model)

        lines = [
            f"=== {model_info.get('display_name', model)} ===",
            f"Repo: {model_info.get('repo', 'N/A')}",
            f"License: {model_info.get('license', 'Unknown')}",
            f"Parameters: {model_info.get('params', 'Unknown')}",
            f"Total Size: {size:.1f}GB",
            f"Status: {model_info.get('status', 'unknown')}",
            "",
            "--- Required Files ---",
        ]

        for f in files:
            lines.append(f"  {f['folder']}/{f['filename']} ({f['size_gb']:.2f}GB)")
            lines.append(f"    URL: {f['url']}")

        lines.append("")
        lines.append("--- Download Command ---")
        if model_info.get("repo"):
            lines.append(f"  pip install -U huggingface_hub")
            lines.append(f"  huggingface-cli download {model_info['repo']}")

        return ("\n".join(lines), url, float(size))


# ============== NODE 5: COMPATIBILITY CHECKER ==============
class LauraCompatibilityChecker:
    """Check LoRA, ControlNet, and IPAdapter compatibility for any model."""

    @classmethod
    def INPUT_TYPES(cls):
        model_choices = sorted([k for k, v in MODEL_REGISTRY.items() if v.get("category") in ("image_gen", "image_edit")])
        return {
            "required": {
                "model": (model_choices,),
                "check_type": (["all", "lora", "controlnet", "ipadapter"], {"default": "all"}),
            },
        }

    RETURN_TYPES = ("STRING", "BOOLEAN")
    RETURN_NAMES = ("compatibility_report", "is_compatible")
    FUNCTION = "check_compatibility"
    CATEGORY = "Laura Studio/Model Manager"
    DESCRIPTION = "Check if LoRA, ControlNet, or IPAdapter works with a given base model."

    def check_compatibility(self, model, check_type="all"):
        model_info = MODEL_REGISTRY.get(model, {})
        compat = model_info.get("compatibility", {})

        lines = [f"=== Compatibility: {model_info.get('display_name', model)} ===", ""]
        any_compatible = False

        checks = {
            "lora": ("LoRA Training/Loading", compat.get("lora", False)),
            "controlnet": ("ControlNet", compat.get("controlnet", False)),
            "ipadapter": ("IPAdapter", compat.get("ipadapter", False)),
        }

        for key, (label, supported) in checks.items():
            if check_type not in ("all", key):
                continue
            icon = "✅" if supported else "❌"
            lines.append(f"  {icon} {label}: {'Supported' if supported else 'Not Supported'}")
            if supported:
                any_compatible = True
                if key == "controlnet" and "controlnet_models" in compat:
                    lines.append(f"      Compatible models: {', '.join(compat['controlnet_models'])}")
                if key == "lora" and "lora_zoo" in compat:
                    lines.append(f"      LoRA Zoo: https://huggingface.co/{compat['lora_zoo']}")
                    if "lora_zoo_models" in compat:
                        lines.append(f"      Available LoRAs: {', '.join(compat['lora_zoo_models'])}")

        # Additional compatibility notes
        if compat.get("negative_prompt") is not None:
            np_icon = "✅" if compat["negative_prompt"] else "❌"
            lines.append(f"  {np_icon} Negative Prompt: {'Supported' if compat['negative_prompt'] else 'Not Supported'}")
        if compat.get("multi_reference"):
            lines.append(f"  ✅ Multi-Reference Editing: Supported")
        if compat.get("image_editing"):
            lines.append(f"  ✅ Native Image Editing: Supported")

        return ("\n".join(lines), any_compatible)


# ============== NODE 6: AUTO CONFIG ==============
class LauraAutoConfig:
    """Run full auto-detection: scan GPU, scan models, generate optimal laura_config.json."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "run_detection": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "force_regenerate": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("detection_report", "config_path")
    FUNCTION = "auto_configure"
    CATEGORY = "Laura Studio/Model Manager"
    OUTPUT_NODE = True
    DESCRIPTION = "Auto-detect GPU, scan installed models, and generate optimal laura_config.json with smart module defaults."

    def auto_configure(self, run_detection=True, force_regenerate=False):
        if not run_detection:
            return ("Detection skipped.", _CONFIG_PATH)

        if os.path.exists(_CONFIG_PATH) and not force_regenerate:
            config = _load_config()
            if config:
                return (
                    f"Config already exists at {_CONFIG_PATH}. Set force_regenerate=True to overwrite.\n"
                    f"Current VRAM tier: {config.get('auto_detected', {}).get('vram_tier', 'unknown')}",
                    _CONFIG_PATH,
                )

        # Use ModuleConfigPanel's auto_detect
        panel = ModuleConfigPanel()
        status, active = panel.manage_config(action="auto_detect")

        # Also run model scan
        manager = LauraModelManager()
        report, _, _ = manager.scan_models(scan_now=True)

        combined = f"{status}\n\n{report}\n\nConfig saved to: {_CONFIG_PATH}"
        return (combined, _CONFIG_PATH)


# ============== REGISTER ALL NODES ==============
NODE_CLASS_MAPPINGS.update({
    "LauraModelManager": LauraModelManager,
    "ModuleConfigPanel": ModuleConfigPanel,
    "LauraQuantizationAdvisor": LauraQuantizationAdvisor,
    "LauraModelDownloadHelper": LauraModelDownloadHelper,
    "LauraCompatibilityChecker": LauraCompatibilityChecker,
    "LauraAutoConfig": LauraAutoConfig,
})

NODE_DISPLAY_NAME_MAPPINGS.update({
    "LauraModelManager": "Laura Model Manager",
    "ModuleConfigPanel": "Module Config Panel",
    "LauraQuantizationAdvisor": "Quantization Advisor",
    "LauraModelDownloadHelper": "Model Download Helper",
    "LauraCompatibilityChecker": "Compatibility Checker",
    "LauraAutoConfig": "Auto Config Generator",
})
```

**Step 2: Verify the module imports cleanly alongside model_registry**

Run the same test_imports pattern to check for syntax errors:
```bash
python -c "
import sys, types
sys.modules['folder_paths'] = types.ModuleType('folder_paths')
sys.modules['folder_paths'].get_filename_list = lambda x: ['test.safetensors']
sys.modules['folder_paths'].get_output_directory = lambda: '/tmp'
sys.path.insert(0, 'custom_nodes')
from Laura_Image_Studio.nodes.model_manager import NODE_CLASS_MAPPINGS
print(f'Loaded {len(NODE_CLASS_MAPPINGS)} model manager nodes')
print('Nodes:', list(NODE_CLASS_MAPPINGS.keys()))
"
```
Expected: `Loaded 6 model manager nodes`

**Step 3: Commit**

```bash
git add custom_nodes/Laura_Image_Studio/nodes/model_manager.py
git commit -m "feat: add 6 model manager nodes

LauraModelManager, ModuleConfigPanel, LauraQuantizationAdvisor,
LauraModelDownloadHelper, LauraCompatibilityChecker, LauraAutoConfig.
All nodes use centralized model_registry.py as source of truth."
```

---

## Task 3: Update `__init__.py` for Module Enable/Disable

**Files:**
- Modify: `custom_nodes/Laura_Image_Studio/__init__.py`

**Step 1: Update __init__.py to support conditional module loading**

Replace the current module loading logic with config-aware loading. The key changes:
1. Add `model_manager` to `_modules_to_load`
2. Load `laura_config.json` before loading modules
3. Skip disabled modules based on config
4. Log which modules were enabled/disabled

The modified `__init__.py` should:
- Always load `model_registry` and `model_manager` (they're the config system itself)
- Check `laura_config.json` for module enable/disable settings
- Fall back to loading everything if no config exists (first run)
- Log module loading status

Key code change in the module loading section:

```python
# Add model_manager to the module list
_modules_to_load = [
    "model_registry",  # Must load first — no nodes, just data
    "model_manager",   # Must load second — config system
    "generation",
    "models",
    "toggle",
    "checkpoint",
    "video",
    "dressing",
    "face",
    "inpainting",
    "upscaling",
    "background",
    "quantization",
    "video_advanced",
    "batch_processing",
    "tile_processing",
    "comparison",
    "flux_tools",
]

# Core modules always load (even if config says otherwise)
_CORE_MODULES = {"model_registry", "model_manager", "models", "toggle",
                 "quantization", "checkpoint", "batch_processing",
                 "tile_processing", "comparison"}

# Load config if available
_config = None
_config_path = os.path.join(os.path.dirname(__file__), "laura_config.json")
if os.path.exists(_config_path):
    try:
        import json
        with open(_config_path, "r") as _cf:
            _config = json.load(_cf)
        print("[Laura Image Studio] Loaded module config from laura_config.json")
    except Exception as _e:
        print(f"[Laura Image Studio] WARNING: Failed to load config: {_e}")

for _mod_name in _modules_to_load:
    # Check if module is disabled in config (core modules always load)
    if _config and _mod_name not in _CORE_MODULES:
        _mod_config = _config.get("modules", {}).get(_mod_name, {})
        if isinstance(_mod_config, dict) and not _mod_config.get("enabled", True):
            print(f"[Laura Image Studio] SKIPPED: {_mod_name} (disabled in config)")
            continue

    try:
        import importlib
        _mod = importlib.import_module(f".nodes.{_mod_name}", package=__name__)
        NODE_CLASS_MAPPINGS.update(getattr(_mod, "NODE_CLASS_MAPPINGS", {}))
        NODE_DISPLAY_NAME_MAPPINGS.update(
            getattr(_mod, "NODE_DISPLAY_NAME_MAPPINGS", {})
        )
    except Exception as e:
        print(f"[Laura Image Studio] WARNING: Failed to load {_mod_name}: {e}")
```

**Note:** `model_registry` has no `NODE_CLASS_MAPPINGS` — its `getattr` will return `{}`, which is fine.

**Step 2: Verify the updated init loads correctly**

```bash
python scripts/test_imports.py
```
Expected: `Laura Image Studio modules loaded successfully`

**Step 3: Commit**

```bash
git add custom_nodes/Laura_Image_Studio/__init__.py
git commit -m "feat: add config-aware module loading to __init__.py

Loads laura_config.json on startup, skips disabled modules,
always loads core modules. Adds model_registry and model_manager
to the module list."
```

---

## Task 4: Update `nodes/models.py` — Registry-Based Detection

**Files:**
- Modify: `custom_nodes/Laura_Image_Studio/nodes/models.py`

**Step 1: Update ModelTypeDetector to use registry**

Replace the hardcoded `detect_type` method with registry-based detection. Import `detect_model_key_from_filename` from `model_registry` and use it.

Key changes to `ModelTypeDetector.detect_type()`:

```python
from .model_registry import detect_model_key_from_filename, MODEL_REGISTRY

def detect_type(self, model_name):
    LauraLogger.info(f"Detecting architecture for: {model_name}")

    # Try registry-based detection first
    model_key = detect_model_key_from_filename(model_name)
    if model_key and model_key in MODEL_REGISTRY:
        model_info = MODEL_REGISTRY[model_key]
        res = model_info.get("inference", {}).get("default_resolution", [1024, 1024])
        # Map registry key to model_type string
        type_map = {
            "z_image_turbo": "zimage_turbo",
            "z_image_base": "zimage",
            "z_image_edit": "zimage_edit",
            "flux2_dev": "flux2",
            "flux1_dev": "flux",
            "flux1_schnell": "flux_schnell",
            "qwen_image_2512": "qwen",
            "glm_image": "glm_image",
            "firered_edit_1_1": "firered",
            "helios_distilled": "helios",
            "helios_base": "helios",
            "ltx_2_3": "ltx23",
            "sd35_medium": "sd35",
        }
        model_type = type_map.get(model_key, model_key)
        return (model_type, res[0], res[1])

    # Fallback to existing detection (for models not in registry)
    # ... keep existing if/elif chain as fallback ...
```

**Step 2: Update UniversalModelLoader and AdvancedModelLoader dropdowns**

Add new model types to both loaders' `model_type` dropdowns:

```python
"model_type": ([
    "auto", "sdxl", "flux", "flux_schnell", "flux2", "flux2_schnell",
    "sd15", "sd3", "sd35", "sd35_medium",
    "wan21", "wan22",
    "zimage", "zimage_turbo", "zimage_edit",
    "qwen", "glm_image", "firered",
    "helios", "ltx23",
    "playground", "pixart", "aura", "kolors",
],),
```

Also add the new types to the `resolution_map` dict in `UniversalModelLoader.load_model()`:
```python
"glm_image": (1024, 1024),
"firered": (1024, 1024),
"helios": (1024, 1024),
"ltx23": (768, 768),
```

**Step 3: Update ModelHealthCheck to use registry**

Replace the hardcoded `required` dict in `ModelHealthCheck.check_health()` with a registry-based scan. Import and use `_scan_installed_models` from `model_manager` or reimplement inline using `MODEL_REGISTRY`.

**Step 4: Verify**

```bash
python scripts/test_imports.py
```

**Step 5: Commit**

```bash
git add custom_nodes/Laura_Image_Studio/nodes/models.py
git commit -m "feat: update model detection and loaders to use registry

ModelTypeDetector now uses registry-based detection with fallback.
UniversalModelLoader and AdvancedModelLoader support new model types:
flux2, glm_image, firered, helios, ltx23. ModelHealthCheck uses
comprehensive registry scan."
```

---

## Task 5: Update `nodes/quantization.py` — Registry-Based Recommendations

**Files:**
- Modify: `custom_nodes/Laura_Image_Studio/nodes/quantization.py`

**Step 1: Update QuantizationSelector to use registry**

Add the new model types to the `model_type` dropdown and use the registry for recommendations:

```python
"model_type": ([
    "auto", "sdxl", "flux", "flux_schnell", "flux2",
    "sd15", "sd3", "wan21", "wan22", "cogvideox",
    "zimage_turbo", "zimage", "qwen", "glm_image",
    "firered", "helios", "ltx23",
],),
```

Update `select_quantization()` to try registry-based lookup first:

```python
def select_quantization(self, vram_tier, model_type):
    # Try registry-based recommendation first
    from .model_registry import get_recommended_quantization
    # Map model_type string to registry key
    type_to_key = {
        "zimage_turbo": "z_image_turbo", "zimage": "z_image_base",
        "flux": "flux1_dev", "flux_schnell": "flux1_schnell",
        "flux2": "flux2_dev", "qwen": "qwen_image_2512",
        "glm_image": "glm_image", "firered": "firered_edit_1_1",
        "helios": "helios_distilled", "ltx23": "ltx_2_3",
        "wan22": "wan22_14b", "cogvideox": "cogvideox_5b",
        "sd3": "sd35_medium", "sd15": "sd35_medium", "sdxl": "sd35_medium",
    }
    registry_key = type_to_key.get(model_type)
    if registry_key:
        rec = get_recommended_quantization(registry_key, vram_tier)
        if rec:
            return (rec,)

    # Fallback to existing logic for unmapped types
    # ... keep existing if/elif chain ...
```

**Step 2: Commit**

```bash
git add custom_nodes/Laura_Image_Studio/nodes/quantization.py
git commit -m "feat: update QuantizationSelector with registry-based recommendations

Supports all new model types (flux2, zimage_turbo, glm_image, firered,
helios, ltx23) via centralized registry lookup with fallback."
```

---

## Task 6: Update `scripts/model_downloader.py` — Use Registry

**Files:**
- Modify: `scripts/model_downloader.py`

**Step 1: Rewrite to use the centralized registry**

Replace the hardcoded `MODEL_REGISTRY` with an import from the registry module. Add `--recommend` flag and improve the CLI:

```python
"""
Laura Image Studio - Model Synchronization Script
Uses centralized model registry for all model metadata.
"""
import os
import sys
import argparse

# Add the custom_nodes path so we can import the registry
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "custom_nodes"))

try:
    from Laura_Image_Studio.nodes.model_registry import (
        MODEL_REGISTRY, get_all_required_files, get_download_url,
        get_recommended_quantization, get_models_by_category, CATEGORIES
    )
except ImportError:
    print("ERROR: Could not import model registry. Make sure Laura_Image_Studio is installed.")
    sys.exit(1)

from huggingface_hub import hf_hub_download


def download_model(model_key, target_base=None):
    """Download a model from HuggingFace."""
    if model_key not in MODEL_REGISTRY:
        print(f"Error: Model '{model_key}' not found in registry.")
        print(f"Available: {', '.join(sorted(MODEL_REGISTRY.keys()))}")
        return False

    model_info = MODEL_REGISTRY[model_key]
    repo = model_info.get("repo")
    if not repo:
        print(f"Error: No repo URL for '{model_key}'")
        return False

    files = get_all_required_files(model_key)
    if not files:
        print(f"Warning: No specific files listed for '{model_key}'. Use manual download:")
        print(f"  huggingface-cli download {repo}")
        return False

    print(f"\n[Laura Studio Sync] Downloading {model_info['display_name']} from {repo}")
    print(f"  Total size: ~{model_info.get('total_size_gb', 0):.1f}GB")

    for f in files:
        target_dir = target_base or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", f["folder"])
        os.makedirs(target_dir, exist_ok=True)
        print(f"  Downloading: {f['filename']} ({f['size_gb']:.2f}GB) -> {target_dir}")
        try:
            path = hf_hub_download(
                repo_id=repo,
                filename=f["filename"],
                local_dir=target_dir,
                local_dir_use_symlinks=False,
            )
            print(f"  Success: {path}")
        except Exception as e:
            print(f"  Failed: {e}")
            return False
    return True


def list_registry(category=None):
    """List all models in the registry."""
    print(f"\n{'='*60}")
    print(f"  LAURA STUDIO MODEL REGISTRY ({len(MODEL_REGISTRY)} models)")
    print(f"{'='*60}\n")

    for cat_key, cat_label in CATEGORIES.items():
        if category and category != cat_key:
            continue
        models = get_models_by_category(cat_key)
        if not models:
            continue
        print(f"  {cat_label}")
        print(f"  {'-'*40}")
        for key, info in models.items():
            status = info.get("status", "unknown")
            size = f"{info.get('total_size_gb', 0):.1f}GB"
            print(f"    {key:<25} {info['display_name']:<30} [{size}] ({status})")
        print()


def recommend(vram_gb=None):
    """Show VRAM-aware recommendations."""
    import torch
    if vram_gb is None and torch.cuda.is_available():
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    elif vram_gb is None:
        vram_gb = 8.0

    # Determine tier
    tiers = [(4.5, "ultra_low"), (6.5, "low"), (8.5, "medium"), (12.5, "high"),
             (16.5, "very_high"), (24.5, "ultra"), (48.5, "extreme"), (999, "hpc")]
    tier = "medium"
    for threshold, t in tiers:
        if vram_gb < threshold:
            tier = t
            break

    print(f"\n  Recommendations for {vram_gb:.1f}GB VRAM (tier: {tier})")
    print(f"  {'='*50}\n")

    for key, info in MODEL_REGISTRY.items():
        rec = get_recommended_quantization(key, tier)
        if rec:
            print(f"    ✅ {info['display_name']:<30} → {rec}")
        else:
            print(f"    ❌ {info['display_name']:<30} → Too large for your GPU")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Laura Image Studio Model Synchronizer")
    parser.add_argument("--list", action="store_true", help="List all models in registry")
    parser.add_argument("--category", type=str, help="Filter by category (image_gen, image_edit, video_gen, upscale, vae)")
    parser.add_argument("--download", type=str, help="Download a specific model by registry key")
    parser.add_argument("--all", action="store_true", help="Download ALL core models (Warning: Massive!)")
    parser.add_argument("--recommend", action="store_true", help="Show VRAM-aware model recommendations")
    parser.add_argument("--vram", type=float, help="Override VRAM in GB for --recommend")

    args = parser.parse_args()

    if args.list:
        list_registry(args.category)
    elif args.recommend:
        recommend(args.vram)
    elif args.download:
        download_model(args.download)
    elif args.all:
        for key in MODEL_REGISTRY:
            if MODEL_REGISTRY[key].get("status") == "released" and MODEL_REGISTRY[key].get("files"):
                download_model(key)
    else:
        parser.print_help()
```

**Step 2: Commit**

```bash
git add scripts/model_downloader.py
git commit -m "feat: rewrite model_downloader.py to use centralized registry

Replaces hardcoded 7-model dict with full registry import.
Adds --recommend flag for VRAM-aware suggestions and --category filter."
```

---

## Task 7: Update Workflow JSONs with Model Metadata

**Files:**
- Modify: All workflow JSON files in `custom_nodes/Laura_Image_Studio/workflows/`

**Step 1: Create a script to inject models metadata into workflow JSONs**

Create a helper script that reads each workflow JSON, determines which models it references, and injects the proper `models` metadata block for ComfyUI's native missing-models dialog.

Save as `scripts/inject_workflow_models.py`:

```python
"""Inject 'models' metadata into workflow JSONs for ComfyUI's native missing-models popup."""
import json
import os
import sys
import glob

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "custom_nodes"))
from Laura_Image_Studio.nodes.model_registry import MODEL_REGISTRY, get_all_required_files

# Common model filename patterns to detect in workflow node widgets
MODEL_PATTERNS = {}
for key, info in MODEL_REGISTRY.items():
    for folder, files in info.get("files", {}).items():
        for f in files:
            MODEL_PATTERNS[f["filename"].lower()] = {
                "name": f["filename"],
                "url": f"https://huggingface.co/{info['repo']}/resolve/main/{f['filename']}" if info.get("repo") else "",
                "directory": folder,
                "size": int(f.get("size_gb", 0) * 1_000_000_000),
            }


def inject_models_metadata(workflow_path):
    """Inject models metadata into a workflow JSON."""
    with open(workflow_path, "r") as f:
        workflow = json.load(f)

    # Scan all nodes' widget values for model filenames
    found_models = []
    seen = set()
    nodes = workflow.get("nodes", [])
    for node in nodes:
        widgets = node.get("widgets_values", [])
        for w in widgets:
            if isinstance(w, str) and w.lower() in MODEL_PATTERNS:
                model_meta = MODEL_PATTERNS[w.lower()]
                if model_meta["name"] not in seen and model_meta["url"]:
                    found_models.append(model_meta)
                    seen.add(model_meta["name"])

    if found_models:
        workflow["models"] = found_models
        with open(workflow_path, "w") as f:
            json.dump(workflow, f, indent=2)
        print(f"  Injected {len(found_models)} model entries into {os.path.basename(workflow_path)}")
    else:
        print(f"  No model references found in {os.path.basename(workflow_path)}")


if __name__ == "__main__":
    workflow_dirs = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "custom_nodes", "Laura_Image_Studio", "workflows"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workflows"),
    ]
    for wdir in workflow_dirs:
        if not os.path.isdir(wdir):
            continue
        print(f"\nProcessing: {wdir}")
        for wf in sorted(glob.glob(os.path.join(wdir, "*.json"))):
            inject_models_metadata(wf)
```

**Step 2: Run the injection script**

```bash
python scripts/inject_workflow_models.py
```

**Step 3: Commit**

```bash
git add scripts/inject_workflow_models.py
git add custom_nodes/Laura_Image_Studio/workflows/*.json
git add workflows/*.json
git commit -m "feat: add workflow model metadata for ComfyUI native download popup

Inject 'models' blocks into all workflow JSONs so ComfyUI's
built-in missing-models dialog shows correct download URLs and sizes.
Adds inject_workflow_models.py utility script."
```

---

## Task 8: Final Integration Test

**Step 1: Run the full import test**

```bash
python scripts/test_imports.py
```

Expected: All modules load, including model_registry and model_manager.

**Step 2: Verify model registry coverage**

```bash
python -c "
import sys, types
sys.modules['folder_paths'] = types.ModuleType('folder_paths')
sys.modules['folder_paths'].get_filename_list = lambda x: []
sys.modules['folder_paths'].get_output_directory = lambda: '/tmp'
sys.path.insert(0, 'custom_nodes')
from Laura_Image_Studio.nodes.model_registry import MODEL_REGISTRY, get_models_by_category
print(f'Total models: {len(MODEL_REGISTRY)}')
for cat in ['image_gen', 'image_edit', 'video_gen', 'upscale', 'vae']:
    models = get_models_by_category(cat)
    print(f'  {cat}: {len(models)} — {[m[\"display_name\"] for m in models.values()]}')
"
```

**Step 3: Verify node count hasn't broken**

```bash
python -c "
import sys, types
sys.modules['folder_paths'] = types.ModuleType('folder_paths')
sys.modules['folder_paths'].get_filename_list = lambda x: ['test.safetensors']
sys.modules['folder_paths'].get_output_directory = lambda: '/tmp'
sys.modules['nodes'] = types.ModuleType('nodes')
sys.path.insert(0, 'custom_nodes')
from Laura_Image_Studio import NODE_CLASS_MAPPINGS
print(f'Total nodes: {len(NODE_CLASS_MAPPINGS)}')
assert len(NODE_CLASS_MAPPINGS) >= 121 + 6, f'Expected 127+ nodes, got {len(NODE_CLASS_MAPPINGS)}'
print('All good — 127+ nodes loaded')
"
```

Expected: 127+ nodes (121 original + 6 new model manager nodes)

**Step 4: Final commit**

```bash
git add -A
git commit -m "feat: Laura Studio v1.0 — SOTA Model Registry + Auto-Config

Major upgrade adding:
- Centralized model registry with 20+ SOTA models (March 2026)
- 6 new model management nodes
- Auto-config detection (VRAM + models + modules)
- Module enable/disable with smart defaults
- Workflow model metadata for ComfyUI download popup
- VRAM-aware quantization recommendations for all models

New models: Z-Image Turbo/Base/Edit, Flux 2 Dev, Qwen-Image-2512,
GLM-Image 16B, FireRed-Image-Edit 1.1, Helios (Distilled/Base),
LTX-2.3, SeedVR2

New nodes: LauraModelManager, ModuleConfigPanel, LauraQuantizationAdvisor,
LauraModelDownloadHelper, LauraCompatibilityChecker, LauraAutoConfig"
```

---

## Execution Notes

- **Task 1** must be done first (other tasks depend on it)
- **Tasks 2-6** can be done in parallel (they import from Task 1 but don't depend on each other)
- **Task 7** depends on Task 1 (needs registry for model patterns)
- **Task 8** must be last (integration test)

## Risk Mitigations

1. **Import failures:** `model_registry.py` has NO external dependencies (no torch, no folder_paths). It will always load.
2. **Backward compatibility:** All existing node interfaces remain unchanged. Only new dropdown options are added.
3. **Config doesn't exist on first run:** `__init__.py` falls back to loading all modules if no config exists.
4. **Registry data may be incomplete:** File sizes and URLs marked "TBD" for models not yet released. These gracefully degrade — the model just shows as "FILES TBD" in the manager.
