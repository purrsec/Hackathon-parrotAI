ParrotAI — Natural Language Drone Control System
================================================

A complete system that turns natural language into safe and executable flight plans for Parrot ANAFI drones using the Olympe SDK. Users send plain-language commands via WebSocket (e.g. "Visit all buildings and come back home") and the system uses Mistral AI to parse, plan, validate, and execute missions in Parrot Sphinx simulator or on real drones.

**Reference:** Parrot Olympe SDK docs: https://developer.parrot.com/docs/olympe/index.html

---

## 🚀 Quick Start

**See [START.md](START.md) for detailed launch instructions.**

**TL;DR:**
1. Launch Parrot Sphinx simulator with ANAFI Ai drone
2. Launch Unreal Engine 4 industrial-city world
3. Start FastAPI server: `cd Olympe-web-server && FAST_MISSION_DSL_MODEL=mistral-tiny-latest uv run fastapi_entrypoint.py`
4. Start chat client: `cd client_debug && uv run chat_client.py`
5. Send commands like: `"Visit a building and come back home"`


## Why this project

- **Natural-language drone control**: Send commands in plain English/French
- **AI-powered mission planning**: Mistral AI translates requests into safe flight plans
- **Safety-first**: Altitude constraints, geofencing, automatic RTH, battery monitoring
- **Real-time execution**: WebSocket-based communication with live mission status
- **Simulator-ready**: Full integration with Parrot Sphinx + Unreal Engine 4

---

## High-level Architecture

```
User (Natural Language)
    ↓
WebSocket Client (Terminal/NextJS/Discord)
    ↓
FastAPI WebSocket Server
    ↓
Natural Language Processor (Mistral AI)
    ↓
Mission DSL (JSON)
    ↓
Mission Executor (Olympe SDK)
    ↓
Parrot Sphinx Simulator + UE4 Visualization
    ↓
ANAFI Ai Drone (Simulated/Real)
```

### Components

- **FastAPI Server** (`Olympe-web-server/fastapi_entrypoint.py`): WebSocket endpoint for receiving natural language commands
- **NLP Processor** (`natural_language_processor.py`): Uses Mistral AI to convert natural language → Mission DSL (JSON)
- **Mission Executor** (`mission_executor.py`): Executes Mission DSL using Olympe SDK (takeoff, move_to, POI inspection, RTH, landing)
- **Chat Client** (`client_debug/chat_client.py`): Terminal-based client for testing and debugging
- **POI Data** (`maps/industrial_city.json`): Points of interest and obstacle definitions

### Mission DSL Flow

1. User sends: `"Visit all buildings and come back home"`
2. Mistral generates Mission DSL with segments: `takeoff → move_to → poi_inspection → return_to_home → land`
3. User confirms the mission
4. Executor translates DSL to Olympe commands and executes on drone
5. Real-time status updates sent back to client


---

## Repository Layout

```
.
├─ Olympe-web-server/         # FastAPI WebSocket server + NLP + Mission Executor
│  ├─ fastapi_entrypoint.py   # Main server entry point
│  ├─ natural_language_processor.py  # Mistral AI integration
│  ├─ mission_executor.py     # Olympe SDK mission execution
│  └─ requirements.txt
├─ client_debug/              # Terminal chat client for testing
│  └─ chat_client.py
├─ maps/                      # POI and obstacle definitions
│  └─ industrial_city.json
├─ archive/                   # Legacy code (for reference only)
│  ├─ apps/cli/               # Old CLI scripts (incl. poi_inspection.py reference)
│  └─ core/world_map/         # Old coordinate utilities
├─ NextJS/                    # Next.js web UI (planned)
├─ discord-bot/               # Discord bot interface (legacy)
├─ docs/
├─ START.md                   # Quick start guide (launch commands)
├─ README.md                  # This file
└─ pyproject.toml
```

---

## Development Conventions

### Code Style
- Keep modules small and cohesive (single responsibility)
- Type hints for all function signatures
- Docstrings for public APIs
- Follow PEP 8 style guide

### Architecture Principles
- Mission DSL is the contract between NLP and execution
- No Olympe SDK leaking outside `mission_executor.py`
- Environment variables for configuration (no hardcoded values)
- Structured logging with appropriate levels

### Testing
- Always test in Parrot Sphinx before real hardware
- Unit tests for business logic
- Integration tests with simulator
- Never commit API keys or tokens

### Git Workflow
- Commit style: `feat:`, `fix:`, `docs:`, `refactor:`, etc.
- Concise, imperative commit messages
- Example: `fix: improve RTH robustness and adjust altitude to 30m`


---

## Mission DSL (JSON) — Current Implementation

