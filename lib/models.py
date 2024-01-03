"""Model of the virtual Wind Tunnel."""

from dataclasses import dataclass, asdict
from typing import Tuple, Dict, Optional

@dataclass
class WindTunnel:
    """Wind tunnel model"""

    flow_velocity: Tuple[float, float, float] = (30, 0, 0)
    domain: Optional[Dict[str, list]] = None

    def __post_init__(self):
        velocity_magnitude = self.flow_velocity[0]**2 + \
                        self.flow_velocity[1]**2 + \
                        self.flow_velocity[2]**2  
        assert velocity_magnitude < 100**2 # Magnitude must be less than 100 m/s
        if self.domain is None:
            self.domain = {"x": [-5, 15], "y": [-4, 4], "z": [0, 8]}

        assert list(self.domain.keys()) == ["x", "y", "z"]

    def to_dict(self):
        """Converts the object to a dictionary."""
        return asdict(self)
