"""Exampel run of a WindTunnel scenario based on Inductiva API."""
import wind_tunnel
import post_processing

# Initialize the scenario
windtunnel_scenario = wind_tunnel.WindTunnel(flow_velocity=[30, 0, 0],
                                             domain={
                                                 "x": [-5, 15],
                                                 "y": [-5, 5],
                                                 "z": [0, 8]
                                             })

# Run a simulation
task = windtunnel_scenario.simulate(object_path="vehicle.obj",
                                    num_iterations=50,
                                    resolution=2)

task.wait()

# Download Results
output_dir = task.download_outputs()

# Post-process Class
output = post_processing.WindTunnelOutput(output_dir)

# Get the pressure field
pressure = output.get_object_pressure_field(save_path="pressure_field.vtk")

# Render the pressure field
pressure.render()
