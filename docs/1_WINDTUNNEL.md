# Wind Tunnel simulation

In this section, we present an example of a custom virtual
WindTunnel by extending the straightforward API calls of a simulator
with the **Inductiva API**.

This abstraction is designated by **simulation scenario** and is
powered by a powerful templating mechanism which prepares the input
files for the simulation from the essential parameters defining the Wind
Tunnel.

### Modelling the Wind Tunnel

We consider our virtual wind tunnel to be a rectangular box with
variable dimensions in `x, y, z` directions and with air flowing from
left to right on the $x$-axis at a given fixed speed.

For this wind tunnel, we assume incompressible fluid flow, which limits
the airflow maximum speed to 100 m/s.

These characteristics are encapsulated in the following Python data
class (see `lib/models.py` for extra detail on how to handle argument
verification).

``` python
from dataclasses import dataclass, asdict
from typing import Dict, Optional, Tuple

@dataclass
class WindTunnel:
    """Wind tunnel model.
    
    Attributes:
        flow_velocity - a tuple with three values that represents
            the air flow direction and magnitude.
        domain - Dict of the type {"x": [x0, x1], "y": [y0, y1], "z": [z0, z1]}.
    """

    flow_velocity: Tuple[float, float, float] = (30, 0, 0)
    domain: Optional[Dict[str, list]] = None

    def to_dict(self):
        """Converts the object to a dictionary."""
        return asdict(self)
```

A specific virtual WindTunnel configuration is created as follows:

``` python
wind_tunnel = WindTunnel(flow_velocity=(45, 0, 0), 
                         domain={"x": [-4, 15], "y": [-4, 4], "z": [0, 5]})
```

### From Model to Simulation Configuration

Before running any simulation, this programmatic characterization of
the wind tunnel needs to be translated into the input files required by
the simulator.

The **Inductiva API** library provides a powerful mechanism to generate
input files from these parameters using a templating engine. This
mechanism allows users to define template files containing tags that get
replaced with specific values upon rendering. The templating mechanism
is integrated into a file packing interface - the `FileManager` class -
that allows users to easily manage the rendering of the template files.

Consider a simple template file (`template.txt.jinja`) containing the
following content:

``` jinja
# content of template.txt.jinja
flowVelocity ({{ flow_velocity[0] }} {{ flow_velocity[1] }} {{ flow_velocity[2] }});
```

Using a `FileManager` object, this file can be easily rendered and
stored in a user-specified folder:

``` python
from inductiva import mixins

manager = mixins.FileManager()

# specify the user-specific folder where files are to be stored
manager.set_root_dir('myfiles')

# render template.txt.jinja by setting the `particle_radius` to 10
# and specifying the name of the rendered file
manager.add_file('assets/template.txt.jinja', 'assets/rendered.txt',
                 **{"flow_velocity": [10, 0, 0]})
```

By executing the above snippet a `myfiles/` folder is created in the
current working directory, containing the rendered file `rendered.txt`
with the following content:

```
# content of rendered.txt
flowVelocity (10 0 0);
```

> **NOTE**: `FileManager.add_file` also allows non-template files to be
> added to the manager. Files are considered to be templates when ending
> with the `.jinja` extension.
> `FileManager` also provides an `add_dir` method that behaves pretty
> much as `add_file` by copying and rendering all files inside a
> directory.

### Building the scenario

The templating tools above allow the creation of another level of
abstraction on top of pre-defined template files. Users can build a
simple interface to configure the parameters and/or model details,
which makes it easy to deploy multiple simulations.

In this section, we introduce the concept of a **Scenario**, the
abstraction that wraps the model, simulation parameters and job
deployment into a single interface.

#### WindTunnel Scenario

Our virtual `WindTunnelScenario` is configured with the model above,
the vehicle for which we want to test the aerodynamics and with a
few simulation parameters.

Hereby, the physics of air flowing inside the wind tunnel is fixed. For
demonstration purposes, we consider the air to be an incompressible
fluid. The simulations performed are steady-state simulations, which
means that the simulations are time-independent and are run until the
flow reaches a steady state.

All of these are configured in the template files for the simulator in
use. To run the `WindTunnelScenario` we will use the `OpenFOAM`
simulator available via the **Inductiva API**.

The following snippets show the implementation of the simulation
parameters and the `WindTunnelScenario` scenario, respectively:

