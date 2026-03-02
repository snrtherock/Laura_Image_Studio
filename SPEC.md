# ComfyUI All-in-One Image Generation Workflow

## Project Overview

**Project Name:** Laura's Complete Image Studio (Universal All-in-One)
**Project Type:** ComfyUI Custom Nodes + Workflow JSONs
**Core Functionality:** A truly all-in-one image generation, editing, virtual dressing, inpainting, outpainting, and multi-resolution upscaling system that supports ALL AI image models (SDXL, Flux, Wan 2.2, SD 1.5, SD 3, etc.) with optional character embedding for user-trained characters (like Laura/Zoriana)
**Target Users:** Content creators, fashion designers, digital artists who need professional-grade human image generation and editing with any model

---

## Supported AI Models

### Stability AI
- SDXL 1.0
- SDXL Refiner
- SD 1.5
- SD 2.1
- SD 3.0 / 3.5

### Community Models
- Juggernaut XL (v8, v9)
- Realistic Vision (V60, V51)
- Playground v2
- Pixart Sigma
- Aura Flow

### Flux (Black Forest Labs)
- Flux 1 [Schnell]
- Flux 1 Dev
- Flux 2 Dev
- Flux 2 (upcoming)

### Wan 2.2 (WannaBay)
- Wan 2.2 / Wan 2.1
- Wan Turbo
- Character: Zoriana (user-trained LoRA)

### Other Models
- Lumina 3
-Kolors
- Playground v2.5

---

## Architecture Overview

### System Components
1. **Custom ComfyUI Nodes** - Python-based nodes for each major function
2. **Workflow JSON Files** - Pre-built workflows for different use cases
3. **Installation Scripts** - Automated setup for all dependencies
4. **Documentation** - Usage guides for each feature

### Required External Resources

#### Model Sources
- **SDXL 1.0** - Base model for image generation (Stability AI)
- **SDXL Refiner** - Quality enhancement
- **Juggernaut XL** - Photorealistic models (recommended)
- **Realistic Vision** - Alternative realistic model
- **IPAdapter Plus** - Face/character embedding
- **ReActor** - Face swapping
- **RMBG** - Background removal
- **4X UltraSharp** - Image upscaling
- **RealESRGAN** - Alternative upscaling

#### Custom Nodes to Install
1. ComfyUI-ReActor - Face swap/identity preservation
2. ComfyUI_IPAdapter_plus - Advanced IPAdapter implementation
3. ComfyUI-RMBG - Background removal
4. ComfyUI-ConstrainResolution - Resolution management
5. ComfyUI-AdvancedUpscripts - Professional upscaling
6. ComfyUI-Inpaint-Anything - Smart masking

---

## UI/UX Specification

### Workflow Organization

#### Main Workflow Categories

1. **Base Generation** - Create initial images of Laura
2. **Virtual Dressing** - Change clothing items individually
3. **Face & Identity** - Face swap, face swap with ref, preserve identity
4. **Image Editing** - Inpainting, outpainting, masking
5. **Upscaling** - 2K, 4K, 8K output options
6. **Background** - Removal, replacement, generation
7. **Composition** - Full body, portrait, fashion shot

### Node Categories

#### 1. Image Generation Nodes
- `LAURA_SDXL_Generator` - Main image generation with Laura embedding
- `LAURA_Prompt_Builder` - Intelligent prompt construction
- `LAURA_Negative_Prompt` - Quality negative prompts
- `LAURA_Seed_Control` - Reproducible generation

#### 2. Virtual Dressing Nodes
- `Clothing_Segmentor` - Detect and isolate clothing items
- `Garment_Reference` - Input reference clothing images
- `Virtual_Dresser` - Replace clothing while preserving pose
- `Accessory_Editor` - Change shoes, watches, jewelry
- `Hair_Stylist` - Change hairstyle independently
- `Makeup_Artist` - Apply different makeup looks

#### 3. Face & Identity Nodes
- `Face_Detector` - Locate face in image
- `Face_Swapper` - Swap face onto body
- `Face_Reference` - Set reference face
- `IPAdapter_Face` - Face embedding for consistency
- `Expression_Transfer` - Transfer expressions

#### 4. Masking & Inpainting Nodes
- `Smart_Mask_Generator` - AI-powered mask creation
- `Inpaint_Anything` - Segment anything for masks
- `Manual_Mask_Editor` - Fine-tune masks
- `Inpainter` - Fill masked areas
- `Outpainter` - Expand image boundaries
- `Edge_Blender` - Seamless inpainting edges

#### 5. Upscaling Nodes
- `Upscale_2K` - 2048x2048 output
- `Upscale_4K` - 4096x4096 output
- `Upscale_8K` - 8192x8192 output
- `Upscale_Chain` - Multiple upscale passes
- `Detail_Enhancer` - Add details after upscale

#### 6. Background Nodes
- `Background_Remover` - RMBG integration
- `Background_Replacer` - Set new background
- `Background_Generator` - AI background from prompt
- `Portrait_Bokeh` - Professional background blur

---

## Functionality Specification

