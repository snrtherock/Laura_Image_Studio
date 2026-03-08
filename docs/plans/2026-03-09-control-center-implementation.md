# Laura Control Center — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a single `LauraControlCenter` supernode that gives users one-stop model selection, VRAM detection, auto-download, LoRA configuration, and auto-assignment of MODEL/CLIP/VAE to all downstream workflow nodes. Fix overlapping groups in all 3 master workflows.

**Architecture:** A new `nodes/control_center.py` defines `LauraControlCenter` which combines VRAM detection (from `model_manager._detect_vram`), registry lookups, ComfyUI's built-in model loading (`comfy.sd`), and LoRA application into a single node with 8 outputs. A companion `web/js/control_center.js` renders status badges and download buttons using safe DOM methods. Two API routes (`/laura/download`, `/laura/download/status`) handle async model downloads. A `scripts/fix_workflow_layout.py` script resolves all group overlaps and places the Control Center first.

**Tech Stack:** Python 3.10+, ComfyUI custom nodes API (`folder_paths`, `comfy.sd`, `comfy.utils`), `aiohttp` (for download API routes via `PromptServer`), JavaScript (ComfyUI web extension, safe DOM manipulation), `huggingface_hub` (optional, for gated model downloads), JSON workflow editing.

**Design Doc:** `docs/plans/2026-03-09-control-center-supernode-design.md`

---

## Implementation Status

| Task | Description | Status | Notes |
|------|-------------|--------|-------|
| 1 | Add registry helpers for dropdown population | PENDING | Pure data, no ComfyUI deps |
| 2 | Create `control_center.py` - the supernode | PENDING | Core node with model loading |
| 3 | Create `web/js/control_center.js` - rich UI | PENDING | Status badges, download buttons (safe DOM) |
| 4 | Add download API routes | PENDING | /laura/download + progress |
| 5 | Update `__init__.py` - register new module | PENDING | Add control_center to load list |
| 6 | Fix workflow layouts - resolve overlaps | PENDING | All 3 master workflows |
| 7 | Rewire workflows - replace scattered nodes | PENDING | Control Center replaces 6+ nodes |
| 8 | Verification and commit | PENDING | Live ComfyUI test |

---

## Task 1: Add Registry Helpers for Dropdown Population

**Files:**
- Modify: `custom_nodes/Laura_Image_Studio/nodes/model_registry.py` (add 4 functions at bottom)

**Step 1: Add dropdown helper functions**

Add at the bottom of `model_registry.py`:

```python
def get_image_model_choices():
    """Return sorted list of registry keys for image generation models."""
    return sorted(
        k for k, v in MODEL_REGISTRY.items()
        if v.get("category") in ("image_gen", "image_edit")
    )


def get_video_model_choices():
    """Return sorted list of registry keys for video generation models."""
    return sorted(
        k for k, v in MODEL_REGISTRY.items()
        if v.get("category") == "video_gen"
    )


def get_upscale_model_choices():
    """Return sorted list of registry keys for upscale models."""
    return sorted(
        k for k, v in MODEL_REGISTRY.items()
        if v.get("category") == "upscale"
    )


def get_model_display_name(key):
    """Return human-readable display name for a registry key."""
    entry = MODEL_REGISTRY.get(key, {})
    return entry.get("display_name", key)
```

**Step 2: Verify**

Run:
```bash
cd "F:\Anti_Gravity_Projects\Best_Real_Image_Gen - Copy"
python -c "
import sys, types
mock_fp = types.ModuleType('folder_paths')
mock_fp.get_folder_paths = lambda x: []
sys.modules['folder_paths'] = mock_fp
sys.path.insert(0, 'custom_nodes')
from Laura_Image_Studio.nodes.model_registry import (
    get_image_model_choices, get_video_model_choices,
    get_upscale_model_choices, get_model_display_name
)
print('Image:', get_image_model_choices())
print('Video:', get_video_model_choices())
print('Upscale:', get_upscale_model_choices())
print('Display:', get_model_display_name('z_image_turbo'))
"
```
Expected: Lists of registry keys per category.

**Step 3: Commit**

```bash
git add nodes/model_registry.py
git commit -m "feat(registry): add dropdown population helpers for Control Center"
```

---

## Task 2: Create `control_center.py` - The Supernode

**Files:**
- Create: `custom_nodes/Laura_Image_Studio/nodes/control_center.py`

