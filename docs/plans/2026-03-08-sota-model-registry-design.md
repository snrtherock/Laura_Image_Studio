# Design: Centralized Model Registry + SOTA Model Upgrade v1.0

**Date:** 2026-03-08
**Status:** Approved
**Author:** snrtherock + Claude

## Problem Statement

Laura Image Studio v0.9 has a fragmented model infrastructure:
- `ModelHealthCheck` only checks 4 models
- `model_downloader.py` has a hardcoded 7-entry registry with no quantization info
- `ModelTypeDetector` is missing detection for Flux 2, GLM-Image, Seedream, LTX-2.3, Helios, FireRed, SeedVR2
- `QuantizationSelector` only maps 6 model types
- No download popup or model manager node exists
- No module enable/disable system
- Missing all March 2026 SOTA models

## Goals

1. Single source of truth for all supported models (registry)
2. Auto-detect GPU config and recommend optimal settings
3. Module enable/disable with smart defaults + user overrides
4. Model download manager node with HuggingFace links, sizes, quantization recommendations
5. Enhanced workflow JSONs for ComfyUI's native missing-models dialog
6. Support ALL current open-source SOTA models (March 2026)

## Architecture: Centralized Model Registry (Approach A)

### New File: `nodes/model_registry.py`

Single Python module with a `MODEL_REGISTRY` dict. Each entry:

