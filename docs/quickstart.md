# Laura Image Studio - Quickstart Guide

## Your First Image Generation

### Step 1: Load a Workflow

1. Open ComfyUI
2. Click **Load** (or press Ctrl+O)
3. Navigate to: `custom_nodes/Laura_Image_Studio/workflows/`
4. Select `base_generation.json`

### Step 2: Configure the Model

1. In the **CheckpointLoader** node:
   - Select your SDXL model (e.g., juggernaut_xl_v8.safetensors)

### Step 3: Set Your Prompt

In the **LauraPromptBuilder** node:
- **Base prompt**: "photo of laura, detailed face"
- **Pose**: Choose from standing/sitting/walking/etc.
- **Lighting**: natural/studio/golden hour
- **Style**: portrait/full body/fashion

### Step 4: Generate

1. Click **Queue Prompt** (or press Ctrl+Enter)
2. Wait for generation to complete
3. View output in the SaveImage node

---

## Virtual Dressing Workflow

### Changing Clothes

1. Load `virtual_dressing.json`
2. Load source image of Laura
3. Configure VirtualDresser:
   - **Category**: top/bottom/dress/shoes/accessory
   - **Prompt**: Describe the clothing you want
4. Run workflow

### Changing Hairstyle

1. Load reference image (or use prompt)
2. Select hairstyle in HairStylist node:
   - short/long/curly/straight/wavy/bob/ponytail
3. Specify hair color
4. Run workflow

### Adding Accessories

Use AccessoryEditor node:
- **watch**: Luxury timepieces
- **glasses**: Eyewear
- **necklace**: Jewelry
- **bag**: Handbags

---

## Face Operations

### Face Swap

1. Load `face_swap.json`
2. Input face reference image
3. Input target body image
4. Choose swap mode:
   - **swap**: Complete face swap
   - **enhance**: Enhance existing face
   - **preserve**: Keep original face

### IPAdapter Face Embedding

Use IPAdapterFace node to maintain character consistency across generations.

---

## Inpainting & Outpainting

### Inpainting (Edit Specific Areas)

1. Load `inpainting.json`
2. Input image
3. Use SmartMaskGenerator to create mask
4. Describe what you want in the masked area
5. Run workflow

### Outpainting (Expand Image)

1. Load `outpainting.json`
2. Input image
3. Set direction:
   - all: Expand all sides
   - top/bottom/left/right: Expand one side
   - custom: Specify directions
4. Set pixels_to_add (256-512 recommended)
5. Run workflow

---

## Upscaling

### 2K Upscale (2048px)

Load `upscale_2k.json` - Good for web/social media

### 4K Upscale (4096px)

Load `upscale_4k.json` - Recommended for print

### 8K Upscale (8192px)

Load `upscale_8k.json` - Maximum quality for large prints

### Custom Resolution

Use UpscaleChain node:
- Select target resolution
- Choose upscale passes
- Select method (ultrasharp/realesrgan/mixed)

---

## Tips for Best Results

### Image Generation
- Use negative prompts to avoid artifacts
- Start with 1024x1024, then upscale
- Use professional lighting presets

### Virtual Dressing
- Provide reference images when possible
- Use specific prompts ("silk blouse" vs just "shirt")
- Start with high-quality source images

### Face Work
- Use clear face photos as references
- IPAdapter for consistent character
- FaceEnhancer for quality improvement

### Upscaling
- Use DetailEnhancer after upscaling
- Chain method for best 8K results
- 4x-UltraSharp model recommended

---

## Common Workflows

### Complete Portrait Session

1. Generate base image (base_generation.json)
2. Apply virtual dressing if needed
3. Enhance face (FaceEnhancer)
4. Remove/replace background
5. Upscale to desired resolution

### Fashion Shoot

1. Generate base
2. Use VirtualDresser for multiple outfits
3. Change hairstyles
4. Apply makeup
5. Background replacement
6. 4K/8K upscale