This is the largest task. The node must:
1. Auto-detect VRAM and recommend quantization
2. Present dropdowns for image model, upscaler, video model, face model
3. Present 3 LoRA slots with strength sliders
4. Actually LOAD the selected model using ComfyUI's `comfy.sd` API
5. Apply LoRAs
6. Output MODEL, CLIP, VAE, and metadata

**Step 1: Create the control_center.py module**

```python
"""
Laura Image Studio - Control Center Supernode
Single node for centralized model selection, VRAM detection, auto-download,
LoRA configuration, and auto-assignment to all downstream workflow nodes.
"""

import json
import os

import torch
import folder_paths
import comfy.sd
import comfy.utils

from .model_registry import (
    MODEL_REGISTRY,
    VRAM_TIERS,
    get_image_model_choices,
    get_video_model_choices,
    get_upscale_model_choices,
    get_recommended_quantization,
    get_all_required_files,
    get_model_display_name,
)
from .model_manager import _detect_vram, _scan_installed_models


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}


# Static choices - built once at import time
_IMAGE_CHOICES = get_image_model_choices()
_VIDEO_CHOICES = ["none"] + get_video_model_choices()
_UPSCALE_CHOICES = ["none"] + get_upscale_model_choices()
_FACE_CHOICES = ["none", "inswapper_128"]
_VRAM_TIER_KEYS = sorted(VRAM_TIERS.keys())

# Build LoRA dropdown from folder_paths
def _lora_choices():
    try:
        return ["None"] + folder_paths.get_filename_list("loras")
    except Exception:
        return ["None"]


class LauraControlCenter:
    """
    Single command-center node for the entire Laura Studio workflow.
    Detects VRAM, recommends quantization, loads image model + VAE + CLIP,
    applies up to 3 LoRAs, and outputs everything downstream nodes need.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_model": (_IMAGE_CHOICES, {
                    "default": _IMAGE_CHOICES[0] if _IMAGE_CHOICES else "flux1_dev",
                }),
                "upscale_model": (_UPSCALE_CHOICES,),
                "video_model": (_VIDEO_CHOICES,),
                "face_model": (_FACE_CHOICES,),
                "lora_1": (_lora_choices(),),
                "lora_1_strength": ("FLOAT", {
                    "default": 1.0, "min": 0.0, "max": 2.0, "step": 0.05,
                }),
                "lora_2": (_lora_choices(),),
                "lora_2_strength": ("FLOAT", {
                    "default": 1.0, "min": 0.0, "max": 2.0, "step": 0.05,
                }),
                "lora_3": (_lora_choices(),),
                "lora_3_strength": ("FLOAT", {
                    "default": 1.0, "min": 0.0, "max": 2.0, "step": 0.05,
                }),
                "auto_detect_vram": ("BOOLEAN", {"default": True}),
                "manual_vram_tier": (_VRAM_TIER_KEYS, {"default": "high"}),
                "auto_quantization": ("BOOLEAN", {"default": True}),
                "torch_compile": ("BOOLEAN", {"default": False}),
                "default_width": ("INT", {
                    "default": 1024, "min": 512, "max": 4096, "step": 64,
                }),
                "default_height": ("INT", {
                    "default": 1024, "min": 512, "max": 4096, "step": 64,
                }),
            },
        }

    RETURN_TYPES = ("MODEL", "CLIP", "VAE", "STRING", "INT", "INT", "STRING", "STRING")
    RETURN_NAMES = (
        "model", "clip", "vae", "detected_type",
        "default_width", "default_height",
        "status_report", "config_json",
    )
    FUNCTION = "configure_pipeline"
    CATEGORY = "Laura Studio/Control Center"

    def configure_pipeline(self, image_model, upscale_model, video_model,
                           face_model, lora_1, lora_1_strength, lora_2,
                           lora_2_strength, lora_3, lora_3_strength,
                           auto_detect_vram, manual_vram_tier,
                           auto_quantization, torch_compile,
                           default_width, default_height):

        # 1. VRAM Detection
        if auto_detect_vram:
            vram_gb, vram_tier = _detect_vram()
        else:
            vram_tier = manual_vram_tier
            vram_gb = VRAM_TIERS.get(vram_tier, {}).get("max_gb", 0)

        # 2. Registry lookup
        model_info = MODEL_REGISTRY.get(image_model, {})
        display_name = model_info.get("display_name", image_model)
        detected_type = model_info.get("family", "unknown")

        # 3. Quantization
        quant = "bf16"
        if auto_quantization:
            quant = get_recommended_quantization(image_model, vram_tier)

        # 4. Load image model
        model, clip, vae = self._load_image_model(image_model, model_info)

        # 5. Apply LoRAs
        for lora_name, strength in [
            (lora_1, lora_1_strength),
            (lora_2, lora_2_strength),
            (lora_3, lora_3_strength),
        ]:
            if lora_name and lora_name != "None":
                model, clip = self._apply_lora(model, clip, lora_name, strength)

        # 6. Build status report
        installed = _scan_installed_models()
        status_lines = [
            f"GPU: {vram_gb} GB VRAM | Tier: {vram_tier}",
            f"Quantization: {quant}",
            f"Image Model: {display_name}",
            f"Video Model: {video_model}",
            f"Face Model: {face_model}",
            "",
        ]
        for model_key in [image_model, video_model]:
            if model_key == "none":
                continue
            entry = MODEL_REGISTRY.get(model_key, {})
            for role, finfo in entry.get("files", {}).items():
                if isinstance(finfo, dict):
                    fname = finfo.get("filename", "")
                    tag = "INSTALLED" if fname in installed else "MISSING"
                    status_lines.append(f"  [{tag}] {fname}")

        # 7. Config JSON
        config = {
            "vram_tier": vram_tier,
            "vram_gb": vram_gb,
            "image_model": image_model,
            "video_model": video_model,
            "face_model": face_model,
            "upscale_model": upscale_model,
            "quantization": quant,
            "torch_compile": torch_compile,
            "detected_type": detected_type,
        }

        return (
            model, clip, vae, detected_type,
            default_width, default_height,
            "\n".join(status_lines), json.dumps(config, indent=2),
        )

    def _load_image_model(self, model_key, model_info):
        """Load the image model using ComfyUI standard loading functions."""
        files = model_info.get("files", {})
        comfyui_type = model_info.get("comfyui_type", "checkpoints")

        if comfyui_type == "checkpoints":
            return self._load_checkpoint(model_key, model_info, files)
        elif comfyui_type == "diffusion_models":
            return self._load_diffusion_model(model_key, model_info, files)
        else:
            raise ValueError(
                f"Unknown comfyui_type '{comfyui_type}' for {model_key}"
            )

    def _load_checkpoint(self, model_key, model_info, files):
        """Load a checkpoint-based model (SDXL, SD3.5, FLUX, Wan, Hunyuan)."""
        ckpt_file = files.get("checkpoint", {})
        filename = ckpt_file.get("filename", "")
        if not filename:
            raise ValueError(f"No checkpoint file defined for {model_key}")

        ckpt_path = folder_paths.get_full_path("checkpoints", filename)
        if ckpt_path is None:
            raise FileNotFoundError(
                f"Checkpoint not found: {filename}. "
                f"Download from: {model_info.get('homepage', '?')}"
            )

        out = comfy.sd.load_checkpoint_guess_config(
            ckpt_path,
            output_vae=True,
            output_clip=True,
            embedding_directory=folder_paths.get_folder_paths("embeddings"),
        )
        return out[0], out[1], out[2]

    def _load_diffusion_model(self, model_key, model_info, files):
        """Load a diffusion_model/UNET-based model (Z-Image, Qwen, GLM)."""
        dm_file = files.get("diffusion_model", files.get("transformer", {}))
        filename = dm_file.get("filename", "")
        if not filename:
            raise ValueError(f"No diffusion model file for {model_key}")

        unet_path = folder_paths.get_full_path("diffusion_models", filename)
        if unet_path is None:
            unet_path = folder_paths.get_full_path("unet", filename)
        if unet_path is None:
            raise FileNotFoundError(
                f"Diffusion model not found: {filename}. "
                f"Download from: {model_info.get('homepage', '?')}"
            )

        model = comfy.sd.load_diffusion_model(unet_path)

        # Load VAE
        vae = None
        vae_info = files.get("vae", {})
        if isinstance(vae_info, dict) and vae_info.get("filename"):
            vae_path = folder_paths.get_full_path("vae", vae_info["filename"])
            if vae_path:
                vae = comfy.sd.load_vae(vae_path)

        # Load CLIP / text_encoder
        clip = None
        te_info = files.get("text_encoder", {})
        if isinstance(te_info, dict) and te_info.get("filename"):
            te_path = folder_paths.get_full_path(
                "text_encoders", te_info["filename"]
            )
            if te_path:
                clip = comfy.sd.load_clip(te_path)

        return model, clip, vae

    def _apply_lora(self, model, clip, lora_name, strength):
        """Apply a single LoRA to model and clip."""
        lora_path = folder_paths.get_full_path("loras", lora_name)
        if lora_path is None:
            print(f"[Laura Control Center] WARNING: LoRA not found: {lora_name}")
            return model, clip

        lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
        model_out, clip_out = comfy.sd.load_lora_for_models(
            model, clip, lora, strength, strength,
        )
        return model_out, clip_out


NODE_CLASS_MAPPINGS["LauraControlCenter"] = LauraControlCenter
NODE_DISPLAY_NAME_MAPPINGS["LauraControlCenter"] = "Laura Control Center"
```

