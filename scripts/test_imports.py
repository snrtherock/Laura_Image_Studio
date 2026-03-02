import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'custom_nodes')))
import types
sys.modules["custom_nodes"] = types.ModuleType("custom_nodes")
sys.modules["folder_paths"] = types.ModuleType("folder_paths")
sys.modules["folder_paths"].get_filename_list = lambda x: ["test_model.safetensors"]

import Laura_Image_Studio
print("Laura Image Studio modules loaded successfully")
print("Classes:", list(Laura_Image_Studio.NODE_CLASS_MAPPINGS.keys())[:5], "...")