The NLP Processor (using Mistral AI) outputs a normalized Mission DSL that the executor can safely validate and execute. 

### Example 1: Single Building Inspection

User command: `"Visit a building and come back home"`

```json
{
  "missionId": "auto-2025-11-08-123456",
  "understanding": "Takeoff, navigate to Advertising Board, perform POI inspection, return home and land",
  "segments": [
    {
      "type": "takeoff",
      "constraints": { "maxWaitSec": 20 }
    },
    {
      "type": "move_to",
      "latitude": 48.87882157897949,
      "longitude": 2.368181582689285,
      "altitude": 30,
      "max_horizontal_speed": 15,
      "max_vertical_speed": 2,
      "max_yaw_rotation_speed": 1
    },
    {
      "type": "poi_inspection",
      "poi_name": "Advertising Board",
      "latitude": 48.87882157897949,
      "longitude": 2.368181582689285,
      "altitude": 30,
      "rotation_duration": 30,
      "roll_rate": 50,
      "offset_distance": 15
    },
    {
      "type": "return_to_home"
    },
    {
      "type": "land"
    }
  ],
  "safety": {
    "geofence": { "enabled": true },
    "maxAltitudeMeters": 80,
    "minBatteryPercent": 25
  }
}
```

### Supported Segment Types

1. **takeoff**: Initial takeoff with constraints
2. **move_to**: Navigate to GPS coordinates at specified altitude
3. **poi_inspection**: Rotate around a point of interest with camera pointing at it
4. **return_to_home**: Automatic RTH with landing behavior
5. **land**: Manual landing command

### Safety Constraints

- **Default altitude**: 30m (safe clearance above 15m obstacle box)
- **Geofencing**: Enabled by default
- **Max altitude**: 80m
- **Min battery**: 25% before RTH
- **POI offset**: 15-25m distance for optimal viewing angle


---

## Usage Examples

### Terminal Chat Client

The chat client (`client_debug/chat_client.py`) connects via WebSocket and provides real-time feedback.

**Example commands:**

```
Visit a building and come back home
```
→ Visits ONE POI (Advertising Board) and returns

```
Visit all buildings
```
→ Visits ALL available POIs (Advertising Board, Ventilation Pipes, etc.)

```
Inspect the Advertising Board at 40 meters altitude
```
→ Custom altitude for specific POI inspection

```
Fly to coordinates 48.878, 2.367 at 35m and return
```
→ Custom GPS waypoint navigation

### Response Flow

1. **Understanding**: Short summary of what the drone will do
2. **Mission DSL Preview**: JSON with all segments (takeoff, move_to, poi_inspection, RTH, land)
3. **Confirmation Prompt**: `yes/no` to approve mission execution
4. **Execution Updates**: Real-time status for each segment
5. **Completion Report**: Success/failure with execution details

### Available POIs (industrial_city map)

- **Advertising Board** (48.878822°, 2.368182°, 19m altitude)
- **Ventilation Pipes** (48.878815°, 2.366594°, 20m altitude)

**Obstacle zones**: 0-15m altitude restricted


Olympe & Parrot Sphinx
----------------------

- Olympe SDK allows Python control of Parrot ANAFI drones (ANAFI, ANAFI Thermal, ANAFI USA, ANAFI AI). See docs: https://developer.parrot.com/docs/olympe/index.html
- During development, prefer the Sphinx simulator for safety, then move to hardware-in-the-loop.

Basic Olympe workflow (conceptual):
1. Connect to drone/sim
2. Wait for states (GPS fix, battery, ready)
3. Send piloting commands (takeoff, move, orbit, RTH, land)
4. Monitor state/telemetry and enforce safety policies


---

## Prerequisites

### Required
- **Python 3.12+** (tested with 3.12)
- **uv** package manager: https://github.com/astral-sh/uv
- **Parrot Sphinx** simulator: https://developer.parrot.com/docs/sphinx/installation.html
- **Parrot UE4** (Unreal Engine 4 world): industrial-city world
- **Mistral API Key**: https://console.mistral.ai/

### Recommended
- **Linux** (Ubuntu/Debian preferred for Olympe compatibility)
- **Arch Linux** also supported (see project setup)
- 8GB+ RAM for running Sphinx + UE4 simultaneously

---

## Installation

### 1. Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd Hackathon-parrotAI

# Install Python dependencies with uv
cd Olympe-web-server
uv venv
source .venv/bin/activate  # or .venv/Scripts/activate on Windows
uv pip install -r requirements.txt

cd ../client_debug
uv pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Set Mistral API key
export MISTRAL_API_KEY="your_mistral_api_key_here"