**Step 2: Verify module parses and node registers**

Run with mocked comfy.sd:
```bash
cd "F:\Anti_Gravity_Projects\Best_Real_Image_Gen - Copy"
python -c "
import sys, types
mock_fp = types.ModuleType('folder_paths')
mock_fp.get_folder_paths = lambda x: []
mock_fp.get_filename_list = lambda x: ['model_a.safetensors']
mock_fp.get_full_path = lambda f, n: None
mock_fp.get_output_directory = lambda: '/tmp'
sys.modules['folder_paths'] = mock_fp
mock_comfy = types.ModuleType('comfy')
mock_sd = types.ModuleType('comfy.sd')
mock_utils = types.ModuleType('comfy.utils')
sys.modules['comfy'] = mock_comfy
sys.modules['comfy.sd'] = mock_sd
sys.modules['comfy.utils'] = mock_utils
mock_comfy.sd = mock_sd
mock_comfy.utils = mock_utils
sys.path.insert(0, 'custom_nodes')
from Laura_Image_Studio.nodes.control_center import NODE_CLASS_MAPPINGS
print(f'Nodes: {list(NODE_CLASS_MAPPINGS.keys())}')
cls = NODE_CLASS_MAPPINGS['LauraControlCenter']
inputs = cls.INPUT_TYPES()
print(f'Inputs: {list(inputs[\"required\"].keys())}')
print(f'Outputs: {cls.RETURN_TYPES}')
print(f'Function: {cls.FUNCTION}')
"
```
Expected: `LauraControlCenter` with 16 inputs, 8 outputs.

