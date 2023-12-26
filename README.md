# Wind Tunnel via Inductiva API

<div align="center">
<img src="assets/f1.gif" width=500 height=300 alt="Duck simulation">
</div>

With [**Inductiva API**](https://github.com/inductiva/inductiva/tree/main), exploring the
aerodynamic of vehicles in a wind tunnel was never easier. 

Physical wind tunnels serve as the base ground for testing the
aerodynamics of vehicles - from your everyday commuter car to the
high-performance F1 car. However, physical testing is expensive and involves the construction of
physical versions of the vehicles under test. This cuts down
significantly the ability to iterate and improve the aerodynamic
performance of the vehicle.

<div align="center">
       <img src="assets/physical_windtunnel.jpg" alt="Physical Wind Tunnel" width=300>
       <p> Fig. 1 - Physical wind tunnel of Mercedez-Benz. </p>
</div>

## Accelerating Discovery

With the rise of [CFD](https://en.wikipedia.org/wiki/Computational_fluid_dynamics)
and computational hardware, the automotive and aeronautic industries turned
to simulations to improve the aerodynamics of vehicles before even
building them. CFD simulations represent **virtual wind tunnels** that
mimic the conditions of the physical ones but allow for a more
cost-effective strategy to start the designing process. Engineers can iterate
over designs much faster and improve the quality of the vehicle, before moving
to production.

<div align="center">
       <img src="assets/virtual_windtunnel.png" alt="Virtual Wind Tunnel" width=478>
       <p> Fig. 2 - Virtual wind tunnel simulation with <b> Inductiva API</b>.
       </p>
</div>

With **Inductiva API** these simulations are further simplified by setting up
a custom virtual wind tunnel that abstracts the complexity of configuring the
[OpenFOAM](https://github.com/inductiva/inductiva/wiki/OpenFOAM)
simulator into the essential parameters necessary to test the
aerodynamics of different vehicles. 

All, through a simple Python interface without having to worry about
downloading/compiling and installing simulation packages and managing/maintaining
computational resources.

To explore the wind tunnel with **Inductiva API**, first
[install this repository and any dependencies](docs/0_INSTALL.md). 

Then, follow the construction of the wind tunnel scenario through 
[a Jupyter Notebook](1_windtunnel_notebook.ipynb) or directly through
the documentation [docs/1_WINDTUNNEL.md].

To learn more about the `inductiva` package, check the
[Inductiva API documentation](https://github.com/inductiva/inductiva/wiki).
