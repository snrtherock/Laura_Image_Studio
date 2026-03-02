#!/usr/bin/env python3
"""
Laura Image Studio - Installation Script
Installs all dependencies and sets up the environment
"""

import os
import sys
import subprocess
import platform

def print_step(step):
    print(f"\n{'='*60}")
    print(f"STEP: {step}")
    print(f"{'='*60}\n")

def run_command(cmd, description, check=True):
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def check_comfyui():
    """Check if ComfyUI is installed"""
    possible_paths = [
        os.path.expanduser("~/ComfyUI"),
        "C:\\ComfyUI",
        "D:\\ComfyUI",
        os.path.join(os.getcwd(), "ComfyUI"),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║         Laura Image Studio - Installation Script            ║
║         All-in-One Image Generation & Editing               ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Step 1: Find ComfyUI
    print_step("1. Finding ComfyUI Installation")

    comfyui_path = check_comfyui()

    if comfyui_path:
        print(f"Found ComfyUI at: {comfyui_path}")
    else:
        print("ComfyUI not found. Please install ComfyUI first.")
        print("Download from: https://github.com/comfyanonymous/ComfyUI")
        return False

    # Step 2: Check custom_nodes directory
    print_step("2. Setting Up Custom Nodes Directory")

    custom_nodes_path = os.path.join(comfyui_path, "custom_nodes", "Laura_Image_Studio")
    os.makedirs(custom_nodes_path, exist_ok=True)
    print(f"Custom nodes directory: {custom_nodes_path}")

    # Step 3: Install required custom nodes
    print_step("3. Installing Required Custom Nodes")

    required_nodes = [
        ("ComfyUI-ReActor", "https://github.com/Gourieff/ComfyUI-ReActor.git"),
        ("ComfyUI_IPAdapter_plus", "https://github.com/cubiq/ComfyUI_IPAdapter_plus.git"),
        ("ComfyUI-RMBG", "https://github.com/1038lab/ComfyUI-RMBG.git"),
        ("ComfyUI-ConstrainResolution", "https://github.com/EnragedAntelope/ComfyUI-ConstrainResolution.git"),
        ("ComfyUI-AdvancedUpscripts", "https://github.com/Kosinkadink/ComfyUI-AdvancedUpscripts.git"),
    ]

    for node_name, repo_url in required_nodes:
        node_path = os.path.join(comfyui_path, "custom_nodes", node_name)
        if os.path.exists(node_path):
            print(f"  [SKIP] {node_name} already installed")
        else:
            print(f"  [INSTALL] {node_name}")
            cmd = f'git clone "{repo_url}" "{node_path}"'
            run_command(cmd, f"Clone {node_name}", check=False)

    # Step 4: Copy this package
    print_step("4. Installing Laura Image Studio")

    # Copy files to ComfyUI custom_nodes
    source_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(source_dir)

    # If running from the package directory
    if os.path.exists(os.path.join(source_dir, "nodes")):
        dest_dir = custom_nodes_path
        print(f"Installing from: {source_dir}")
        print(f"Installing to: {dest_dir}")

        # Create directory
        os.makedirs(dest_dir, exist_ok=True)

        # Copy files
        import shutil

        files_to_copy = ["__init__.py", "README.md"]
        for f in files_to_copy:
            src = os.path.join(source_dir, f)
            if os.path.exists(src):
                shutil.copy2(src, dest_dir)

        # Copy nodes directory
        nodes_src = os.path.join(source_dir, "nodes")
        nodes_dest = os.path.join(dest_dir, "nodes")
        if os.path.exists(nodes_src):
            if os.path.exists(nodes_dest):
                shutil.rmtree(nodes_dest)
            shutil.copytree(nodes_src, nodes_dest)

        # Copy workflows
        workflows_src = os.path.join(source_dir, "workflows")
        if os.path.exists(workflows_src):
            workflows_dest = os.path.join(dest_dir, "workflows")
            os.makedirs(workflows_dest, exist_ok=True)
            shutil.copytree(workflows_src, workflows_dest, dirs_exist_ok=True)

        print("  [OK] Laura Image Studio installed")

    # Step 5: Install Python dependencies
    print_step("5. Installing Python Dependencies")

    deps = [
        "torch",
        "torchvision",
        "Pillow",
        "numpy",
        "opencv-python",
        "scipy",
        "transformers",
        "imageio[ffmpeg]",
    ]

    for dep in deps:
        print(f"  Checking {dep}...")
        try:
            __import__(dep.replace("-", "_"))
            print(f"  [OK] {dep}")
        except ImportError:
            print(f"  [INSTALL] {dep}")
            run_command(f"pip install {dep}", f"Install {dep}", check=False)

    # Step 6: Download models
    print_step("6. Model Download Information")

    print("""
    The following models need to be downloaded manually:

    Base Models (SDXL):
    - juggernaut_xl_v8.safetensors
    - realisticVisionV60_v1.safetensors
    - sdxl_base_1.0.safetensors

    Upscaling Models:
    - 4x-UltraSharp.pth
    - RealESRGAN_x4plus.pth
    - ScuNet_GAN.pth

    Face Models:
    - inswapper_128.onnx (ReActor)
    - ip-adapter-faceid-plusv2.bin (IPAdapter)

    Background Removal:
    - RMBG-1.4.pth

    Place models in ComfyUI/models/ directory.
    """)

    # Step 7: Verify installation
    print_step("7. Verification")

    print("""
    Installation complete! Please:

    1. Restart ComfyUI
    2. Check if nodes appear in the node browser
    3. Load a workflow from the workflows folder
    4. Start generating!

    Quick Start:
    - Open ComfyUI
    - Load workflow/all_in_one.json
    - Configure your model paths
    - Run the workflow

    For help, see docs/installation.md
    """)

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