```python
@dataclass
class SimulationParameters:

    num_iterations: float = 100
    resolution: int = 2

    def to_dict(self):
        return asdict(self)
```

The `SimulationParameters` data class is a placeholder of the parameters
specific to the simulation into a single object, that allows the user to
test different simulation configurations using the same `WindTunnel` and
vehicle.

```python
import inductiva
from inductiva import mixins, resources, simulators

class WindTunnelScenario(mixins.FileManager):
    """WindTunnel scenario."""

    SCENARIO_DIR = "wind_tunnel_input"
    SCENARIO_TEMPLATE_DIR = "lib/templates"

    def __init__(self,
                 wind_tunnel: WindTunnel):
        """Initializes the `WindTunnel` conditions.

        Args:
            wind_tunnel: Wind tunnel model.
        """
        self.wind_tunnel = wind_tunnel

    def get_commands(self):
        commands = [
            {"cmd": "runApplication surfaceFeatures", "prompts": []},
            {"cmd": "runApplication blockMesh", "prompts":[]},
            {"cmd": "runApplication decomposePar -copyZero", "prompts":[]},
            {"cmd": "runParallel snappyHexMesh -overwrite", "prompts":[]},
            {"cmd": "runParallel potentialFoam", "prompts":[]},
            {"cmd": "runParallel simpleFoam", "prompts":[]},
            {"cmd": "runApplication reconstructParMesh -constant", "prompts":[]},
            {"cmd": "runApplication reconstructPar -latestTime", "prompts": []}
        ]

        return commands

    def simulate(self,
                 object_path: str,
                 sim_params: SimulationParameters,
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
        self.add_dir(self.SCENARIO_TEMPLATE_DIR, **sim_params.to_dict(),
                     **self.wind_tunnel.to_dict())
        self.add_file(object_path, "constant/triSurface/object.obj")


        task = simulators.OpenFOAM().run(
            input_dir=self.get_root_dir(),
            machine_group=machine_group,
            commands=self.get_commands())

        return task
```

The `WindTunnelScenario` inherits from `FileManager` all the file
management and rendering tools previously discussed. An instance of the
`WindTunnelScenario` is initialized just with a model of the
`WindTunnel`, and then the vehicle to be tested is passed as an argument to
the `simulate` method. This is merely a design choice, where the
reasoning follows that the wind tunnel is invariant between different
simulation runs, but different vehicles can be tested within the same
wind tunnel. Note, however, that users need not follow this pattern when
implementing their own scenarios.

All the required logic to render the template files and deploy the
simulation is implemented in the `simulate` method. This method consumes
3 arguments: the path to the vehicle to be tested, a
`SimulationParameters` and a `MachineGroup` objects.

Like the template files, the `vehicle_path` needs to be added to the
input directory. For some simulators, like `OpenFOAM`, the user should
set the `vehicle` in a specific directory. The template directory can
already have this directory prepared, and hence by adding/rendering the
template files first, the vehicle can be added to the correct place
afterwards, without extra directory creation.

To run an `OpenFOAM` simulation several commands need to be performed. These, are
defined in the `get_commands()` method of the class and will be executed
sequentially as one single job.

