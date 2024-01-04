## Templating the wind tunnel simulation

In the [the previous section](/docs/1_OPENFOAM_SIM.md), we seen how to launch
OpenFOAM simulations with **Inductiva API** and how difficult it becomes when we
want to explore several configuration setups in our **wind tunnel**.

In our path to build the simulation scenario, let's simplify the exploration first
with the powerful templating mechanism within **Inductiva API**. 

This mechanism allows users to template their simulation files with tags that get
replaced with specific values upon rendering. The templating mechanism
is integrated into a file packing interface - the `FileManager` class -
that allows users to easily manage the rendering of the template files.

### Introduction to templating

Consider a simple template file (`template.txt.jinja`) containing the
following content:

``` jinja
# content of template.txt.jinja
flowVelocity ({{ flow_velocity[0] }} {{ flow_velocity[1] }} {{ flow_velocity[2] }});
```

With a `FileManager` object, we can render this file with given values and
store it a user-specified folder to be used later:

``` python
from inductiva import mixins

manager = mixins.FileManager()

# specify the user-specific folder where files are to be stored
manager.set_root_dir("myfiles")

# render template.txt.jinja by setting the `flow_velocity` to 10
# and specifying the name of the rendered file
manager.add_file("assets/template.txt.jinja", "rendered.txt",
                 **{"flow_velocity": (10, 0, 0)})
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

### Simulating with template files

The `FileManager` gives the capabilities to add, copy or render files on the spot,
which provides a lot of flexibility for users to establish their templating
workflows as they wish. In the following, we will provide two examples of
templating workflows.

##### Example A

In the first example, we use the input files from the low-level simulation
of the [previous tutorial](/docs/1_OPENFOAM_SIM.md) and a single template file 
`initialConditions.jinja`. This template file contains the tags introduced above
for the airflow velocity and a few extra fixed parameters. 

Hence, we add the directory with the input files to a root dir, then we render this 
file on the `0/include` which will substitute the already existing file
`initialConditions` we have used in the previous simulation. 

```python
from inductiva import mixins

# Initialize the manager
file_manager = mixins.FileManager()

# Set the root dir where all files are added and render to
file_manager.set_root_dir("velocity_dir")

# Add the previously prepared input files
file_manager.add_dir("assets/openfoam_input")

# Render the flow velocity in the template file `initialConditions.jinja`
file_manager.add_file("assets/initialConditions.jinja",
                      "0/include/initialConditions",
                      **{"flow_velocity": (50, 0, 0)})
```

This code snippet has prepared a new directory named `velocity_dir` that contains
the simulation as before, but now at an airflow speed of $50$ m/s in the x-axis direction.
Therefore, we can now use it to simulate with the same commands:

```python
import inductiva

openfoam = inductiva.simulators.OpenFOAM()

commands = [{"cmd": "runApplication surfaceFeatures", "prompts": []},
            {"cmd": "runApplication blockMesh", "prompts":[]},
            {"cmd": "runApplication decomposePar -copyZero", "prompts":[]},
            {"cmd": "runParallel snappyHexMesh -overwrite", "prompts":[]},
            {"cmd": "runParallel potentialFoam", "prompts":[]},
            {"cmd": "runParallel simpleFoam", "prompts":[]},
            {"cmd": "runApplication reconstructParMesh -constant", "prompts":[]},
            {"cmd": "runApplication reconstructPar -latestTime", "prompts": []}]

# Fetch the input dir prepared with the file manager and run the simulation
task = openfoam.run(input_dir=file_manager.get_root_dir(),
                    commands=commands)

# Wait for the task to finish and download the outputs.
task.wait()
task.download_outputs()
```

To iterate over different values of the flow velocity, it is enough to set
a for loop at the start and everything will work out smoothly!


#### Example B

In this second example, we prepare the template files for a more general 
wind tunnel scenario, where we want to provide the flexibility to change the domain
geometry, the number of iterations of the solver in use, `simpleFoam`, and the 
resolution of the mesh, besides the airflow velocity.

These parameters are spread over several files, hence, in this example, we start 
from a template directory, which contains the template files and the other files
needed to run the simulation. 

To create this directory we have started from the `assets/openfoam_dir` from the
previous tutorial and templated the following files:
- `0/include/initialConditions.jinja` with the `flow_velocity`;
- `system/blockMeshDict.jinja` with the `domain` geometry;
- `system/controlDict.jinja` with the `num_iterations` of the solver;
- `system/snappyHexMeshDict.jinja` with the `resolution` of the mesh.

For the latter case, we have performed the substitution of the `resolution` tag
in several places to control the resolution of the mesh in different levels at the
same time. The template directory is placed at `lib/templates`. 

To perform the simulation from this template directory we render it completely
on the spot with all of the parameters. In this case, the rendered directory
keeps the same structure and the template files are rendered into files named
without the `.jinja` extension. Moreover, in this directory the vehicle
geometry is not present, so we will add to the root directory directly with a
common name, like `object.obj`, that permits to change vehicles without
altering the input files to much.

The following snippet runs a simulation by performing the above steps:

```python
from inductiva import mixins
import inductiva

