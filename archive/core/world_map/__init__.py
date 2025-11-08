"""
Simple world map loader - just load JSON files.
"""

import json
from pathlib import Path
from typing import Dict, Any

from .coordinate_converter import CoordinateConverter, convert_sphinx_coordinates


def load_world_map(file_path: str) -> Dict[str, Any]:
    """
    Load a world map from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the world map data
        
    Example:
        world_map = load_world_map("maps/paris.json")
        world_map_json = json.dumps(world_map, indent=2)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"World map file not found: {file_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


__all__ = ["load_world_map", "CoordinateConverter", "convert_sphinx_coordinates"]
