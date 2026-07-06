# Laura Image Studio v0.8 — Comprehensive Audit Report & Improvement Suggestions

**Date:** 2026-03-03
**Audited By:** Automated deep audit of all code, workflows, builder scripts, and documentation
**Scope:** All 15 node modules, 3 workflow JSONs, 3 builder scripts, 6 documentation files

---

## PART 1: AUDIT FINDINGS

### Severity Legend
- **CRITICAL** — Will crash at runtime, must fix before any release
- **HIGH** — Major functional issue, will cause incorrect behavior or broken features
- **MEDIUM** — Will cause confusion or partial malfunction, fix before public release
- **LOW** — Cosmetic, architectural, or minor issue, fix when convenient

---

### SECTION A: Python Code Issues (15 Node Modules)

#### A1. CRITICAL — Transposed Image Dimensions (upscaling.py, models.py)
- **Files:** `nodes/upscaling.py` (Upscale2K, Upscale4K, Upscale8K, UpscaleChain, ResolutionConstrainer), `nodes/models.py` (UniversalImg2Img)
- **Problem:** ComfyUI IMAGE tensors are `[B, H, W, C]` where `shape[1]=H, shape[2]=W, shape[3]=C`. These classes use `shape[2]` for height and `shape[3]` for width, but `shape[3]` is actually channels (always 3). This means they read the channel count as if it were width.
- **Impact:** Every upscaling operation will compute incorrect target dimensions. Images may be distorted or crash.
- **Fix:** Change `h, w = img.shape[2], img.shape[3]` to `h, w = img.shape[1], img.shape[2]` everywhere.

#### A2. CRITICAL — torchvision resize on wrong tensor format (upscaling.py)
- **File:** `nodes/upscaling.py` (all upscale classes)
- **Problem:** `torchvision.transforms.functional.resize()` expects `[C, H, W]` or `[B, C, H, W]` format, but is being called on `[B, H, W, C]` tensors without permuting.
- **Impact:** Will either crash with dimension error or produce garbled output.
- **Fix:** Add `img = img.permute(0, 3, 1, 2)` before resize and `img = img.permute(0, 2, 3, 1)` after.

#### A3. CRITICAL — Missing `colorama` in requirements.txt
- **File:** `requirements.txt` + multiple node files using `LauraLogger`
- **Problem:** `LauraLogger` class uses `colorama` for colored terminal output, but `colorama` is not listed in `requirements.txt`.
- **Impact:** Every log call crashes with `ModuleNotFoundError: No module named 'colorama'` if not coincidentally installed.
- **Fix:** Add `colorama>=0.4.6` to requirements.txt.

#### A4. HIGH — Duplicate `AdvancedModelLoader` class definition (models.py)
- **File:** `nodes/models.py`, defined at both line ~153 and line ~392
- **Problem:** Two different class implementations with the same name. The second silently overwrites the first.
- **Impact:** The first implementation's features are lost. If they differ in behavior, this is a logic bug.
- **Fix:** Rename one (e.g., `AdvancedModelLoaderV2`) or merge them into a single class.

#### A5. HIGH — Missing imports in models.py
- **File:** `nodes/models.py`
- **Problem:** `CharacterLoRALoader` calls `LoraLoader()` and the first `AdvancedModelLoader` calls `CheckpointLoaderSimple()` without importing these ComfyUI classes.
- **Impact:** These nodes will crash when their load functions are called.
- **Fix:** Add proper imports: `from comfy.sd import load_checkpoint_guess_config` or use ComfyUI's internal loader APIs.

#### A6. HIGH — `LauraLogger.warning()` called but method is `warn()` (video_advanced.py)
- **File:** `nodes/video_advanced.py`, line ~674
- **Problem:** Code calls `logger.warning("...")` but the `LauraLogger` class only defines a `warn()` method, not `warning()`.
- **Impact:** `AttributeError` at runtime when this code path is hit.
- **Fix:** Change `logger.warning(...)` to `logger.warn(...)`.

#### A7. HIGH — `LauraPromptBuilder` RETURN_TYPES mismatch (generation.py)
- **File:** `nodes/generation.py`
- **Problem:** `RETURN_TYPES = ("STRING",)` declares 1 output, but the function returns 2 values `(positive, negative)`.
- **Impact:** ComfyUI will only pass the first return value. The negative prompt output is silently lost.
- **Fix:** Change to `RETURN_TYPES = ("STRING", "STRING")` and add `RETURN_NAMES = ("positive", "negative")`.

