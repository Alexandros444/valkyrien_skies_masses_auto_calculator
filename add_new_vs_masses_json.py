# Script for creating Valkyrien Skies 2 Masses from Mod

from doctest import debug
import os
import json
import re
from pathlib import Path
from typing import Any, Optional
import sys
import requests
import time

# Configuration
LOCALAI_URL = os.environ.get("LOCALAI_URL", "http://localhost:8080")
LLM_MODEL = os.environ.get("LOCALAI_MODEL", "versatillama-llama-3.2-3b-instruct-abliterated")  # Model name available in LocalAI


# - Wood/planks: ~300 kg/m³
# - Wood/logs: ~600 kg/m³
# - Stone/concrete: ~2000 kg/m³
# - Metal (iron, copper): ~3000-8000 kg/m³
# - Lighter materials: ~50-100 kg/m³


# Carefully Consider block sizes like Bars or catwalks filling only around 5~10% of the volume, and adjust mass accordingly. For example, a Bar might be around 100-200 kg/m³, while a full block of iron would be around 7000 kg/m³.
# Also Doors, Ladders, Fences, and similar should be considered as partial blocks with much lower mass.
# All Bars, Ladders, Fences, and similar should be considered as partial blocks with much lower mass, around 100-200 kg/m³.


def get_llm_mass(block_name: str, max_retries: int = 3, debug_print: bool = False) -> Optional[float]:
    """
    Call self-hosted LLM API to calculate a reasonable mass for a block based on its name.
    Requires a local LLM service running via Docker (e.g., Ollama on localhost:11434).
    
    Args:
        block_name: The name of the block (e.g., "oak_log", "iron_block")
        max_retries: Number of retries if API is not responding
        
    Returns:
        A float representing the mass, or None if LLM call fails
    """
    prompt = f"""Given the Minecraft/modded block name "{block_name}", estimate a approximate mass in kilograms for a single block.
        
Consider mostly the Shape of the object:
- Partial blocks also from andersite or Iron (like bars, fences, ladders, Doors, catwalks, railings, windows, facades, supports, lamps etc.) should have much lower mass (e.g., 100-200).
- Full blocks (like stone, iron blocks) should have higher mass (e.g., 2000-7000).
- Full Wooden blocks should be around 300 for planks, 600 for logs.



Return ONLY a single number (float) representing the mass. No units, no explanation.
Example response: 2000"""
    
    url = f"{LOCALAI_URL}/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": LLM_MODEL,
        "messages" : [
            {
                "role": "user",
                "content": prompt
            }
        ],
        # "temperature": 0.5,
        "stream": False,
        # "max_tokens": 100,
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            if response.status_code != 200:
                raise Exception(f"API returned status {response.status_code}: {response.text}")
            
            result = response.json()

            if debug_print:
                print(f"LLM response for '{block_name}': {result}")

            mass_str = result["choices"][0]["message"]["content"].strip()

            # Extract the first number from the response
            import re
            numbers = re.findall(r'-?\d+\.?\d*', mass_str)
            if numbers:
                mass = float(numbers[0])
                print(f"  {block_name} -> {mass} kg/m³")
                return mass
            else:
                raise ValueError(f"No numeric value in response: {mass_str}")
                
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                print(f"  Connection failed (attempt {attempt + 1}/{max_retries}). Retrying in 2s...")
                time.sleep(2)
            else:
                print(f"  Error: Could not connect to LLM API at {LOCALAI_URL}")
                print(f"  Make sure Docker is running with Ollama or similar on {LOCALAI_URL}")
                return None
        except Exception as e:
            print(f"  Error calculating mass for {block_name}: {e}")
            return None
    
    return None



def process_subdirectories(root_dir: str = ".", debug_print: bool = False) -> None:
    """
    Process all subdirectories in the given root directory.
    For each subdirectory, create a JSON file with block mass data.
    
    Args:
        root_dir: The root directory to process (default is current directory)
        debug_print: Whether to print debug information
    """
    root_path = Path(root_dir)
    
    if not root_path.exists():
        print(f"Error: Directory {root_dir} does not exist")
        return
    
    # Iterate through subdirectories
    for dir_entry in root_path.iterdir():
        if not dir_entry.is_dir():
            continue
        
        dirname = dir_entry.name
        print(f"\nProcessing directory: {dirname}")
        if dirname == "examples":
            continue
        
        blocks_data = []
        
        # Find all .json files in this subdirectory
        json_files = list(dir_entry.glob("*.json"))
        
        if not json_files:
            print(f"  No .json files found in {dirname}")
            continue
        
        print(f"  Found {len(json_files)} JSON files")
        
        for json_file in sorted(json_files):
            blockname = json_file.stem  # filename without .json extension
            block_id = f"{dirname}:{blockname}"
            
            # Call LLM to get mass
            mass = get_llm_mass(blockname, debug_print=debug_print)
            
            if mass is not None:
                blocks_data.append({
                    "block": block_id,
                    "mass": mass
                })
        
        # Write output JSON file
        if blocks_data:
            output_file = root_path / f"{dirname}.json"
            try:
                with open(output_file, 'w') as f:
                    json.dump(blocks_data, f, indent=2)
                print(f"  ✓ Created {output_file} with {len(blocks_data)} entries")
            except Exception as e:
                print(f"  Error writing {output_file}: {e}")
        else:
            print(f"  No valid mass data collected for {dirname}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Create Valkyrien Skies 2 mass JSON files from mod block data using self-hosted LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--dir",
        default=".",
        help="Root directory containing subdirectories with block JSON files (default: current directory)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Valkyrien Skies 2 Mass Generator (Self-Hosted LLM)")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  LLM API URL: {LOCALAI_URL}")
    print(f"  LLM Model:   {LLM_MODEL}")
    print(f"  Directory:   {Path(args.dir).absolute()}\n")
    
    # Check if API is accessible
    try:
        response = requests.get(f"{LOCALAI_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ LLM API is accessible")
            models = response.json().get("models", [])
            available_models = [m.get("name") for m in models]
            print(f"  Available models: {', '.join(available_models) if available_models else 'none'}\n")
        else:
            print(f"✗ LLM API returned status {response.status_code}")
            print("  Make sure Docker is running and Ollama is accessible\n")
    except Exception as e:
        print(f"✗ Cannot reach LLM API at {LOCALAI_URL}")
        print(f"  Error: {e}")
    
    process_subdirectories(args.dir, debug_print=args.debug)
    print("\nDone!")


