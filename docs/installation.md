# Laura Image Studio - Installation Guide

## Prerequisites

### System Requirements
- **OS**: Windows 10/11, Linux, or macOS
- **RAM**: 16GB minimum (32GB recommended)
- **GPU**: NVIDIA GPU with 8GB VRAM (16GB recommended)
- **Storage**: 50GB+ free space for models

### Required Software
1. **Python 3.10+**
2. **Git**
3. **ComfyUI**

---

## Step 1: Install ComfyUI

If you don't have ComfyUI installed:

```bash
# Clone ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git

# Navigate to directory
cd ComfyUI

# Install dependencies
pip install -r requirements.txt
```

---

## Step 2: Install Required Custom Nodes

Launch ComfyUI and install these nodes via the **Custom Nodes Manager** (or clone manually):

### Required Nodes

| Node | Purpose | Repository |
|------|---------|------------|
| ReActor | Face swapping | https://github.com/Gourieff/ComfyUI-ReActor |
| IPAdapter Plus | Face embedding | https://github.com/cubiq/ComfyUI_IPAdapter_plus |
| RMBG | Background removal | https://github.com/1038lab/ComfyUI-RMBG |
| ConstrainResolution | Resolution management | https://github.com/EnragedAntelope/ComfyUI-ConstrainResolution |
| AdvancedUpscripts | Professional upscaling | https://github.com/Kosinkadink/ComfyUI-AdvancedUpscripts |

### Install via Git

```bash
cd ComfyUI/custom_nodes

# Install ReActor
git clone https://github.com/Gourieff/ComfyUI-ReActor.git

# Install IPAdapter Plus
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git

# Install RMBG
git clone https://github.com/1038lab/ComfyUI-RMBG.git

# Install ConstrainResolution
git clone https://github.com/EnragedAntelope/ComfyUI-ConstrainResolution.git

# Install AdvancedUpscripts
git clone https://github.com/Kosinkadink/ComfyUI-AdvancedUpscripts.git
```

---

## Step 3: Download Models

### Base Models (SDXL)

Download these to `ComfyUI/models/checkpoints/`:

| Model | Description |
|-------|-------------|
| juggernaut_xl_v8.safetensors | Recommended for realistic images |
| realisticVisionV60_v1.safetensors | Alternative realistic model |
| sdxl_base_1.0.safetensors | Official SDXL base |

### Upscaling Models

Download to `ComfyUI/models/upscale_models/`:

| Model | Description |
|-------|-------------|
| 4x-UltraSharp.pth | Best quality upscaling |
| RealESRGAN_x4plus.pth | Alternative upscaler |
| ScuNet_GAN.pth | Neural upscaling |

### Face Models

Download to specified directories:

| Model | Path |
|-------|------|
| inswapper_128.onnx | ComfyUI/models/face_swap/ |
| ip-adapter-faceid-plusv2.bin | ComfyUI/models/ipadapter/ |
| RMBG-1.4.pth | ComfyUI/models/rmbg/ |

---

## Step 4: Install Laura Image Studio

```bash
# Clone this repository
git clone https://github.com/your-repo/Laura_Image_Studio.git

# Copy to ComfyUI custom_nodes
cp -r Laura_Image_Studio ComfyUI/custom_nodes/
```

---

## Step 5: Verify Installation

1. Restart ComfyUI
2. Check the node browser (right-click menu)
3. Look for "Laura Studio" category
4. All nodes should appear

---

## Troubleshooting

### Common Issues

**Nodes not appearing:**
- Restart ComfyUI
- Check console for errors
- Verify custom_nodes directory structure

**Out of memory errors:**
- Reduce image resolution
- Use smaller batch sizes
- Enable model offloading

**Model not found:**
- Verify model paths
- Check model filenames match workflow

**CUDA errors:**
- Update NVIDIA drivers
- Reinstall PyTorch with CUDA support

---

## Next Steps

See [Quickstart Guide](quickstart.md) to begin generating images!