# Initialize the manager and set the root directory
file_manager = mixins.FileManager()
file_manager.set_root_dir("windtunnel_dir")

# Render the template directory with the parameters
file_manager.add_dir("lib/templates",
                     **{"flow_velocity": (50, 0, 0),
                        "x_min": -6, "x_max": 12, "y_min": -4,
                        "y_max": 4, "z_min": 0, "z_max": 8,
                        "num_iterations": 100,
                        "resolution": 3})

# Add the motorbike geometry
file_manager.add_file("assets/vehicle.obj", "constant/triSurface/object.obj")

# Run the simulation as before
openfoam = inductiva.simulators.OpenFOAM()

commands = [{"cmd": "runApplication surfaceFeatures", "prompts": []},
            {"cmd": "runApplication blockMesh", "prompts":[]},
            {"cmd": "runApplication decomposePar -copyZero", "prompts":[]},
            {"cmd": "runParallel snappyHexMesh -overwrite", "prompts":[]},
            {"cmd": "runParallel potentialFoam", "prompts":[]},
            {"cmd": "runParallel simpleFoam", "prompts":[]},
            {"cmd": "runApplication reconstructParMesh -constant", "prompts":[]},
            {"cmd": "runApplication reconstructPar -latestTime", "prompts": []}]

# Fetch the input dir prepared with the file manager and run the simulation
task = openfoam.run(input_dir=file_manager.get_root_dir(),
                    commands=commands)

# Wait for the task to finish and download the outputs.
task.wait()
task.download_outputs()
```

That's it! The parameters can now be configured to run multiple **wind tunnel**
setups.

### Is this the best way to do it?

Let's assume again that we want to iterate over the airflow velocity, for example,
from 10 to 50 m/s. With the templating approach we won't need to create an input
directory manually with the desired changes. For example, based on the example A,
we iterate over the airflow velocity and render each time a directory with the
new airflow velocity, as follows:

```python
from inductiva import mixins, simulators

flow_velocities_list = [10, 20, 30, 40, 50]
tasks_list = []

# Initialize the manager
file_manager = mixins.FileManager()

# Initialize the simulator and commands (which are fixed for the wind tunnel).
openfoam = inductiva.simulators.OpenFOAM()

commands = [{"cmd": "runApplication surfaceFeatures", "prompts": []},
            {"cmd": "runApplication blockMesh", "prompts":[]},
            {"cmd": "runApplication decomposePar -copyZero", "prompts":[]},
            {"cmd": "runParallel snappyHexMesh -overwrite", "prompts":[]},
            {"cmd": "runParallel potentialFoam", "prompts":[]},
            {"cmd": "runParallel simpleFoam", "prompts":[]},
            {"cmd": "runApplication reconstructParMesh -constant", "prompts":[]},
            {"cmd": "runApplication reconstructPar -latestTime", "prompts": []}]

for flow_velocity in flow_velocities_list:

    # Set the root dir to add/render files/dir. If folder exists, new one
    # is created with a number appended to it.
    file_manager.set_root_dir("velocity_dir")

    # Add the previously prepared input files
    file_manager.add_dir("assets/openfoam_input")

    # Render the flow velocity in the template file `initialConditions.jinja`
    file_manager.add_file("assets/initialConditions.jinja",
                        "0/include/initialConditions",
                        **{"flow_velocity": (flow_velocity, 0, 0)})

    # Fetch the input dir prepared with the file manager and run the simulation
    task = openfoam.run(input_dir=file_manager.get_root_dir(), commands=commands)
    tasks_list.append(task)

# Wait for the task to finish and download the outputs.
for task in tasks_list:
    task.wait()
    task.download_outputs()
```

This approach is way more scalable than the manual change of the input directories,
however, a tidy bit of code still needs to be written to iterate over the different
flow velocities. With more code to be written, more chances of errors are introduced.

Imagine, we want to generate a dataset to train a scientific machine learning model.
Maybe, the expert in OpenFOAM simulations is not the same as the expert in machine
learning. Therefore, simplifying this workflow even further and abstracting completely
the OpenFOAM setup would be great. Hence,  we are on the right track, but we can do better!

To improve this workflow, we can encapsulate the code to run the **wind tunnel**
simulation into a single class, which simplifies the workflow completely and there
is only the need to write the templating mechanism once. Following this idea, in
the [next tutorial,](/docs/3_WINDTUNNEL_SCENARIO.md) we will create the
`WindTunnelScenario` class to run the specific **wind tunnel** simulations we have
been performing so far.
