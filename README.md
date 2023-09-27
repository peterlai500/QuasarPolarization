# QuasarPol Package

## Goal
To charactorized the properties of accretion gas steam around even horizon by massively systemically downloading, calibrating, and doing fitting to proper quasar.

## Obtaining
Can directly obtain the source code and notebook file from GitHub with the `git clone` command.

## Environment requirements
Most of the necessary packages can be installed through the [`Quasarpol.yml`](https://github.com/peterlai500/QuasarPolarization/blob/main/Quasarpol.yml) file.  
By running in bash:  
`conda env create -f Quasarpol.yml `

- astropy(>=4.2.1)

- astroquery(v0.4.7.dev8738)  
  Common use install:  
  `python -m pip install -U --pre astroquery`  
  Installing all the mandatory and optional dependencies in astroquery by adding `[all]`:  
  `python -m pip install -U --pre astroquery[all]`
## Instructions
Initialize the package:  
Run the below line in the environment installed require packages, and save the initialized result in the variable you like, for me it is the `result`, i.e.,  
`result = QuasarPol(source, sci_obs, pol, table_length)`  

- To visualize the practical effect, the [`sample.ipynb`](https://github.com/peterlai500/QuasarPolarization/blob/main/sample.ipynb) provides a more detailed demonstration.

### For users who would like to do interactively. 
Use the jupyter notebook for the following step.
1. Check the data using `result.get_table()`. 

2. Check the parallactic angle change for each observation using `result.get_ParaAngle()`.

3. Filter the data in a certain parallactic angle change range using  
`filter_data(min_change_in_PA, Max_change_in_PA)`.
It is OK to directly replace the `min_change_in_PA` and `Max_change_in_PA` into the lower bound and upper bound you would like to be.

5. Downloading and untaring data is quite simple. If you want to download the filtered data you just run:  
`download_path = path/to/your/storage`  
`result.download(filtered=True, save_directory=download_path)`  
`result.untar()`
6. Running calibration script can be achieved just by running  
`result.run_script()`

### For advanced users
It is totally fine to do the upper tasks with Python scripts.  
The [`script_template.py`](https://github.com/peterlai500/QuasarPolarization/blob/main/script_template.py) in the repository can be regarded as the reference for composing a python script.

## Caution
Running CASA pipeline script may cause some systemic errors, such as the OS's in-built library not being compatible with CASA versions and you may need to manually downgrade the libraries. 