```python
MODEL_REGISTRY = {
    # ============== IMAGE GENERATION ==============
    "z_image_turbo": {
        "display_name": "Z-Image Turbo",
        "family": "zimage",
        "category": "image_gen",
        "repo": "Tongyi-MAI/Z-Image-Turbo",
        "homepage": "https://tongyi-mai.github.io/Z-Image-blog/",
        "license": "Apache-2.0",
        "params": "6B",
        "architecture": "S3-DiT (Single-Stream DiT)",
        "files": {
            "diffusion_models": [
                {
                    "filename": "z_image_turbo_bf16.safetensors",
                    "size_gb": 11.46,
                    "precision": "bf16",
                    "required": True,
                }
            ],
            "text_encoders": [
                {
                    "filename": "qwen_3_4b.safetensors",
                    "size_gb": 7.49,
                    "precision": "bf16",
                    "required": True,
                }
            ],
            "vae": [
                {
                    "filename": "ae.safetensors",
                    "size_gb": 0.31,
                    "precision": "bf16",
                    "required": True,
                }
            ],
        },
        "quantization_variants": {
            "bf16": {"vram_gb": 16, "quality": "best", "speed": "fast (8 steps)"},
            "fp8": {"vram_gb": 10, "quality": "near-best", "speed": "fast"},
            "gguf_q8": {"vram_gb": 8, "quality": "good", "speed": "medium"},
            "gguf_q4": {"vram_gb": 6, "quality": "acceptable", "speed": "medium"},
            "nvfp4": {"vram_gb": 6, "quality": "good", "speed": "fast (Ada+)"},
        },
        "quantization_recommendation": {
            "ultra_low": "gguf_q4",
            "low": "gguf_q8",
            "medium": "fp8",
            "high": "bf16",
            "very_high": "bf16",
            "ultra": "bf16",
            "extreme": "bf16",
            "hpc": "bf16",
        },
        "inference": {
            "steps": 8,
            "cfg": False,
            "resolution_range": [512, 2048],
            "default_resolution": [1024, 1024],
        },
        "compatibility": {
            "lora": False,
            "controlnet": True,
            "controlnet_models": ["ControlNet Union 2.1"],
            "ipadapter": True,
            "negative_prompt": False,
        },
        "quality_score": {
            "elo_rank": "#1 open-source (Alibaba AI Arena)",
            "strengths": ["photorealism", "bilingual text rendering", "prompt adherence"],
            "weaknesses": ["low diversity", "no LoRA support", "no negative prompt"],
        },
        "module_dependency": "generation",
    },

    "z_image_base": {
        "display_name": "Z-Image (Base)",
        "family": "zimage",
        "category": "image_gen",
        "repo": "Tongyi-MAI/Z-Image",
        "license": "Apache-2.0",
        "params": "6B",
        "architecture": "S3-DiT",
        "files": {
            "diffusion_models": [
                {
                    "filename": "z_image_bf16.safetensors",
                    "size_gb": 11.46,
                    "precision": "bf16",
                    "required": True,
                }
            ],
            "text_encoders": [
                {
                    "filename": "qwen_3_4b.safetensors",
                    "size_gb": 7.49,
                    "precision": "bf16",
                    "required": True,
                    "shared_with": ["z_image_turbo"],
                }
            ],
            "vae": [
                {
                    "filename": "ae.safetensors",
                    "size_gb": 0.31,
                    "precision": "bf16",
                    "required": True,
                    "shared_with": ["z_image_turbo"],
                }
            ],
        },
        "quantization_variants": {
            "bf16": {"vram_gb": 16, "quality": "best", "speed": "slow (28-50 steps)"},
            "fp8": {"vram_gb": 10, "quality": "near-best", "speed": "medium"},
            "gguf_q8": {"vram_gb": 8, "quality": "good", "speed": "medium"},
            "gguf_q4": {"vram_gb": 6, "quality": "acceptable", "speed": "medium"},
        },
        "quantization_recommendation": {
            "ultra_low": "gguf_q4",
            "low": "gguf_q8",
            "medium": "fp8",
            "high": "bf16",
            "very_high": "bf16",
            "ultra": "bf16",
            "extreme": "bf16",
            "hpc": "bf16",
        },
        "inference": {
            "steps": 50,
            "cfg": True,
            "cfg_scale": [3.0, 5.0],
            "resolution_range": [512, 2048],
            "default_resolution": [1024, 1024],
        },
        "compatibility": {
            "lora": True,
            "controlnet": True,
            "controlnet_models": ["ControlNet Union 2.1"],
            "ipadapter": True,
            "negative_prompt": True,
        },
        "quality_score": {
            "strengths": ["high diversity", "LoRA training", "negative prompting", "fine-tunability"],
            "weaknesses": ["slower than Turbo (28-50 steps)"],
        },
        "module_dependency": "generation",
    },

    "z_image_edit": {
        "display_name": "Z-Image Edit",
        "family": "zimage",
        "category": "image_edit",
        "repo": "Tongyi-MAI/Z-Image-Edit",
        "license": "Apache-2.0",
        "params": "6B",
        "architecture": "S3-DiT",
        "status": "pending_release",
        "files": {},
        "quantization_recommendation": {},
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
        "files": {
            "checkpoints": [
                {
                    "filename": "flux2-dev.safetensors",
                    "size_gb": 24.0,
                    "precision": "bf16",
                    "required": True,
                }
            ],
        },
        "quantization_variants": {
            "bf16": {"vram_gb": 48, "quality": "best", "speed": "medium"},
            "fp8": {"vram_gb": 24, "quality": "near-best", "speed": "medium"},
            "bnb_4bit": {
                "vram_gb": 8,
                "quality": "good",
                "speed": "medium",
                "repo": "diffusers/FLUX.2-dev-bnb-4bit",
            },
            "nvfp4": {
                "vram_gb": 10,
                "quality": "good",
                "speed": "fast (Ada+)",
                "repo": "black-forest-labs/FLUX.2-dev-NVFP4",
            },
        },
        "quantization_recommendation": {
            "ultra_low": None,
            "low": "bnb_4bit",
            "medium": "bnb_4bit",
            "high": "fp8",
            "very_high": "fp8",
            "ultra": "bf16",
            "extreme": "bf16",
            "hpc": "bf16",
        },
        "inference": {
            "steps": 50,
            "cfg": True,
            "cfg_scale": 4.0,
            "resolution_range": [512, 2048],
            "default_resolution": [1024, 1024],
        },
        "compatibility": {
            "lora": True,
            "controlnet": True,
            "ipadapter": True,
            "negative_prompt": True,
            "multi_reference": True,
            "image_editing": True,
        },
        "quality_score": {
            "strengths": [
                "SOTA multi-reference",
                "generation + editing in one model",
                "32B parameters",
            ],
            "weaknesses": ["very large model", "requires agreement on HF"],
        },
        "module_dependency": "generation",
    },

    "flux1_dev": {
        "display_name": "Flux 1 Dev",
        "family": "flux",
        "category": "image_gen",
        "repo": "black-forest-labs/FLUX.1-dev",
        "license": "FLUX Non-Commercial License",
        "params": "12B",
        "files": {
            "checkpoints": [
                {
                    "filename": "flux1-dev.safetensors",
                    "size_gb": 24.0,
                    "precision": "bf16",
                    "required": True,
                }
            ],
        },
        "quantization_variants": {
            "bf16": {"vram_gb": 24, "quality": "best"},
            "fp8": {"vram_gb": 12, "quality": "near-best"},
            "gguf_q8": {"vram_gb": 8, "quality": "good"},
        },
        "quantization_recommendation": {
            "ultra_low": "gguf_q4",
            "low": "gguf_q8",
            "medium": "fp8",
            "high": "bf16",
            "very_high": "bf16",
            "ultra": "bf16",
            "extreme": "bf16",
            "hpc": "bf16",
        },
        "compatibility": {"lora": True, "controlnet": True, "ipadapter": True},
        "module_dependency": "generation",
    },

    "flux1_schnell": {
        "display_name": "Flux 1 Schnell",
        "family": "flux",
        "category": "image_gen",
        "repo": "black-forest-labs/FLUX.1-schnell",
        "license": "Apache-2.0",
        "params": "12B",
        "files": {
            "checkpoints": [
                {
                    "filename": "flux1-schnell.safetensors",
                    "size_gb": 24.0,
                    "precision": "bf16",
                    "required": True,
                }
            ],
        },
        "quantization_recommendation": {
            "ultra_low": "gguf_q4",
            "low": "gguf_q8",
            "medium": "fp8",
            "high": "bf16",
            "very_high": "bf16",
            "ultra": "bf16",
            "extreme": "bf16",
            "hpc": "bf16",
        },
        "compatibility": {"lora": False, "controlnet": True, "ipadapter": True},
        "module_dependency": "generation",
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
        "files": {},
        "quantization_variants": {
            "bf16": {"vram_gb": 16, "quality": "best"},
            "fp8": {"vram_gb": 10, "quality": "near-best"},
        },
        "quantization_recommendation": {
            "ultra_low": None,
            "low": "fp8",
            "medium": "fp8",
            "high": "bf16",
            "very_high": "bf16",
            "ultra": "bf16",
            "extreme": "bf16",
            "hpc": "bf16",
        },
        "compatibility": {"lora": True, "controlnet": False, "ipadapter": False},
        "quality_score": {
            "strengths": ["enterprise workflows", "precise detail", "realism"],
        },
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
        "files": {},
        "quantization_variants": {
            "bf16": {"vram_gb": 32, "quality": "best"},
            "fp8": {"vram_gb": 16, "quality": "near-best"},
            "gguf_q8": {"vram_gb": 12, "quality": "good"},
        },
        "quantization_recommendation": {
            "ultra_low": None,
            "low": None,
            "medium": "gguf_q8",
            "high": "fp8",
            "very_high": "fp8",
            "ultra": "bf16",
            "extreme": "bf16",
            "hpc": "bf16",
        },
        "compatibility": {"lora": False, "controlnet": False, "ipadapter": False},
        "quality_score": {
            "strengths": ["beats Nano Banana Pro at text-heavy images", "high fidelity"],
        },
        "module_dependency": "generation",
    },

    "sd35_medium": {
        "display_name": "SD 3.5 Medium",
        "family": "sd3",
        "category": "image_gen",
        "repo": "stabilityai/stable-diffusion-3.5-medium",
        "license": "Stability Community License",
        "params": "2.5B",
        "files": {
            "checkpoints": [
                {
                    "filename": "sd3.5_medium.safetensors",
                    "size_gb": 6.0,
                    "required": True,
                }
            ],
        },
        "quantization_recommendation": {
            "ultra_low": "fp8",
            "low": "fp16",
            "medium": "fp16",
            "high": "fp16",
            "very_high": "fp16",
            "ultra": "fp16",
            "extreme": "fp16",
            "hpc": "fp16",
        },
        "compatibility": {"lora": True, "controlnet": True, "ipadapter": True},
        "module_dependency": "generation",
    },

    # ============== IMAGE EDITING ==============
    "firered_edit_1_1": {
        "display_name": "FireRed-Image-Edit 1.1",
        "family": "firered",
        "category": "image_edit",
        "repo": "FireRedTeam/FireRed-Image-Edit-1.1",
        "homepage": "https://github.com/FireRedTeam/FireRed-Image-Edit",
        "license": "Apache-2.0",
        "params": "~12B",
        "files": {},
        "quantization_variants": {
            "bf16": {"vram_gb": 30, "quality": "best", "speed": "4.5s end-to-end"},
            "gguf_q8": {
                "vram_gb": 10,
                "quality": "good",
                "repo": "drbaph/FireRed-Image-Edit-1.0_ComfyUI_Quants",
            },
        },
        "quantization_recommendation": {
            "ultra_low": None,
            "low": None,
            "medium": "gguf_q8",
            "high": "gguf_q8",
            "very_high": "bf16",
            "ultra": "bf16",
            "extreme": "bf16",
            "hpc": "bf16",
        },
        "compatibility": {
            "lora": True,
            "lora_zoo": "FireRedTeam/FireRed-Image-Edit-LoRA-Zoo",
            "lora_zoo_models": ["Makeup", "Covercraft", "Style"],
            "comfyui_native": True,
        },
        "quality_score": {
            "elo_rank": "SOTA open-source image editing",
            "strengths": [
                "identity consistency",
                "multi-element fusion",
                "portrait makeup",
                "text style reference",
                "photo restoration",
            ],
        },
        "module_dependency": "inpainting",
    },

    # ============== VIDEO GENERATION ==============
    "helios_distilled": {
        "display_name": "Helios (Distilled)",
        "family": "helios",
        "category": "video_gen",
        "repo": "BestWishYsh/Helios-Distilled",
        "homepage": "https://github.com/PKU-YuanGroup/Helios",
        "license": "Open Source",
        "params": "14B distilled",
        "status": "brand_new",
        "released": "2026-03-04",
        "files": {},
        "quantization_recommendation": {},
        "quality_score": {
            "strengths": ["real-time", "long video", "cheaper than 1.3B models"],
        },
        "module_dependency": "video_advanced",
    },

    "helios_base": {
        "display_name": "Helios (Base)",
        "family": "helios",
        "category": "video_gen",
        "repo": "BestWishYsh/Helios-Base",
        "license": "Open Source",
        "params": "14B",
        "status": "brand_new",
        "released": "2026-03-04",
        "files": {},
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
        "files": {},
        "quantization_variants": {
            "bf16": {"vram_gb": 12, "quality": "best"},
            "fp8": {"vram_gb": 8, "quality": "good"},
        },
        "quality_score": {
            "strengths": ["audio support", "portrait video", "sharper detail", "vertical format"],
        },
        "module_dependency": "video_advanced",
    },

    "wan22_14b": {
        "display_name": "Wan 2.2 14B",
        "family": "wan",
        "category": "video_gen",
        "repo": "Wan-AI/Wan2.2-14B-T2V",
        "params": "14B",
        "files": {
            "checkpoints": [
                {
                    "filename": "diffusion_pytorch_model.safetensors",
                    "size_gb": 28.0,
                    "required": True,
                }
            ],
        },
        "quantization_recommendation": {
            "ultra_low": None,
            "low": None,
            "medium": None,
            "high": "fp8",
            "very_high": "fp8",
            "ultra": "bf16",
            "extreme": "bf16",
            "hpc": "bf16",
        },
        "compatibility": {"motion_control": True, "i2v": True, "t2v": True},
        "module_dependency": "video_advanced",
    },

    "hunyuan_video": {
        "display_name": "HunyuanVideo 2.0",
        "family": "hunyuan",
        "category": "video_gen",
        "repo": "tencent/HunyuanVideo",
        "params": "~13B",
        "files": {
            "checkpoints": [
                {
                    "filename": "hunyuan_video_v1.0.safetensors",
                    "size_gb": 24.0,
                    "required": True,
                }
            ],
        },
        "quantization_recommendation": {
            "ultra_low": None,
            "low": None,
            "medium": "fp8",
            "high": "fp8",
            "very_high": "bf16",
            "ultra": "bf16",
            "extreme": "bf16",
            "hpc": "bf16",
        },
        "module_dependency": "video_advanced",
    },

    "cogvideox_5b": {
        "display_name": "CogVideoX 5B",
        "family": "cogvideo",
        "category": "video_gen",
        "repo": "THUDM/CogVideoX-5b",
        "params": "5B",
        "files": {},
        "quantization_recommendation": {
            "ultra_low": None,
            "low": None,
            "medium": "fp8",
            "high": "bf16",
            "very_high": "bf16",
            "ultra": "bf16",
            "extreme": "bf16",
            "hpc": "bf16",
        },
        "module_dependency": "video_advanced",
    },

    # ============== UPSCALE ==============
    "seedvr2": {
        "display_name": "SeedVR2",
        "family": "seedvr",
        "category": "upscale",
        "repo": "TBD",
        "quality_score": {
            "strengths": ["best i2i upscale (community consensus March 2026)"],
        },
        "module_dependency": "upscaling",
    },

    # ============== SHARED COMPONENTS ==============
    "flux_vae": {
        "display_name": "Flux VAE (ae.safetensors)",
        "family": "flux",
        "category": "vae",
        "repo": "black-forest-labs/FLUX.1-dev",
        "files": {
            "vae": [
                {
                    "filename": "ae.safetensors",
                    "size_gb": 0.31,
                    "required": True,
                    "shared_with": ["flux1_dev", "flux1_schnell", "z_image_turbo", "z_image_base"],
                }
            ],
        },
    },

    "cosmos_vae": {
        "display_name": "Cosmos VAE",
        "family": "cosmos",
        "category": "vae",
        "repo": "nvidia/Cosmos-1.0-VAE",
        "files": {
            "vae": [
                {
                    "filename": "cosmos_vae.safetensors",
                    "size_gb": 0.5,
                    "required": False,
                }
            ],
        },
    },
}
```

