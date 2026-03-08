"""
Laura Image Studio - Model Synchronization Script
Uses centralized model registry for all model metadata.

Usage:
    python model_downloader.py --list                     # List all models
    python model_downloader.py --list --category image_gen # List image_gen models
    python model_downloader.py --download z_image_turbo   # Download a specific model
    python model_downloader.py --all                      # Download ALL models
    python model_downloader.py --recommend                # VRAM-aware recommendations
    python model_downloader.py --recommend --vram 12      # Override detected VRAM
"""

import os
import sys
import argparse

# ---------------------------------------------------------------------------
# Path setup: allow importing the centralized registry from custom_nodes
# ---------------------------------------------------------------------------
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
_CUSTOM_NODES_DIR = os.path.join(_PROJECT_ROOT, "custom_nodes")

sys.path.insert(0, _CUSTOM_NODES_DIR)

try:
    from Laura_Image_Studio.nodes.model_registry import (
        MODEL_REGISTRY,
        get_all_required_files,
        get_download_url,
        get_recommended_quantization,
        get_models_by_category,
        CATEGORIES,
        VRAM_TIERS,
    )
except ImportError as exc:
    print(f"ERROR: Could not import model registry: {exc}")
    print("Make sure the Laura_Image_Studio custom node is installed under custom_nodes/.")
    sys.exit(1)

from huggingface_hub import hf_hub_download

# ---------------------------------------------------------------------------
# Base model directory (sibling to the scripts/ folder)
# ---------------------------------------------------------------------------
MODELS_DIR = os.path.join(_PROJECT_ROOT, "models")


# ===========================================================================
# Helpers
# ===========================================================================

def _detect_vram_gb():
    """Attempt to detect GPU VRAM using torch.cuda. Returns float or None."""
    try:
        import torch
        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            return round(props.total_mem / (1024 ** 3), 1)
    except Exception:
        pass
    return None


def _vram_to_tier(vram_gb):
    """Map a VRAM value in GB to the appropriate VRAM_TIERS key."""
    for tier_key, tier_info in VRAM_TIERS.items():
        if tier_info["min_gb"] <= vram_gb < tier_info["max_gb"]:
            return tier_key
    # Fallback for values >= 999 (should not happen in practice)
    return "hpc"


def _format_size(size_gb):
    """Return a human-friendly size string."""
    if size_gb >= 1.0:
        return f"{size_gb:.2f} GB"
    return f"{size_gb * 1024:.0f} MB"


# ===========================================================================
# Core actions
# ===========================================================================

def download_model(model_key):
    """Download all required files for a model using huggingface_hub."""
    if model_key not in MODEL_REGISTRY:
        print(f"Error: Model '{model_key}' not found in registry.")
        print("Use --list to see available models.")
        return False

    entry = MODEL_REGISTRY[model_key]
    display_name = entry.get("display_name", model_key)
    status = entry.get("status", "unknown")

    if status == "pending_release":
        print(f"Skipping '{display_name}': status is pending_release (not yet available).")
        return False

    repo = entry.get("repo", "")
    if not repo or repo == "TBD":
        print(f"Skipping '{display_name}': no repository URL available yet.")
        return False

    required_files = get_all_required_files(model_key)
    if not required_files:
        print(f"Skipping '{display_name}': no files listed in registry.")
        return False

    total_size = sum(f["size_gb"] for f in required_files)
    print(f"\n[Laura Studio Sync] Downloading {display_name} ({len(required_files)} file(s), ~{_format_size(total_size)})")
    print(f"  Repository: {repo}")

    success = True
    for file_info in required_files:
        folder = file_info["folder"]
        filename = file_info["filename"]
        size_gb = file_info["size_gb"]

        if not filename:
            continue

        target_dir = os.path.join(MODELS_DIR, folder) if folder else MODELS_DIR
        os.makedirs(target_dir, exist_ok=True)

        print(f"  -> {filename} ({_format_size(size_gb)}) -> {folder}/")
        try:
            path = hf_hub_download(
                repo_id=repo,
                filename=filename,
                local_dir=target_dir,
                local_dir_use_symlinks=False,
            )
            print(f"     OK: {path}")
        except Exception as e:
            print(f"     FAILED: {e}")
            success = False

    return success