The `MachineGroup` is an **Inductiva API** construct that allows the
user to configure the computational resources used to run the
simulations. By default (`machine_group = None`), the user does not need
to configure this parameter and resources will be managed by default
pool (see the
[MachineGroup](https://github.com/inductiva/inductiva/wiki/Machines)
documentation for details on how to configure and use machine groups).

### Running Wind Tunnel simulations

With the scenario, models and a vehicle (`assets/vehicle.obj`), we are
now ready to `simulate` a virtual wind tunnel!

#### Single simulation

```python
# Initialize a wind tunnel with 45 m/s flow velocity
wind_tunnel = WindTunnel(flow_velocity=(45, 0, 0),
                         domain={"x": [-4, 15], "y": [-4, 4], "z": [0, 5]})

sim_params = SimulationParameters(num_iterations=100, resolution=2)

# Initialize a scenario with the wind tunnel and the simulation parameters
scenario = WindTunnelScenario(wind_tunnel)

# Simulate the scenario with the object at the given path
task = scenario.simulate(object_path="assets/vehicle.obj",
                         sim_params=sim_params)

# Wait for the simulation to finish and download the results
task.wait()
output = task.download_outputs()
```

Running this scenario we obtain the following logs:

```bash
2023-12-26 11:46:07 INFO Task ID: 1703591167165582244
2023-12-26 11:46:07 INFO Packing input archive to upload to inductiva.ai.
2023-12-26 11:46:07 INFO Uploading packed input archive with size 1.31 MB.
2023-12-26 11:46:08 INFO Input archive uploaded.
2023-12-26 11:46:08 INFO Task submitted to the default resource pool.
2023-12-26 11:46:08 INFO Waiting for resources...
2023-12-26 11:46:13 INFO The task is being executed remotely.
2023-12-26 11:46:58 INFO Task completed successfully.

2023-12-26 11:46:59 INFO Downloading simulation outputs to /Users/ivanpombo/Documents/wind-tunnel/inductiva_output/1703591167165582244/output.zip.
100%|██████████| 14.7M/14.7M [00:00<00:00, 32.3MB/s]
2023-12-26 11:46:59 INFO Uncompressing the outputs to /Users/ivanpombo/Documents/wind-tunnel/inductiva_output/1703591167165582244.
```

For this scenario, there are a few methods prepared to post-process and
visualize the results, check the `lib/post_processing.py` file for more
details. Here, we visualize the pressure distribution and a slice of the
velocity field.

``` python
from lib import post_processing

processor = post_processing.WindTunnelOutput(output)

pressure = processor.get_object_pressure_field()
pressure.render()
```

<div align=center>
    <img src="../assets/pressure_field.png" alt="Pressure field" width=400>
    <p> Fig. 3 - Pressure field of the vehicle. </p>
</div>

``` python
slice = processor.get_flow_slice()
slice.render("velocity")
```

<div align=center>
    <img src="../assets/flow_slice.png" alt="Flow slice" width=400>
    <p> Fig. 4 - Velocity field of the vehicle. </p>
</div>

#### Multiple simulations

Iterating over the parameters and submitting multiple wind tunnel
simulations is now straightforward. To exemplify this, let's test the
same vehicle under different flow velocities.

For running all the simulations in parallel, we launch a machine group
with 3 machines and will submit the simulations to it.

```python
machines = resources.MachineGroup(
    machine_type="c2-standard-4", num_machines=3)

machines.start()
```

The machines will be started with the following specifications:
```bash
2023-12-26 11:16:47 INFO Registering machine group configurations:
2023-12-26 11:16:48 INFO > Name: api-73e45a8f-13b0-41dc-bcb8-c5ca5ef53d49
2023-12-26 11:16:48 INFO > Machine type: c2-standard-4
2023-12-26 11:16:48 INFO > Spot: False
2023-12-26 11:16:48 INFO > Disk size: 70 GB
2023-12-26 11:16:48 INFO > Number of machines: 3
2023-12-26 11:16:48 INFO Estimated cloud cost per hour for all machines : 0.6890999999999999 $/h
2023-12-26 11:16:48 INFO Starting machine group. This may take a few minutes.
2023-12-26 11:16:48 INFO Note that stopping this local process will not interrupt the creation of the machine group. Please wait...
2023-12-26 11:17:08 INFO Machine group successfully started in 0.33 mins.
```

Thereafter, we can submit several simulations to the machine group:

``` python
tasks_list = []
flow_velocity_list = [(10, 0, 0), (30, 0, 0), (50, 0, 0)]


for flow_velocity in flow_velocity_list:
    # Initialize a wind tunnel with the given flow velocity
    wind_tunnel = WindTunnel(flow_velocity=flow_velocity,
                             domain={"x": [-4, 15], "y": [-4, 4], "z": [0, 5]})

    # Initialize a scenario with the wind tunnel and the simulation parameters
    scenario = WindTunnelScenario(wind_tunnel)

    # Submit the simulation, with the sim_params of the previus section
    task = scenario.simulate(object_path="assets/vehicle.obj",
                             sim_params=sim_params,
                             machine_group=machines)
    tasks_list.append(task)
```

All simulations have been submitted, and now we can wait for them to
finish, and then download the results.

``` python
for task in tasks_list:
    task.wait()
    task.download_outputs()
```

With the simulations finished, we can now terminate the machines:

``` python
machines.terminate()
```

If your interest was piqued, go deeper by exploring this scenario
implemented in the `lib` folder and create your own virtual **wind
tunnel**!
