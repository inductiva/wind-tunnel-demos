"""Exampel run of a WindTunnel scenario based on Inductiva API."""
from lib import models
from lib import scenarios
from lib import post_processing

# Initialize the scenario
wind_tunnel = models.WindTunnel(flow_velocity=(30, 0, 0),
                                x_min=-5,
                                x_max=15,
                                y_min=-5,
                                y_max=5,
                                z_min=0,
                                z_max=8)

# Set the simulation parameters with 200 iterations of the solver and a mesh
# resolution level of 3.
sim_parameters = scenarios.SimulationParameters(num_iterations=50, resolution=3)

scenario = scenarios.WindTunnelScenario(wind_tunnel=wind_tunnel)

# Submit the simulation task
task = scenario.simulate(object_path="assets/vehicle.obj",
                         sim_params=sim_parameters)

# Wait for the task to finish
task.wait()

# Download all of the output files of the simulation
output_dir = task.download_outputs()

# Post-process methods: Render the pressure field over the object
output = post_processing.WindTunnelOutput(output_dir, 50)

pressure_field = output.get_object_pressure_field()
pressure_field.render()
