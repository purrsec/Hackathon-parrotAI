import os
import sys
from typing import Callable


EXIT_SUCCESS = 0
EXIT_IMPORT_ERROR = 2
EXIT_CONNECTION_ERROR = 3
EXIT_TEST_FAILURE = 4


def log(message: str) -> None:
    print(f"[SIMPLE_SMOKE] {message}")


def with_step(name: str, fn: Callable[[], bool]) -> bool:
    log(f"START: {name}")
    ok = fn()
    log(("OK" if ok else "FAIL") + f": {name}")
    return ok


def main() -> int:
    try:
        import olympe  # type: ignore
        from olympe import Drone  # type: ignore
        from olympe.messages.ardrone3.Piloting import (  # type: ignore
            TakeOff,
            Landing,
            moveBy,
        )
        from olympe.messages.ardrone3.PilotingState import FlyingStateChanged  # type: ignore
    except Exception as exc:  # noqa: BLE001
        log(f"Olympe import failed: {exc}")
        return EXIT_IMPORT_ERROR

    drone_ip = os.environ.get("DRONE_IP", "10.202.0.1.")
    climb_alt_m = float(os.environ.get("SMOKE_ALT_M", "2.0"))  # meters to climb after takeoff
    timeout_sec = float(os.environ.get("SMOKE_TIMEOUT_SEC", "25"))

    drone = Drone(drone_ip)
    connected = False

    def step_connect() -> bool:
        nonlocal connected
        log(f"Connecting to drone at {drone_ip} ...")
        try:
            connected = bool(drone.connect())
            if not connected:
                log("Connection failed")
            return connected
        except Exception as exc:  # noqa: BLE001
            log(f"Connection error: {exc}")
            return False

    def step_takeoff() -> bool:
        log("Sending TakeOff ...")
        if not drone(TakeOff()).wait(_timeout=timeout_sec).success():
            log("TakeOff failed")
            return False
        # Wait hovering as a simple ready check
        return bool(drone(FlyingStateChanged(state="hovering")).wait(_timeout=timeout_sec))

    def step_climb() -> bool:
        # Olympe moveBy uses body frame: dz is in meters (down positive), so up is negative
        dz = -abs(climb_alt_m)
        log(f"Climbing {abs(dz)} m ...")
        return bool(drone(moveBy(0.0, 0.0, dz, 0.0)).wait(_timeout=timeout_sec).success())

    def step_land() -> bool:
        log("Sending Landing ...")
        if not drone(Landing()).wait(_timeout=timeout_sec).success():
            log("Landing failed")
            return False
        return bool(drone(FlyingStateChanged(state="landed")).wait(_timeout=timeout_sec))

    steps = [
        ("connect", step_connect),
        ("takeoff", step_takeoff),
        ("climb", step_climb),
        ("land", step_land),
    ]

    overall_ok = True
    try:
        for name, fn in steps:
            if not with_step(name, fn):
                overall_ok = False
                break
    finally:
        if connected:
            try:
                drone.disconnect()
                log("Disconnected")
            except Exception:  # noqa: BLE001
                pass

    if not overall_ok:
        return EXIT_TEST_FAILURE if connected else EXIT_CONNECTION_ERROR
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())


