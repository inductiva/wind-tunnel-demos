## OpenFOAM simulation via Inductiva API

**Inductiva API** provides low-level access to several simulators, OpenFOAM
being one of them. As usual, users need to configure the OpenFOAM simulation files
and the OpenFOAM commands, then they can submit the simulation with 
the `inductiva` package, all from Python.

For this tutorial, we use the simulation files provided in the OpenFOAM
[wind tunnel tutorial](https://github.com/OpenFOAM/OpenFOAM-8/tree/master/tutorials/incompressible/simpleFoam/motorBike).

### OpenFOAM configuration

The configuration of the simulator is already familiar to OpenFOAM users, thus we
go straight to the point. For this simulation, we use the input directory
`assets/openfoam_input` which contains three folders: `0`, `constant` and `system`.
- `0` with the initial conditions;
- `constant` with the constant and physical properties, e.g., the motorbike file, 
`motorBike.obj`, is located in the `triSurface` subdirectory;
- `system` which configures the simulation parameters.

Check [here](https://doc.cfd.direct/openfoam/user-guide-v11/case-file-structure)
to see more details.

The next step is to select the OpenFOAM commands. There are multiple commands
available, some involve pre-processing steps, others
run the solvers and others post-process the results. For each command, you can
use `runApplication` and `runParallel` to distinguish between a serial or parallel
run, respectively.

### Running the simulation

Let's simulate a wind tunnel via **Inductiva API** with a randomly generated
vehicle!

```python
import inductiva

# Initialize an instance of OpenFOAM
openfoam = inductiva.simulators.OpenFOAM()

# Set the commands. The meshing and solver commands are run in parallel.
commands = [{"cmd": "runApplication surfaceFeatures", "prompts": []},
            {"cmd": "runApplication blockMesh", "prompts":[]},
            {"cmd": "runApplication decomposePar -copyZero", "prompts":[]},
            {"cmd": "runParallel snappyHexMesh -overwrite", "prompts":[]},
            {"cmd": "runParallel potentialFoam", "prompts":[]},
            {"cmd": "runParallel simpleFoam", "prompts":[]},
            {"cmd": "runApplication reconstructParMesh -constant", "prompts":[]},
            {"cmd": "runApplication reconstructPar -latestTime", "prompts": []}]

# Submit the simulation
task = openfoam.run(input_dir="assets/openfoam_input",
                    commands=commands)
```

With this code snippet, the simulation is submitted to a remote machine
from **Inductiva** default resource pool. The `run` method is non-blocking so that
users can continue working while the simulation is running. To check the 
simulation status and retrieve the results when finished, we can do:

```python
# Check the status of the simulation and download all of the result files
task.wait()
task.download_results()
```

With a bit of post-processing, we obtain the pressure field over the vehicle:

<div align="center">
<img src="/assets/pressure_field.png" width=300 alt="Simulation Image">
</div>


### Problem: How to change the airflow velocity?

Assume now, we want to iterate over the airflow velocity, for example,
from 10 to 50 m/s. There are two methods to do it:
- create an input directory for each simulation, with the different airflow velocities;
- template your files to facilitate changes.

The first method is not scalable, and, hence not recommended. Due to this, OpenFOAM
already provides a few mechanisms to template your files. One method is to configure
the variables to be changed in a single file, which can be manually changed. Another
is to use the `foamDictionary` command, which is more flexible and allows for
automated changes. However, the commands need to be passed before starting the
simulation and for multiple changes, it starts to get cumbersome.

To provide this flexibility, **Inductiva API** provides a templating mechanism
that allows users to change the simulation parameters on the spot, and the
variables can be modified via Python. The goal is to simplify the iteration
over several parameters and run several tests in parallel.

Let's see this in action in the [next tutorial](/docs/2_TEMPLATING.md) and start
abstracting the configuration of our **Wind Tunnel**.
