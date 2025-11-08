"""
Simple example: Load JSON world map and use in LLM prompt.
"""

import json
from . import load_world_map


def example_load_and_use():
    """Load a world map and use it in an LLM prompt."""
    # Load the world map
    world_map = load_world_map("maps/example_paris.json")
    
    # Convert to JSON string for LLM
    world_map_json = json.dumps(world_map, indent=2)
    
    # Use in LLM prompt
    user_input = "Je veux faire un survol autour de la Tour Eiffel puis revenir"
    
    prompt = f"""You are a drone mission planner. Given the world map, generate flight instructions.

World Map:
{world_map_json}

Starting Position: ({world_map['starting_position']['coordinates']['latitude']}, {world_map['starting_position']['coordinates']['longitude']})

User Request: {user_input}

Generate a Mission DSL JSON that:
1. Satisfies the user's request
2. Uses POI names from the map (e.g., "Tour Eiffel" refers to the POI in the map)
3. Respects all boundaries and restrictions
4. Accounts for obstacles and height restrictions

Available POIs: {', '.join([poi['name'] for poi in world_map.get('points_of_interest', [])])}
Max altitude: {world_map.get('default_max_altitude_meters', 60)}m
Max distance: {world_map.get('default_max_distance_meters', 2000)}m

Return only valid Mission DSL JSON, no additional text.
"""
    
    return prompt


if __name__ == "__main__":
    try:
        prompt = example_load_and_use()
        print("=" * 80)
        print("Example LLM Prompt")
        print("=" * 80)
        print(prompt)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nMake sure maps/example_paris.json exists")

