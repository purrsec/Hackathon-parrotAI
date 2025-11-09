"""
Mission Executor - Execute a mission DSL (from Mistral) using Parrot Olympe.

This module maps the generated mission JSON to Olympe commands, reusing the
techniques proven in apps/cli/poi_inspection.py (connect, wait_ready,
extended_move_to, StartPilotedPOIV2 + PCMD orbit, RTH, landing).
"""

import logging
import math
import os
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class MissionExecutionError(Exception):
    pass


def _import_olympe():
    """
    Lazy import of Olympe to allow environments where Olympe is not installed.
    Raises a clear error if import fails.
    """
    try:
        import olympe  # type: ignore
        import olympe.log  # type: ignore
        # Reduce Olympe logging verbosity - only show warnings and errors
        olympe.log.update_config({
            "loggers": {
                "olympe": {"level": "WARNING"},
                "ulog": {"level": "WARNING"}
            }
        })
        from olympe import Drone  # type: ignore
        from olympe.messages.ardrone3.Piloting import (  # type: ignore
            TakeOff,
            Landing,
            NavigateHome,
            StartPilotedPOIV2,
            StopPilotedPOI,
            PCMD,
        )
        from olympe.messages.ardrone3.PilotingState import (  # type: ignore
            FlyingStateChanged,
            PilotedPOI,
        )
        from olympe.messages.move import extended_move_to  # type: ignore
        from olympe.messages.obstacle_avoidance import set_mode  # type: ignore
        from olympe.enums.obstacle_avoidance import mode  # type: ignore
        return {
            "Drone": Drone,
            "TakeOff": TakeOff,
            "Landing": Landing,
            "NavigateHome": NavigateHome,
            "StartPilotedPOIV2": StartPilotedPOIV2,
            "StopPilotedPOI": StopPilotedPOI,
            "PCMD": PCMD,
            "FlyingStateChanged": FlyingStateChanged,
            "PilotedPOI": PilotedPOI,
            "extended_move_to": extended_move_to,
            "set_mode": set_mode,
            "oa_mode": mode,
        }
    except Exception as exc:  # noqa: BLE001
        raise MissionExecutionError(
            f"Olympe import failed: {exc}. Ensure Parrot Olympe SDK is installed and accessible."
        ) from exc


def _meters_to_lat_offset_meters(lat_deg: float, meters: float) -> float:
    """
    Convert a northward offset in meters to degrees of latitude.
    Approximation: 1 degree latitude ~ 111,000 meters.
    """
    if meters == 0:
        return 0.0
    return meters / 111000.0


def _clamp(value: float, min_v: float, max_v: float) -> float:
    return max(min_v, min(value, max_v))


def _apply_geofence_altitude(altitude: float, max_altitude_m: Optional[float]) -> float:
    if max_altitude_m is None:
        return altitude
    # Clamp strictly within safe range (>= 1.0m to avoid ground scrape)
    return _clamp(altitude, 1.0, max_altitude_m)


