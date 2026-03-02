# Laura Image Studio - Enhanced Master Workflow

## Overview
The Enhanced Master Workflow is a comprehensive all-in-one image generation workflow for ComfyUI that supports character Laura with virtual dressing, face operations, inpainting/outpainting, and multi-resolution upscaling (2K/4K/8K).

---

## Workflow File
**Location:** `custom_nodes/Laura_Image_Studio/workflows/enhanced_master_workflow.json`

---

## Features Summary

### 1. Model Loading Section
| Node ID | Type | Purpose |
|---------|------|---------|
| 1 | CheckpointLoader | Loads base model (juggernaut_xl_v8.safetensors) |
| 2 | LoraLoader | Loads character LoRA (zoriana_lora.safetensors) - strength 0.8 |
| 3 | LoraLoader | Loads clothing LoRA (clothing_lora.safetensors) - strength 0.6 |

### 2. Input Images
| Node ID | Type | Purpose |
|---------|------|---------|
| 10 | LoadImage | Character reference image |
| 11 | LoadImage | Clothing reference image |
| 12 | LoadImage | Target image to edit |

### 3. Face Operations
| Node ID | Type | Purpose |
|---------|------|---------|
| 20 | FaceDetect | Detect faces using YOLOFace |
| 21 | IPAdapter | Face embedding with plus model |
| 22 | FaceSwap | Swap faces using Inswapper |
| 120 | FaceEnhancer | Enhance face details |
| 121 | FaceDetailer | Face restoration with GFPGAN |

### 4. Image Generation
| Node ID | Type | Purpose |
|---------|------|---------|
| 30 | EmptyLatentImage | Generate 1024x1024 latent |
| 31 | CLIPTextEncode | Positive prompt encoding |
| 32 | CLIPTextEncode | Negative prompt encoding |
| 33 | KSampler | Sampling (Euler, 25 steps, CFG 5.0) |
| 34 | VAEDecode | Decode latent to image |

### 5. Virtual Dressing
| Node ID | Type | Purpose |
|---------|------|---------|
| 40 | VAEEncodeForInpaint | Encode image with mask |
| 41 | InpaintModel | Prepare inpainting model |
| 42 | KSampler | Inpainting (30 steps, CFG 7.0) |
| 43 | VAEDecode | Decode inpainting result |
| 80 | VirtualDresser | Dedicated dressing node |

### 6. Mask Generation
| Node ID | Type | Purpose |
|---------|------|---------|
| 44 | MaskEditor | Manual mask editing |
| 45 | SAMLoader | Load SAM model |
| 46 | SAMMaskGenerator | Auto mask generation |

### 7. Inpainting/Outpainting
| Node ID | Type | Purpose |
|---------|------|---------|
| 40-43 | Inpainting Pipeline | Fill masked areas |
| 50 | LauraOutPainter | Outpainting with direction options |
| 150 | ImagePadForOutpaint | Prepare for outpainting |

### 8. Background Operations
| Node ID | Type | Purpose |
|---------|------|---------|
| 60 | RMBG | Background removal |
| 61 | ImageCompositeMasked | Background replacement |
| 62 | PortraitBokeh | Portrait bokeh effect |

### 9. Upscaling (Multiple Options)
| Node ID | Type | Output |
|---------|------|--------|
| 70 | Upscale2K | 2048px |
| 71 | Upscale4K | 4096px |
| 72 | Upscale8K | 8192px |
| 73 | DetailEnhancer | SD-based detail enhancement |
| 74 | UltimateSDUpscale | Advanced tiled upscaling |

### 10. Output Nodes
| Node ID | Type | Output |
|---------|------|--------|
| 100 | SaveImage | Master output |
| 101 | SaveImage | 2K output |
| 102 | SaveImage | 4K output |
| 103 | SaveImage | 8K output |
| 104 | SaveImage | Final enhanced output |

---

## Required Custom Nodes

Install these via ComfyUI Manager or git clone:

