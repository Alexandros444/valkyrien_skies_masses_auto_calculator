from typing import Any, Optional
import json
import os

masses_dict = {
    "bars" : 100,
    "wedge" : 50,
    "catwalk" : 100,
    "stairs" : 100,
    "lamp" : 10,
    "ladder" : 100,
    "letter" : 1,
    "trapdoor" : 100,
    "window" : 100,
    "pane" : 50,
    "fence" : 100,
    "support" : 100,
    "facade" : 50,
    "door" : 250,
}

def get_defined_masses(block_name: str) -> Optional[float]:


    for key in masses_dict:
        if key in block_name:
            try:
                return float(masses_dict.get(key))
            except (ValueError, TypeError):
                pass
    
    return float(1000)


def process_mod_json(mod_name: str) -> None:
    """
    Read block names from src/<mod_name>.json and generate out/<mod_name>.json with masses.
    """
    src_file = f"src/{mod_name}.json"
    out_file = f"out/{mod_name}.json"
    
    # Read the source JSON
    with open(src_file, 'r') as f:
        blocks_dict = json.load(f)
    
    # Process each block and calculate mass
    output_data = []
    for full_block_name in blocks_dict.keys():
        # Extract the block identifier (remove "block." prefix)
        # Format: "block.createdeco.andesite_bars" -> "andesite_bars"
        parts = full_block_name.split('.')
        if len(parts) >= 3:
            block_id = parts[-1]  # Gets the last part (e.g., "andesite_bars")
            mass = get_defined_masses(block_id)
            
            # Format as "createdeco:andesite_bars"
            block_ref = f"{parts[1]}:{block_id}"
            
            output_data.append({
                "block": block_ref,
                "mass": mass
            })
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    
    # Write the output JSON
    with open(out_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Generated {out_file} with {len(output_data)} blocks")


if __name__ == "__main__":
    # Process createdeco mod
    # for each mod in src/*.json, call process_mod_json(mod_name)
    src_dir = "src"
    for filename in os.listdir(src_dir):
        if filename.endswith(".json"):
            mod_name = filename[:-5]  # Remove .json extension
            process_mod_json(mod_name)






