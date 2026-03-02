# Laura Image Studio - Workflow Guide

## Table of Contents
1. [Base Generation](#base-generation)
2. [Virtual Dressing](#virtual-dressing)
3. [Face & Identity](#face--identity)
4. [Inpainting](#inpainting)
5. [Outpainting](#outpainting)
6. [Upscaling](#upscaling)
7. [Background Operations](#background-operations)

---

## Base Generation

### Recommended Workflow

```
CheckpointLoader → LauraPromptBuilder → CLIPTextEncode → KSampler → VAEDecode → SaveImage
```

### Best Settings

| Parameter | Recommended Value |
|-----------|-------------------|
| Model | Juggernaut XL v8 |
| Resolution | 1024x1024 or 832x1152 |
| Steps | 25-35 |
| CFG | 5.0-7.0 |
| Sampler | Euler or DPM++ 2M |

### Laura-Specific Tips

- Include "laura" in prompt for character consistency
- Use "detailed face, beautiful woman" for quality
- Add lighting presets: "studio lighting", "golden hour"

---

## Virtual Dressing

### Clothing Categories

| Node | Categories |
|------|------------|
| VirtualDresser | top, bottom, dress, shoes, accessory, watch, glasses, bag |
| HairStylist | short, long, curly, straight, wavy, bob, ponytail, braided, updo, pixie |
| AccessoryEditor | watch, glasses, necklace, earrings, bracelet, ring, bag, belt |
| MakeupArtist | natural, glam, dramatic, nude, vintage, bold, soft, editorial |

### Tips for Best Results

1. **Use Reference Images**: When possible, provide reference images for accurate clothing matching
2. **Specific Prompts**: "elegant silk blouse" works better than just "shirt"
3. **Preserve Settings**: Enable "preserve_face" and "preserve_pose" for realistic results
4. **Denoise**: Lower denoise (0.6-0.8) for subtle changes, higher for complete overhaul

---

## Face & Identity

### Nodes Overview

| Node | Function |
|------|----------|
| FaceDetector | Locate faces in image |
| FaceSwapper | Swap face onto body |
| FaceReference | Create face embedding |
| IPAdapterFace | Apply face embedding for consistency |
| ExpressionTransfer | Transfer expressions between images |
| AgeAdjuster | Modify perceived age |
| FaceEnhancer | Improve face quality |

### Face Swap Workflow

```
LoadImage (face) → FaceDetector → FaceReference
LoadImage (body)  → FaceSwapper (with face reference) → SaveImage
```

### IPAdapter for Character Consistency

1. Load reference face image
2. Connect to IPAdapterFace node
3. Apply to model for generation
4. All generated images will have consistent face

---

## Inpainting

### Workflow

```
LoadImage → SmartMaskGenerator → ManualMaskEditor → LauraInpainter → EdgeBlender → SaveImage
```

### Smart Mask Generator Modes

| Mode | Use Case |
|------|----------|
| auto | Automatic segmentation |
| subject | Isolate main subject |
| object | Select specific object |
| background | Select background |

### Inpainting Tips

1. **Mask Size**: Don't make masks too large - inpaints only what's needed
2. **Edge Blur**: Use 8-16px blur for seamless blending
3. **Denoise**: Higher (0.8-1.0) for major changes, lower for subtle edits
4. **Prompts**: Be specific about what you want in the masked area

---

## Outpainting

### Direction Options

| Direction | Description |
|-----------|-------------|
| all | Expand all four sides |
| top | Expand upward only |
| bottom | Expand downward only |
| left | Expand to the left |
| right | Expand to the right |
| top-bottom | Vertical expansion |
| left-right | Horizontal expansion |
| custom | Specify custom directions |

### Best Practices

1. **Pixels to Add**: Start with 256, increase if needed
2. **Blend Width**: Use 64-128px for smooth edges
3. **Prompts**: Describe the expanded area realistically
4. **Multiple Passes**: For large expansions, do multiple smaller expansions

---

## Upscaling

### Resolution Options

| Workflow | Output | Use Case |
|----------|--------|----------|
| upscale_2k.json | 2048px | Web, social media |
| upscale_4k.json | 4096px | Print, displays |
| upscale_8k.json | 8192px | Large format |

### Upscale Methods

| Method | Quality | Speed |
|--------|---------|-------|
| ultrasharp | Best | Medium |
| realesrgan | Good | Fast |
| pixelperfect | Good | Fast |
| chain | Best | Slow |
| mixed | Very Good | Medium |

### Recommended Workflow

1. Generate base at 1024x1024
2. Upscale to target resolution
3. Apply DetailEnhancer (strength 0.2-0.3)
4. Save final image

---

## Background Operations

### Workflow Options

#### Remove Background
```
LoadImage → BackgroundRemover → SaveImage
```

#### Replace Background
```
LoadImage → BackgroundRemover → LoadImage (new bg) → BackgroundReplacer → SaveImage
```

#### Generate New Background
```
LoadImage → BackgroundRemover → BackgroundGenerator → BackgroundReplacer → SaveImage
```

### Professional Effects

- **PortraitBokeh**: Add professional bokeh blur
- **ProLighting**: Add studio lighting effects
- **BackgroundColorize**: Add color tint

---

## Advanced Tips

### Quality Optimization

1. **Generation**: Use proper negative prompts
2. **Upscaling**: Chain method for 8K
3. **Face**: Use IPAdapter for consistency

### Speed Optimization

1. Use tile-based upscaling for large images
2. Enable model offloading if VRAM limited
3. Use smaller resolutions for previews

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Artifacts | Increase steps, lower CFG |
| Blurry | Use higher denoise, add sharpening |
| Wrong colors | Adjust prompt, check model |
| Face issues | Use IPAdapter, check reference |

---

## Complete Example Workflow

### Portrait Session

1. **Generate**: base_generation.json
   - Prompt: "photo of laura, professional portrait"
   - Resolution: 1024x1024

2. **Dress**: virtual_dressing.json
   - Change outfit
   - Adjust hairstyle
   - Apply makeup

3. **Face**: face_swap.json (if needed)
   - Apply IPAdapter for consistency

4. **Background**:
   - Remove background
   - Add new background or bokeh

5. **Upscale**: upscale_4k.json
   - 4K output
   - Detail enhancement

6. **Save**: Final high-quality portrait
