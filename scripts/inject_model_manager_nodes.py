#!/usr/bin/env python3
"""
Inject 7 Laura Studio Model Manager nodes into master workflow JSONs.

Adds: LauraModelLinks, LauraModelManager, LauraAutoConfig,
      LauraQuantizationAdvisor, LauraModelDownloadHelper,
      LauraCompatibilityChecker, ModuleConfigPanel
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TARGET_FILES = [
    os.path.join(BASE_DIR, "custom_nodes", "Laura_Image_Studio", "workflows", "enhanced_master_workflow.json"),
    os.path.join(BASE_DIR, "custom_nodes", "Laura_Image_Studio", "workflows", "master_all_in_one.json"),
    os.path.join(BASE_DIR, "workflows", "master", "Laura_Master_Studio_v0.8.json"),
]


def build_new_nodes(start_id, start_order, x_offset=2000, y_start=50, y_spacing=300):
    """Build the 7 model manager node definitions."""
    nodes = []
    idx = 0

    # 1. LauraModelLinks
    nodes.append({
        "id": start_id + idx,
        "type": "LauraModelLinks",
        "pos": [x_offset, y_start + y_spacing * idx],
        "size": [400, 200],
        "flags": {},
        "order": start_order + idx,
        "mode": 0,
        "inputs": [],
        "outputs": [
            {"name": "model_links", "type": "STRING", "slot_index": 0},
            {"name": "directory_tree", "type": "STRING", "slot_index": 1},
            {"name": "download_urls_json", "type": "STRING", "slot_index": 2}
        ],
        "properties": {"Node name for S&R": "LauraModelLinks"},
        "widgets_values": ["z_image_turbo"]
    })
    idx += 1

    # 2. LauraModelManager
    nodes.append({
        "id": start_id + idx,
        "type": "LauraModelManager",
        "pos": [x_offset, y_start + y_spacing * idx],
        "size": [400, 250],
        "flags": {},
        "order": start_order + idx,
        "mode": 0,
        "inputs": [],
        "outputs": [
            {"name": "model_info", "type": "STRING", "slot_index": 0},
            {"name": "recommended_quant", "type": "STRING", "slot_index": 1},
            {"name": "install_status", "type": "STRING", "slot_index": 2},
            {"name": "model_key", "type": "STRING", "slot_index": 3},
            {"name": "total_size_gb", "type": "FLOAT", "slot_index": 4}
        ],
        "properties": {"Node name for S&R": "LauraModelManager"},
        "widgets_values": ["flux1_dev", True, "high"]
    })
    idx += 1

    # 3. LauraAutoConfig
    nodes.append({
        "id": start_id + idx,
        "type": "LauraAutoConfig",
        "pos": [x_offset, y_start + y_spacing * idx],
        "size": [400, 200],
        "flags": {},
        "order": start_order + idx,
        "mode": 0,
        "inputs": [],
        "outputs": [
            {"name": "auto_config", "type": "STRING", "slot_index": 0},
            {"name": "recommended_model", "type": "STRING", "slot_index": 1},
            {"name": "recommended_quant", "type": "STRING", "slot_index": 2}
        ],
        "properties": {"Node name for S&R": "LauraAutoConfig"},
        "widgets_values": ["image_gen", True, False]
    })
    idx += 1

    # 4. LauraQuantizationAdvisor
    nodes.append({
        "id": start_id + idx,
        "type": "LauraQuantizationAdvisor",
        "pos": [x_offset, y_start + y_spacing * idx],
        "size": [400, 150],
        "flags": {},
        "order": start_order + idx,
        "mode": 0,
        "inputs": [],
        "outputs": [
            {"name": "recommendation", "type": "STRING", "slot_index": 0},
            {"name": "all_variants", "type": "STRING", "slot_index": 1}
        ],
        "properties": {"Node name for S&R": "LauraQuantizationAdvisor"},
        "widgets_values": ["flux1_dev"]
    })
    idx += 1

    # 5. LauraModelDownloadHelper
    nodes.append({
        "id": start_id + idx,
        "type": "LauraModelDownloadHelper",
        "pos": [x_offset, y_start + y_spacing * idx],
        "size": [400, 150],
        "flags": {},
        "order": start_order + idx,
        "mode": 0,
        "inputs": [],
        "outputs": [
            {"name": "download_info", "type": "STRING", "slot_index": 0},
            {"name": "urls_json", "type": "STRING", "slot_index": 1}
        ],
        "properties": {"Node name for S&R": "LauraModelDownloadHelper"},
        "widgets_values": ["flux1_dev"]
    })
    idx += 1

    # 6. LauraCompatibilityChecker
    nodes.append({
        "id": start_id + idx,
        "type": "LauraCompatibilityChecker",
        "pos": [x_offset, y_start + y_spacing * idx],
        "size": [400, 150],
        "flags": {},
        "order": start_order + idx,
        "mode": 0,
        "inputs": [],
        "outputs": [
            {"name": "compatibility_report", "type": "STRING", "slot_index": 0},
            {"name": "compatibility_json", "type": "STRING", "slot_index": 1}
        ],
        "properties": {"Node name for S&R": "LauraCompatibilityChecker"},
        "widgets_values": ["flux1_dev"]
    })
    idx += 1

    # 7. ModuleConfigPanel
    nodes.append({
        "id": start_id + idx,
        "type": "ModuleConfigPanel",
        "pos": [x_offset, y_start + y_spacing * idx],
        "size": [400, 300],
        "flags": {},
        "order": start_order + idx,
        "mode": 0,
        "inputs": [],
        "outputs": [
            {"name": "config_summary", "type": "STRING", "slot_index": 0}
        ],
        "properties": {"Node name for S&R": "ModuleConfigPanel"},
        "widgets_values": [True, True, True, True, True, True, False]
    })

    return nodes


def inject_nodes(filepath):
    """Read a workflow JSON, inject 7 model manager nodes, write back."""
    print(f"\n{'='*70}")
    print(f"Processing: {filepath}")
    print(f"{'='*70}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    nodes = data.get("nodes", [])
    node_count_before = len(nodes)

    # Find max existing ID and order
    max_id = max((n["id"] for n in nodes), default=0)
    max_order = max((n.get("order", 0) for n in nodes), default=0)

    print(f"  Nodes before:    {node_count_before}")
    print(f"  Max existing ID: {max_id}")
    print(f"  Max order:       {max_order}")

    # Build new nodes starting from max_id + 1
    start_id = max(max_id + 1, 1000)  # Use at least 1000 as requested
    start_order = max_order + 1

    new_nodes = build_new_nodes(start_id, start_order)

    # Check no ID collision
    existing_ids = {n["id"] for n in nodes}
    for nn in new_nodes:
        assert nn["id"] not in existing_ids, f"ID collision: {nn['id']}"

    # Append
    nodes.extend(new_nodes)
    data["nodes"] = nodes

    # Update last_node_id if it exists
    new_max_id = max(n["id"] for n in nodes)
    if "last_node_id" in data:
        old_val = data["last_node_id"]
        data["last_node_id"] = max(old_val, new_max_id)
        print(f"  last_node_id:    {old_val} -> {data['last_node_id']}")

    node_count_after = len(nodes)
    print(f"  Nodes after:     {node_count_after}")
    print(f"  Added node IDs:  {[n['id'] for n in new_nodes]}")
    print(f"  Added types:     {[n['type'] for n in new_nodes]}")

    # Write back
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  Written successfully.")
    return node_count_before, node_count_after


def main():
    print("Laura Studio Model Manager Node Injector")
    print("=========================================")

    results = []
    for fp in TARGET_FILES:
        if not os.path.exists(fp):
            print(f"\n  WARNING: File not found: {fp}")
            continue
        before, after = inject_nodes(fp)
        results.append((os.path.basename(fp), before, after))

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    for name, before, after in results:
        print(f"  {name}: {before} -> {after} nodes (+{after - before})")
    print("\nDone.")


if __name__ == "__main__":
    main()
