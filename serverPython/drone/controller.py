"""
Contrôleur du drone - Gère les commandes Olympe
"""

import logging
import time
from typing import Optional, Any

# Imports conditionnels pour supporter exécution directe et import comme module
try:
    from ..models.command import Command, CommandResponse, ok, err
    from .state import DroneState
except ImportError:
    from models.command import Command, CommandResponse, ok, err
    from drone.state import DroneState

logger = logging.getLogger(__name__)

# Import Olympe
try:
    import olympe
    from olympe.messages.ardrone3.Piloting import TakeOff, Landing, moveBy, moveTo, Circle
    from olympe.messages.ardrone3.PilotingState import FlyingStateChanged
    from olympe.enums.ardrone3.Piloting import Circle_Direction, MoveTo_Orientation_mode
    OLYMPE_AVAILABLE = True
except ImportError:
    logger.warning("Olympe non disponible - mode mock activé")
    OLYMPE_AVAILABLE = False
    olympe = None
    TakeOff = Landing = moveBy = moveTo = Circle = None
    FlyingStateChanged = None
    Circle_Direction = MoveTo_Orientation_mode = None


class DroneController:
    """Contrôleur principal du drone"""
    
    def __init__(self, drone_state: DroneState, drone_ip: str = "10.202.0.1"):
        self.drone_state = drone_state
        self.drone_ip = drone_ip
        self.drone: Optional[Any] = None
        self.olympe_available = OLYMPE_AVAILABLE
    
    def connect(self):
        """Connecte le drone"""
        if self.olympe_available and olympe:
            try:
                self.drone = olympe.Drone(self.drone_ip)
                self.drone.connect()
                self.drone_state.update_state(connected=True)
                logger.info(f"Drone connecté à {self.drone_ip}")
            except Exception as e:
                logger.error(f"Erreur de connexion au drone: {e}")
                self.drone_state.update_state(connected=False)
        else:
            logger.info("Mode mock activé - Olympe non disponible")
            self.drone_state.update_state(connected=True)
    
    def disconnect(self):
        """Déconnecte le drone"""
        if self.drone and self.olympe_available:
            try:
                self.drone.disconnect()
                logger.info("Drone déconnecté")
            except Exception as e:
                logger.error(f"Erreur lors de la déconnexion: {e}")
    
    async def handle_takeoff(self, cmd: Command) -> CommandResponse:
        """Gère la commande de décollage"""
        alt_m = cmd.parameters.get("alt_m", 10)
        logger.info(f"   🚁 Décollage demandé à {alt_m}m d'altitude")
        
        if self.olympe_available and self.drone:
            try:
                logger.info(f"   🚁 Décollage...")
                result = self.drone(TakeOff() >> FlyingStateChanged(state="hovering", _timeout=10)).wait()
                if result.success():
                    self.drone_state.update_state(state="hovering")
                    current_alt = self.drone_state.state["gps"].get("alt", 0)
                    
                    # Si l'altitude demandée est différente, ajuster
                    if alt_m != current_alt:
                        alt_diff = alt_m - current_alt
                        logger.info(f"   📈 Ajustement d'altitude: {alt_diff}m")
                        result = self.drone(moveBy(0, 0, alt_diff, 0) >> FlyingStateChanged(state="hovering", _timeout=30)).wait()
                        if not result.success():
                            logger.warning(f"   ⚠️  Échec de l'ajustement d'altitude")
                    
                    self.drone_state.update_gps(alt=alt_m)
                    logger.info(f"   ✓ Décollage réussi - État: hovering, Altitude: {alt_m}m")
                    return ok(cmd.id, f"Décollage réussi à {alt_m}m", {
                        "altitude": alt_m,
                        "state": self.drone_state.state["state"]
                    })
                else:
                    return err(cmd.id, "Échec du décollage")
            except Exception as e:
                logger.error(f"   ❌ Erreur décollage: {e}")
                logger.exception(e)
                return err(cmd.id, f"Erreur décollage: {str(e)}")
        else:
            # Mode mock
            logger.info(f"   [MOCK] Simulation du décollage...")
            time.sleep(0.5)
            self.drone_state.update_state(state="hovering")
            self.drone_state.update_gps(alt=alt_m)
            logger.info(f"   [MOCK] ✓ Décollage simulé - État: hovering, Altitude: {alt_m}m")
            return ok(cmd.id, f"[MOCK] Décollage réussi à {alt_m}m", {
                "altitude": alt_m,
                "state": self.drone_state.state["state"]
            })
    
    async def handle_goto(self, cmd: Command) -> CommandResponse:
        """Gère la commande de déplacement vers un point GPS"""
        lat = cmd.parameters.get("lat")
        lon = cmd.parameters.get("lon")
        alt_m = cmd.parameters.get("alt_m")
        speed_mps = cmd.parameters.get("speed_mps", 5)
        orientation_mode_str = cmd.parameters.get("orientation_mode", "TO_TARGET")
        heading = cmd.parameters.get("heading", 0.0)
        
        logger.info(f"   🗺️  Navigation demandée:")
        logger.info(f"      Destination: ({lat}, {lon})")
        logger.info(f"      Altitude: {alt_m}m")
        logger.info(f"      Vitesse: {speed_mps} m/s")
        logger.info(f"      Orientation: {orientation_mode_str}")
        logger.info(f"      Heading: {heading}°")
        
        if lat is None or lon is None or alt_m is None:
            logger.error(f"   ❌ Paramètres manquants: lat={lat}, lon={lon}, alt_m={alt_m}")
            return err(cmd.id, "Paramètres manquants: lat, lon, alt_m requis")
        
        if self.olympe_available and self.drone:
            try:
                orientation_map = {
                    "NONE": MoveTo_Orientation_mode.NONE,
                    "TO_TARGET": MoveTo_Orientation_mode.TO_TARGET,
                    "HEADING_START": MoveTo_Orientation_mode.HEADING_START,
                    "HEADING_DURING": MoveTo_Orientation_mode.HEADING_DURING,
                }
                orientation_mode = orientation_map.get(orientation_mode_str, MoveTo_Orientation_mode.TO_TARGET)
                heading_deg = float(heading)
                
                logger.info(f"   🗺️  Exécution moveTo avec orientation_mode={orientation_mode_str}, heading={heading_deg}°")
                
                result = self.drone(moveTo(lat, lon, alt_m, orientation_mode, heading_deg) >> FlyingStateChanged(state="hovering", _timeout=30)).wait()
                
                if result.success():
                    self.drone_state.update_gps(lat=lat, lon=lon, alt=alt_m)
                    self.drone_state.update_state(state="hovering")
                    logger.info(f"   ✓ Déplacement réussi vers ({lat}, {lon}) à {alt_m}m")
                    return ok(cmd.id, f"Déplacement vers ({lat}, {lon}) à {alt_m}m", {
                        "gps": self.drone_state.state["gps"],
                        "state": self.drone_state.state["state"]
                    })
                else:
                    logger.error(f"   ❌ Échec du déplacement")
                    return err(cmd.id, "Échec du déplacement")
            except Exception as e:
                logger.error(f"   ❌ Erreur déplacement: {e}")
                logger.exception(e)
                return err(cmd.id, f"Erreur déplacement: {str(e)}")
        else:
            # Mode mock
            logger.info(f"   [MOCK] Simulation du déplacement...")
            time.sleep(1)
            self.drone_state.update_gps(lat=lat, lon=lon, alt=alt_m)
            self.drone_state.update_state(state="flying")
            logger.info(f"   [MOCK] ✓ Position mise à jour: {self.drone_state.state['gps']}")
            return ok(cmd.id, f"[MOCK] Déplacement vers ({lat}, {lon}) à {alt_m}m", {
                "gps": self.drone_state.state["gps"],
                "state": self.drone_state.state["state"]
            })
    
    async def handle_circle(self, cmd: Command) -> CommandResponse:
        """Gère la commande d'orbite circulaire"""
        target_lat = cmd.parameters.get("target_lat")
        target_lon = cmd.parameters.get("target_lon")
        alt_m = cmd.parameters.get("alt_m")
        radius_m = cmd.parameters.get("radius_m", 50)
        laps = cmd.parameters.get("laps", 1)
        direction_str = cmd.parameters.get("direction", "default")
        
        logger.info(f"   ⭕ Orbite demandée:")
        logger.info(f"      Centre: ({target_lat}, {target_lon})")
        logger.info(f"      Altitude: {alt_m}m")
        logger.info(f"      Rayon: {radius_m}m")
        logger.info(f"      Tours: {laps}")
        logger.info(f"      Direction: {direction_str}")
        
        if target_lat is None or target_lon is None or alt_m is None:
            logger.error(f"   ❌ Paramètres manquants")
            return err(cmd.id, "Paramètres manquants: target_lat, target_lon, alt_m requis")
        
        if self.olympe_available and self.drone:
            try:
                direction_map = {
                    "CW": Circle_Direction.CW,
                    "CCW": Circle_Direction.CCW,
                    "default": Circle_Direction.default
                }
                direction_enum = direction_map.get(direction_str, Circle_Direction.default)
                
                # Aller au centre de l'orbite
                logger.info(f"   🗺️  Navigation vers le centre de l'orbite...")
                result = self.drone(moveTo(target_lat, target_lon, alt_m, MoveTo_Orientation_mode.TO_TARGET, 0.0) >> FlyingStateChanged(state="hovering", _timeout=30)).wait()
                
                if not result.success():
                    return err(cmd.id, "Échec du déplacement vers le centre de l'orbite")
                
                # Effectuer l'orbite pour chaque tour
                for lap in range(laps):
                    logger.info(f"   ⭕ Tour {lap + 1}/{laps} en direction {direction_str}...")
                    result = self.drone(Circle(direction=direction_enum, _timeout=30) >> FlyingStateChanged(state="hovering", _timeout=30)).wait()
                    
                    if not result.success():
                        return err(cmd.id, f"Échec de l'orbite au tour {lap + 1}")
                
                self.drone_state.update_gps(lat=target_lat, lon=target_lon, alt=alt_m)
                self.drone_state.update_state(state="hovering")
                logger.info(f"   ✓ Orbite effectuée avec succès")
                return ok(cmd.id, f"Orbite effectuée autour de ({target_lat}, {target_lon})", {
                    "target": {"lat": target_lat, "lon": target_lon},
                    "radius": radius_m,
                    "laps": laps,
                    "direction": direction_str,
                    "state": self.drone_state.state["state"]
                })
            except Exception as e:
                logger.error(f"   ❌ Erreur orbite: {e}")
                logger.exception(e)
                return err(cmd.id, f"Erreur orbite: {str(e)}")
        else:
            # Mode mock
            logger.info(f"   [MOCK] Simulation de l'orbite...")
            time.sleep(2)
            self.drone_state.update_state(state="flying")
            logger.info(f"   [MOCK] ✓ Orbite simulée")
            return ok(cmd.id, f"[MOCK] Orbite effectuée autour de ({target_lat}, {target_lon})", {
                "target": {"lat": target_lat, "lon": target_lon},
                "radius": radius_m,
                "laps": laps,
                "direction": direction_str
            })
    
    async def handle_capture(self, cmd: Command) -> CommandResponse:
        """Gère la commande de capture photo/vidéo"""
        capture_type = cmd.parameters.get("type", "photo")
        duration_s = cmd.parameters.get("duration_s", 10)
        
        logger.info(f"   📸 Capture demandée: {capture_type}")
        
        if self.olympe_available and self.drone:
            try:
                # À implémenter avec MediaRecordState selon la doc Olympe
                return ok(cmd.id, f"Capture {capture_type} effectuée", {
                    "type": capture_type,
                    "duration": duration_s if capture_type == "video" else None,
                    "artifact_url": f"/media/{int(time.time())}.{'mp4' if capture_type == 'video' else 'jpg'}"
                })
            except Exception as e:
                return err(cmd.id, f"Erreur capture: {str(e)}")
        else:
            # Mode mock
            logger.info(f"   [MOCK] Simulation de la capture...")
            time.sleep(0.5)
            artifact_url = f"/media/{int(time.time())}.{'mp4' if capture_type == 'video' else 'jpg'}"
            logger.info(f"   [MOCK] ✓ Capture simulée - URL: {artifact_url}")
            return ok(cmd.id, f"[MOCK] Capture {capture_type} effectuée", {
                "type": capture_type,
                "duration": duration_s if capture_type == "video" else None,
                "artifact_url": artifact_url
            })
    
    async def handle_return_to_home(self, cmd: Command) -> CommandResponse:
        """Gère la commande de retour au point de départ"""
        home = self.drone_state.state["home"]
        logger.info(f"   🏠 Retour au point de départ demandé: {home}")
        
        if self.olympe_available and self.drone:
            try:
                result = self.drone(moveTo(home["lat"], home["lon"], home["alt"], MoveTo_Orientation_mode.TO_TARGET, 0.0) >> FlyingStateChanged(state="hovering", _timeout=30)).wait()
                if result.success():
                    self.drone_state.update_gps(lat=home["lat"], lon=home["lon"], alt=home["alt"])
                    self.drone_state.update_state(state="hovering")
                    return ok(cmd.id, "Retour au point de départ réussi", {
                        "gps": self.drone_state.state["gps"]
                    })
                else:
                    return err(cmd.id, "Échec du retour au point de départ")
            except Exception as e:
                return err(cmd.id, f"Erreur retour: {str(e)}")
        else:
            # Mode mock
            logger.info(f"   [MOCK] Simulation du retour à la base...")
            time.sleep(2)
            self.drone_state.update_gps(lat=home["lat"], lon=home["lon"], alt=home["alt"])
            self.drone_state.update_state(state="hovering")
            logger.info(f"   [MOCK] ✓ Retour simulé")
            return ok(cmd.id, "[MOCK] Retour au point de départ réussi", {
                "gps": self.drone_state.state["gps"]
            })
    
    async def handle_land(self, cmd: Command) -> CommandResponse:
        """Gère la commande d'atterrissage"""
        logger.info(f"   🛬 Atterrissage demandé")
        if self.olympe_available and self.drone:
            try:
                result = self.drone(Landing() >> FlyingStateChanged(state="landed", _timeout=10)).wait()
                if result.success():
                    self.drone_state.update_state(state="idle")
                    self.drone_state.update_gps(alt=0)
                    return ok(cmd.id, "Atterrissage réussi", {
                        "state": self.drone_state.state["state"]
                    })
                else:
                    return err(cmd.id, "Échec de l'atterrissage")
            except Exception as e:
                return err(cmd.id, f"Erreur atterrissage: {str(e)}")
        else:
            # Mode mock
            logger.info(f"   [MOCK] Simulation de l'atterrissage...")
            time.sleep(1)
            self.drone_state.update_state(state="idle")
            self.drone_state.update_gps(alt=0)
            logger.info(f"   [MOCK] ✓ Atterrissage simulé")
            return ok(cmd.id, "[MOCK] Atterrissage réussi", {
                "state": self.drone_state.state["state"]
            })
    
    async def handle_status(self, cmd: Command) -> CommandResponse:
        """Gère la requête de statut du drone"""
        # Mettre à jour la batterie (simulation de décharge)
        if self.drone_state.state["state"] in ["flying", "hovering"]:
            battery = max(0, self.drone_state.state["battery"] - 0.1)
            self.drone_state.update_state(battery=battery)
        
        return ok(cmd.id, "Statut récupéré", {
            "state": self.drone_state.state["state"],
            "battery_pct": self.drone_state.state["battery"],
            "gps": self.drone_state.state["gps"],
            "connected": self.drone_state.state["connected"],
            "message": f"Drone en état: {self.drone_state.state['state']}"
        })

