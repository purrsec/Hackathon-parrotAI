ParrotAI Intel Agent — Discord Conversational Interface for Parrot Olympe
========================================================================

Build a modular, multi-contributor agent that turns natural language into safe and executable flight plans for Parrot ANAFI drones using the Olympe SDK. Users issue plain-language commands via Discord (e.g. `!intel je veux faire un survol autour de la tour DesChamps puis reviens`) and the system parses, plans, validates, and executes the mission in simulation or on a real drone.

Reference: Parrot Olympe SDK docs: https://developer.parrot.com/docs/olympe/index.html


TL;DR
-----

1. Create `.env` with your tokens and settings (see "Configuration").
2. Install deps (choose one):
   - uv: `uv venv .venv && source .venv/bin/activate && uv pip install -r requirements.txt` (or `uv sync` if using `pyproject.toml`)
   - Docker: `docker compose up -d dev && docker compose exec dev bash`
3. Start Sphinx simulator (optional, recommended during dev). See "Simulator (Parrot Sphinx)".
4. Run the bot: `uv run python -m apps.discord_bot` (or `python -m apps.discord_bot` with the venv activated).
5. In Discord, type: `!intel je veux faire un survol autour de la tour DesChamps puis reviens`.


Why this project
----------------

- Natural-language tasking of Parrot drones through Discord.
- Safety-first orchestration: planning, constraints, validation, and dry-run in simulator.
- Modular architecture to enable parallel work across small, well-defined modules (avoid monoliths).


High-level architecture
----------------------

```
Discord (user)  ->  Discord Bot  ->  NLP Agent (LLM)  ->  Mission Planner
                        |                     |                |
                        v                     |                v
                  Command Router              |         Validation/Policies
                        |                     |                |
                        v                     v                v
                     Olympe Driver  <----  Mission DSL  ->  Execution Engine
                        |
                        v
                Drone (real) / Sphinx (sim)
```

- Discord Bot: Receives `!intel ...` commands, handles replies.
- NLP Agent: Uses an LLM (Claude / OpenAI / etc.) to parse free text into a Mission DSL (JSON) + constraints.
- Mission Planner: Validates and converts the Mission DSL into Olympe commands.
- Olympe Driver: Connects to drone or simulator and executes commands with telemetry/feedback.
- Policy/Validation: Safety checks (geofence, max altitude/speed, RTH availability, battery margins).


Repository layout (proposed)
----------------------------

```
.
├─ apps/
│  ├─ discord_bot/           # Entry point for Discord bot
│  └─ cli/                   # Optional: local CLI runner for offline tests
├─ core/
│  ├─ nlp_agent/             # LLM interface + prompt templates + schemas
│  ├─ mission_dsl/           # JSON schema + validators + converters
│  ├─ planner/               # Path planning, waypoints, orbit, RTH logic
│  ├─ policies/              # Safety constraints & checks
│  └─ execution/             # Orchestrates Olympe calls from validated plans
├─ adapters/
│  ├─ olympe_driver/         # Thin wrapper over Parrot Olympe SDK
│  └─ geocoding/             # POI resolution (e.g., Nominatim), caching
├─ infra/
│  ├─ config/                # .env templates, settings loader
│  ├─ logging/               # Structured logging setup
│  ├─ docker/                # Dockerfile/devcontainer/compose
│  └─ scripts/               # Helper scripts (start_sphinx, check_env, etc.)
├─ tests/
│  ├─ unit/
│  └─ integration/
├─ requirements.txt or pyproject.toml
├─ .env.example
└─ README.md
```

Conventions for contributors
----------------------------

- Keep modules small and cohesive (single responsibility).
- Public interfaces are typed and documented; no leaking Olympe details outside `adapters/olympe_driver`.
- Prefer dependency injection across modules; avoid global state.
- Use the Mission DSL as the only contract between NLP parsing and planning/execution.
- Always add unit tests for new logic; use Sphinx sim for integration tests before real flights.
- Commit style: concise, imperative; include scope (e.g., `planner: add orbit strategy`).


