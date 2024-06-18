# Document of Fitting

For the `[fitting.py](https://github.com/peterlai500/QuasarPolarization/blob/main/fitting.py)` in this project.

## Functions
### `ChanAverage`
Utilizing the mstransform in CASA, averaging the channels in  the measurement set.
It would make a new single-channel ms without affect the original multi-channel ms. The new ms name would be assign to the variable name and based on the name of the original one. According to the code, the new filename would be `original.chanaver`  
E.g., 
```Python
# known the ms name
vis = 'path/of/vis.ms'
chaver_vis = ChanAverage(vis)

# The channel averaged ms is `"path/of/vis.ms.chanaver"`
```

### `read_DATA`
Read the XX and YY and UV-distance information of certain field spw by spw, and save them into a dictionary.  
The input field must be a list and the ids in list must are integer. If not, e.g., a integer or string were input, then it would read every fields in the ms.
E.g., 
```Python
field_list = [2, 5, 24, 92, 13]
XXYYdata = read_DATA(vis ,field_list)`
```
The dictionary of all the information is assigned to `read_XXYY`. We can read all the data in dict to extract the XX, YY, and uvdist respectively. The specific field we desire would be saved by the order the list gave.
E.g., 
```Python
XX = XXYYdata[0]
YY = XXYYdata[1]
uvdist = XXYYdata[2]

# field 5 XX
XX_f5 = XX[1]
```

### `Fit_I`
Fit the the Stokes I to uvdist by the point source model. To get a proper value of Stokes I for following analyze. This function would output both original Stokes I and fitted Stokes I value at the same time  
E.g., 
```Python
StokesI = Fit_I(XXYY)
StokesI[0]	# The unfitted Stokes I
StokesI[1]	# fitted value
```

### `Fit_Rpol`
Calculate the $\frac{XX-YY}{I}$ value. It will also output the unfitted data and the fitted value.
```Python 
Rpol = FitRpol(XXYYdata, StokesI)
Rpol[0]      # The unfitted 
Rpol[1]      # fitted value
```

### `get_ParAngle`
Using the tool, `plotms`, in CASA, draw a plot about the parallactic angle and observation time relation. Then we can export the "plot" into a ascii .txt file, we then can directly read the parallactic angle through the ascii files.  
This function create a `plot_result` directory for saving the output files. It is fine to delete the directory after finishing this function. 
```Python
ParAngle_list = get_ParAngle(vis, field_list)
```

### `Fit_RpolPA`
For analyzing the $$\frac{Q}{I} - \delta \equiv \frac{XX-YY}{2I} - \delta = P \cdot \cos 2(\Psi - \eta - \phi) $$