### 1. Base Image Generation

#### Features
- Text-to-image generation with Laura character
- Image-to-image with character consistency
- Multiple pose options
- Full body and portrait modes
- Professional lighting presets

#### Technical Details
- Model: Juggernaut XL or Realistic Vision
- Default Resolution: 1024x1024 or 832x1152
- CFG Scale: 3.5-7.0
- Steps: 25-50

### 2. Virtual Dressing System

#### Clothing Categories
- Tops (shirts, blouses, jackets, coats)
- Bottoms (pants, skirts, shorts)
- Dresses
- Footwear (shoes, boots, heels)
- Accessories (watches, glasses, bags)
- Jewelry (necklaces, earrings, bracelets)
- Hair styles
- Makeup

#### Workflow
1. Input source image of Laura
2. Select clothing category to change
3. Provide reference image OR text prompt
4. AI detects and replaces only selected item
5. Maintains pose and lighting consistency

#### Key Technologies
- ReActor for face preservation
- IPAdapter for style transfer
- Inpainting for garment replacement
- Segment Anything for precise masks

### 3. Face & Identity Management

#### Capabilities
- Face swap to different body
- Face preservation during editing
- Expression transfer
- Age adjustment
- Makeup transfer

### 4. Inpainting & Outpainting

#### Inpainting
- Text-guided inpainting
- Mask-based editing
- Object removal
- Clothing modification
- Face retouching

#### Outpainting
- Automatic image expansion
- Seamless edge blending
- Multiple direction expansion
- Context-aware generation

### 5. Multi-Resolution Upscaling

#### Options
| Mode | Input | Output | Use Case |
|------|-------|--------|----------|
| 2K Standard | 1024 | 2048 | Web, social media |
| 4K Standard | 1024 | 4096 | Print, high-res display |
| 8K Ultra | 1024 | 8192 | Large format print |
| Chain | Any | Any | Maximum quality |

#### Techniques
- 4X UltraSharp
- RealESRGAN
- SDXL-based upscaling
- Detail enhancement pass

---

## File Structure

```
Best_Real_Image_Gen/
├── custom_nodes/
│   └── Laura_Image_Studio/
│       ├── __init__.py
│       ├── nodes/
│       │   ├── __init__.py
│       │   ├── generation.py
│       │   ├── dressing.py
│       │   ├── face.py
│       │   ├── inpainting.py
│       │   ├── upscaling.py
│       │   └── background.py
│       ├── workflows/
│       │   ├── base_generation.json
│       │   ├── virtual_dressing.json
│       │   ├── face_swap.json
│       │   ├── inpainting.json
│       │   ├── outpainting.json
│       │   ├── upscale_2k.json
│       │   ├── upscale_4k.json
│       │   ├── upscale_8k.json
│       │   └── all_in_one.json
│       └── README.md
├── scripts/
│   ├── install_dependencies.py
│   ├── download_models.py
│   └── setup_workflows.py
└── docs/
    ├── installation.md
    ├── quickstart.md
    ├── workflow_guide.md
    └── troubleshooting.md
```

---

## Acceptance Criteria

### Must Have
- [ ] All 6 major node categories functional
- [ ] All 3 upscale resolutions available (2K, 4K, 8K)
- [ ] Virtual dressing for at least 8 clothing categories
- [ ] Inpainting with smart masking
- [ ] Outpainting with edge blending
- [ ] Face swap and identity preservation
- [ ] Background removal and replacement
- [ ] Working workflow JSON files

### Should Have
- [ ] Complete installation script
- [ ] Model download helper
- [ ] Documentation for each workflow
- [ ] Troubleshooting guide

### Nice to Have
- [ ] Batch processing support
- [ ] Video generation capability
- [ ] Animation support

---

## Model Recommendations

### For Realistic Human Generation
1. **Juggernaut XL v8** - Primary recommendation
2. **Realistic Vision V60** - Alternative
3. **SDXL 1.0 + Refiner** - Official stability

### For Face Work
- **ReActor** model (inswapper_128.onnx)
- **IPAdapter** face models

### For Upscaling
- **4X-UltraSharp**
- **RealESRGAN_x4plus**
- **ScuNet**

---

## Dependencies

### Required Python Packages
- torch
- torchvision
- PIL
- numpy
- opencv-python
- scipy
- transformers
- insightface
- onnxruntime

### Required ComfyUI Nodes
- ComfyUI-ReActor
- ComfyUI_IPAdapter_plus
- ComfyUI-RMBG
- ComfyUI-ConstrainResolution
- ComfyUI-AdvancedUpscripts
- ComfyUI-Inpaint-Anything

---

## Installation Priority

### Phase 1: Core Setup
1. Install ComfyUI
2. Install custom nodes
3. Download base models

### Phase 2: Face & Identity
1. Install ReActor
2. Install IPAdapter Plus
3. Download face models

### Phase 3: Advanced Features
1. Install RMBG
2. Install Inpaint Anything
3. Install upscaling models

---

*Document Version: 1.0*
*Last Updated: 2026-02-23*
