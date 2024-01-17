"""Submits simulations to the API."""
import os

import numpy as np

from lib import models
from lib import scenarios

import inductiva

INPUT_DATASET = "Path/to/meshes"
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


def run_simulation(object_path, flow_velocity_range_x, flow_velocity_range_y,
                   flow_velocity_range_z, domain_x, domain_y, domain_z,
                   num_iterations, resolution, machine_group):
    flow_velocity = [
        np.random.uniform(flow_velocity_range_x[0], flow_velocity_range_x[1]),
        np.random.uniform(flow_velocity_range_y[0], flow_velocity_range_y[1]),
        np.random.uniform(flow_velocity_range_y[0], flow_velocity_range_z[1]),
    ]
    wind_tunnel = models.WindTunnel(flow_velocity=flow_velocity,
                                    x_min=domain_x[0],
                                    x_max=domain_x[1],
                                    y_min=domain_y[0],
                                    y_max=domain_y[1],
                                    z_min=domain_z[0],
                                    z_max=domain_z[1])

    sim_parameters = scenarios.SimulationParameters(
        num_iterations=num_iterations, resolution=resolution)

    scenario = scenarios.WindTunnelScenario(wind_tunnel=wind_tunnel)
    scenario.simulate(object_path=object_path,
                      sim_params=sim_parameters,
                      on=machine_group)


def main():
    object_paths = [
        os.path.join(INPUT_DATASET, path) for path in os.listdir(INPUT_DATASET)
    ]

    if WORKING_DIR is not None:
        inductiva.working_dir = WORKING_DIR

    machine_group = inductiva.resources.MachineGroup(machine_type=MACHINE_TYPE,
                                                     num_machines=NUM_MACHINES,
                                                     disk_size_gb=DISK_SIZE_GB)
    machine_group.start()

    for object_path in object_paths:
        for _ in range(NUM_SIMULATIONS_PER_OBJECT):
            run_simulation(object_path, FLOW_VELOCITY_RANGE_X,
                           FLOW_VELOCITY_RANGE_Y, FLOW_VELOCITY_RANGE_Z,
                           DOMAIN_X, DOMAIN_Y, DOMAIN_Z, NUM_ITERATIONS,
                           RESOLUTION, machine_group)


if __name__ == "__main__":
    main()
