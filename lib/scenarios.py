"""Physical scenario of a configurable wind tunnel simulation.

A wind tunnel is a tool used in aerodynamic research to study the
effects of air moving past solid objects. Here, the tunnel consists
of a box object in 3D space (x, y, z) space, where air flows in the
positive x-direction with a certain velocity.

An arbitrary object is placed within the tunnel, sucht that air flows
around it, as illustrated in the schematic below:
|--------------------------------|
|->          _____               |
|->        _/     |              |
|->_______|_o___O_|______________|

This scenario solves steady-state continuity and momentum equations
(time-independent) with incompressible flow.
The simulation solves the time-independent equations for several
time steps, based on the state of the previous one. The end goal is
to determine the steady-state of the system, i.e., where the flow
does not change in time anymore.

Currently, the following variables are fixed:
- The fluid being inject is air.
- The flow is incompressible (this restricts the max air velocity).
- Air only flows in the positive x-direction.
- Some post-processing of the data occurs at run-time: streamlines,
pressure_field, cutting planes and force coefficients.
"""

import os
from typing import Optional
from dataclasses import dataclass, asdict

from inductiva import mixins, resources, simulators

from .models import WindTunnel

SCENARIO_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


@dataclass
class SimulationParameters:
    """Simulation-specific configuration parameters"""

    num_iterations: float = 100
    resolution: int = 2

    def to_dict(self):
        """Returns a dictionary representation of the simulation parameters."""
        return asdict(self)


class WindTunnelScenario(mixins.FileManager):
    """WindTunnel scenario."""

    SCENARIO_DIR = "wind_tunnel_input"

    def __init__(self, wind_tunnel: WindTunnel):
        """Initializes the `WindTunnel` conditions.

        Args:
            wind_tunnel: Wind tunnel model.
        """
        self.wind_tunnel = wind_tunnel

    def get_commands(self):
        commands = [
            "runApplication surfaceFeatures",
            "runApplication blockMesh",
            "runApplication decomposePar -copyZero",
            "runParallel snappyHexMesh -overwrite",
            "runParallel potentialFoam",
            "runParallel simpleFoam",
            "runApplication reconstructParMesh -constant",
            "runApplication reconstructPar -latestTime",
        ]

        return commands

    def simulate(
        self,
        object_path: str,
        sim_params: SimulationParameters = SimulationParameters(),
        machine_group: Optional[resources.MachineGroup] = None,
    ):
        """Simulates the wind tunnel scenario synchronously.

        Args:
            object_path: Path to object inserted in the wind tunnel.
            sim_params: Simulation-specific configuration parameters.
            machine_group: The machine group to use for the simulation.
        """

        self.set_root_dir(self.SCENARIO_DIR)
        # add dir first to create the input directory structure from templates
        self.add_dir(SCENARIO_TEMPLATE_DIR, **sim_params.to_dict(),
                     **self.wind_tunnel.to_dict())
        self.add_file(object_path, "constant/triSurface/object.obj")

        task = simulators.OpenFOAM().run(input_dir=self.get_root_dir(),
                                         machine_group=machine_group,
                                         commands=self.get_commands())

        return task
