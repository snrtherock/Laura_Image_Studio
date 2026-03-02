"""Generate Virtual Dressing Room v2.1 - Enhanced guides with sticky notes
and comprehensive model download links."""
import json


class WB:
    def __init__(self):
        self.nodes = {}
        self.links = []
        self.lc = 0
        self.groups = []

    def n(self, nid, ntype, pos, size, title=None, widgets=None,
          color=None, bgcolor=None, mode=0, props=None):
        nd = {"id": nid, "type": ntype, "pos": pos, "size": size,
              "flags": {}, "order": 0, "mode": mode,
              "_i": [], "_o": [],
              "properties": props or {"Node name for S&R": ntype}}
        if widgets is not None:
            nd["widgets_values"] = widgets
        if title:
            nd["title"] = title
        if color:
            nd["color"] = color
            nd["bgcolor"] = bgcolor
        self.nodes[nid] = nd
        return nid

    def o(self, nid, name, typ):
        nd = self.nodes[nid]
        s = len(nd["_o"])
        nd["_o"].append({"name": name, "type": typ, "links": [], "slot_index": s})
        return s

    def i(self, nid, name, typ):
        nd = self.nodes[nid]
        s = len(nd["_i"])
        nd["_i"].append({"name": name, "type": typ, "link": None})
        return s

    def L(self, src, ss, tgt, ts, typ):
        self.lc += 1
        self.links.append([self.lc, src, ss, tgt, ts, typ])
        self.nodes[src]["_o"][ss]["links"].append(self.lc)
        self.nodes[tgt]["_i"][ts]["link"] = self.lc

    def g(self, title, bb, color):
        self.groups.append({"title": title, "bounding": bb,
                            "color": color, "font_size": 24})

    def build(self):
        nl = []
        for idx, (nid, nd) in enumerate(sorted(self.nodes.items())):
            nd["order"] = idx
            out = dict(nd)
            del out["_i"]; del out["_o"]
            if nd["_i"]:
                out["inputs"] = nd["_i"]
            if nd["_o"]:
                outs = []
                for oo in nd["_o"]:
                    oc = dict(oo)
                    if not oc["links"]:
                        oc["links"] = None
                    outs.append(oc)
                out["outputs"] = outs
            nl.append(out)
        return {"last_node_id": max(self.nodes.keys()),
                "last_link_id": self.lc,
                "nodes": nl, "links": self.links,
                "groups": self.groups, "config": {}, "extra": {},
                "version": 0.4}


def seg_w(indices):
    b = [False]*18
    for ii in indices:
        b[ii] = True
    return b + [512, 0, 0, False, "Alpha", "#222222"]


def note(w, nid, pos, size, text, title=None, color="#432", bgcolor="#653"):
    w.n(nid, "Note", pos, size, title=title, widgets=[text],
        props={"text": text}, color=color, bgcolor=bgcolor)


def label(w, nid, pos, size, title, font_size=18, font_color="#FFFFFF",
          bg_color="#333366", align="left", padding=10):
    w.n(nid, "Label (rgthree)", pos, size, title=title,
        props={"fontSize": font_size, "fontFamily": "Arial",
               "fontColor": font_color, "backgroundColor": bg_color,
               "textAlign": align, "padding": padding,
               "borderRadius": 8, "angle": 0})


def save_img(w, nid, pos, prefix, mode=0):
    w.n(nid, "SaveImage", pos, [300, 80], title=f"Save: {prefix}",
        widgets=[prefix], mode=mode, color="#223", bgcolor="#335")
    w.i(nid, "images", "IMAGE")


def preview(w, nid, pos, title, mode=0):
    w.n(nid, "PreviewImage", pos, [300, 300], title=title, mode=mode)
    w.i(nid, "images", "IMAGE")