#### A8. HIGH — Shared `NODE_CLASS_MAPPINGS` dict mutation pattern
- **Files:** `nodes/generation.py`, `nodes/video.py`, `nodes/video_advanced.py` all import and `.update()` into `models.py`'s dict
- **Problem:** Three modules share the same dict object reference from models.py. When `__init__.py` iterates modules, each `.update()` into the main dict re-registers nodes that were already added by a previous module.
- **Impact:** Works but fragile — if module load order changes or a module fails, other modules' nodes may not register. Also causes confusing behavior if debugging which module contributes which node.
- **Fix:** Each module should define its own independent `NODE_CLASS_MAPPINGS = {}` and `NODE_DISPLAY_NAME_MAPPINGS = {}`.

#### A9. MEDIUM — Stub/placeholder implementations that return input unchanged
- **Files and classes:**
  - `nodes/face.py` → `LauraVideoFaceDrive.drive_face()` — returns input image unchanged (no face driving)
  - `nodes/upscaling.py` → `ImageToSquare.to_square()` — returns input unchanged (no squaring)
  - `nodes/tile_processing.py` → `TileInpainter.inpaint_tiles()` — returns input unchanged (no inpainting)
  - `nodes/upscaling.py` → `LauraVideoCinemaUpscale` — SUPIR code path has `pass` (never executes)
- **Impact:** These nodes load and appear functional in the UI, but do nothing. Users will think they're broken.
- **Fix:** Either implement the actual logic or add clear warnings in the UI (e.g., display name "[WIP] Video Face Drive").

#### A10. LOW — Non-standard `LIST` return type in batch_processing.py
- **File:** `nodes/batch_processing.py`
- **Problem:** Uses `RETURN_TYPES = ("LIST",)` which is not a standard ComfyUI type. Should use `("IMAGE",)` for batched images or a custom type.
- **Impact:** May cause connection compatibility issues in ComfyUI's link type validation.

---

### SECTION B: Builder Script Issues

#### B1. HIGH — `LoadText||pysssss` double-pipe typo (build_community_workflow.py)
- **File:** `workflows/master/build_community_workflow.py`, line ~438
- **Problem:** Uses `"LoadText||pysssss"` (double pipe) but the correct ComfyUI node name is `"LoadText|pysssss"` (single pipe).
- **Impact:** This node will show as RED (not found) in ComfyUI when loading the Community workflow.
- **Fix:** Change `||` to `|`.

#### B2. HIGH — Self-referencing BASE_FILE (build_community_workflow.py)
- **File:** `workflows/master/build_community_workflow.py`, line ~36
- **Problem:** `BASE_FILE = OUTPUT_FILE = "Laura_Master_Community_v0.8.json"`. Reads itself as input. On first run from a clean state, the file doesn't exist → `FileNotFoundError`.
- **Impact:** Cannot build Community workflow from scratch. Must already have a previous copy.
- **Fix:** Change to read from `../virtual_dressing_room.json` like the other two scripts.

