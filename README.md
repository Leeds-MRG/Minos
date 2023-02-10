<div align="center">
    <h1>Minos</h1>
</div>

*Minos* is a dynamic microsimulation being developed to investigate (firstly) the pathways in which an improvement to a national living wage could affect mental health outcomes. 

It is based on [**Icarus**](https://github.com/RobertClay/Icarus), which is another dynamic microsimulation model being developed as part of Robert Clay's PhD project, all being part of the SIPHER consortium's work on the design of policy for interventions in 'inclusive economies'.

See the Github pages for more information: https://leeds-mrg.github.io/Minos/

Docker images hosted on Dockerhub, including a readme for how to setup and use MINOS within the container: https://hub.docker.com/repository/docker/ldarcher/minos

### Installation and quick start guide

*Minos* was developed in Python and R using a ```conda``` (i.e. Anaconda/Miniconda) environment. It has been tested with Python 3.9 and R 4.1.3. It is recommended that you follow the installation instructions below, which will install *Minos* in development mode.

1. Clone this repository, ensuring you have ```git``` installed, to a location of your choice.

```> git clone https://github.com/Leeds-MRG/Minos```

2. Download and unpack the Understanding Society dataset from the UK Data Service (UKDA) website [here](https://ukdataservice.ac.uk/find-data/) (more information [here](https://www.understandingsociety.ac.uk/documentation/access-data)), for which you will need a UKDA account. Ensure you download the dataset in STATA format such that the folder is named ```UK-6614-stata```. Understanding Society is a longitudinal study of UK households and is used as input data for *Minos*; more details [here](https://www.understandingsociety.ac.uk/).

3. Contact the developers to obtain the spatially disaggregated version of the Understanding Society data (in a folder called ```US_spatial_lookup```) that will allow you to plot results produced by *Minos*. The resulting directory structure should look as it does below.

```
yourproject/
└─  Minos/
└─  US-6614-stata/
└─  US_spatial_lookup/
```

4. Create a ```conda``` environment in which to run *Minos* using the file provided, as below. Then activate it with either ```source activate minos_conda``` or ```conda activate minos_conda```, depending on your system. NOTE: This can cause conflicts with conda R packages that are already installed. Some R packages may need to be removed in the environment this is being installed from (e.g. ```base```). A known issue is that R packages installed via ```install.packages()``` can cause conflicts with instances of the same packages installed via ```conda install```. In this case, it is recommended that you uninstall the offending packages with ```remove.packages()``` and then, if necessary, uninstall and reinstall via ```conda uninstall``` and ```conda install```. If that fails, we recommend you uninstall and reinstall Anaconda/Miniconda entirely to start from a fresh base environment.

```
> conda env create -n minos_conda -f environment.yml
```

5. Navigate to the uppermost *Minos* folder. The following command will install *Minos* and all its dependencies. All replenishing and transition data necessary to run *Minos* will be generated, all of which are derived from the Understanding Society dataset. This may take several minutes. You will then be able to run any of the microsimulation scenarios provided.

```> make setup```

### Information, issues and contacts

*Minos* has been developed as part of the SIPHER Research Consortium (more information, including funding details, can be found here: https://sipher.ac.uk/), under Workstrand 5, "Policy Microsimulation".

If you find a bug in *Minos* please submit an issue here at Github. If you have any suggestions or questions, please contact one of the developers below.

- Rob Clay (principal): gyrc@leeds.ac.uk
- Luke Archer (principal): l.archer@leeds.ac.uk
- Hugh Rice: h.p.rice@leeds.ac.uk
- Nik Lomax n.m.lomax@leeds.ac.uk
- Nick Rhodes: n.g.rhodes@leeds.ac.uk