def _validate_mission_dsl(mission: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    if not isinstance(mission, dict):
        raise MissionExecutionError("Mission DSL must be a JSON object")
    segments = mission.get("segments")
    if not isinstance(segments, list) or not segments:
        raise MissionExecutionError("Mission DSL must contain a non-empty 'segments' list")
    safety = mission.get("safety", {})
    # Basic structural checks (non-fatal; log warnings for flexibility)
    first_type = segments[0].get("type")
    last_types = [s.get("type") for s in segments[-2:]]
    if first_type != "takeoff":
        logger.warning("First segment is not 'takeoff' - proceeding but this is non-standard")
    if last_types != ["return_to_home", "land"]:
        logger.warning("Last segments are not ['return_to_home', 'land'] - proceeding but this is non-standard")
    return segments, safety


def _enable_obstacle_avoidance(drone, set_mode, oa_mode, timeout_sec: float) -> None:
    """
    Enable obstacle avoidance in standard mode.
    The drone will automatically adjust its trajectory to avoid obstacles.
    """
    logger.info("Enabling obstacle avoidance (standard mode)...")
    result = drone(set_mode(mode=oa_mode.standard)).wait(_timeout=timeout_sec)
    if not result.success():
        logger.warning(f"Failed to enable obstacle avoidance: {result.explain()}")
        logger.warning("Continuing without obstacle avoidance")
    else:
        logger.info("✓ Obstacle avoidance enabled - drone will auto-correct trajectory")


def _connect_and_prepare(drone, FlyingStateChanged, set_mode, oa_mode, timeout_sec: float) -> None:
    # Connect
    drone_ip = os.environ.get("DRONE_IP", "10.202.0.1")
    logger.info(f"Connecting to drone at {drone_ip} ...")
    if not bool(drone.connect()):
        raise MissionExecutionError("Failed to connect to drone (check simulator/physical drone/network)")
    logger.info("Connected to drone")
    # Wait ready
    logger.info("Waiting for drone to be ready (flying state available)...")
    if not drone(FlyingStateChanged(_policy="check")).wait(_timeout=timeout_sec):
        raise MissionExecutionError("Drone not ready (flying state unavailable)")
    state = drone.get_state(FlyingStateChanged)
    logger.info(f"Initial flying state: {state}")
    # Enable obstacle avoidance
    _enable_obstacle_avoidance(drone, set_mode, oa_mode, timeout_sec)


def _wait_hover(drone, FlyingStateChanged, timeout_sec: float) -> bool:
    return bool(drone(FlyingStateChanged(state="hovering")).wait(_timeout=timeout_sec))


def _segment_takeoff(drone, TakeOff, FlyingStateChanged, timeout_sec: float) -> None:
    logger.info("Segment: takeoff")
    if not drone(TakeOff()).wait(_timeout=timeout_sec).success():
        raise MissionExecutionError("TakeOff command failed")
    if not _wait_hover(drone, FlyingStateChanged, timeout_sec):
        logger.warning("Did not observe hovering state after takeoff")


def _segment_move_to(
    drone,
    extended_move_to,
    FlyingStateChanged,
    segment: Dict[str, Any],
    move_timeout_sec: float,
) -> None:
    lat = float(segment.get("latitude"))
    lon = float(segment.get("longitude"))
    alt = float(segment.get("altitude"))
    max_horizontal_speed = float(segment.get("max_horizontal_speed", 15.0))
    max_vertical_speed = float(segment.get("max_vertical_speed", 2.0))
    max_yaw_rotation_speed = float(segment.get("max_yaw_rotation_speed", 1.0))
    logger.info(
        f"Segment: move_to lat={lat:.6f} lon={lon:.6f} alt={alt} hs={max_horizontal_speed} vs={max_vertical_speed} yaw={max_yaw_rotation_speed}"
    )
    result = drone(
        extended_move_to(
            latitude=lat,
            longitude=lon,
            altitude=alt,
            orientation_mode="to_target",
            heading=0.0,
            max_horizontal_speed=max_horizontal_speed,
            max_vertical_speed=max_vertical_speed,
            max_yaw_rotation_speed=max_yaw_rotation_speed,
        )
    ).wait(_timeout=move_timeout_sec)
    if not result.success():
        raise MissionExecutionError(f"Move_to failed: {result.explain()}")
    # Wait for hover for stability
    drone(FlyingStateChanged(state="hovering")).wait(_timeout=move_timeout_sec)


def _segment_poi_inspection(
    drone,
    StartPilotedPOIV2,
    StopPilotedPOI,
    PCMD,
    PilotedPOI,
    segment: Dict[str, Any],
    command_rate_hz: float,
) -> None:
    poi_name = segment.get("poi_name", "unknown")
    lat = float(segment.get("latitude"))
    lon = float(segment.get("longitude"))
    alt = float(segment.get("altitude"))
    rotation_duration = float(segment.get("rotation_duration", 30.0))
    roll_rate = int(segment.get("roll_rate", 50))
    logger.info(
        f"Segment: poi_inspection name={poi_name} lat={lat:.6f} lon={lon:.6f} alt={alt} duration={rotation_duration}s roll_rate={roll_rate}"
    )
    # Start POI mode
    result = drone(
        StartPilotedPOIV2(latitude=lat, longitude=lon, altitude=alt, mode="locked_gimbal")
    ).wait(_timeout=5)
    if not result.success():
        raise MissionExecutionError(f"StartPilotedPOIV2 failed: {result.explain()}")
    time.sleep(1.0)
    # Optional: observe POI state
    try:
        poi_state = drone.get_state(PilotedPOI)
        if poi_state:
            logger.info(f"POI state: {poi_state}")
    except Exception:
        logger.warning("POI state unavailable")
    # Orbit by constant roll
    total_steps = max(1, int(rotation_duration * command_rate_hz))
    sleep_dt = 1.0 / command_rate_hz
    for _ in range(total_steps):
        drone(PCMD(1, roll_rate, 0, 0, 0, timestampAndSeqNum=0))
        time.sleep(sleep_dt)
    # Stop movement and POI mode
    drone(PCMD(0, 0, 0, 0, 0, timestampAndSeqNum=0))
    try:
        drone(StopPilotedPOI()).wait(_timeout=5)
    except Exception as exc:
        logger.warning(f"StopPilotedPOI warning: {exc}")


def _segment_return_to_home(drone, timeout_sec: float) -> None:
    """
    Return to home. Based on poi_inspection.py approach:
    - Set ending_behavior to landing if supported
    - Start RTH
    - Wait for completion
    Note: With ending_behavior='landing', RTH will land automatically
    """
    logger.info("Segment: return_to_home")
    rth_timeout_sec = float(os.environ.get("RTH_TIMEOUT_SEC", "300"))
    
    try:
        from olympe.messages import rth  # type: ignore
        # Try to set ending behavior first
        try:
            if hasattr(rth, "set_ending_behavior"):
                drone(rth.set_ending_behavior(ending_behavior="landing")).wait(_timeout=timeout_sec)
                logger.info("RTH ending behavior set to 'landing'")
        except Exception as e:
            logger.info(f"Could not set RTH ending behavior: {e}")
        
        # Try return_to_home without 'start' parameter first
        try:
            if not drone(rth.return_to_home()).wait(_timeout=timeout_sec).success():
                raise MissionExecutionError("Failed to start RTH via rth.return_to_home()")
        except (TypeError, KeyError) as e:
            logger.info(f"rth.return_to_home() failed with {e}, trying with start=1")
            if not drone(rth.return_to_home(start=1)).wait(_timeout=timeout_sec).success():
                raise MissionExecutionError("Failed to start RTH via rth.return_to_home")
        
        logger.info("RTH started, waiting for completion...")
        # Wait for RTH completion
        finished = drone(rth.state(state="available", reason="finished")).wait(_timeout=rth_timeout_sec)
        if not finished:
            logger.warning("RTH did not report completion in time")
    except Exception as e:
        # Fallback to NavigateHome
        logger.info(f"rth API not available ({e}); fallback to NavigateHome")
        from olympe.messages.ardrone3.Piloting import NavigateHome  # type: ignore
        # NavigateHome also might not need 'start' parameter
        try:
            if not drone(NavigateHome(start=1)).wait(_timeout=timeout_sec).success():
                raise MissionExecutionError("Failed to start NavigateHome with start=1")
        except (TypeError, KeyError):
            logger.info("NavigateHome(start=1) failed, trying NavigateHome() without parameters")
            if not drone(NavigateHome()).wait(_timeout=timeout_sec).success():
                raise MissionExecutionError("Failed to start NavigateHome")
        time.sleep(5.0)


def _segment_land(drone, Landing, FlyingStateChanged, timeout_sec: float) -> None:
    """
    Land the drone. Based on poi_inspection.py approach.
    This should be called after RTH or as a standalone landing command.
    If RTH was called with ending_behavior='landing', the drone may already be landing.
    """
    logger.info("Segment: land")
    
    # Check current state before attempting landing
    from olympe.messages.ardrone3.PilotingState import FlyingStateChanged as FSC  # type: ignore
    try:
        current_state = drone.get_state(FSC)
        if current_state:
            state_value = current_state.get("state") if isinstance(current_state, dict) else None
            state_str = str(state_value).split(".")[-1] if state_value else None
            logger.info(f"Current flying state before landing: {state_str}")
            
            # If already landed or landing, just wait for confirmation
            if state_str in ["landed", "landing"]:
                logger.info("Drone is already landed or landing, waiting for confirmation...")
                if drone(FlyingStateChanged(state="landed")).wait(_timeout=timeout_sec * 2):
                    logger.info("✓ Drone is landed")
                    return
                else:
                    logger.warning("Landing status not confirmed within timeout, but continuing")
                    return
    except Exception as e:
        logger.warning(f"Could not check flying state: {e}, proceeding with landing command")
    
    # Send landing command
    logger.info("Initiating landing command...")
    land_ok = drone(Landing()).wait(_timeout=timeout_sec * 2).success()
    if not land_ok:
        logger.warning("Landing command did not return success")
    
    # Wait for landed state
    landed = drone(FlyingStateChanged(state="landed")).wait(_timeout=timeout_sec * 2)
    if landed:
        logger.info("✓ Drone landed successfully")
    else:
        logger.warning("Landing status not confirmed within timeout")


def execute_mission(mission_dsl: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """
    Execute a mission DSL on a Parrot drone using Olympe.
    Returns an execution report with status and per-segment results.
    """
    # Import Olympe symbols
    symbols = _import_olympe()
    Drone = symbols["Drone"]
    TakeOff = symbols["TakeOff"]
    Landing = symbols["Landing"]
    NavigateHome = symbols["NavigateHome"]
    StartPilotedPOIV2 = symbols["StartPilotedPOIV2"]
    StopPilotedPOI = symbols["StopPilotedPOI"]
    PCMD = symbols["PCMD"]
    FlyingStateChanged = symbols["FlyingStateChanged"]
    PilotedPOI = symbols["PilotedPOI"]
    extended_move_to = symbols["extended_move_to"]
    set_mode = symbols["set_mode"]
    oa_mode = symbols["oa_mode"]
    # Timeouts and params
    timeout_sec = float(os.environ.get("TIMEOUT_SEC", "25"))
    move_timeout_sec = float(os.environ.get("MOVE_TIMEOUT_SEC", "120"))
    command_rate_hz = float(os.environ.get("COMMAND_RATE_HZ", "20"))
    # Validate mission and extract segments
    segments, safety = _validate_mission_dsl(mission_dsl)
    geofence = safety.get("geofence", {}) if isinstance(safety, dict) else {}
    geofence_enabled = bool(geofence.get("enabled", False))
    max_altitude_m = float(safety.get("maxAltitudeMeters", 80.0)) if isinstance(safety, dict) else None
    min_battery_percent = safety.get("minBatteryPercent") if isinstance(safety, dict) else None
    # Prepare execution report
    report: Dict[str, Any] = {
        "status": "pending",
        "executed_segments": [],
        "failed_segment": None,
        "errors": [],
    }
    drone = Drone(os.environ.get("DRONE_IP", "10.202.0.1"))
    connected = False
    airborne = False
    try:
        if dry_run:
            logger.info("[DRY RUN] Skipping Olympe connection and commands")
        else:
            _connect_and_prepare(drone, FlyingStateChanged, set_mode, oa_mode, timeout_sec)
            connected = True
        for idx, segment in enumerate(segments):
            seg_type = str(segment.get("type", "")).strip()
            if not seg_type:
                raise MissionExecutionError(f"Segment {idx} missing 'type'")
            # Geofence altitude clamp for relevant segments
            if geofence_enabled and max_altitude_m is not None:
                if seg_type in ("move_to", "poi_inspection") and "altitude" in segment:
                    original_alt = float(segment["altitude"])
                    clamped_alt = _apply_geofence_altitude(original_alt, max_altitude_m)
                    if clamped_alt != original_alt:
                        logger.warning(f"Clamping altitude from {original_alt}m to {clamped_alt}m due to geofence")
                        segment = dict(segment)
                        segment["altitude"] = clamped_alt
            start_ts = time.time()
            if seg_type == "takeoff":
                if dry_run:
                    logger.info("[DRY RUN] takeoff")
                else:
                    _segment_takeoff(drone, TakeOff, FlyingStateChanged, timeout_sec)
                    airborne = True
            elif seg_type == "move_to":
                if dry_run:
                    logger.info(f"[DRY RUN] move_to: {segment}")
                else:
                    _segment_move_to(drone, extended_move_to, FlyingStateChanged, segment, move_timeout_sec)
            elif seg_type == "poi_inspection":
                if dry_run:
                    logger.info(f"[DRY RUN] poi_inspection: {segment}")
                else:
                    _segment_poi_inspection(drone, StartPilotedPOIV2, StopPilotedPOI, PCMD, PilotedPOI, segment, command_rate_hz)
            elif seg_type == "return_to_home":
                if dry_run:
                    logger.info("[DRY RUN] return_to_home")
                else:
                    _segment_return_to_home(drone, timeout_sec)
            elif seg_type == "land":
                if dry_run:
                    logger.info("[DRY RUN] land")
                else:
                    _segment_land(drone, Landing, FlyingStateChanged, timeout_sec)
                    airborne = False
            else:
                raise MissionExecutionError(f"Unsupported segment type: {seg_type}")
            elapsed_ms = (time.time() - start_ts) * 1000.0
            report["executed_segments"].append({"index": idx, "type": seg_type, "elapsed_ms": elapsed_ms})
        report["status"] = "completed"
        return report
    except Exception as exc:
        logger.error(f"Mission execution failed: {exc}")
        report["status"] = "error"
        report["failed_segment"] = report["executed_segments"][-1]["index"] + 1 if report["executed_segments"] else 0
        report["errors"].append(str(exc))
        # Safety: attempt RTH + land if airborne
        try:
            if not dry_run and connected and airborne:
                logger.warning("Safety: Attempting Return-To-Home and Landing after failure")
                try:
                    _segment_return_to_home(drone, timeout_sec)
                except Exception as rth_exc:
                    logger.warning(f"RTH attempt failed: {rth_exc}")
                try:
                    _segment_land(drone, Landing, symbols["FlyingStateChanged"], timeout_sec)
                except Exception as land_exc:
                    logger.warning(f"Landing attempt failed: {land_exc}")
        except Exception:
            pass
        return report
    finally:
        if not dry_run and connected:
            try:
                drone.disconnect()
                logger.info("Disconnected from drone")
            except Exception:
                pass


def get_drone_identity(timeout_sec: float = 10.0) -> Dict[str, Any]:
    """
    Best-effort retrieval of a drone identity using Olympe.
    Returns a dict with at least 'id' and 'ip'. If richer metadata is available,
    includes 'model' as well.
    """
    ip = os.environ.get("DRONE_IP", "10.202.0.1")
    # Simplified for hackathon: return a fixed identity without contacting the drone
    return {"id": "drone_1", "ip": ip}


def check_olympe_ready(timeout_sec: float = 10.0) -> Tuple[bool, str]:
    """
    Quick readiness probe: attempts to connect and fetch a basic state.
    Returns (ready, reason).
    """
    try:
        symbols = _import_olympe()
        Drone = symbols["Drone"]
        FlyingStateChanged = symbols["FlyingStateChanged"]
    except Exception as exc:
        return False, f"Olympe import failed: {exc}"
    
    ip = os.environ.get("DRONE_IP", "10.202.0.1")
    drone = Drone(ip)
    try:
        if not bool(drone.connect()):
            return False, f"Failed to connect to drone at {ip}. Is Sphinx/Drone running?"
        # Probe state
        ok = drone(FlyingStateChanged(_policy="check")).wait(_timeout=timeout_sec)
        if not ok:
            return False, "Drone flying state unavailable"
        return True, "ok"
    except Exception as exc:
        return False, f"Exception during readiness check: {exc}"
    finally:
        try:
            drone.disconnect()
        except Exception:
            pass


