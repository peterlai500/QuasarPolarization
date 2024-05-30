# QuasarPol

## Introduction
For the purpose of constraining the magnetic field configuration around the event horizon, we developed this project. It enable us to extensively query and download historical ALMA calibrators with the desired correlations for analysis. Additionally fitting code provides a guide to analysis the parallel-hand correlation and parallactic angle of understanding polarization properties.

## Environment requirements
Most of the necessary packages can be installed through the [`Quasarpol.yml`](https://github.com/peterlai500/QuasarPolarization/blob/main/Quasarpol.yml) file.  
By running in terminal:  
`conda env create -f Quasarpol.yml `

- astropy(>=4.2.1)
- astroquery(v0.4.7.dev8738)  
  Common use install:  
  `python -m pip install -U --pre astroquery`  
  Installing all the mandatory and optional dependencies in astroquery by adding `[all]`:  
  `python -m pip install -U --pre astroquery[all]`
- Docker  
  The required images are in the docker_env.
- CASA 6.4.1
  For stablely executing the fitting code.

## Query and Download
Run the functions in the [`demo.ipynb`](https://github.com/peterlai500/QuasarPolarization/blob/main/demo.ipynb) notebook in order. This will generate a table of quasars in the data archive that satisfy our desired conditions.  
Alternatively, we can directly obtain the table and download the data by running [`script_template.py`](https://github.com/peterlai500/QuasarPolarization/blob/main/script_template.py) or other script based on it usign Python.

## Calibration
The most recommended method for now is utilizing the provided Docker image tarball to build containers set up for each ALMA  data cycle. Next, mount the downloaded data to the corresponfing container. By entering the container, you can directly execute the calibration pipeline script as usual.  
Note that one container can only process one task. It is fine to build more than one container for multitask.

## Analyze Calibtated Measurement Set
We can execute the [fitting.py](https://github.com/peterlai500/QuasarPolarization/blob/main/fitting.py) in the CASA 6.4.1 stable environment.  
One can get the $XX$, $YY$, Stokes I, parallactic angle, and running fitting result step by step.Alternatively, we can exexcute the scripy  directly.

The value of E-vector differs depends on the observation band. The E-vector in the fitting script has been set to 0.0 for band 8 observations. Refer to Table 2. of [Liu et al. 2016](https://ui.adsabs.harvard.edu/abs/2016A%26A...593A.107L/abstract) for the values for other bands.

## Flowcharts for This Project
![Query Flowchart](https://github.com/peterlai500/QuasarPolarization/blob/main/images/QuasarPol_flowchart.pdf) ![Analyze Flowchart](https://github.com/peterlai500/QuasarPolarization/blob/main/images/PolAnalyze_flowchart.pdf)

## Issues
The parallactic angle is calculated using the observation time of the entire observation. The result is highly incorrect regarding the coverage as the target you want to analysis.
