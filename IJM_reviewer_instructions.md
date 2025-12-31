
1. In an Unix terminal clone the MINOS GitHub repository www.github.com/Leeds-MRG/Minos. 
    Once downloaded, move into the Minos directory and switch to the required branch using command 'git checkout IJM_paper_June_2025'.

git clone https://github.com/Leeds-MRG/Minos
cd Minos
git checkout IJM_paper_June_2025

3. Download and unpack version 20 of the Understanding Society dataset from the UK Data Service (UKDA) website [here](http://doi.org/10.5255/UKDA-SN-6614-20) (more information [here](https://www.understandingsociety.ac.uk/documentation/access-data)), for which you will need a UKDA account.
    Ensure you download the dataset in STATA format such that the folder is named ```UKDA-6614-stata```. 
    Understanding Society is a longitudinal study of UK households and is used as input data for *Minos*.
    The resulting directory structure should look as it does below.

```
yourproject/
└─  Minos/
└─  UKDA-6614-stata/
```

4. Install the conda environment ```minos_conda_IJM``` containing the required R. and python packages.
    It is strongly recommended to use the [micromamba](https://mamba.readthedocs.io/) package manager for installation speed and stability but any conda environment manager can be used.
    The environment is installed using the command.

```
> micromamba env create -f environment.yml
```

and activated using

```
> micromamba activate minos_conda_ijm
```

5. 

If this environment is correctly installed, the following make command will then generate the data, tables, and plots used in this paper.

```
> make IJM_transitions_notebook
```

All plots and tables are saved in the folder ```Minos/IJM_plots_and_tables```. The R. Markdown notebook used to create all plots and tables is provided in ```Minos/outcomes/IJM_paper_transitions_notebook.Rmd```.
It is strongly recommended to view this code in an R. IDE such as RStudio. 
This Rmd notebook when knitted will also produce an html file ```Minos/outcomes/IJM_paper_transitions_notebook.html``` rendering all plots, tables, and code in a single file.