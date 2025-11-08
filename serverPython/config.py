"""
Configuration du serveur drone
"""

import os
from typing import List

# Configuration du drone
DRONE_IP = os.getenv("DRONE_IP", "10.202.0.1")  # IP par défaut du Sphinx/ANAFI

# Configuration FastAPI
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# CORS - Origines autorisées
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

# Configuration Olympe
OLYMPE_AVAILABLE = False  # Sera mis à jour lors de l'import

# Configuration du logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