Mission DSL (JSON) — example
----------------------------

The NLP Agent should output a normalized mission request the planner can safely validate and execute. Example for the command "je veux faire un survol autour de la tour DesChamps puis reviens":

```json
{
  "missionId": "auto-2025-11-07-123456",
  "segments": [
    {
      "type": "takeoff",
      "constraints": { "maxWaitSec": 20 }
    },
    {
      "type": "orbit",
      "poi": { "name": "tour DesChamps" },
      "altitudeMeters": 30,
      "radiusMeters": 20,
      "laps": 1,
      "clockwise": true,
      "speedMetersPerSecond": 3
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
    "maxAltitudeMeters": 60,
    "minBatteryPercent": 25
  }
}
```

The planner is responsible for POI resolution (geocoding), airspace/geofence checks, battery/time feasibility, and converting to Olympe commands.


Discord usage
-------------

- Prefix: `!intel`
- Examples:
  - `!intel fais un cercle de 20m autour de la tour DesChamps à 30m d'altitude`
  - `!intel décolle, va au point (48.858370, 2.294481) puis RTH`
  - `!intel inspection lente de la façade nord, vitesse 1.5 m/s`

The bot will respond with:
1) Parsed Mission DSL preview
2) Safety/feasibility report and required confirmations
3) Execution status updates (sim or real)


Olympe & Parrot Sphinx
----------------------

- Olympe SDK allows Python control of Parrot ANAFI drones (ANAFI, ANAFI Thermal, ANAFI USA, ANAFI AI). See docs: https://developer.parrot.com/docs/olympe/index.html
- During development, prefer the Sphinx simulator for safety, then move to hardware-in-the-loop.

Basic Olympe workflow (conceptual):
1. Connect to drone/sim
2. Wait for states (GPS fix, battery, ready)
3. Send piloting commands (takeoff, move, orbit, RTH, land)
4. Monitor state/telemetry and enforce safety policies


Prerequisites
-------------

- Python 3.10+ recommended
- A Discord bot token and a test server
- Optional: Access to an LLM provider (Anthropic Claude, OpenAI, etc.)
- For Olympe:
  - On x86_64 Debian/Ubuntu, you can install Olympe via `uv` (pip-compatible) (see official docs)
  - On other distros (e.g., Arch), prefer Docker/devcontainer or a Debian-based container for Olympe
- For simulation: Parrot Sphinx installed and configured


Setup
-----

Using uv
```
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
# or, if using pyproject.toml:
uv sync
```

Using Docker (recommended for non-Debian hosts)
```
docker compose up -d dev
docker compose exec dev bash
python -m apps.discord_bot
```


Configuration
-------------

Copy `.env.example` to `.env` and set:

```
# Discord
DISCORD_BOT_TOKEN=...
DISCORD_GUILD_ID=...

# LLM (choose your provider)
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...

# Olympe / Drone
DRONE_IP=192.168.42.1            # physical drone default, or sim IP
RTH_ALTITUDE_METERS=30
MAX_ALTITUDE_METERS=60
MIN_BATTERY_PERCENT=25

# Geocoding (optional)
NOMINATIM_BASE_URL=https://nominatim.openstreetmap.org
```


Running the bot
---------------

```
# Option A: run within the venv
source .venv/bin/activate
python -m apps.discord_bot

# Option B: run without activating the venv
uv run python -m apps.discord_bot
```

Invite the bot to your Discord server and post a command in a channel the bot can read.


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


Roadmap
-------

- POI name resolution with caching and disambiguation prompts
- Rich safety model (wind, GNSS accuracy, distance from home, link quality)
- Video streaming capture and media management via Olympe
- Interactive mission editing in Discord threads (approve/adjust segments)
- Advanced patterns: lawnmower, facade inspection, 3D orbit, corridor mapping


References
----------

- Parrot Olympe SDK documentation: https://developer.parrot.com/docs/olympe/index.html
 - Olympe control methods catalog (this repo): docs/Olympe_Control_Methods.md


License
-------

TBD (e.g., MIT). Ensure third-party licenses are respected.


