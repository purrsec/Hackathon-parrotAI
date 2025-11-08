"""
Coordinate converter for translating local Sphinx coordinates to GPS lat/long.

Derived from actual coordinate pairs from Sphinx simulator.
"""

import math
from typing import Tuple


class CoordinateConverter:
    """
    Converts local Sphinx coordinates to GPS coordinates.
    
    Conversion derived from calibration points:
    - Local (0, 0) -> GPS (48.87892150878906, 2.367792844772339)
    - Local (0, 100) -> GPS (48.87982177734375, 2.367793321609497)
    - Local (100, 110) -> GPS (48.879913330078125, 2.369156837463379)
    """
    
    def __init__(self, origin_lat: float, origin_lon: float, origin_alt: float = 0.0):
        """
        Initialize converter with a reference origin point.
        
        Args:
            origin_lat: Latitude of the origin point (GPS reference)
            origin_lon: Longitude of the origin point (GPS reference)
            origin_alt: Altitude of the origin point in meters (default: 0.0)
        """
        self.origin_lat = origin_lat
        self.origin_lon = origin_lon
        self.origin_alt = origin_alt
        
        # Calibration points from Sphinx
        # Local (0, 0) -> GPS (48.87892150878906, 2.367792844772339)
        # Local (0, 100) -> GPS (48.87982177734375, 2.367793321609497)
        # Local (100, 110) -> GPS (48.879913330078125, 2.369156837463379)
        
        # Calculate conversion factors from calibration data
        # From (0,0) to (0,100): delta_lat = 0.00090026855469, delta_lon ≈ 0
        # So 100 local units in y direction = 0.00090026855469 degrees latitude
        self.degrees_per_unit_y = 0.00090026855469 / 100.0  # latitude direction
        
        # From (0,0) to (100,110): 
        # delta_lat = 0.0009918212890625, delta_lon = 0.00136399269104
        # delta_lat from y component: 110 * degrees_per_unit_y = 0.000990295410159
        # delta_lon from x component: 100 * degrees_per_unit_x = 0.00136399269104
        self.degrees_per_unit_x = 0.00136399269104 / 100.0  # longitude direction
        
        # Origin point (local 0,0) in GPS
        self.origin_lat_calibrated = 48.87892150878906
        self.origin_lon_calibrated = 2.367792844772339
    
    def local_to_gps(
        self, 
        local_x: float, 
        local_y: float, 
        local_z: float = 0.0
    ) -> Tuple[float, float, float]:
        """
        Convert local Sphinx coordinates to GPS coordinates.
        
        Args:
            local_x: Local x coordinate (longitude direction)
            local_y: Local y coordinate (latitude direction)
            local_z: Local z coordinate (altitude in meters)
            
        Returns:
            Tuple of (latitude, longitude, altitude_meters)
        """
        # Calculate GPS coordinates from local coordinates
        # Using calibrated origin and conversion factors
        gps_lat = self.origin_lat_calibrated + (local_y * self.degrees_per_unit_y)
        gps_lon = self.origin_lon_calibrated + (local_x * self.degrees_per_unit_x)
        gps_alt = self.origin_alt + local_z
        
        return (gps_lat, gps_lon, gps_alt)
    
    def gps_to_local(
        self,
        gps_lat: float,
        gps_lon: float,
        gps_alt: float = 0.0
    ) -> Tuple[float, float, float]:
        """
        Convert GPS coordinates to local Sphinx coordinates.
        
        Args:
            gps_lat: Target latitude
            gps_lon: Target longitude
            gps_alt: Target altitude in meters
            
        Returns:
            Tuple of (local_x, local_y, local_z) in local units
        """
        # Calculate local coordinates from GPS
        delta_lat = gps_lat - self.origin_lat_calibrated
        delta_lon = gps_lon - self.origin_lon_calibrated
        
        local_y = delta_lat / self.degrees_per_unit_y
        local_x = delta_lon / self.degrees_per_unit_x
        local_z = gps_alt - self.origin_alt
        
        return (local_x, local_y, local_z)
    
    @staticmethod
    def from_world_map(world_map: dict) -> 'CoordinateConverter':
        """
        Create a converter using the starting position from a world map as origin.
        
        Note: The converter uses calibrated origin (48.87892150878906, 2.367792844772339)
        which corresponds to local (0, 0). The world map starting position should match
        this or be converted.
        
        Args:
            world_map: World map dictionary (loaded from JSON)
            
        Returns:
            CoordinateConverter instance
        """
        # Use the calibrated origin, not the world map starting position
        # since the calibration is based on local (0,0)
        return CoordinateConverter(
            origin_lat=48.87892150878906,
            origin_lon=2.367792844772339,
            origin_alt=world_map['starting_position']['coordinates'].get('altitude_meters', 0.0)
        )


def convert_sphinx_coordinates(
    local_x: float,
    local_y: float,
    local_z: float = 0.0,
    origin_lat: float = 48.87892150878906,
    origin_lon: float = 2.367792844772339,
    origin_alt: float = 0.0
) -> Tuple[float, float, float]:
    """
    Convenience function to convert Sphinx local coordinates to GPS.
    
    Uses calibrated conversion factors derived from Sphinx coordinate pairs.
    
    Args:
        local_x: Local x coordinate (longitude direction)
        local_y: Local y coordinate (latitude direction)
        local_z: Local z coordinate (altitude in meters)
        origin_lat: Reference latitude (default: calibrated origin)
        origin_lon: Reference longitude (default: calibrated origin)
        origin_alt: Reference altitude in meters
        
    Returns:
        Tuple of (latitude, longitude, altitude_meters)
        
    Example:
        # Convert Sphinx local coordinates
        lat, lon, alt = convert_sphinx_coordinates(
            local_x=100.0,  # 100 units east
            local_y=110.0,  # 110 units north
            local_z=20.0    # 20m altitude
        )
    """
    converter = CoordinateConverter(origin_lat, origin_lon, origin_alt)
    return converter.local_to_gps(local_x, local_y, local_z)


def verify_calibration():
    """
    Verify the calibration by converting known points back.
    """
    converter = CoordinateConverter(0, 0, 0)
    
    test_points = [
        (0, 0, (48.87892150878906, 2.367792844772339)),
        (0, 100, (48.87982177734375, 2.367793321609497)),
        (100, 110, (48.879913330078125, 2.369156837463379)),
    ]
    
    print("Calibration Verification:")
    print("=" * 80)
    for local_x, local_y, expected_gps in test_points:
        lat, lon, _ = converter.local_to_gps(local_x, local_y, 0)
        expected_lat, expected_lon = expected_gps
        lat_diff = abs(lat - expected_lat)
        lon_diff = abs(lon - expected_lon)
        
        print(f"Local ({local_x}, {local_y})")
        print(f"  Expected: ({expected_lat}, {expected_lon})")
        print(f"  Got:       ({lat}, {lon})")
        print(f"  Error:     lat={lat_diff:.12f}, lon={lon_diff:.12f}")
        print()


if __name__ == "__main__":
    verify_calibration()

