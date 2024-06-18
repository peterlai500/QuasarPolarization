# Document of Fitting

For the `[fitting.py](https://github.com/peterlai500/QuasarPolarization/blob/main/fitting.py)` in this project

## Functions
### `ChanAverage`
Utilizing the mstransform in CASA, averaging the channels in  the measurement set

### `read_DATA`
Read the XX and YY and UV-distance information spw by spw

### `Fit_I`
The definition of the Stokes parameters are $$I = \frac{XX+YY}{2}\\Q = \frac{XX-YY}{2}$$