def list_registry(category=None):
    """Print models in the registry, optionally filtered by category."""
    if category:
        if category not in CATEGORIES:
            print(f"Error: Unknown category '{category}'.")
            print(f"Valid categories: {', '.join(CATEGORIES.keys())}")
            return
        models = get_models_by_category(category)
        cat_label = CATEGORIES[category]["label"]
        print(f"\nModels in category '{cat_label}':")
    else:
        models = MODEL_REGISTRY
        print(f"\nAll models in registry ({len(models)} total):")

    if not models:
        print("  (none)")
        return

    # Group by category for nicer output
    by_cat = {}
    for key, entry in models.items():
        cat = entry.get("category", "unknown")
        by_cat.setdefault(cat, []).append((key, entry))

    for cat_key in sorted(by_cat.keys()):
        cat_label = CATEGORIES.get(cat_key, {}).get("label", cat_key)
        entries = by_cat[cat_key]
        print(f"\n  [{cat_label}]")
        for key, entry in entries:
            display = entry.get("display_name", key)
            status = entry.get("status", "")
            size = entry.get("total_size_gb", 0)
            params = entry.get("params", "")

            status_tag = f" [{status}]" if status == "pending_release" else ""
            size_str = f" ({_format_size(size)})" if size > 0 else ""
            params_str = f" [{params}]" if params else ""

            print(f"    {key:30s} {display}{params_str}{size_str}{status_tag}")


def recommend(vram_gb=None):
    """Show VRAM-aware model recommendations."""
    if vram_gb is None:
        vram_gb = _detect_vram_gb()

    if vram_gb is None:
        print("Could not detect GPU VRAM. Use --vram <GB> to specify manually.")
        print("Example: python model_downloader.py --recommend --vram 12")
        return

    tier = _vram_to_tier(vram_gb)
    tier_label = VRAM_TIERS.get(tier, {}).get("label", tier)

    print(f"\nVRAM Detected: {vram_gb} GB  ->  Tier: {tier_label}")
    print("=" * 72)
    print(f"{'Model':<30s} {'Quantization':<15s} {'VRAM':<10s} {'Quality':<15s} {'Speed':<6s}")
    print("-" * 72)

    for model_key, entry in MODEL_REGISTRY.items():
        if entry.get("status") == "pending_release":
            continue
        if not entry.get("files"):
            continue

        display = entry.get("display_name", model_key)
        rec_quant = get_recommended_quantization(model_key, tier)

        if rec_quant is None:
            # No recommendation for this tier -- model may not support it
            continue

        variants = entry.get("quantization_variants", {})
        variant_info = variants.get(rec_quant, {})
        q_vram = variant_info.get("vram_gb", "?")
        quality = variant_info.get("quality", "?")
        speed = variant_info.get("speed", "?")

        vram_str = f"{q_vram} GB" if isinstance(q_vram, (int, float)) else str(q_vram)

        print(f"  {display:<28s} {rec_quant:<15s} {vram_str:<10s} {quality:<15s} {speed:<6s}")

    print()
    print("Tip: Use a lower --vram value to see more memory-efficient quantizations.")


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Laura Image Studio - Model Synchronizer (powered by centralized registry)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  %(prog)s --list                          List all registered models
  %(prog)s --list --category image_gen     List only image generation models
  %(prog)s --download z_image_turbo        Download Z-Image Turbo
  %(prog)s --all                           Download ALL released models
  %(prog)s --recommend                     Show VRAM-aware recommendations
  %(prog)s --recommend --vram 8            Recommendations for 8 GB VRAM
""",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List available models in the registry",
    )
    parser.add_argument(
        "--download",
        type=str,
        metavar="MODEL_KEY",
        help="Download a specific model by its registry key",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download ALL released models (Warning: very large download!)",
    )
    parser.add_argument(
        "--recommend",
        action="store_true",
        help="Show VRAM-aware quantization recommendations",
    )
    parser.add_argument(
        "--category",
        type=str,
        metavar="CATEGORY",
        help=f"Filter by category (valid: {', '.join(CATEGORIES.keys())})",
    )
    parser.add_argument(
        "--vram",
        type=float,
        metavar="GB",
        help="Override detected VRAM (in GB) for --recommend",
    )

    args = parser.parse_args()

    if args.list:
        list_registry(category=args.category)
    elif args.download:
        download_model(args.download)
    elif args.all:
        print(f"Downloading all released models from registry ({len(MODEL_REGISTRY)} entries)...")
        successes = 0
        failures = 0
        skipped = 0
        for key in MODEL_REGISTRY:
            entry = MODEL_REGISTRY[key]
            if entry.get("status") == "pending_release" or not entry.get("files"):
                skipped += 1
                continue
            if download_model(key):
                successes += 1
            else:
                failures += 1
        print(f"\nDone. {successes} succeeded, {failures} failed, {skipped} skipped.")
    elif args.recommend:
        recommend(vram_gb=args.vram)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