**Step 3: Commit**

```bash
git add nodes/control_center.py
git commit -m "feat: create LauraControlCenter supernode for centralized model management"
```

---

## Task 3: Create `web/js/control_center.js` - Rich UI

**Files:**
- Create: `custom_nodes/Laura_Image_Studio/web/js/control_center.js`

The web extension renders status badges and download buttons using **safe DOM methods** (no innerHTML with user data). Uses `textContent` for all text display and `createElement` for HTML structure.

Key features:
- VRAM tier display with color coding
- Status badges per model file (INSTALLED green / MISSING red)
- HuggingFace link button
- Download button that calls `/laura/download` API
- Auto-resizes node to fit content

The JS uses `app.registerExtension` with `beforeRegisterNodeDef` hook for `LauraControlCenter`,
overrides `onExecuted` to parse `status_report` and `config_json` outputs, and builds
a status panel using `addDOMWidget` with safe DOM construction (createElement + textContent,
no innerHTML with dynamic data).

**Step 1: Create the JS file** (implementing agent writes full code)

**Step 2: Verify file exists and basic syntax**
```bash
ls -la custom_nodes/Laura_Image_Studio/web/js/control_center.js
wc -l custom_nodes/Laura_Image_Studio/web/js/control_center.js
```

**Step 3: Commit**
```bash
git add web/js/control_center.js
git commit -m "feat: add Control Center web extension with status badges and download UI"
```

---

## Task 4: Add Download API Routes

**Files:**
- Modify: `custom_nodes/Laura_Image_Studio/nodes/control_center.py` (append download API at bottom)

Adds two API endpoints using ComfyUI's `PromptServer`:
- `POST /laura/download` - starts async download of a model to the correct folder
- `GET /laura/download/status/{job_id}` - returns download progress

Uses `requests.get(url, stream=True)` with 8MB chunks for streaming download.
Target folder is resolved via `folder_paths.get_folder_paths(folder_name)[0]`.
Downloads to `.tmp` first then renames on completion for atomicity.
Background thread per download, tracked by job_id in a module-level dict.