#### B3. MEDIUM — `WAN_LATENT` vs `WANLATENT` type mismatch
- **Files:** Community builder uses `"WAN_LATENT"`, Hybrid builder uses `"WANLATENT"` for the same WanImageEncode node output
- **Impact:** One of them will fail link type matching at runtime (the wrong one just won't connect).
- **Fix:** Check the actual `ComfyUI-WanVideoWrapper` source for the correct type name and use it consistently.

#### B4. MEDIUM — Hybrid's WanSampler missing wan_latent input
- **File:** `workflows/master/build_hybrid_workflow.py`, line ~677
- **Problem:** `WanSampler` is created with only `wan_model` input, but the community version also connects `wan_latent` from `WanImageEncode`.
- **Impact:** The WanSampler may not generate video correctly without encoded latent input, making WanImageEncode an orphaned node.
- **Fix:** Add the wan_latent input connection.

#### B5. MEDIUM — `CogVideoX` model type inconsistency
- **Files:** Community uses `"COGVIDEOMODEL"`, Hybrid uses `"COGVIDEOPIPE"`
- **Impact:** Same as B3 — one of them has the wrong type name.
- **Fix:** Check actual CogVideoX wrapper source for the correct type name.

#### B6. LOW — Dead `BASE_FILE` variable (build_studio_workflow.py)
- **File:** `workflows/master/build_studio_workflow.py`, line 16
- **Problem:** `BASE_FILE = "Laura_Master_Community_v0.8.json"` defined but never used.
- **Fix:** Remove the dead variable.

---

### SECTION C: Workflow JSON Issues

#### C1. LOW — `AILab_LoadImage` node type (all 3 workflows)
- **Files:** All 3 workflow JSONs contain node ID 17 with type `AILab_LoadImage`
- **Problem:** This is a community node from the AILab pack. It was inherited from the base `virtual_dressing_room.json`. If users don't have the AILab pack installed, this node shows as RED.
- **Impact:** Low — it's a single LoadImage-equivalent node, users can replace it with standard `LoadImage`.
- **Fix:** Either document as a dependency, or replace with standard `LoadImage` in the builder scripts.

#### C2. PASSED — Structural Integrity
- All 3 JSONs are valid JSON
- All have correct `last_node_id` and `last_link_id`
- Node counts match expected: Community=158, Studio=161, Hybrid=160
- Link counts match: Community=152, Studio=164, Hybrid=164
- Group counts: All 27
- No duplicate node IDs
- No duplicate link IDs
- All links reference valid node IDs
- No null/undefined values in critical fields

---

### SECTION D: Documentation Issues

#### D1. HIGH — VRAM tier inconsistency across documents
- **PLAN.md:** 8 tiers (ultra_low through hpc)
- **README.md:** Claims "8 tiers" but table shows only 7 (missing HPC)
- **WORKSPACE.md:** Shows only 4 tiers with different range definitions
- **WORKFLOW_GUIDE.md:** Shows 7 tiers (missing HPC)
- **NODE_REFERENCE_GUIDE.md:** Shows 9 options (auto + 8 tiers) — matches code
- **Actual code (quantization.py):** 8 operational tiers + "auto"
- **Fix:** Standardize all docs to show 8 tiers matching the code. WORKSPACE needs the full tier list.

#### D2. MEDIUM — `CogVideoXGenerator` missing from NODE_REFERENCE_GUIDE
- **File:** `workflows/master/NODE_REFERENCE_GUIDE.md`
- **Problem:** Documents only 10 of 11 video_advanced nodes. `CogVideoXGenerator` (Text-to-Video) is omitted.
- **Fix:** Add documentation entry for CogVideoXGenerator.

#### D3. MEDIUM — `LauraVideoCinemaUpscale` wrong module attribution in NODE_REFERENCE_GUIDE
- **File:** `workflows/master/NODE_REFERENCE_GUIDE.md`, line ~314
- **Problem:** Claims it's "registered in video_advanced.py" but it's actually in upscaling.py (line 671 of code).
- **Fix:** Correct the attribution to upscaling.py.

#### D4. MEDIUM — TASK_TRACKING.md is stale
- **Problem:** Still shows node_config.json and model-list.json as "In Progress" with old counts (6 nodes, 7 models), but both were updated to 107 nodes and 38 models earlier this session.
- **Fix:** Update to reflect completed state.

#### D5. MEDIUM — Stage count arithmetic error in PLAN.md
- **File:** `PLAN.md`, line ~135
- **Problem:** Header says "Extended Pipeline (11 New Stages)" but then lists Stages 15-26, which is 12 entries.
- **Fix:** Either change to "12 New Stages" or clarify that Stage 26 is the relocated Final Output (not a "new" stage).

#### D6. MEDIUM — Wan 2.1 vs 2.2 URL inconsistency
- **Files:** README.md links to Wan2.1 HuggingFace repos, WORKSPACE.md links to Wan2.2
- **Problem:** Project claims Wan 2.2 support but README download links point to 2.1 versions.
- **Fix:** Verify which model versions exist on HuggingFace and use consistent URLs.

#### D7. LOW — Placeholder Patreon/BMAC links in README
- **File:** `custom_nodes/Laura_Image_Studio/README.md`, lines 137 and 230
- **Problem:** Shows "Links coming soon!" — expected before launch but should be tracked.

---

## PART 2: IMPROVEMENT SUGGESTIONS (SOTA 2025-2026)

### CATEGORY 1: VRAM Optimization & Low-End GPU Support

#### 1A. FP8 Transformer Engine Integration [HIGH PRIORITY]
- **What:** PyTorch 2.10+ (which the user has!) supports native FP8 via `torch.float8_e4m3fn` and `torch.float8_e5m2`. The current `QuantizationConfig` node should use this instead of manual quantization.
- **Why:** 2x memory savings over FP16 with <1% quality loss for inference. Enables 14B models on 12GB cards.
- **Implementation:** Add `torch.compile()` with FP8 backend option to `UniversalModelLoader`. Auto-detect if GPU supports FP8 (RTX 40xx Ada Lovelace or newer).
- **VRAM Impact:** 14B model drops from ~28GB FP16 to ~14GB FP8. Wan 2.2 14B becomes viable on 12GB.

#### 1B. Aggressive CPU Offloading with Smart Prefetching [HIGH PRIORITY]
- **What:** Instead of the current simple offload (entire model to CPU), implement layer-by-layer offloading with GPU prefetching of the next layer while the current one executes.
- **Why:** Current offloading is all-or-nothing. Smart prefetching keeps the GPU busy while moving layers on/off, reducing the offload speed penalty by 40-60%.
- **Implementation:** Wrap the model's forward pass with a `LayerOffloader` that uses `torch.cuda.Stream()` for async data transfer.
- **VRAM Impact:** Run 14B models with only 6-8GB VRAM (with speed penalty, but no OOM).

#### 1C. Tiled VAE Processing with Overlap [MEDIUM PRIORITY]
- **What:** ComfyUI has built-in `VAEDecodeTiled`/`VAEEncodeTiled`, but these use fixed tiles. Implement adaptive tiling that adjusts tile size based on free VRAM, with configurable overlap to eliminate seam artifacts.
- **Why:** VAE decode of 4K images can OOM on 8GB cards. Adaptive tiling with overlap fixes this.
- **Implementation:** Add `adaptive_tile_size` parameter to upscaling nodes that auto-computes optimal tile dimensions from `torch.cuda.mem_get_info()`.

#### 1D. Model Unloading Queue with Priority [LOW PRIORITY]
- **What:** Instead of manually placing `LauraVRAMCleaner` nodes, implement an automatic model unloading queue that tracks which models are loaded and evicts the least-recently-used when VRAM is needed.
- **Why:** Users currently must manually manage model loading/unloading. An LRU cache makes the workflow self-managing.
- **Implementation:** Singleton `ModelCache` class that wraps `comfy.model_management` with LRU eviction policy.

---

### CATEGORY 2: Video Generation (Latest SOTA)

#### 2A. Wan 2.2 FunCtrl Motion Control [HIGH PRIORITY]
- **What:** Wan 2.2 introduced FunCtrl — function-level motion control that lets users define motion trajectories for specific objects in the scene (e.g., "person walks left to right while camera pans").
- **Why:** Current `LauraWanDirectedVideo` uses basic motion prompts. FunCtrl provides precise trajectory control via control points, which is essential for professional viral video content.
- **Implementation:** New node `LauraWanFunCtrl` that accepts trajectory keypoints (x, y, frame) and converts them to Wan 2.2's FunCtrl conditioning format.
- **Models needed:** Wan 2.2 FunCtrl adapter weights from HuggingFace.

#### 2B. HunyuanVideo 2.0 Support [HIGH PRIORITY]
- **What:** Tencent released HunyuanVideo 2.0 in early 2026 with significant quality improvements over 1.0 — better temporal consistency, 1080p native support, and lower VRAM requirement (8GB FP8).
- **Why:** It's now competitive with Wan 2.2 for quality and easier to run on lower VRAM.
- **Implementation:** Add `HunyuanVideo2Loader` and `HunyuanVideo2Generator` nodes to `video_advanced.py`. Pattern after the existing HunyuanDiT loader.

#### 2C. Step-Video Open Source Integration [MEDIUM PRIORITY]
- **What:** Step-Video (by StepFun) released their open-source 30B parameter video model in late 2025. It generates 16-second clips at 720p with industry-leading motion quality.
- **Why:** Currently one of the highest-quality open video models. The 8B variant runs on 12GB with FP8.
- **Implementation:** New node pair `StepVideoLoader` + `StepVideoGenerator`.

#### 2D. Video-to-Video Style Transfer with Temporal Consistency [MEDIUM PRIORITY]
- **What:** Current `VideoToVideo` node processes frames independently. Implement optical-flow-guided style transfer that maintains temporal consistency across frames.
- **Why:** Frame-by-frame processing causes flickering/jitter. Temporal consistency is critical for professional video.
- **Implementation:** Use RAFT optical flow to compute frame-to-frame warping, then blend the stylized frame with the warped previous frame.

---

### CATEGORY 3: Face & Character

#### 3A. Implement Actual LivePortrait v2 Face Driving [CRITICAL]
- **What:** `LauraVideoFaceDrive` is currently a STUB (returns input unchanged). Implement the actual LivePortrait v2 pipeline.
- **Why:** This is a advertised feature that doesn't work. Users paying for Studio/Hybrid editions expect this.
- **Implementation:** 
  1. Load LivePortrait model using existing community weights
  2. Extract face landmarks from source video using MediaPipe or InsightFace
  3. Apply stitching and retargeting using LivePortrait's official pipeline
  4. Composite driven face back into the original frame
- **Dependencies:** `mediapipe`, `insightface`, LivePortrait model weights.

#### 3B. PuLID Identity Preservation [MEDIUM PRIORITY]
- **What:** PuLID (Pure and Lightning ID Customization) is a 2025/2026 advancement over IPAdapter for identity-preserving generation. It maintains facial identity with higher fidelity across poses and expressions.
- **Why:** Current IPAdapterFace loses identity details in extreme poses. PuLID maintains identity 95%+ even in profile views.
- **Implementation:** New node `PuLIDFaceReference` that loads PuLID weights and applies identity conditioning to the diffusion process.

#### 3C. Audio-Driven Lip Sync (SadTalker / Wav2Lip) [LOW PRIORITY]
- **What:** Generate lip movements from audio input. Combined with LivePortrait face driving, this enables talking-head viral content from a single photo + audio file.
- **Why:** Huge demand for AI influencer content that talks. Currently requires external tools.
- **Implementation:** New node `AudioLipSync` that takes (IMAGE, AUDIO) and outputs VIDEO with lip-synced face.

---

### CATEGORY 4: Image Quality & Generation

#### 4A. FLUX.1 Tools (Fill, Depth, Canny, Redux) Support [HIGH PRIORITY]
- **What:** Black Forest Labs released FLUX.1 Tools — specialized variants for inpainting (Fill), depth-guided generation (Depth), edge-guided generation (Canny), and image variation (Redux).
- **Why:** These are the SOTA for controlled generation. FLUX Fill outperforms all other inpainting models.
- **Implementation:** Add `FLUXFillLoader`, `FLUXDepthLoader`, `FLUXCannyLoader`, `FLUXReduxLoader` nodes with matching generator nodes. These use the same FLUX architecture but different conditioning.

#### 4B. SD 3.5 Large Turbo Support [MEDIUM PRIORITY]
- **What:** Stability AI's distilled version of SD 3.5 Large that generates in 4-8 steps instead of 28+.
- **Why:** 4x faster generation with minimal quality loss. Great for preview/iteration.
- **Implementation:** Add as a model option in `UniversalModelLoader` with appropriate step count defaults.

#### 4C. OmniGen 2 Multi-Modal Generation [MEDIUM PRIORITY]
- **What:** OmniGen 2 (2026) is a unified model that handles text-to-image, image editing, subject-driven generation, and style transfer in a single model without separate ControlNets or IPAdapters.
- **Why:** Simplifies the pipeline dramatically. One model replaces 4-5 specialized models.
- **Implementation:** New node pair `OmniGenLoader` + `OmniGenGenerate` with mode selection (t2i, edit, subject, style).

#### 4D. IC-Light v2 Relighting [LOW PRIORITY]
- **What:** Improved version of IC-Light for physically-based relighting of portraits. Lets users change lighting direction, color temperature, and intensity after generation.
- **Why:** Lighting is one of the biggest quality differentiators for photorealistic AI portraits.
- **Implementation:** New node `ICLightRelight` that takes IMAGE + light_direction + temperature parameters.

---

### CATEGORY 5: Workflow UX & Quality of Life

#### 5A. Preview Node for Every Stage [HIGH PRIORITY]
- **What:** Add a `PreviewImage` node at the output of every stage so users can inspect intermediate results without running the full pipeline.
- **Why:** Currently users must run the entire pipeline to see results. With 27 groups, debugging which stage has an issue is painful.
- **Implementation:** Add PreviewImage nodes (bypassed by default, mode=4) at each stage output. Users toggle on the ones they want to inspect.

#### 5B. Workflow Progress Indicator Node [MEDIUM PRIORITY]
- **What:** A node that displays "Stage X of 27 - [Stage Name] - Elapsed: 00:00 - ETA: 00:00" in the ComfyUI terminal and node UI.
- **Why:** Long pipelines with 27 stages give no feedback about progress. Users don't know if it's stuck or still working.
- **Implementation:** New node `LauraProgressIndicator` that reads the group name and logs timing info. Place one at the start of each stage.

#### 5C. Preset Manager Node [MEDIUM PRIORITY]
- **What:** A node that saves/loads all widget values across the workflow as named presets (e.g., "Instagram Portrait", "TikTok Video", "Product Shot").
- **Why:** Users want to switch between different generation configs quickly. Currently they must manually adjust dozens of widgets.
- **Implementation:** New node `LauraPresetManager` with save/load/delete buttons and preset name input. Stores presets as JSON in a `presets/` directory.

#### 5D. One-Click Quality Presets [LOW PRIORITY]
- **What:** A single dropdown node that sets resolution, steps, CFG, sampler, and model variant based on quality level: "Draft (fast)", "Standard", "High Quality", "Ultra (slow)".
- **Why:** New users are overwhelmed by widget options. A single quality selector simplifies the experience.
- **Implementation:** New node `LauraQualityPreset` with a single dropdown that outputs recommended values to downstream nodes.

---

### CATEGORY 6: Performance & Technical

#### 6A. torch.compile() Integration [HIGH PRIORITY]
- **What:** PyTorch 2.10's `torch.compile()` with `mode="reduce-overhead"` can speed up inference by 20-40% by compiling the model into optimized CUDA kernels.
- **Why:** Free speed boost with no quality impact. The user's PyTorch 2.10 already supports this.
- **Implementation:** Add a `compile_model` boolean option to `UniversalModelLoader`. When enabled, wrap the model with `torch.compile(model, mode="reduce-overhead")` after loading.
- **Caveat:** First run is slow (compilation), subsequent runs are fast. Good for batch processing.

#### 6B. CUDA Graph Caching for Repeated Generations [MEDIUM PRIORITY]
- **What:** Use CUDA graphs to capture and replay the GPU execution of the inference pipeline, eliminating CPU-GPU kernel launch overhead.
- **Why:** For batch processing (same model, different prompts/seeds), CUDA graphs can provide 2-3x throughput improvement.
- **Implementation:** Integrate with ComfyUI's execution engine to detect when the same pipeline is being re-executed and use cached CUDA graphs.

#### 6C. Quantized KV-Cache for Video Models [MEDIUM PRIORITY]
- **What:** Video generation models (Wan 2.2, CogVideoX) have large KV-caches that consume significant VRAM. Quantizing the KV-cache to INT8 reduces memory usage by 50% with <0.5% quality loss.
- **Why:** This is the single biggest VRAM optimization for video models. Makes 14B Wan 2.2 practical on 12GB.
- **Implementation:** Hook into the model's attention layers and replace KV-cache storage with INT8 quantized versions.

---

## PART 3: PRIORITY IMPLEMENTATION ROADMAP

### v0.8.1 — Bug Fix Release (Immediate)
Focus: Fix all CRITICAL and HIGH issues found in this audit.

| Priority | Issue | Effort |
|----------|-------|--------|
| 1 | Fix transposed dimensions in upscaling.py (A1) | 30 min |
| 2 | Fix torchvision resize tensor format (A2) | 30 min |
| 3 | Add colorama to requirements.txt (A3) | 1 min |
| 4 | Remove duplicate AdvancedModelLoader (A4) | 15 min |
| 5 | Fix missing imports in models.py (A5) | 15 min |
| 6 | Fix LauraLogger.warning → .warn (A6) | 5 min |
| 7 | Fix LauraPromptBuilder RETURN_TYPES (A7) | 5 min |
| 8 | Fix shared NODE_CLASS_MAPPINGS pattern (A8) | 1 hour |
| 9 | Fix LoadText double-pipe typo in community builder (B1) | 5 min |
| 10 | Fix community builder BASE_FILE to read from VDR (B2) | 10 min |
| 11 | Standardize VRAM tier docs across all files (D1) | 30 min |
| 12 | Update TASK_TRACKING to reflect current state (D4) | 15 min |

**Total estimated effort: ~3.5 hours**

### v0.8.5 — Stub Implementation Release
Focus: Replace all stub/placeholder implementations with working code.

| Priority | Feature | Effort |
|----------|---------|--------|
| 1 | Implement LauraVideoFaceDrive (LivePortrait v2) (3A) | 2-3 days |
| 2 | Implement ImageToSquare | 1 hour |
| 3 | Implement TileInpainter | 4 hours |
| 4 | Implement LauraVideoCinemaUpscale SUPIR path | 1 day |

### v0.9 — SOTA Features Release
Focus: Add the highest-impact new features.

| Priority | Feature | Impact | Effort |
|----------|---------|--------|--------|
| 1 | FP8 Transformer Engine (1A) | VRAM -50% | 2 days |
| 2 | torch.compile() integration (6A) | Speed +30% | 1 day |
| 3 | FLUX.1 Tools support (4A) | Quality | 3 days |
| 4 | Wan 2.2 FunCtrl (2A) | Video quality | 2 days |
| 5 | Preview nodes per stage (5A) | UX | 4 hours |
| 6 | HunyuanVideo 2.0 (2B) | Video options | 2 days |

### v1.0 — Stable Release
Focus: Complete the feature set and polish.

| Priority | Feature | Impact | Effort |
|----------|---------|--------|--------|
| 1 | Smart CPU offloading with prefetch (1B) | Low-VRAM | 3 days |
| 2 | PuLID identity preservation (3B) | Face quality | 2 days |
| 3 | Preset manager (5C) | UX | 1 day |
| 4 | Progress indicator (5B) | UX | 4 hours |
| 5 | Step-Video integration (2C) | Video quality | 2 days |
| 6 | OmniGen 2 support (4C) | Simplification | 2 days |

---

## PART 4: QUICK-FIX CHECKLIST (For v0.8.1)

```
[ ] A1. Fix image dimension indexing in upscaling.py (shape[1]/shape[2] not shape[2]/shape[3])
[ ] A2. Add permute() calls around torchvision.resize in upscaling.py
[ ] A3. Add 'colorama>=0.4.6' to requirements.txt
[ ] A4. Remove duplicate AdvancedModelLoader in models.py
[ ] A5. Fix missing ComfyUI class imports in models.py
[ ] A6. Change logger.warning() to logger.warn() in video_advanced.py
[ ] A7. Fix LauraPromptBuilder RETURN_TYPES to ("STRING", "STRING")
[ ] A8. Give each module its own independent NODE_CLASS_MAPPINGS dict
[ ] B1. Fix LoadText||pysssss → LoadText|pysssss in community builder
[ ] B2. Change community builder BASE_FILE to ../virtual_dressing_room.json
[ ] B3. Standardize WAN_LATENT type name across builders
[ ] B4. Add wan_latent input to Hybrid's WanSampler
[ ] B5. Standardize CogVideoX model type name across builders
[ ] D1. Standardize VRAM tiers to 8 tiers across all docs
[ ] D2. Add CogVideoXGenerator to NODE_REFERENCE_GUIDE
[ ] D3. Fix LauraVideoCinemaUpscale module attribution
[ ] D4. Update TASK_TRACKING progress metrics
[ ] D5. Fix "11 stages" → "12 stages" in PLAN.md
[ ] D6. Standardize Wan model version URLs
[ ] Rebuild all 3 workflow JSONs after builder fixes
```

---

*This document is for internal use. Do NOT commit to the public GitHub repo.*
*Next action: Fix v0.8.1 issues, then rebuild workflows.*
