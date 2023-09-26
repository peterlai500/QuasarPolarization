# QuasarPol Package

## Goal

## Obtaining
Can directly obtain the source code and notebook file from Github with `git clone` command

## Enviroment requirements
Most of the necessary packages can be install through the [`Quasarpol.yml`](https://github.com/peterlai500/QuasarPolarization/blob/main/Quasarpol.yml) file.  
By running in bash:  
`conda env create -f Quasarpol.yml `

- astropy(>=4.2.1)

- astroquery(v0.4.7.dev8738)  
  Common use install:  
  `python -m pip install -U --pre astroquery`  
  Installing all the mandatory and optional dependencies in  astroquery by adding `[all]`:  
  `python -m pip install -U --pre astroquery[all]`
## Instructions
Initialize the package:  
Run the below line in the envornment installed require paakage, and save the initialized result in the varible wou like, for me it is the `result`, i.e.,  
`result = QuasarPol(source, sci_obs, pol, table_length)`  

- To visualized the practical effect, the [`sample.ipynb`](https://github.com/peterlai500/QuasarPolarization/blob/main/sample.ipynb) provide more detailed demonstration.

### For users would like to do interactively. 
Use the jupyter notebook for following step.
1. Check the data using `result.get_table()`. 

2. Check the parallactic angle change for each observation using `result.get_ParaAngle()`.

3. Filter the data in cerrtain parallactic angle change range using  
`filter_data(min_change_in_PA, Max_change_in_PA)`.  
   It is OK to directly replace the `min_change_in_PA` and `Max_change_in_PA` in to the lower bound and upper bound you would like to be.

4. Downloading and untaring data is quite simple. If you want to download the flitered data you just run:  
`download_path = path/to/your/storage`  
`result.download(filtered=True, save_directory=download_path)`  
`result.untar()`
5. Running calibration script can be achieve just running  
`result.run_script()`

- - -
### For adavnced users
It is totally fine to do the upper tasks with python scripts.  
The [`script_template.py`](https://github.com/peterlai500/QuasarPolarization/blob/main/script_template.py) in the repository can be regard as reference of composing a python script.
