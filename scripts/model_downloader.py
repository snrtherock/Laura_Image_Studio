"""
Laura Image Studio - Model Synchronization Script
Automate the downloading of required SOTA models and VAEs for 2026.
"""

import os
import sys
import argparse
from huggingface_hub import hf_hub_download

# Base directories (Update if needed)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
CHECKPOINTS_DIR = os.path.join(MODELS_DIR, "checkpoints")
VAE_DIR = os.path.join(MODELS_DIR, "vae")
CLIP_DIR = os.path.join(MODELS_DIR, "clip")
LORA_DIR = os.path.join(MODELS_DIR, "loras")

# SOTA Model Registry
MODEL_REGISTRY = {
    "FLUX.1-dev": {
        "repo": "black-forest-labs/FLUX.1-dev",
        "file": "flux1-dev.safetensors",
        "target": CHECKPOINTS_DIR,
    },
    "FLUX.1-schnell": {
        "repo": "black-forest-labs/FLUX.1-schnell",
        "file": "flux1-schnell.safetensors",
        "target": CHECKPOINTS_DIR,
    },
    "Wan-2.2-14B": {
        "repo": "Wan-AI/Wan2.2-14B-T2V",
        "file": "diffusion_pytorch_model.safetensors",
        "target": CHECKPOINTS_DIR,
    },
    "HunyuanVideo": {
        "repo": "tencent/HunyuanVideo",
        "file": "hunyuan_video_v1.0.safetensors",
        "target": CHECKPOINTS_DIR,
    },
    "SD3.5-Medium": {
        "repo": "stabilityai/stable-diffusion-3.5-medium",
        "file": "sd3.5_medium.safetensors",
        "target": CHECKPOINTS_DIR,
    },
    "Cosmos-VAE": {
        "repo": "nvidia/Cosmos-1.0-VAE",
        "file": "cosmos_vae.safetensors",
        "target": VAE_DIR,
    },
    "Flux-VAE": {
        "repo": "black-forest-labs/FLUX.1-dev",
        "file": "ae.safetensors",
        "target": VAE_DIR,
    },
}


def download_model(name):
    if name not in MODEL_REGISTRY:
        print(f"Error: Model '{name}' not found in registry.")
        return False

    config = MODEL_REGISTRY[name]
    repo_id = config["repo"]
    filename = config["file"]
    local_dir = config["target"]

    os.makedirs(local_dir, exist_ok=True)

    print(f"[Laura Studio Sync] Downloading {name} from {repo_id}...")
    try:
        path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
        )
        print(f"Success: {name} downloaded to {path}")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False


def list_registry():
    print("Available SOTA Models in Registry:")
    for name in MODEL_REGISTRY.keys():
        print(f" - {name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Laura Image Studio Model Synchronizer"
    )
    parser.add_argument("--list", action="store_true", help="List available models")
    parser.add_argument(
        "--download", type=str, help="Download a specific model by name"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download ALL core models (Warning: Massive download size!)",
    )

    args = parser.parse_args()

    if args.list:
        list_registry()
    elif args.download:
        download_model(args.download)
    elif args.all:
        for name in MODEL_REGISTRY.keys():
            download_model(name)
    else:
        parser.print_help()