### New File: `nodes/model_manager.py`

6 new nodes:

1. **`LauraModelManager`** — Main health check + download guidance node
   - Scans all ComfyUI model folders against registry
   - Returns: `status_report` (formatted string), `download_urls` (JSON), `recommended_config` (string)
   - Shows installed/missing status per model, with size and quantization recommendation based on detected VRAM tier

2. **`ModuleConfigPanel`** — Toggle modules on/off
   - Reads/writes `laura_config.json`
   - Shows current module states, auto-detected reasons
   - Allows user overrides
   - Returns: `config_status` (string), `active_modules` (string list)

3. **`LauraQuantizationAdvisor`** — Per-model quantization recommendation
   - Input: model_name, vram_tier
   - Output: recommended_precision, download_url (for quantized variant if available), vram_usage_estimate

4. **`LauraModelDownloadHelper`** — Generates download commands/URLs for missing models
   - Input: model_key from registry
   - Output: huggingface_url, download_command, estimated_size, recommended_folder

5. **`LauraCompatibilityChecker`** — Check if auxiliary models work with a base model
   - Input: base_model_key, auxiliary_type (lora/controlnet/ipadapter)
   - Output: compatible (bool), compatible_models (list), notes (string)

6. **`LauraAutoConfig`** — Run full auto-detection and generate optimal laura_config.json
   - Detects VRAM tier, scans installed models, recommends module states
   - Writes config to disk
   - Returns summary report

