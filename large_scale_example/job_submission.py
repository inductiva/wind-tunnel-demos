"""Submits simulations to the API."""
import os

from absl import app
from absl import flags

import numpy as np

from lib import models
from lib import scenarios

import inductiva

FLAGS = flags.FLAGS

flags.DEFINE_string("input_dataset", None, "Path to the dataset of objects.")
flags.DEFINE_string("working_dir", None, "Path to the working dir.")

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

flags.mark_flag_as_required("input_dataset")
flags.mark_flag_as_required("flow_velocity_range_x")
flags.mark_flag_as_required("flow_velocity_range_y")
flags.mark_flag_as_required("flow_velocity_range_z")


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


def make_machine_group(machine_type, num_machines, disk_size_gb,
                       elastic_machine_group):
    if elastic_machine_group:
        return inductiva.resources.ElasticMachineGroup(
            machine_type=machine_type,
            min_machines=1,
            max_machines=num_machines,
            disk_size_gb=disk_size_gb)
    return inductiva.resources.MachineGroup(machine_type=machine_type,
                                            num_machines=num_machines,
                                            disk_size_gb=disk_size_gb)


def main(_):
    object_paths = [
        os.path.join(FLAGS.input_dataset, path)
        for path in os.listdir(FLAGS.input_dataset)
    ]

    if FLAGS.working_dir is not None:
        inductiva.working_dir = FLAGS.working_dir

    flow_velocity_range_x = list(map(float, FLAGS.flow_velocity_range_x))
    flow_velocity_range_y = list(map(float, FLAGS.flow_velocity_range_y))
    flow_velocity_range_z = list(map(float, FLAGS.flow_velocity_range_z))

    domain_x = list(map(float, FLAGS.x_domain))
    domain_y = list(map(float, FLAGS.y_domain))
    domain_z = list(map(float, FLAGS.z_domain))

    machine_group = make_machine_group(FLAGS.machine_type, FLAGS.num_machines,
                                       FLAGS.disk_size_gb,
                                       FLAGS.elastic_machine_group)
    machine_group.start()

    for object_path in object_paths:
        for _ in range(FLAGS.num_simulations_per_object):
            run_simulation(object_path, flow_velocity_range_x,
                           flow_velocity_range_y, flow_velocity_range_z,
                           domain_x, domain_y, domain_z, FLAGS.num_iterations,
                           FLAGS.resolution, machine_group)


if __name__ == '__main__':
    app.run(main)
