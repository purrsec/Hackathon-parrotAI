"""Natural Language Processor - Converts user messages to drone mission DSL."""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any
from api_clients.mistral_socket import get_mistral_socket

logger = logging.getLogger(__name__)


class NaturalLanguageProcessor:
	"""Process natural language user requests and convert them to drone mission DSL."""
	
	def __init__(self, poi_file_path: str = None):
		"""
		Initialize the NLP processor.
		
		Args:
			poi_file_path: Path to the POI (Points of Interest) JSON file.
						  Defaults to industrial_city.json in the maps folder.
		"""
		self.mistral_socket = get_mistral_socket()
		
		# Default to industrial_city.json if not provided
		if poi_file_path is None:
			# Compute repo root from this file: Olympe-web-server → repo root
			repo_root = Path(__file__).parent.parent
			poi_file_path = repo_root / "maps" / "industrial_city.json"
		
		self.poi_data = self._load_poi_data(str(poi_file_path))
		self.system_prompt = self._build_system_prompt()
	
	def _load_poi_data(self, file_path: str) -> Dict[str, Any]:
		"""Load points of interest from JSON file."""
		try:
			with open(file_path, 'r', encoding='utf-8') as f:
				return json.load(f)
		except FileNotFoundError:
			logger.error(f"POI file not found: {file_path}")
			return {}
		except json.JSONDecodeError:
			logger.error(f"Invalid JSON in POI file: {file_path}")
			return {}
	
	def _build_system_prompt(self) -> str:
		"""Build the system prompt with POI information and available actions."""
		poi_list = self._format_poi_list()
		
	system_prompt = """You are a drone mission planner. Generate missions as JSON ONLY.

Actions (use ONLY these):
- takeoff: {"type":"takeoff","constraints":{"maxWaitSec":20}}
- move_to: {"type":"move_to","latitude":48.88,"longitude":2.37,"altitude":60,"max_horizontal_speed":15,"max_vertical_speed":2,"max_yaw_rotation_speed":1}
- poi_inspection: {"type":"poi_inspection","poi_name":"NAME","latitude":LAT,"longitude":LON,"altitude":65,"rotation_duration":30,"roll_rate":50,"offset_distance":15}
- return_to_home: {"type":"return_to_home"}
- land: {"type":"land"}

POIs:
"""
	system_prompt += poi_list
	
	system_prompt += """
Template:
{"missionId":"auto-2025-11-08-X","segments":[{"type":"takeoff","constraints":{"maxWaitSec":20}},{"type":"move_to",...},{"type":"poi_inspection",...},{"type":"return_to_home"},{"type":"land"}],"safety":{"geofence":{"enabled":true},"maxAltitudeMeters":80,"minBatteryPercent":25}}

Rules:
1. ONLY use action types: takeoff,move_to,poi_inspection,return_to_home,land
2. NO orbit/loiter/survey
3. Use real POI coordinates
4. Start with takeoff, end with return_to_home+land
5. Add move_to before each poi_inspection
6. Output ONLY valid JSON, no text, NO markdown, NO code fences/backticks
7. CRITICAL SAFETY: MINIMUM altitude 60m for move_to, 65m for poi_inspection
8. Buildings are 30-40m tall - NEVER fly below 55m altitude
9. For inspection, position drone ABOVE buildings at 65m minimum
"""
		
		return system_prompt
	
	def _format_poi_list(self) -> str:
		"""Format the points of interest list from the POI data."""
		poi_list = ""
		
		if not self.poi_data or "points_of_interest" not in self.poi_data:
			return "No points of interest available."
		
		for poi in self.poi_data["points_of_interest"]:
			poi_list += f"\n- {poi.get('name', 'Unknown')}: {poi.get('description', 'No description')}"
			if "coordinates" in poi:
				coords = poi["coordinates"]
				poi_list += f" (Latitude: {coords.get('latitude')}, Longitude: {coords.get('longitude')}, Altitude: {coords.get('altitude_meters')}m)"
		
		return poi_list
	
	async def process_user_message(self, user_message: str) -> Dict[str, Any]:
		"""
		Process a user message and return a drone mission DSL.
		
		Args:
			user_message: Natural language message from the user
			
		Returns:
			Dictionary containing the mission DSL with understanding summary
		"""
		try:
			logger.info(f"Processing user message: {user_message}")
			
			# Generate a human-readable understanding of what the user wants
			understanding = await self._generate_mission_understanding(user_message)
			
			# Call Mistral with the system prompt and user message
			# Use a fast/accurate model optimized for low-latency JSON generation
			model_name = os.getenv("FAST_MISSION_DSL_MODEL", "mistral-medium-latest")
			max_out_tokens = int(os.getenv("FAST_MISSION_MAX_TOKENS", "600"))
			extra_args = {}
			# Mistral uses `max_tokens`, supports temperature; no response_format enforcement.
			extra_args["max_tokens"] = max_out_tokens
			extra_args["temperature"] = 0.1
			# Avoid adding extra verbosity from safety prompts to keep strict JSON
			extra_args["safe_prompt"] = False
			
			response = self.mistral_socket.create_completion(
				model=model_name,
				messages=[
					{"role": "system", "content": self.system_prompt},
					{"role": "user", "content": user_message}
				],
				**extra_args
			)
			
			# Extract the response content
			response_text = response.choices[0].message.content
			
			# Log detailed response information
			finish_reason = response.choices[0].finish_reason if response.choices else "unknown"
			logger.info(f"Mistral response length: {len(response_text) if response_text else 0} characters")
			logger.info(f"Mistral response type: {type(response_text)}")
			logger.info(f"Mistral finish_reason: {finish_reason}")
			logger.info(f"Mistral response (raw): {repr(response_text)}")
			logger.info(f"Full response object: {response}")
			
			# If the model was cut off due to token limit, retry with bigger budget and stricter instruction
			if str(finish_reason).lower() == "length":
				try:
					logger.warning("Mistral completion stopped due to length; retrying with larger token budget and stricter JSON-only instruction")
					retry_args = dict(extra_args)
					retry_args["max_tokens"] = max(600, int(max_out_tokens * 1.5))
					retry_args["temperature"] = 0
					retry_args["safe_prompt"] = False
					retry_messages = [
						{"role": "system", "content": self.system_prompt + "\n\nRègle CRITIQUE: réponds UNIQUEMENT en JSON valide conforme au Template. Aucune mise en forme, AUCUNE balise markdown, AUCUNS backticks. Réponds en JSON compact (minifié, sans espaces ni retours à la ligne)."},
						{"role": "user", "content": user_message}
					]
					retry_response = self.mistral_socket.create_completion(
						model=model_name,
						messages=retry_messages,
						**retry_args
					)
					response_text = retry_response.choices[0].message.content
					logger.info(f"Retry-after-length response length: {len(response_text) if response_text else 0} characters")
				except Exception as retry_len_err:
					logger.error(f"Retry after length stop failed: {retry_len_err}")
			
			# Check if response is empty
			if not response_text or not response_text.strip():
				logger.error(f"Empty response from Mistral")
				# One-shot retry with safer defaults to elicit JSON output
				try:
					retry_args = dict(extra_args)
					retry_args["max_tokens"] = max(256, int(max_out_tokens * 0.5))
					retry_args["temperature"] = 0
					retry_args["safe_prompt"] = False
					retry_messages = [
						{"role": "system", "content": self.system_prompt + "\n\nRègle CRITIQUE: réponds UNIQUEMENT en JSON valide conforme au Template. Aucune mise en forme, AUCUNE balise markdown, AUCUNS backticks."},
						{"role": "user", "content": user_message}
					]
					retry_response = self.mistral_socket.create_completion(
						model=model_name,
						messages=retry_messages,
						**retry_args
					)
					retry_text = retry_response.choices[0].message.content
					logger.info(f"Retry response length: {len(retry_text) if retry_text else 0} characters")
					logger.info(f"Retry finish_reason: {retry_response.choices[0].finish_reason if retry_response.choices else 'unknown'}")
					if retry_text and retry_text.strip():
						response_text = retry_text
					else:
						return {
							"error": "Empty response from Mistral model",
							"raw_response": retry_text
						}
				except Exception as retry_err:
					logger.error(f"Retry after empty response failed: {retry_err}")
					return {
						"error": "Empty response from Mistral model",
						"raw_response": None
					}
			
			# Parse the JSON response
			try:
				normalized = self._extract_json_from_text(response_text)
				mission_dsl = json.loads(normalized)
				logger.info(f"Successfully parsed mission DSL")
				
				# Add the understanding to the mission DSL
				mission_dsl["understanding"] = understanding
				logger.info(f"Added understanding to mission DSL: {understanding}")
				
				return mission_dsl
			except json.JSONDecodeError as e:
				logger.error(f"Failed to parse Mistral response as JSON: {response_text}")
				logger.error(f"JSON parsing error: {str(e)}")
				return {
					"error": "Failed to parse mission DSL",
					"raw_response": response_text,
					"parse_error": str(e)
				}
		
		except Exception as e:
			logger.error(f"Error processing user message: {str(e)}")
			return {
				"error": f"Error processing request: {str(e)}"
			}

	async def _generate_mission_understanding(self, user_message: str) -> str:
		"""
		Generate a human-readable understanding of what the user wants.
		
		Args:
			user_message: Natural language message from the user
			
		Returns:
			Short summary like "Yes, I can fly over all towers and come back"
		"""
		try:
			# Create a prompt to generate a short understanding
			understanding_prompt = f"""You are a helpful drone assistant. 
Given this user request, respond with a SHORT confirmation (1 sentence max).
Format: "Yes, I can [action] [details]"

User request: {user_message}

Respond with ONLY the confirmation sentence, nothing else."""
			
			logger.info(f"🤖 Generating understanding for: {user_message}")
			
			response = self.mistral_socket.create_completion(
				model=os.getenv("FAST_MISSION_DSL_MODEL", "mistral-medium-latest"),
				messages=[
					{"role": "user", "content": understanding_prompt}
				],
				max_tokens=100,
				temperature=0.5,
				safe_prompt=False
			)
			
			understanding = response.choices[0].message.content.strip()
			logger.info(f"✅ Generated understanding: {understanding}")
			return understanding
		
		except Exception as e:
			logger.error(f"❌ Failed to generate understanding: {e}", exc_info=True)
			# Fallback to a generic response
			fallback = f"Yes, I can execute: {user_message[:60]}..."
			logger.info(f"Using fallback understanding: {fallback}")
			return fallback
	
	def _extract_json_from_text(self, text: str) -> str:
		"""
		Extract a JSON object from a model response that may include markdown fences.
		Strategy:
		1) Strip leading/trailing markdown code fences if present.
		2) Otherwise, scan and extract the first balanced JSON object by braces.
		"""
		if not text:
			raise json.JSONDecodeError("Empty text", "", 0)
		
		s = text.strip()
		# Remove markdown code fences like ```json ... ``` or ``` ...
		if s.startswith("```"):
			# Drop the opening fence line (e.g., ```json)
			first_newline = s.find("\n")
			if first_newline != -1:
				s = s[first_newline + 1 :].strip()
			# Drop trailing closing fence if present
			if s.endswith("```"):
				s = s[:-3].strip()
			# If we trimmed fences successfully, try returning
			candidate = s.strip()
			if candidate.startswith("{") and candidate.endswith("}"):
				return candidate
			# fallthrough to balanced extraction
		
		# Balanced brace extraction (ignores braces inside quoted strings)
		in_string = False
		escape = False
		depth = 0
		start_idx = -1
		for i, ch in enumerate(s):
			if escape:
				escape = False
				continue
			if ch == "\\":
				escape = True
				continue
			if ch == '"':
				in_string = not in_string
				continue
			if in_string:
				continue
			if ch == "{":
				if depth == 0:
					start_idx = i
				depth += 1
			elif ch == "}":
				if depth > 0:
					depth -= 1
					if depth == 0 and start_idx != -1:
						obj_str = s[start_idx : i + 1]
						return obj_str
		# If we get here, no valid object was found; raise to be handled by caller
		raise json.JSONDecodeError("No JSON object found in text", s, 0)


def get_nlp_processor(poi_file_path: str = None) -> NaturalLanguageProcessor:
	"""Factory function to get or create NaturalLanguageProcessor instance."""
	return NaturalLanguageProcessor(poi_file_path)


