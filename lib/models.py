"""Model of the virtual Wind Tunnel."""

from dataclasses import dataclass, asdict
from typing import Tuple
import numpy as np


@dataclass
class WindTunnel:
    """Wind tunnel model"""

    flow_velocity: Tuple[float, float, float] = (30, 0, 0)
    x_min: float = -5
    x_max: float = 15
    y_min: float = -5
    y_max: float = 5
    z_min: float = 0
    z_max: float = 8

    def __post_init__(self):
        # Airflow velocity magnitude must be less than 100m/s
        assert np.linalg.norm(self.flow_velocity) < 100

        assert self.x_min < self.x_max
        assert self.y_min < self.y_max
        assert self.z_min < self.z_max

    def to_dict(self):
        """Converts the object to a dictionary."""
        return asdict(self)
