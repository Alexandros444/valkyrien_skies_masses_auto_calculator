"""Extract masses from example JSON files and create a formatted txt file"""

import json
from pathlib import Path


def extract_masses_from_examples(examples_dir: str = "examples", output_file: str = "extracted_masses.txt"):
    """
    Read all JSON files in the examples directory and extract block/mass data.
    
    Args:
        examples_dir: Directory containing JSON files
        output_file: Output text file to write formatted data to
    """
    examples_path = Path(examples_dir)
    
    if not examples_path.exists():
        print(f"Error: Directory {examples_dir} does not exist")
        return
    
    # Collect all block/mass data
    blocks_data = []
    
    # Find all .json files
    json_files = list(examples_path.glob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in {examples_dir}")
        return
    
    print(f"Found {len(json_files)} JSON files\n")
    
    # Parse each JSON file
    for json_file in sorted(json_files):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                
            # Handle both list and single object formats
            if isinstance(data, list):
                items = data
            else:
                items = [data]
            
            # Extract block and mass from each item
            for item in items:
                if isinstance(item, dict) and "block" in item and "mass" in item:
                    block_name = item["block"]
                    mass = item["mass"]
                    # Format as integer if it's a whole number
                    mass_str = str(int(mass)) if mass == int(mass) else str(mass)
                    blocks_data.append(f"{block_name} - {mass_str}")
                    print(f"✓ {json_file.name}: {block_name} - {mass_str}")
                    
        except json.JSONDecodeError as e:
            print(f"✗ Error parsing {json_file.name}: {e}")
        except Exception as e:
            print(f"✗ Error processing {json_file.name}: {e}")
    
    # Write to output file
    if blocks_data:
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            f.write('\n'.join(blocks_data))
        print(f"\n✓ Created {output_path} with {len(blocks_data)} entries")
    else:
        print("\nNo block/mass data found to write")


if __name__ == "__main__":
    extract_masses_from_examples()

