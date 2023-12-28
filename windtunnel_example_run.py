"""Exampel run of a WindTunnel scenario based on Inductiva API."""
from lib import models
from lib import scenarios
from lib import post_processing

# Initialize the scenario
wind_tunnel = models.WindTunnel(flow_velocity=[30, 0, 0],
                                domain={
                                    "x": [-5, 15],
                                    "y": [-5, 5],
                                    "z": [0, 8]
                                })

# Set the simulation parameters with 200 iterations of the solver and a mesh
# resolution level of 3.
sim_parameters = scenarios.SimulationParameters(num_iterations=200,
                                                resolution=3)

scenario = scenarios.WindTunnelScenario(wind_tunnel=wind_tunnel)

# Submit the simulation task
task = scenario.simulate(object_path="assets/vehicle.obj",
                         sim_params=sim_parameters)

# Wait for the task to finish
task.wait()

# Download all of the output files of the simulation
output_dir = task.download_outputs()

# Initialize a post-processing object from the output directory
output = post_processing.WindTunnelOutput(output_dir)

# Get the pressure field
pressure = output.get_object_pressure_field(save_path="pressure_field.vtk")

# Render the pressure field
pressure.render()