### Updated File: `nodes/models.py`

- `ModelTypeDetector.detect_type()` — Uses `MODEL_REGISTRY` for detection instead of hardcoded if/elif chain. Add detection for: `flux2`, `glm_image`, `qwen_image`, `firered`, `helios`, `ltx23`, `seedvr2`
- `UniversalModelLoader` — Add new model types to the dropdown: `flux2`, `flux2_schnell`, `glm_image`, `qwen_image`, `firered`, `helios`, `ltx23`
- `AdvancedModelLoader` — Same dropdown updates
- `ModelHealthCheck` — Rewrite to use `MODEL_REGISTRY` for comprehensive scanning

### Updated File: `nodes/quantization.py`

- `QuantizationSelector.select_quantization()` — Use `MODEL_REGISTRY[model_type]["quantization_recommendation"][vram_tier]` instead of hardcoded logic
- Add model types: `flux2`, `glm_image`, `qwen_image`, `firered`, `helios`, `ltx23`, `zimage_turbo`, `zimage_base`

### Updated File: `__init__.py`

- On startup: check for `laura_config.json`
  - If exists: load and respect module enable/disable settings
  - If not exists: run auto-detection, generate config, save to disk
- Skip `importlib.import_module()` for disabled modules
- Log which modules were enabled/disabled and why