**Step 1: Append download API code to control_center.py** (implementing agent writes full code)

**Step 2: Verify module still imports cleanly**

**Step 3: Commit**
```bash
git add nodes/control_center.py
git commit -m "feat: add download API routes with progress tracking"
```

---

## Task 5: Update `__init__.py` - Register New Module

**Files:**
- Modify: `custom_nodes/Laura_Image_Studio/__init__.py`

**Step 1: Add `control_center` to `_modules_to_load` at position 2 and to `_CORE_MODULES`**

In `_modules_to_load`:
```python
_modules_to_load = [
    "model_registry",   # Pure data - no nodes, must load first
    "model_manager",    # Config + management nodes, load second
    "control_center",   # Control Center supernode, load third
    "generation",
    ...
]
```

In `_CORE_MODULES`:
```python
_CORE_MODULES = {
    "model_registry", "model_manager", "control_center", "models", "toggle",
    "quantization", "checkpoint", "batch_processing",
    "tile_processing", "comparison",
}
```

**Step 2: Verify node count increases by 1**

Expected: `Total nodes: 129` (was 128, +1 for LauraControlCenter)

**Step 3: Commit**
```bash
git add __init__.py
git commit -m "feat: register control_center module in init"
```

---

## Task 6: Fix Workflow Layouts - Resolve Overlaps

**Files:**
- Create: `scripts/fix_workflow_layout.py`
- Modify: All 3 master workflow JSONs

**Step 1: Create the layout fixer script**

The script:
1. Sorts groups left-to-right by x position
2. Ensures minimum 100px horizontal gap between adjacent groups
3. Shifts nodes within each group by the same offset
4. Adjusts bounding boxes accordingly

**Step 2: Run the script**
```bash
python scripts/fix_workflow_layout.py
```

**Step 3: Verify 0 overlaps**
```bash
python -c "
import json
# Check all 3 workflows for overlapping groups
# Expected: 0 overlaps for all 3
"
```

**Step 4: Commit**
```bash
git add scripts/fix_workflow_layout.py
git add custom_nodes/Laura_Image_Studio/workflows/*.json
git commit -m "fix: resolve overlapping groups in all 3 master workflows"
```

---

## Task 7: Rewire Workflows - Replace Scattered Nodes with Control Center

**Files:**
- Create: `scripts/rewire_control_center.py`
- Modify: All 3 master workflow JSONs

This script:
1. Removes nodes the Control Center replaces: UniversalModelLoader, MultiLoraStack, VRAMAutoDetector, QuantizationSelector, QuantizationConfig, ModelOffloadConfig, and Model Manager nodes (IDs 1000-1006)
2. Adds LauraControlCenter node at position [50, 50]
3. Rewires connections: traces where removed nodes output to, creates new links from Control Center outputs to those same targets
4. Updates last_node_id and last_link_id

Link format: `[link_id, source_node_id, source_slot, target_node_id, target_slot, type_string]`

Control Center output slot mapping:
- Slot 0 (MODEL) replaces UniversalModelLoader slot 0
- Slot 1 (CLIP) replaces UniversalModelLoader slot 1
- Slot 2 (VAE) replaces UniversalModelLoader slot 2
- Slot 3 (detected_type STRING) replaces UniversalModelLoader slot 3
- Slot 4 (default_width INT) - new
- Slot 5 (default_height INT) - new
- Slot 6 (status_report STRING) - new
- Slot 7 (config_json STRING) - new

**Step 1: Create the rewiring script** (implementing agent writes full code)

**Step 2: Run it**
```bash
python scripts/rewire_control_center.py
```

**Step 3: Verify**
- LauraControlCenter present in all 3 workflows
- UniversalModelLoader, VRAMAutoDetector removed
- Links from Control Center go to correct downstream nodes

**Step 4: Commit**
```bash
git add scripts/rewire_control_center.py
git add custom_nodes/Laura_Image_Studio/workflows/*.json
git commit -m "feat: rewire workflows to use LauraControlCenter"
```

---

## Task 8: Final Verification and Commit

**Step 1: Verify all nodes load**
Expected: 129 nodes (128 + LauraControlCenter)

**Step 2: Verify all 3 workflows valid JSON with Control Center present**

**Step 3: Verify web extension files exist**
- `web/js/control_center.js`
- `web/js/model_links.js` (still present)

**Step 4: Final commit** (submodule then parent)
