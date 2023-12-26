### Install

#### `inductiva` client

The `inductiva` package is required to run the examples in this repository.

It provides the user with mechanisms to run simulations at scale, without
having to be worried about installing simulation packages and managing
physical resources. Users need only to handle the science behind the problem
and configure the simulation using the packages they know and love.

**You handle the science, Inductiva manages the rest.**

The `inductiva` package is easily installed using `pip`:

```bash
$ pip install inductiva
```

A successful installation can be tested using:

```bash
$ python -c 'import inductiva; print(inductiva.__version__)'
<some version number printed here> 
```

#### Demo repository

Having the `inductiva` client available, the next step is to clone this repository:

```bash
$ git clone https://github.com/inductiva/wind-tunnel.git
```

Then, we suggest the installation of a few extra dependencies specific to the demos:

```bash
$ cd wind-tunnel
$ pip install -r requirements.txt
```

Some of the final visualizations require `ffmpeg`, an external dependency that needs
to be downloaded separately from [ffmpeg.org](https://ffmpeg.org/download.html) or
through Anaconda/Miniconda with `conda install -c conda-forge ffmpeg`.
