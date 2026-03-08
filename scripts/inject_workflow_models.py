"""
Laura Image Studio - Workflow Model Metadata Injector

Scans workflow JSON files for model references and injects a 'models' metadata
block for ComfyUI's native missing-models popup. Each entry includes the model
filename, HuggingFace download URL, target directory, and approximate size.

Usage:
    python scripts/inject_workflow_models.py           # Inject all workflows
    python scripts/inject_workflow_models.py --dry-run  # Preview without writing

Requires: model_registry.py (centralized registry)
"""

import json
import os
import sys
import glob
import argparse

# Add custom_nodes to path so we can import the registry
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_project_root, "custom_nodes"))

try:
    from Laura_Image_Studio.nodes.model_registry import MODEL_REGISTRY
except ImportError:
    print("ERROR: Could not import model_registry. Make sure Laura_Image_Studio is installed.")
    sys.exit(1)


# =============================================================================
# Build a lookup: filename (lowercased) -> model metadata for the workflow JSON
# =============================================================================

def _build_model_patterns():
    """Build a dict mapping lowercased filenames to ComfyUI model metadata blocks."""
    patterns = {}
    for _key, info in MODEL_REGISTRY.items():
        repo = info.get("repo", "")
        if not repo or repo == "TBD":
            continue
        for _role, file_info in info.get("files", {}).items():
            if not isinstance(file_info, dict):
                continue
            filename = file_info.get("filename", "")
            folder = file_info.get("folder", "")
            size_gb = file_info.get("size_gb", 0)
            if not filename:
                continue
            patterns[filename.lower()] = {
                "name": filename,
                "url": f"https://huggingface.co/{repo}/resolve/main/{filename}",
                "directory": folder,
                "size": int(size_gb * 1_000_000_000),
            }
    return patterns


MODEL_PATTERNS = _build_model_patterns()


def inject_models_metadata(workflow_path, dry_run=False):
    """Scan a workflow JSON for model references and inject metadata.

    Returns the number of models found.
    """
    try:
        with open(workflow_path, "r", encoding="utf-8") as f:
            workflow = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"  SKIP: {os.path.basename(workflow_path)} — {e}")
        return 0

    # Scan all nodes' widget values for model filenames
    found_models = []
    seen = set()
    nodes = workflow.get("nodes", [])

    for node in nodes:
        widgets = node.get("widgets_values", [])
        if not isinstance(widgets, list):
            continue
        for w in widgets:
            if not isinstance(w, str):
                continue
            w_lower = w.lower()
            if w_lower in MODEL_PATTERNS:
                model_meta = MODEL_PATTERNS[w_lower]
                if model_meta["name"] not in seen and model_meta["url"]:
                    found_models.append(model_meta)
                    seen.add(model_meta["name"])

    basename = os.path.basename(workflow_path)
    if found_models:
        if dry_run:
            print(f"  [DRY RUN] Would inject {len(found_models)} model(s) into {basename}")
            for m in found_models:
                print(f"    - {m['name']} ({m['directory']})")
        else:
            workflow["models"] = found_models
            with open(workflow_path, "w", encoding="utf-8") as f:
                json.dump(workflow, f, indent=2)
            print(f"  Injected {len(found_models)} model(s) into {basename}")
    else:
        print(f"  No model references found in {basename}")

    return len(found_models)


def main():
    parser = argparse.ArgumentParser(
        description="Inject model metadata into workflow JSONs for ComfyUI's missing-models popup"
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing files")
    args = parser.parse_args()

    workflow_dirs = [
        os.path.join(_project_root, "custom_nodes", "Laura_Image_Studio", "workflows"),
        os.path.join(_project_root, "workflows"),
        os.path.join(_project_root, "workflows", "master"),
    ]

    total_files = 0
    total_models = 0

    for wdir in workflow_dirs:
        if not os.path.isdir(wdir):
            continue
        print(f"\nProcessing: {wdir}")
        for wf in sorted(glob.glob(os.path.join(wdir, "*.json"))):
            total_files += 1
            count = inject_models_metadata(wf, dry_run=args.dry_run)
            total_models += count

    print(f"\n{'='*50}")
    print(f"  Processed {total_files} workflow file(s)")
    print(f"  Found {total_models} model reference(s)")
    if args.dry_run:
        print("  (DRY RUN — no files were modified)")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