### Updated File: `scripts/model_downloader.py`

- Import `MODEL_REGISTRY` from `nodes/model_registry.py`
- Remove hardcoded `MODEL_REGISTRY` dict
- Add `--recommend` flag that shows VRAM-aware recommendations
- Add `--quantized` flag that downloads quantized variants

### Updated Files: Workflow JSONs

All workflow JSONs get a `models` metadata block for ComfyUI's native missing-models dialog:

```json
{
  "models": [
    {
      "name": "z_image_turbo_bf16.safetensors",
      "url": "https://huggingface.co/Tongyi-MAI/Z-Image-Turbo/resolve/main/z_image_turbo_bf16.safetensors",
      "directory": "diffusion_models",
      "size": 11460000000
    },
    {
      "name": "qwen_3_4b.safetensors",
      "url": "https://huggingface.co/Tongyi-MAI/Z-Image-Turbo/resolve/main/text_encoders/qwen_3_4b.safetensors",
      "directory": "text_encoders",
      "size": 7490000000
    },
    {
      "name": "ae.safetensors",
      "url": "https://huggingface.co/Tongyi-MAI/Z-Image-Turbo/resolve/main/vae/ae.safetensors",
      "directory": "vae",
      "size": 319000000
    }
  ]
}
```

### New File: `laura_config.json` (auto-generated)

