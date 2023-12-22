"""Exampel run of a WindTunnel scenario based on Inductiva API."""
from . import modelos
from lib import scenarios
from lib import post_processing

# Initialize the scenario
wind_tunnel = modelos.WindTunnel(
    flow_velocity=[30, 0, 0],
    domain={"x": [-5, 15], "y": [-5, 5], "z": [0, 8]})

sim_parameters = modelos.SimulationParameters()

scenario = scenarios.WindTunnelScenario(wind_tunnel=wind_tunnel)

task = scenario.simulate(object_path="vehicle.obj",
                         sim_params=sim_parameters)


task.wait()

# Download Results
output_dir = task.download_outputs()

# Post-process Class
output = post_processing.WindTunnelOutput(output_dir)

# Get the pressure field
pressure = output.get_object_pressure_field(save_path="pressure_field.vtk")

# Render the pressure field
pressure.render()
