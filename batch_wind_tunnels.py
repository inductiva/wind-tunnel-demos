"""Submits simulations to the API."""
import numpy as np

from lib import models
from lib import scenarios

import inductiva

OBJECT_PATH = "metaballs/metaball.obj"
WORKING_DIR = None

FLOW_VELOCITY_RANGE_X = [20, 30]
FLOW_VELOCITY_RANGE_Y = [0, 0]
FLOW_VELOCITY_RANGE_Z = [0, 0]
NUM_SIMULATIONS_PER_OBJECT = 1

DOMAIN_X = [-5, 20]
DOMAIN_Y = [-5, 5]
DOMAIN_Z = [0, 8]
NUM_ITERATIONS = 100
RESOLUTION = 2

MACHINE_TYPE = "c2-standard-16"
NUM_MACHINES = 1
DISK_SIZE_GB = 70


def run_simulation(machine_group):
    flow_velocity = [
        np.random.uniform(FLOW_VELOCITY_RANGE_X[0], FLOW_VELOCITY_RANGE_X[1]),
        np.random.uniform(FLOW_VELOCITY_RANGE_Y[0], FLOW_VELOCITY_RANGE_Y[1]),
        np.random.uniform(FLOW_VELOCITY_RANGE_Y[0], FLOW_VELOCITY_RANGE_Z[1]),
    ]
    wind_tunnel = models.WindTunnel(flow_velocity=flow_velocity,
                                    x_min=DOMAIN_X[0],
                                    x_max=DOMAIN_X[1],
                                    y_min=DOMAIN_Y[0],
                                    y_max=DOMAIN_Y[1],
                                    z_min=DOMAIN_Z[0],
                                    z_max=DOMAIN_Z[1])

    sim_parameters = scenarios.SimulationParameters(
        num_iterations=NUM_ITERATIONS, resolution=RESOLUTION)

    scenario = scenarios.WindTunnelScenario(wind_tunnel=wind_tunnel)
    scenario.simulate(object_path=OBJECT_PATH,
                      sim_params=sim_parameters,
                      on=machine_group)


def main():
    if WORKING_DIR is not None:
        inductiva.working_dir = WORKING_DIR

    machine_group = inductiva.resources.MachineGroup(machine_type=MACHINE_TYPE,
                                                     num_machines=NUM_MACHINES,
                                                     disk_size_gb=DISK_SIZE_GB)
    machine_group.start()

    for _ in range(NUM_SIMULATIONS_PER_OBJECT):
        run_simulation(machine_group)


if __name__ == "__main__":
    main()