```json
{
  "version": "1.0",
  "generated": "2026-03-08T12:00:00",
  "auto_detected": {
    "vram_tier": "high",
    "vram_gb": 12.0,
    "gpu_name": "NVIDIA GeForce RTX 4070",
    "fp8_capable": true,
    "compute_capability": [8, 9]
  },
  "modules": {
    "models": {"enabled": true, "reason": "core module, always enabled"},
    "generation": {"enabled": true, "reason": "auto: Z-Image Turbo found"},
    "video": {"enabled": true, "reason": "auto: basic video always available"},
    "video_advanced": {"enabled": false, "reason": "auto: no SOTA video models found"},
    "flux_tools": {"enabled": false, "reason": "auto: no FLUX Fill/Depth/Canny models found"},
    "toggle": {"enabled": true, "reason": "core module, always enabled"},
    "upscaling": {"enabled": true, "reason": "auto: upscale models found"},
    "face": {"enabled": true, "reason": "auto: ReActor found"},
    "dressing": {"enabled": true, "reason": "auto: RMBG found"},
    "inpainting": {"enabled": true, "reason": "auto: SAM2 found"},
    "background": {"enabled": true, "reason": "auto: RMBG found"},
    "quantization": {"enabled": true, "reason": "core module, always enabled"},
    "checkpoint": {"enabled": true, "reason": "core module, always enabled"},
    "batch_processing": {"enabled": true, "reason": "core module, always enabled"},
    "tile_processing": {"enabled": true, "reason": "core module, always enabled"},
    "comparison": {"enabled": true, "reason": "core module, always enabled"}
  },
  "user_overrides": {}
}
```

## Files Changed Summary

| File | Action | Description |
|------|--------|-------------|
| `nodes/model_registry.py` | **NEW** | Central registry (~500 lines) |
| `nodes/model_manager.py` | **NEW** | 6 new management nodes (~400 lines) |
| `nodes/models.py` | UPDATE | Use registry for detection + add new model types |
| `nodes/quantization.py` | UPDATE | Use registry for recommendations + add model types |
| `__init__.py` | UPDATE | Module enable/disable from config |
| `scripts/model_downloader.py` | UPDATE | Use registry instead of hardcoded dict |
| `laura_config.json` | **NEW** | Auto-generated on first load |
| `workflows/*.json` | UPDATE | Add `models` metadata blocks |

## New Nodes Summary

| Node | Category | Purpose |
|------|----------|---------|
| `LauraModelManager` | Laura Studio/Utility | Full model health check + download guidance |
| `ModuleConfigPanel` | Laura Studio/Utility | Toggle modules with smart defaults |
| `LauraQuantizationAdvisor` | Laura Studio/Optimization | Per-model quantization recommendation |
| `LauraModelDownloadHelper` | Laura Studio/Utility | Generate download URLs/commands |
| `LauraCompatibilityChecker` | Laura Studio/Utility | Check LoRA/ControlNet/IPAdapter compatibility |
| `LauraAutoConfig` | Laura Studio/Utility | Run full auto-detection + config generation |

## Non-Goals (Explicitly Out of Scope)

- API-based models (Kling 3.0, Seedream 4.5, Nano Banana) — not open source
- Automatic model downloading without user consent
- Breaking changes to existing node interfaces
- New workflow files (separate task)