| Node | Repository |
|------|------------|
| ReActor | https://github.com/Gourieff/ComfyUI-ReActor |
| IPAdapter Plus | https://github.com/cubiq/ComfyUI_IPAdapter_plus |
| RMBG | https://github.com/1038lab/ComfyUI-RMBG |
| Ultimate SD Upscale | https://github.com/ssitu12345/ComfyUI_UltimateSDUpscale |
| ComfyUI Impact Pack | https://github.com/Kosinkadink/ComfyUI-Impact-Pack |
| ComfyUI ControlNet | https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet |
| ComfyUI Segment Anything | https://github.com/Gourieff/ComfyUI-Anything-World |

---

## Required Models

### Checkpoints
- `juggernaut_xl_v8.safetensors` (SDXL)
- `realisticVisionV60_v1.safetensors` (Alternative)

### LoRAs
- `zoriana_lora.safetensors` (Character Laura)
- `clothing_lora.safetensors` (Clothing styles)

### Upscale Models (ComfyUI/models/upscale_models/)
- `4x-UltraSharp.pth`
- `RealESRGAN_x4plus.pth`
- `ScuNet_GAN.pth`

### Face Models
- `inswapper_128.onnx` (Face swap - ComfyUI/models/face_swap/)
- `ip-adapter-plus-face_sdxl.safetensors` (IPAdapter - ComfyUI/models/ipadapter/)
- `GFPGAN.pth` (Face restoration - ComfyUI/models/facerestore_models/)
- `CodeFormer.pth` (Face restoration)

### Background Removal
- `RMBG-1.4.pth` (ComfyUI/models/rmbg/)

### SAM Model
- `sam_vit_b.pth` (ComfyUI/models/sam/)

---

## Usage Guide

### Basic Generation
1. Load `enhanced_master_workflow.json` in ComfyUI
2. Select your base model in CheckpointLoader (Node 1)
3. Connect character reference to Node 10
4. Enter positive/negative prompts in Nodes 31/32
5. Run workflow - output saved at Node 100

### Virtual Dressing
1. Load target image at Node 12
2. Use Node 11 for clothing reference OR enter prompt in VirtualDresser (Node 80)
3. Use SAMMaskGenerator (Node 46) to create clothing mask
4. Connect mask to VirtualDresser
5. Run inpainting pipeline (Nodes 40-43)

### Face Swap
1. Load source face at Node 10
2. Load target body at Node 12
3. FaceSwap (Node 22) will swap the face
4. Optional: Use FaceEnhancer (Node 120) for better quality

### Upscaling
1. Connect generated image to any upscale node:
   - Node 70: 2K (2048px)
   - Node 71: 4K (4096px) - Recommended for 4K output
   - Node 72: 8K (8192px) - For large format print
2. Results saved at Nodes 101-103

### Background Removal
1. Load image at Node 12
2. Connect to RMBG (Node 60)
3. Output: separated subject + mask
4. For replacement: connect new background to Node 61

---

## Workflow Statistics
- **Total Nodes:** 50
- **Total Links:** 83
- **JSON Size:** 28,508 bytes
- **Valid:** Yes (syntax verified)

---

## Troubleshooting

### Node Not Found Error
- Install required custom nodes (see Required Custom Nodes above)

### Model Not Found Error
- Download required models to correct folders (see Required Models above)

### Out of Memory
- Reduce image resolution
- Use tile-based upscaling (UltimateSDUpscale)
- Enable model offloading

### Face Swap Not Working
- Ensure ReActor is installed
- Check inswapper_128.onnx is in correct folder
- Verify face is frontal and well-lit

---

## Alternative Workflows

| File | Purpose |
|------|---------|
| `master_all_in_one.json` | Legacy master workflow |
| `base_generation.json` | Simple text-to-image |
| `virtual_dressing.json` | Clothing changes only |
| `face_swap.json` | Face swapping |
| `inpainting.json` | Inpainting |
| `outpainting.json` | Outpainting |
| `upscale_2k.json` | 2K upscaling |
| `upscale_4k.json` | 4K upscaling |
| `upscale_8k.json` | 8K upscaling |

---

*Last Updated: 2026-02-23*
*Version: 1.0*
