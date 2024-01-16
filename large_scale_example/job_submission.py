import os

from absl import app
from absl import flags
from absl import logging

import numpy as np

from lib import models
from lib import scenarios
from lib import post_processing

FLAGS = flags.FLAGS

flags.DEFINE_string("input_dataset", None, "Path to the dataset of objects.")

flags.DEFINE_list("flow_velocity_range_x", None,
                  "Range of flow velocity in the x-direction.")
flags.DEFINE_list("flow_velocity_range_y", None,
                  "Range of flow velocity in the y-direction.")
flags.DEFINE_list("flow_velocity_range_z", None,
                  "Range of flow velocity in the z-direction.")
flags.DEFINE_integer("num_simulations_per_object", 1,
                     "Number of simulations to run for each object.")

flags.DEFINE_list("x_domain", [-5, 20], "X geometry of the domain.")
flags.DEFINE_list("y_domain", [-5, 5], "Y geometry of the domain.")
flags.DEFINE_list("z_domain", [0, 8], "Z geometry of the domain.")
flags.DEFINE_integer("num_iterations", 100, "Number of iterations to run.")
flags.DEFINE_integer("resolution", 2, "Mesh resolution.")

flags.DEFINE_string("machine_type", "c2-standard-16", "Machine type.")
flags.DEFINE_integer("num_machines", 1, "Number of machines.")
flags.DEFINE_integer("disk_size_gb", 70, "Disk size in GB.")
flags.DEFINE_boolean("elastic_machine_group", True,
                     "Whether to use an elastic machine group.")


def run_simulation(object_path, flow_velocity_range_x, flow_velocity_range_y,
                   flow_velocity_range_z, domain_x, domain_y, domain_z,
                   num_iterations, resolution):
    flow_velocity = [
        np.random.uniform(flow_velocity_range_x[0], flow_velocity_range_x[1]),
        np.random.uniform(flow_velocity_range_y[0], flow_velocity_range_y[1]),
        np.random.uniform(flow_velocity_range_y[0], flow_velocity_range_z[1]),
    ]
    wind_tunnel = models.WindTunnel(flow_velocity=flow_velocity,
                                    domain={
                                        "x": domain_x,
                                        "y": domain_y,
                                        "z": domain_z
                                    })

    sim_parameters = scenarios.SimulationParameters(
        num_iterations=num_iterations, resolution=resolution)

    scenario = scenarios.WindTunnelScenario(wind_tunnel=wind_tunnel)
    task = scenario.simulate(object_path=object_path, sim_params=sim_parameters)


def main(_):
    object_paths = [
        os.path.join(FLAGS.input_dataset, path)
        for path in os.listdir(FLAGS.input_dataset)
    ]

    flow_velocity_range_x = list(map(float, FLAGS.flow_velocity_range_x))
    flow_velocity_range_y = list(map(float, FLAGS.flow_velocity_range_y))
    flow_velocity_range_z = list(map(float, FLAGS.flow_velocity_range_z))

    domain_x = list(map(float, FLAGS.x_domain))
    domain_y = list(map(float, FLAGS.y_domain))
    domain_z = list(map(float, FLAGS.z_domain))

    for object_path in object_paths:
        for _ in range(FLAGS.num_simulations_per_object):
            run_simulation(object_path, flow_velocity_range_x,
                           flow_velocity_range_y, flow_velocity_range_z,
                           domain_x, domain_y, domain_z, FLAGS.num_iterations,
                           FLAGS.resolution)


if __name__ == '__main__':
    app.run(main)