def build():
    w = WB()

    # ══════════════════════════════════════════════════════════════════
    # CONTROL PANEL
    # ══════════════════════════════════════════════════════════════════
    w.n(900, "Fast Groups Bypasser (rgthree)", [50, 50], [340, 600],
        title="TOGGLE PANEL - Enable/Disable Sections",
        widgets=[],
        props={"matchColors": "", "matchTitle": "", "showNav": True,
               "showAllGraphs": True, "sort": "position",
               "customSortAlphabet": "", "toggleRestriction": "default"},
        color="#446", bgcolor="#557")
    w.o(900, "OPT_CONNECTION", "*")

    # ══════════════════════════════════════════════════════════════════
    # DEDICATED GUIDES SECTION - Sticky Notes + Note Nodes
    # ══════════════════════════════════════════════════════════════════

    # --- Section Header ---
    label(w, 800, [50, 720], [340, 40],
          "MODELS & DOWNLOADS GUIDE",
          font_size=20, font_color="#FFFFFF", bg_color="#884411",
          align="center", padding=8)

    # --- Checkpoint Models Guide ---
    note(w, 801, [50, 780], [340, 440],
         "=== CHECKPOINT MODELS ===\n"
         "Folder: models/checkpoints/\n"
         "Pick ONE based on your VRAM:\n\n"
         "[8GB VRAM - Budget]\n"
         "DreamShaperXL Turbo (~7GB)\n"
         "huggingface.co/Lykon/\n"
         "  dreamshaper-xl-v2-turbo\n\n"
         "[12GB VRAM - Recommended]\n"
         "JuggernautXL v11 (~7GB) BEST\n"
         "huggingface.co/RunDiffusion/\n"
         "  Juggernaut-XI-v11\n\n"
         "RealVisXL V5.0 (~7GB)\n"
         "huggingface.co/SG161222/\n"
         "  RealVisXL_V5.0\n\n"
         "[24GB VRAM - Premium]\n"
         "FLUX.1-dev fp8 (~17GB)\n"
         "huggingface.co/Comfy-Org/\n"
         "  flux1-dev\n"
         "  File: flux1-dev-fp8.safetensors\n\n"
         "FLUX.1-dev fp16 (~23GB)\n"
         "huggingface.co/\n"
         "  black-forest-labs/FLUX.1-dev\n"
         "  (Gated - accept license first)",
         title="Checkpoint Models",
         color="#442", bgcolor="#663")

    # --- IPAdapter + CLIP Vision Guide ---
    note(w, 802, [50, 1240], [340, 380],
         "=== IPADAPTER MODELS ===\n"
         "Folder: models/ipadapter/\n\n"
         "For SDXL (recommended):\n"
         "ip-adapter-plus_sdxl_vit-h\n"
         "  .safetensors (~848MB)\n"
         "huggingface.co/h94/IP-Adapter/\n"
         "  resolve/main/sdxl_models/\n\n"
         "For SD1.5:\n"
         "ip-adapter-plus_sd15\n"
         "  .safetensors (~98MB)\n"
         "huggingface.co/h94/IP-Adapter/\n"
         "  resolve/main/models/\n\n"
         "=== CLIP VISION MODELS ===\n"
         "Folder: models/clip_vision/\n\n"
         "For SDXL: (~3.7GB)\n"
         "CLIP-ViT-bigG-14-laion2B\n"
         "huggingface.co/shiertier/\n"
         "  clip_vision\n\n"
         "For SD1.5: (~2.5GB)\n"
         "CLIP-ViT-H-14-laion2B\n"
         "huggingface.co/h94/IP-Adapter/\n"
         "  resolve/main/models/\n"
         "  image_encoder/model.safetensors",
         title="IPAdapter & CLIP Vision",
         color="#244", bgcolor="#366")

    # --- Face Swap Models Guide ---
    note(w, 803, [50, 1640], [340, 300],
         "=== FACE SWAP MODELS ===\n\n"
         "inswapper_128.onnx (~554MB)\n"
         "Folder: models/insightface/\n"
         "huggingface.co/datasets/\n"
         "  Gourieff/ReActor/resolve/\n"
         "  main/models/\n"
         "  inswapper_128.onnx\n\n"
         "codeformer-v0.1.0.pth (~377MB)\n"
         "Folder: models/facerestore_models/\n"
         "huggingface.co/datasets/\n"
         "  Gourieff/ReActor/resolve/\n"
         "  main/models/facerestore_models/\n\n"
         "GFPGANv1.4.pth (~349MB)\n"
         "Same folder as codeformer\n"
         "Same HuggingFace repo",
         title="Face Swap Models",
         color="#424", bgcolor="#646")

    # --- Upscale Models Guide ---
    note(w, 804, [50, 1960], [340, 220],
         "=== UPSCALE MODELS ===\n"
         "Folder: models/upscale_models/\n\n"
         "4x-UltraSharp.pth (~67MB)\n"
         "RECOMMENDED - sharpest results\n"
         "huggingface.co/uwg/upscaler/\n"
         "  resolve/main/ESRGAN/\n"
         "  4x-UltraSharp.pth\n\n"
         "RealESRGAN_x4plus.pth (~67MB)\n"
         "Alternative - smoother\n"
         "huggingface.co/alexgenovese/\n"
         "  upscalers/resolve/main/\n"
         "  RealESRGAN_x4plus.pth",
         title="Upscale Models",
         color="#242", bgcolor="#464")

    # --- Video Models Guide ---
    note(w, 805, [50, 2200], [340, 300],
         "=== VIDEO MODELS ===\n"
         "Folder: models/diffusion_models/\n\n"
         "[12GB] Wan 2.1 1.3B (~2.8GB)\n"
         "huggingface.co/Comfy-Org/\n"
         "  Wan_2.1_ComfyUI_repackaged\n"
         "  File: wan2.1_t2v_1.3B_bf16\n\n"
         "[24GB] Wan 2.1 14B (~28GB)\n"
         "Same repo, larger model\n"
         "  File: wan2.1_t2v_14B_bf16\n\n"
         "Text Encoder (~6.7GB):\n"
         "  umt5_xxl_fp8_e4m3fn_scaled\n"
         "  Folder: models/text_encoders/\n\n"
         "VAE (~254MB):\n"
         "  wan_2.1_vae.safetensors\n"
         "  Folder: models/vae/",
         title="Video Models (Wan 2.1)",
         color="#234", bgcolor="#456")

    # --- FLUX VAE + Extras ---
    note(w, 806, [50, 2520], [340, 220],
         "=== FLUX VAE ===\n"
         "ae.safetensors (~335MB)\n"
         "Folder: models/vae/\n"
         "huggingface.co/\n"
         "  black-forest-labs/\n"
         "  FLUX.1-schnell/resolve/\n"
         "  main/ae.safetensors\n\n"
         "=== BACKGROUND REMOVAL ===\n"
         "RMBG-2.0: Auto-downloads\n"
         "on first use (no action needed)\n\n"
         "=== LORAS ===\n"
         "Use any LoRA compatible with\n"
         "your checkpoint model.\n"
         "Load up to 3 in LoRA Stack.",
         title="VAE, RMBG & LoRAs",
         color="#324", bgcolor="#546")

    # --- Aspect Ratio Guide ---
    label(w, 807, [50, 2760], [340, 40],
          "ASPECT RATIO & RESOLUTION GUIDE",
          font_size=18, font_color="#FFFFFF", bg_color="#116644",
          align="center", padding=8)

    note(w, 808, [50, 2820], [340, 280],
         "=== ASPECT RATIOS ===\n"
         "Set in EmptyLatentImage nodes:\n\n"
         "1:1  = 1024 x 1024 (Square)\n"
         "4:5  = 896  x 1120 (Instagram)\n"
         "2:3  = 832  x 1248 (Portrait)\n"
         "9:16 = 720  x 1280 (TikTok)\n"
         "3:4  = 896  x 1152 (Portrait)\n"
         "16:9 = 1280 x 720  (YouTube)\n"
         "4:3  = 1152 x 896  (Landscape)\n\n"
         "=== UPSCALE TARGETS ===\n"
         "From 1024px base:\n"
         "  2X = target_resolution 2048\n"
         "  4X = target_resolution 4096\n"
         "  8X = target_resolution 8192\n\n"
         "Tip: Higher upscale = more VRAM.\n"
         "Use 2X for 8GB, 4X for 12GB+.",
         title="Ratios & Upscale Targets",
         color="#243", bgcolor="#465")

    # --- How to Use Guide ---
    label(w, 809, [50, 3120], [340, 40],
          "HOW TO USE THIS WORKFLOW",
          font_size=18, font_color="#FFFFFF", bg_color="#664411",
          align="center", padding=8)

    note(w, 810, [50, 3180], [340, 460],
         "=== QUICK START ===\n\n"
         "1. Select checkpoint model in\n"
         "   Universal Model Loader\n\n"
         "2. (Optional) Add LoRAs in\n"
         "   the LoRA Stack\n\n"
         "3. Upload FACE image (for swap)\n\n"
         "4. Upload BODY image (person\n"
         "   to dress)\n\n"
         "5. Upload clothing images:\n"
         "   Hat, Top, Pants, Shoes, etc.\n"
         "   MUTE unused slots!\n"
         "   (Right-click > Mute Node)\n\n"
         "6. Edit Person Prompt and\n"
         "   Background Prompt\n\n"
         "7. Click Queue Prompt!\n\n"
         "=== TOGGLE SYSTEM ===\n"
         "Use the TOGGLE PANEL (top-left)\n"
         "to enable/disable sections:\n"
         "- Click group name to toggle\n"
         "- Green = active, Gray = off\n"
         "- Inpainting, Outpainting,\n"
         "  Upscaling, Video start OFF\n"
         "- Toggle ON only what you need\n\n"
         "=== SAVE CHECKPOINTS ===\n"
         "Each section saves its output.\n"
         "Check output/ folder for results.",
         title="Usage Instructions",
         color="#432", bgcolor="#653")

    # ══════════════════════════════════════════════════════════════════
    # GROUP 1: MODEL SETUP
    # ══════════════════════════════════════════════════════════════════
    w.n(1, "UniversalModelLoader", [450, 50], [320, 140],
        title="Universal Model Loader", widgets=["", "auto"],
        color="#223", bgcolor="#335")
    w.o(1, "MODEL", "MODEL")
    w.o(1, "CLIP", "CLIP")
    w.o(1, "VAE", "VAE")
    w.o(1, "detected_type", "STRING")

    w.n(2, "MultiLoraStack", [450, 250], [320, 180],
        title="LoRA Stack (3 Slots)", widgets=["", 1.0, "", 1.0, "", 1.0],
        color="#223", bgcolor="#335")
    w.i(2, "model", "MODEL")
    w.i(2, "clip", "CLIP")
    w.o(2, "MODEL", "MODEL")
    w.o(2, "CLIP", "CLIP")

    w.n(3, "IPAdapterUnifiedLoader", [450, 490], [320, 100],
        title="IPAdapter Loader (PLUS)", widgets=["PLUS (high strength)"],
        color="#232", bgcolor="#353")
    w.i(3, "model", "MODEL")
    w.o(3, "model", "MODEL")
    w.o(3, "ipadapter", "IPADAPTER")

    note(w, 902, [450, 640], [320, 100],
         "Select checkpoint model above.\n"
         "Add up to 3 LoRAs (optional).\n"
         "IPAdapter transfers clothing\n"
         "styles from reference photos.",
         title="Model Setup Guide")

    w.L(1, 0, 2, 0, "MODEL")
    w.L(1, 1, 2, 1, "CLIP")
    w.L(2, 0, 3, 0, "MODEL")

    # ══════════════════════════════════════════════════════════════════
    # GROUP 2: PROMPTS
    # ══════════════════════════════════════════════════════════════════
    w.n(6, "CLIPTextEncode", [830, 50], [380, 160],
        title="Person Prompt (Positive)",
        widgets=["a woman, full body, standing, professional fashion photo, studio lighting, 8k, sharp focus"],
        color="#131", bgcolor="#242")
    w.i(6, "clip", "CLIP")
    w.o(6, "CONDITIONING", "CONDITIONING")

    w.n(7, "CLIPTextEncode", [830, 270], [380, 160],
        title="Negative Prompt",
        widgets=["nsfw, naked, nude, deformed, semi-realistic, cgi, 3d, render, sketch, cartoon, anime, mutated hands, bad anatomy, wrong anatomy, extra limb, missing limb, ugly, text, logo, watermark"],
        color="#311", bgcolor="#422")
    w.i(7, "clip", "CLIP")
    w.o(7, "CONDITIONING", "CONDITIONING")

    w.n(8, "CLIPTextEncode", [830, 490], [380, 160],
        title="Background Prompt (Positive)",
        widgets=["photo studio, clean white cyclorama, professional backdrop, soft lighting"],
        color="#131", bgcolor="#242")
    w.i(8, "clip", "CLIP")
    w.o(8, "CONDITIONING", "CONDITIONING")

    note(w, 903, [830, 700], [380, 80],
         "Edit prompts to describe your scene.\n"
         "Be specific: pose, clothing style, lighting.\n"
         "Background prompt generates the backdrop.",
         title="Prompt Guide")

    w.L(2, 1, 6, 0, "CLIP")
    w.L(2, 1, 7, 0, "CLIP")
    w.L(2, 1, 8, 0, "CLIP")

    # ══════════════════════════════════════════════════════════════════
    # GROUP 3: FACE PREPARATION
    # ══════════════════════════════════════════════════════════════════
    w.n(9, "LoadImage", [1280, 50], [260, 320],
        title="Face Image", widgets=[""],
        color="#326", bgcolor="#437")
    w.o(9, "IMAGE", "IMAGE")
    w.o(9, "MASK", "MASK")

    w.n(10, "ConstrainResolution", [1280, 420], [280, 200],
        title="Constrain (Face)",
        widgets=[512, 1024, 2, "Prioritize Max Resolution (Strict)", True, "center"],
        color="#223", bgcolor="#335")
    w.i(10, "image", "IMAGE")
    w.o(10, "resized_image", "IMAGE")
    w.o(10, "original_image", "IMAGE")
    w.o(10, "width", "INT")
    w.o(10, "height", "INT")

    w.n(11, "AutoCropFaces", [1280, 680], [280, 240],
        title="Auto Crop Faces", widgets=[1, 1.9, 0.60, 0, 50, "4:5"],
        color="#223", bgcolor="#335")
    w.i(11, "image", "IMAGE")
    w.o(11, "face", "IMAGE")
    w.o(11, "crop_data", "CROP_DATA")

    preview(w, 12, [1280, 980], "Cropped Face Preview")

    note(w, 904, [1610, 50], [220, 140],
         "Upload clear face photo.\n"
         "Auto-crop detects the\n"
         "face for swap later.\n\n"
         "Change aspect_ratio in\n"
         "AutoCropFaces for\n"
         "different crops:\n"
         "9:16, 4:5, 1:1, 3:2",
         title="Face Guide")

    w.L(9, 0, 10, 0, "IMAGE")
    w.L(10, 0, 11, 0, "IMAGE")
    w.L(11, 0, 12, 0, "IMAGE")

    # ══════════════════════════════════════════════════════════════════
    # GROUP 4: BACKGROUND GENERATION
    # ══════════════════════════════════════════════════════════════════
    w.n(13, "EmptyLatentImage", [1280, 1340], [260, 120],
        title="Background Latent (704x1280)", widgets=[704, 1280, 1],
        color="#223", bgcolor="#335")
    w.o(13, "LATENT", "LATENT")

    w.n(14, "KSampler", [1280, 1520], [300, 300],
        title="Background KSampler",
        widgets=[616089985860999, "fixed", 20, 8.0, "euler", "normal", 1.00],
        color="#223", bgcolor="#335")
    w.i(14, "model", "MODEL")
    w.i(14, "positive", "CONDITIONING")
    w.i(14, "negative", "CONDITIONING")
    w.i(14, "latent_image", "LATENT")
    w.o(14, "LATENT", "LATENT")

    w.n(15, "VAEDecode", [1640, 1520], [200, 80],
        title="VAE Decode Background", color="#223", bgcolor="#335")
    w.i(15, "samples", "LATENT")
    w.i(15, "vae", "VAE")
    w.o(15, "IMAGE", "IMAGE")

    preview(w, 16, [1640, 1660], "Background Preview")

    note(w, 905, [1640, 1340], [200, 120],
         "Generates AI background.\n"
         "Change seed for variety.\n"
         "Edit Background Prompt\n"
         "to customize the scene.\n"
         "Adjust width/height in\n"
         "EmptyLatentImage.",
         title="Background Guide")

    w.L(3, 0, 14, 0, "MODEL")
    w.L(8, 0, 14, 1, "CONDITIONING")
    w.L(7, 0, 14, 2, "CONDITIONING")
    w.L(13, 0, 14, 3, "LATENT")
    w.L(14, 0, 15, 0, "LATENT")
    w.L(1, 2, 15, 1, "VAE")
    w.L(15, 0, 16, 0, "IMAGE")

    # ══════════════════════════════════════════════════════════════════
    # GROUP 5: BODY / MODEL IMAGE
    # ══════════════════════════════════════════════════════════════════
    w.n(17, "AILab_LoadImage", [1920, 50], [280, 380],
        title="Model Image (Person to Dress)",
        widgets=["", "", "lanczos", 0.0, 1.0, "longest_side", 0],
        color="#326", bgcolor="#437")
    w.o(17, "IMAGE", "IMAGE")
    w.o(17, "MASK", "MASK")
    w.o(17, "WIDTH", "INT")
    w.o(17, "HEIGHT", "INT")

    w.n(18, "ConstrainResolution", [1920, 490], [280, 200],
        title="Auto Crop (Body Ratio)",
        widgets=[704, 1280, 2, "Prioritize Max Resolution (Strict)", True, "center"],
        color="#223", bgcolor="#335")
    w.i(18, "image", "IMAGE")
    w.o(18, "resized_image", "IMAGE")
    w.o(18, "original_image", "IMAGE")
    w.o(18, "width", "INT")
    w.o(18, "height", "INT")

    note(w, 906, [1920, 740], [280, 140],
         "Upload body/person to dress.\n"
         "Auto Crop adjusts ratio:\n"
         " 9:16 = min 720, max 1280\n"
         " 1:1  = min 1024, max 1024\n"
         " 16:9 = min 720, max 1280\n"
         "Change min_res/max_res.",
         title="Body Image Guide")

    w.L(17, 0, 18, 0, "IMAGE")

    # ══════════════════════════════════════════════════════════════════
    # GROUP 6: CLOTHING SLOTS (10 items)
    # ══════════════════════════════════════════════════════════════════
    SLOTS = [
        ("HAT",        [0],      "#623", "#734"),
        ("SUNGLASSES", [3],      "#362", "#473"),
        ("TOP (Shirt/Blouse)", [4], "#326", "#437"),
        ("DRESS",      [6],      "#632", "#743"),
        ("SKIRT",      [5],      "#263", "#374"),
        ("PANTS",      [8],      "#236", "#347"),
        ("BELT",       [7],      "#623", "#734"),
        ("SCARF",      [14],     "#362", "#473"),
        ("BAG",        [13],     "#326", "#437"),
        ("SHOES",      [15, 16], "#263", "#374"),
    ]

    load_ids, seg_ids, ipa_ids = [], [], []
    x_ld, x_sg, x_ip = 2300, 2650, 3050
    y_sp = 600

    for idx, (lbl, si, clr, bg) in enumerate(SLOTS):
        y = 50 + idx * y_sp
        lid = 100 + idx * 3
        sid = 100 + idx * 3 + 1
        iid = 100 + idx * 3 + 2
        load_ids.append(lid)
        seg_ids.append(sid)
        ipa_ids.append(iid)

        w.n(lid, "LoadImage", [x_ld, y], [260, 280],
            title=lbl, widgets=[""], color=clr, bgcolor=bg)
        w.o(lid, "IMAGE", "IMAGE")
        w.o(lid, "MASK", "MASK")

        w.n(sid, "ClothesSegment", [x_sg, y], [300, 550],
            title=f"Segment: {lbl}", widgets=seg_w(si),
            color="#326", bgcolor="#437")
        w.i(sid, "images", "IMAGE")
        w.o(sid, "IMAGE", "IMAGE")
        w.o(sid, "MASK", "MASK")
        w.o(sid, "MASK_IMAGE", "IMAGE")

        w.n(iid, "IPAdapterAdvanced", [x_ip, y + 50], [320, 340],
            title=f"IPAdapter: {lbl}",
            widgets=[1.00, "linear", "concat", 0.000, 1.000, "K+V"],
            color=clr, bgcolor=bg)
        w.i(iid, "model", "MODEL")
        w.i(iid, "ipadapter", "IPADAPTER")
        w.i(iid, "image", "IMAGE")
        w.i(iid, "image_negative", "IMAGE")
        w.i(iid, "attn_mask", "MASK")
        w.i(iid, "clip_vision", "CLIP_VISION")
        w.o(iid, "MODEL", "MODEL")

        w.L(18, 0, sid, 0, "IMAGE")
        w.L(lid, 0, iid, 2, "IMAGE")
        w.L(sid, 1, iid, 4, "MASK")
        w.L(3, 1, iid, 1, "IPADAPTER")

    w.L(3, 0, ipa_ids[0], 0, "MODEL")
    for idx in range(1, len(ipa_ids)):
        w.L(ipa_ids[idx-1], 0, ipa_ids[idx], 0, "MODEL")

    note(w, 907, [x_ld, 50 + len(SLOTS) * y_sp], [600, 130],
         "Upload reference clothing photos. MUTE unused slots!\n"
         "Right-click any node > Mute (or Ctrl+M on selected nodes).\n"
         "Each item's style transfers via IPAdapter with body-region mask.\n"
         "Chain order: Hat > Sunglasses > Top > Dress > ... > Shoes.",
         title="Clothing Slots Guide")

    # ══════════════════════════════════════════════════════════════════
    # GROUP 7: GENERATE DRESSED PERSON
    # ══════════════════════════════════════════════════════════════════
    GX = 3450
    w.n(50, "EmptyLatentImage", [GX, 50], [260, 120],
        title="Person Latent (704x1280)", widgets=[704, 1280, 1])
    w.o(50, "LATENT", "LATENT")

    w.n(51, "KSampler", [GX, 230], [300, 300],
        title="Main KSampler (Dressed Person)",
        widgets=[42, "fixed", 20, 8.0, "euler", "normal", 1.00],
        color="#223", bgcolor="#335")
    w.i(51, "model", "MODEL")
    w.i(51, "positive", "CONDITIONING")
    w.i(51, "negative", "CONDITIONING")
    w.i(51, "latent_image", "LATENT")
    w.o(51, "LATENT", "LATENT")

    w.n(52, "VAEDecode", [GX + 360, 230], [200, 80],
        title="VAE Decode Person")
    w.i(52, "samples", "LATENT")
    w.i(52, "vae", "VAE")
    w.o(52, "IMAGE", "IMAGE")

    preview(w, 53, [GX + 360, 370], "Dressed Person Preview")

    note(w, 908, [GX, 590], [560, 80],
         "Generates dressed person using all enabled clothing styles.\n"
         "Change seed for different poses. Adjust steps (20-30) and CFG (6-8).",
         title="Generation Guide")

    w.L(ipa_ids[-1], 0, 51, 0, "MODEL")
    w.L(6, 0, 51, 1, "CONDITIONING")
    w.L(7, 0, 51, 2, "CONDITIONING")
    w.L(50, 0, 51, 3, "LATENT")
    w.L(51, 0, 52, 0, "LATENT")
    w.L(1, 2, 52, 1, "VAE")
    w.L(52, 0, 53, 0, "IMAGE")

    # ══════════════════════════════════════════════════════════════════
    # GROUP 8: FACE SWAP
    # ══════════════════════════════════════════════════════════════════
    FX = 4100
    w.n(54, "ReActorFaceSwap", [FX, 50], [340, 400],
        title="ReActor Face Swap",
        widgets=[True, "inswapper_128.onnx", "YOLOv5l",
                 "codeformer-v0.1.0.pth", 1.00, 0.50,
                 "no", "no", "0", "0", 1],
        color="#632", bgcolor="#743")
    w.i(54, "input_image", "IMAGE")
    w.i(54, "source_image", "IMAGE")
    w.i(54, "face_model", "FACE_MODEL")
    w.i(54, "face_boost", "FACE_BOOST")
    w.o(54, "SWAPPED_IMAGE", "IMAGE")
    w.o(54, "FACE_MODEL", "FACE_MODEL")
    w.o(54, "ORIGINAL_IMAGE", "IMAGE")

    preview(w, 55, [FX, 510], "Face Swap Preview")
    save_img(w, 56, [FX, 870], "checkpoint/face_swap")

    note(w, 909, [FX + 350, 50], [200, 160],
         "Swaps AI face with your\n"
         "uploaded face photo.\n\n"
         "Models needed:\n"
         "- inswapper_128.onnx\n"
         "- codeformer-v0.1.0.pth\n\n"
         "Adjust restore strength\n"
         "(0.5 = natural,\n"
         " 1.0 = maximum fix)",
         title="Face Swap Guide")

    w.L(52, 0, 54, 0, "IMAGE")
    w.L(9, 0, 54, 1, "IMAGE")
    w.L(54, 0, 55, 0, "IMAGE")
    w.L(54, 0, 56, 0, "IMAGE")

    # ══════════════════════════════════════════════════════════════════
    # GROUP 9: BACKGROUND COMPOSITE
    # ══════════════════════════════════════════════════════════════════
    BX = 4550
    w.n(57, "RMBG", [BX, 50], [320, 320],
        title="Remove Background (RMBG)",
        widgets=["RMBG-2.0", 1.00, 1024, 0, 0, False, True, "Alpha", "#222222"],
        color="#326", bgcolor="#437")
    w.i(57, "image", "IMAGE")
    w.o(57, "image", "IMAGE")
    w.o(57, "mask", "MASK")
    w.o(57, "mask_image", "IMAGE")

    w.n(58, "ImageCompositeMasked", [BX, 430], [320, 200],
        title="Composite onto Background", widgets=[0, 0, False],
        color="#232", bgcolor="#353")
    w.i(58, "destination", "IMAGE")
    w.i(58, "source", "IMAGE")
    w.i(58, "mask", "MASK")
    w.o(58, "IMAGE", "IMAGE")

    preview(w, 59, [BX + 380, 50], "Mask Preview")
    preview(w, 60, [BX + 380, 430], "COMPOSITE OUTPUT")
    save_img(w, 61, [BX + 380, 790], "checkpoint/composite")

    note(w, 910, [BX, 690], [320, 80],
         "Removes background (RMBG-2.0) and composites\n"
         "the person onto the AI-generated background.",
         title="Composite Guide")

    w.L(54, 0, 57, 0, "IMAGE")
    w.L(57, 0, 58, 1, "IMAGE")
    w.L(57, 1, 58, 2, "MASK")
    w.L(15, 0, 58, 0, "IMAGE")
    w.L(57, 2, 59, 0, "IMAGE")
    w.L(58, 0, 60, 0, "IMAGE")
    w.L(58, 0, 61, 0, "IMAGE")

    # ══════════════════════════════════════════════════════════════════
    # GROUP 10: INPAINTING (bypassed)
    # ══════════════════════════════════════════════════════════════════
    IX = 5350
    BY = 4

    w.n(62, "SmartMaskGenerator", [IX, 50], [320, 200],
        title="Smart Mask (Text-Guided)",
        widgets=["area to fix", "text_detect", 0.3, 5, False],
        color="#623", bgcolor="#734", mode=BY)
    w.i(62, "image", "IMAGE")
    w.o(62, "mask", "MASK")
    w.o(62, "preview", "IMAGE")

    w.n(63, "LauraInpainter", [IX, 310], [320, 360],
        title="Inpainter",
        widgets=["fix this area, high quality, detailed", 42, 20, 8.0, 0.75, "", 8],
        color="#623", bgcolor="#734", mode=BY)
    w.i(63, "model", "MODEL")
    w.i(63, "clip", "CLIP")
    w.i(63, "vae", "VAE")
    w.i(63, "image", "IMAGE")
    w.i(63, "mask", "MASK")
    w.o(63, "IMAGE", "IMAGE")

    preview(w, 64, [IX, 730], "Inpainting Result", mode=BY)
    save_img(w, 65, [IX, 1090], "checkpoint/inpaint", mode=BY)

    note(w, 911, [IX + 340, 50], [230, 200],
         "INPAINTING: Fix specific\n"
         "areas of the image.\n\n"
         "1. Type what to detect:\n"
         "   e.g. 'hand', 'face',\n"
         "   'wrinkle', 'artifact'\n"
         "2. Describe the fix in\n"
         "   Inpainter prompt\n"
         "3. Denoise: 0.5-0.8\n"
         "   (lower = subtle fix,\n"
         "    higher = more change)\n\n"
         "BYPASSED by default.\n"
         "Toggle ON in panel.",
         title="Inpainting Guide",
         color="#623", bgcolor="#734")

    w.L(58, 0, 62, 0, "IMAGE")
    w.L(58, 0, 63, 3, "IMAGE")
    w.L(62, 0, 63, 4, "MASK")
    w.L(2, 0, 63, 0, "MODEL")
    w.L(2, 1, 63, 1, "CLIP")
    w.L(1, 2, 63, 2, "VAE")
    w.L(63, 0, 64, 0, "IMAGE")
    w.L(63, 0, 65, 0, "IMAGE")

    # ══════════════════════════════════════════════════════════════════
    # GROUP 11: OUTPAINTING (bypassed)
    # ══════════════════════════════════════════════════════════════════
    OX = 5700
    w.n(66, "LauraOutpainter", [OX, 50], [320, 380],
        title="Outpainter (Extend Image)",
        widgets=["all", 128,
                 "continue the scene naturally, high quality",
                 42, 20, 8.0, 0.85, "", 32],
        color="#362", bgcolor="#473", mode=BY)
    w.i(66, "model", "MODEL")
    w.i(66, "clip", "CLIP")
    w.i(66, "vae", "VAE")
    w.i(66, "image", "IMAGE")
    w.o(66, "IMAGE", "IMAGE")
    w.o(66, "new_width", "INT")
    w.o(66, "new_height", "INT")

    preview(w, 67, [OX, 490], "Outpainting Result", mode=BY)
    save_img(w, 68, [OX, 850], "checkpoint/outpaint", mode=BY)

    note(w, 912, [OX + 340, 50], [220, 180],
         "OUTPAINTING: Extend\n"
         "image beyond borders.\n\n"
         "Direction options:\n"
         "  all, top, bottom,\n"
         "  left, right,\n"
         "  top-bottom,\n"
         "  left-right\n\n"
         "Pixels: how much\n"
         "to extend (64-256)\n\n"
         "BYPASSED by default.\n"
         "Toggle ON in panel.",
         title="Outpainting Guide",
         color="#362", bgcolor="#473")

    w.L(63, 0, 66, 3, "IMAGE")
    w.L(2, 0, 66, 0, "MODEL")
    w.L(2, 1, 66, 1, "CLIP")
    w.L(1, 2, 66, 2, "VAE")
    w.L(66, 0, 67, 0, "IMAGE")
    w.L(66, 0, 68, 0, "IMAGE")

    # ══════════════════════════════════════════════════════════════════
    # GROUP 12: UPSCALING (bypassed)
    # ══════════════════════════════════════════════════════════════════
    UX = 6100
    w.n(69, "UpscaleModelLoader", [UX, 50], [260, 80],
        title="Load Upscale Model", widgets=[""],
        color="#223", bgcolor="#335", mode=BY)
    w.o(69, "UPSCALE_MODEL", "UPSCALE_MODEL")

    w.n(70, "UpscaleChain", [UX, 190], [320, 300],
        title="Upscale (2K/4K/8K)",
        widgets=[4096, 0, 0, 2, "realesrgan", 0.3],
        color="#223", bgcolor="#335", mode=BY)
    w.i(70, "image", "IMAGE")
    w.i(70, "upscale_model", "UPSCALE_MODEL")
    w.o(70, "IMAGE", "IMAGE")
    w.o(70, "width", "INT")
    w.o(70, "height", "INT")

    preview(w, 71, [UX, 550], "Upscaled Result", mode=BY)
    save_img(w, 72, [UX, 910], "checkpoint/upscaled", mode=BY)

    note(w, 913, [UX + 340, 50], [220, 220],
         "UPSCALING: Boost res.\n\n"
         "Target presets:\n"
         "  2048 = ~2X (8GB OK)\n"
         "  4096 = ~4X (12GB+)\n"
         "  8192 = ~8X (24GB+)\n\n"
         "Model needed:\n"
         "4x-UltraSharp.pth\n"
         "  or RealESRGAN_x4plus\n"
         "Folder: upscale_models/\n\n"
         "BYPASSED by default.\n"
         "Toggle ON in panel.",
         title="Upscaling Guide",
         color="#223", bgcolor="#335")

    w.L(66, 0, 70, 0, "IMAGE")
    w.L(69, 0, 70, 1, "UPSCALE_MODEL")
    w.L(70, 0, 71, 0, "IMAGE")
    w.L(70, 0, 72, 0, "IMAGE")

    # ══════════════════════════════════════════════════════════════════
    # GROUP 13: VIDEO GENERATION (bypassed)
    # ══════════════════════════════════════════════════════════════════
    VX = 6500
    w.n(73, "ImageToVideo", [VX, 50], [320, 400],
        title="Image to Video",
        widgets=["fashion model walking, smooth motion", "",
                 16, 8, 42, 20, 7.0, 0.5, "wan22_video"],
        color="#236", bgcolor="#347", mode=BY)
    w.i(73, "image", "IMAGE")
    w.i(73, "model", "MODEL")
    w.i(73, "clip", "CLIP")
    w.i(73, "vae", "VAE")
    w.o(73, "frames", "IMAGE")
    w.o(73, "frame_count", "INT")
    w.o(73, "fps", "INT")

    w.n(74, "VideoSaver", [VX, 510], [320, 200],
        title="Save Video",
        widgets=["dressing_room_video", 8, "mp4", "high", False],
        color="#236", bgcolor="#347", mode=BY)
    w.i(74, "frames", "IMAGE")
    w.o(74, "video_path", "STRING")

    preview(w, 75, [VX + 380, 50], "Video Frames Preview", mode=BY)

    note(w, 914, [VX, 770], [320, 200],
         "VIDEO: Generate from image.\n\n"
         "Models needed (diffusion_models/):\n"
         "[12GB] wan2.1_t2v_1.3B (~2.8GB)\n"
         "[24GB] wan2.1_t2v_14B (~28GB)\n\n"
         "Also need (text_encoders/):\n"
         "umt5_xxl_fp8 (~6.7GB)\n\n"
         "VAE (vae/):\n"
         "wan_2.1_vae.safetensors\n\n"
         "BYPASSED by default.\n"
         "Toggle ON in panel.",
         title="Video Guide",
         color="#236", bgcolor="#347")

    # Linear chain: upscaler → video
    w.L(70, 0, 73, 0, "IMAGE")
    w.L(2, 0, 73, 1, "MODEL")
    w.L(2, 1, 73, 2, "CLIP")
    w.L(1, 2, 73, 3, "VAE")
    w.L(73, 0, 74, 0, "IMAGE")
    w.L(73, 0, 75, 0, "IMAGE")

    # ══════════════════════════════════════════════════════════════════
    # GROUP 14: FINAL OUTPUT
    # ══════════════════════════════════════════════════════════════════
    FX2 = 7000
    preview(w, 80, [FX2, 50], "FINAL IMAGE")
    save_img(w, 81, [FX2, 410], "final/output")

    note(w, 915, [FX2, 550], [300, 130],
         "Final output saves automatically.\n"
         "  output/final/ = final result\n"
         "  output/checkpoint/ = per-stage\n\n"
         "The final image reflects all\n"
         "active (non-bypassed) sections.",
         title="Output Guide")

    w.L(70, 0, 80, 0, "IMAGE")
    w.L(70, 0, 81, 0, "IMAGE")

    # ══════════════════════════════════════════════════════════════════
    # GROUPS
    # ══════════════════════════════════════════════════════════════════
    w.g("CONTROL PANEL", [30, 10, 380, 680], "#557")
    w.g("GUIDES & DOWNLOADS",
        [30, 700, 380, 2960], "#663")
    w.g("1. MODEL SETUP",
        [430, 10, 370, 780], "#335")
    w.g("2. PROMPTS",
        [810, 10, 420, 830], "#242")
    w.g("3. FACE PREPARATION",
        [1260, 10, 600, 1280], "#437")
    w.g("4. BACKGROUND GENERATION",
        [1260, 1300, 620, 680], "#353")
    w.g("5. BODY / MODEL IMAGE",
        [1900, 10, 330, 930], "#437")
    w.g("6. CLOTHING ITEMS (Mute Unused Slots)",
        [2280, 10, 1120, 50 + len(SLOTS) * y_sp + 160], "#734")
    w.g("7. GENERATE DRESSED PERSON",
        [3430, 10, 600, 720], "#335")
    w.g("8. FACE SWAP",
        [4080, 10, 480, 1000], "#743")
    w.g("9. BACKGROUND COMPOSITE",
        [4530, 10, 730, 830], "#353")
    w.g("10. INPAINTING (Toggle ON to use)",
        [5330, 10, 570, 1250], "#734")
    w.g("11. OUTPAINTING (Toggle ON to use)",
        [5680, 10, 510, 1080], "#473")
    w.g("12. UPSCALING (Toggle ON to use)",
        [6080, 10, 510, 1180], "#335")
    w.g("13. VIDEO GENERATION (Toggle ON to use)",
        [6480, 10, 730, 1020], "#347")
    w.g("14. FINAL OUTPUT",
        [6980, 10, 340, 730], "#242")

    return w.build()


if __name__ == "__main__":
    wf = build()
    path = "workflows/virtual_dressing_room.json"
    with open(path, "w") as f:
        json.dump(wf, f, indent=2)
    nn = len(wf["nodes"])
    nl = len(wf["links"])
    ng = len(wf["groups"])
    types = {}
    for n in wf["nodes"]:
        types[n["type"]] = types.get(n["type"], 0) + 1
    print(f"Generated: {path}")
    print(f"  Nodes: {nn}, Links: {nl}, Groups: {ng}")
    print(f"  Note nodes: {types.get('Note', 0)}")
    print(f"  Label (rgthree) sticky notes: {types.get('Label (rgthree)', 0)}")
    print(f"  Bypassed: {sum(1 for n in wf['nodes'] if n['mode']==4)}")
