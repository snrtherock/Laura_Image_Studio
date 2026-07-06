# Laura Image Studio - Troubleshooting Guide

## Common Issues and Solutions

---

## Installation Issues

### Custom Nodes Not Appearing

**Symptoms**: Laura Studio nodes don't appear in node browser

**Solutions**:
1. Restart ComfyUI completely
2. Check console for Python errors
3. Verify directory structure:
   ```
   ComfyUI/custom_nodes/Laura_Image_Studio/
   ├── __init__.py
   ├── nodes/
   │   ├── __init__.py
   │   ├── generation.py
   │   ├── dressing.py
   │   ├── face.py
   │   ├── inpainting.py
   │   ├── upscaling.py
   │   └── background.py
   └── workflows/
   ```

### Model Not Found

**Symptoms**: "Model not found" errors

**Solutions**:
1. Verify model is in correct directory
2. Check filename matches exactly
3. Common paths:
   - Checkpoints: `ComfyUI/models/checkpoints/`
   - Upscale models: `ComfyUI/models/upscale_models/`
   - Face models: `ComfyUI/models/face_swap/`

---

## Generation Issues

### Poor Image Quality

**Symptoms**: Blurry, artifacts, unnatural images

**Solutions**:
- Increase sampling steps (25-50)
- Adjust CFG scale (4-7)
- Use better base model (Juggernaut XL recommended)
- Add quality negative prompts

### Face Not Looking Like Laura

**Symptoms**: Generated face doesn't match character

**Solutions**:
1. Include "laura" in positive prompt
2. Use IPAdapter face embedding
3. Lower CFG for more prompt adherence
4. Use face reference image

### Wrong Colors/Skin Tone

**Symptoms**: Unnatural skin colors

**Solutions**:
- Check model compatibility
- Adjust prompt: "natural skin tone"
- Use professional lighting presets
- Avoid conflicting color descriptors

---

## Virtual Dressing Issues

### Clothing Not Changing

**Symptoms**: Outfit stays the same

**Solutions**:
- Increase denoise (0.7-0.9)
- Provide reference image
- Make prompt more specific
- Check mask is properly applied

### Body Distortion

**Symptoms**: Weird body proportions

**Solutions**:
- Enable "preserve_pose" option
- Use lower denoise
- Provide clearer reference
- Reduce prompt complexity

### Inconsistent Lighting

**Symptoms**: New clothes look different from original

**Solutions**:
- Use "preserve_pose" and "preserve_face"
- Reference original lighting in prompt
- Use lower denoise strength

---

## Face Operation Issues

### Face Swap Not Working

**Symptoms**: Face doesn't transfer

**Solutions**:
1. Verify ReActor is installed
2. Check inswapper model is downloaded
3. Use clear face photos
4. Try "enhance" mode instead of "swap"

### IPAdapter Not Working

**Symptoms**: Character consistency lost

**Solutions**:
1. Verify IPAdapter model installed
2. Check face image is clear
3. Adjust weight (0.8-1.2 recommended)
4. Use correct IPAdapter model type

### Multiple Faces Issue

**Symptoms**: Wrong face selected

**Solutions**:
- Use MultiFaceHandler node
- Adjust detection threshold
- Crop image to single face first

---

## Inpainting/Outpainting Issues

### Mask Not Working

**Symptoms**: Inpainting affects wrong area

**Solutions**:
1. Check mask is properly connected
2. Verify mask is black/white (not grayscale)
3. Use SmartMaskGenerator for auto-masking
4. Manual mask editor for fine-tuning

### Edge artifacts

**Symptoms**: Visible seams at mask edges

**Solutions**:
- Increase edge_blur parameter
- Use "gaussian" blend mode
- Apply EdgeBlender node
- Multiple smaller inpainting passes

### Outpainting Fails

**Symptoms**: Expansion looks wrong

**Solutions**:
1. Use smaller pixels_to_add (128-256)
2. Increase blend_width
3. Add more detail to background prompt
4. Try different directions sequentially

---

## Upscaling Issues

### Out of Memory (OOM)

**Symptoms**: CUDA out of memory error

**Solutions**:
1. Reduce tile_size (256-512)
2. Enable tiled upscaling
3. Use smaller upscale model
4. Close other applications
5. Enable model offloading

### Upscaled Image Too Large

**Symptoms**: Can't save or view image

**Solutions**:
1. Use smaller target resolution
2. Use tile-based upscaling
3. Reduce passes in UpscaleChain

### Quality Loss

**Symptoms**: Upscaled image looks worse

**Solutions**:
- Use 4x-UltraSharp model
- Enable "preserve_details"
- Apply DetailEnhancer after upscale
- Use chain method for 8K

---

## Background Issues

### Background Removal Fails

**Symptoms**: Background not removed

**Solutions**:
1. Verify RMBG model installed
2. Check image has clear subject
3. Try different threshold values
4. Use manual mask for difficult images

### Edge Fringing

**Symptoms**: White/colored edges on subject

**Solutions**:
- Increase matte_feather
- Use edge_blur in BackgroundReplacer
- Post-process with edge cleaner

---

## Performance Issues

### Slow Generation

**Symptoms**: Takes too long

**Solutions**:
- Use faster samplers (Euler, DPM++ 2M)
- Reduce steps (20-25 is often enough)
- Use smaller resolutions for previews
- Enable VAE tiling for large images

### VRAM Usage High

**Symptoms**: Running out of GPU memory

**Solutions**:
1. Enable model offloading
2. Use smaller batch sizes
3. Close GPU applications
4. Upgrade GPU or add more RAM

---

## Error Messages

### "module not found"

**Fix**: Install required packages
```bash
pip install torch torchvision pillow numpy opencv-python
```

### "invalid model file"

**Fix**: Re-download model, verify file integrity

### "connection error"

**Fix**: Check internet for model downloads

---

## Getting Help

If issues persist:

1. Check ComfyUI documentation
2. Verify all dependencies installed
3. Check GPU drivers up to date
4. Try fresh ComfyUI installation

---

## Diagnostic Information

When asking for help, include:

1. Error message (full text)
2. ComfyUI version
3. GPU model and VRAM
4. OS version
5. Steps to reproduce
6. Screenshots if applicable