# Optional: customize model
export FAST_MISSION_DSL_MODEL="mistral-tiny-latest"
export FAST_MISSION_MAX_TOKENS=900
```

### 3. Verify Parrot Sphinx Installation

```bash
# Check Sphinx is installed
which sphinx

# Check UE4 world is available
which parrot-ue4-industrial-city
```

---

## Configuration

### Environment Variables

Set the following environment variables before starting the FastAPI server:

```bash
# Mistral AI (required)
MISTRAL_API_KEY=your_mistral_api_key_here

# Mission DSL Model (optional)
FAST_MISSION_DSL_MODEL=mistral-tiny-latest    # Default: mistral-medium-latest
FAST_MISSION_MAX_TOKENS=900                   # Default: 600

# Olympe / Drone
DRONE_IP=10.202.0.1                           # Sphinx simulator default
TIMEOUT_SEC=25                                # Default command timeout
MOVE_TIMEOUT_SEC=120                          # Move command timeout
RTH_TIMEOUT_SEC=300                           # RTH timeout (5 minutes)

# Safety
STRICT=1                                      # Stop mission on first failure (default)
```

### Model Selection

- **mistral-tiny-latest**: Fast, economical, good for simple missions
- **mistral-small-latest**: Balanced performance
- **mistral-medium-latest**: High accuracy for complex missions

---

## Running the System

See **[START.md](START.md)** for complete launch instructions.

### Quick Launch (4 terminals)

**Terminal 1 - Sphinx:**
```bash
sphinx "/opt/parrot-sphinx/usr/share/sphinx/drones/anafi_ai.drone"::name="drone_1"::pose="120 120 2 0 0 200"::firmware="https://firmware.parrot.com/Versions/anafi2/pc/%23latest/images/anafi2-pc.ext2.zip"
```

**Terminal 2 - UE4:**
```bash
parrot-ue4-industrial-city
```

**Terminal 3 - FastAPI Server:**
```bash
cd Olympe-web-server
FAST_MISSION_DSL_MODEL=mistral-tiny-latest FAST_MISSION_MAX_TOKENS=900 uv run fastapi_entrypoint.py
```

**Terminal 4 - Chat Client:**
```bash
cd client_debug
uv run chat_client.py
```


Simulator (Parrot Sphinx)
-------------------------

- Install and run Sphinx per Parrot docs, then start a simulated ANAFI near your POI of interest.
- Ensure the `DRONE_IP` matches the simulated drone endpoint.
- Use the same Discord commands; the driver should detect simulator vs real device by connection parameters.


Safety and policies
-------------------

- The system must refuse missions that violate configured constraints (geofence, altitude, battery, no-fly zones if available).
- Always test in Sphinx first; only then proceed to hardware.
- For hardware flights: ensure visual line of sight, legal compliance, and safe environment.
- Provide an "emergency stop" command and bind to a quick Discord action.


Testing
-------

- Unit tests: `pytest -q`
- Integration tests: run against Sphinx; the CI can spin a headless sim if available.
- Add fixtures/mocks for LLM responses; never test against live LLMs in CI.


---

## Implemented Features ✅

- ✅ Natural language processing with Mistral AI
- ✅ WebSocket-based real-time communication
- ✅ Mission DSL generation and validation
- ✅ Takeoff, move_to, POI inspection, RTH, landing
- ✅ User confirmation before mission execution
- ✅ Safety constraints (altitude, geofencing, battery)
- ✅ Parrot Sphinx + UE4 integration
- ✅ Real-time execution status updates
- ✅ Robust RTH with automatic landing detection
- ✅ Singular/plural POI selection logic
- ✅ Olympe logging verbosity control

## Roadmap

### Short-term
- [ ] NextJS web interface (replace terminal chat client)
- [ ] Video streaming capture during POI inspection
- [ ] Enhanced error recovery and mission resume
- [ ] Multiple drone support (swarm coordination)

### Mid-term
- [ ] Discord bot integration (legacy code modernization)
- [ ] Mission history and replay
- [ ] Custom POI definition via UI
- [ ] Advanced patterns: orbit, facade inspection, corridor mapping
- [ ] Weather and wind safety checks

### Long-term
- [ ] Real ANAFI Ai hardware integration
- [ ] Computer vision for autonomous inspection
- [ ] AI-powered anomaly detection
- [ ] Multi-modal input (voice, images, sketches)


References
----------

- Parrot Olympe SDK documentation: https://developer.parrot.com/docs/olympe/index.html
 - Olympe control methods catalog (this repo): docs/Olympe_Control_Methods.md


License
-------

TBD (e.g., MIT). Ensure third-party licenses are respected.


