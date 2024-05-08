# 03/07

# fitting script
# Still need to fit field to each spw.



# import uvmultifit as uvm
import numpy as np
from datetime import datetime

from astropy.time import Time
from astropy.coordinates import SkyCoord
from astropy import units as u

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

vis       = "/home/pinhsien/Research/Baobab_2016data/sgrastar_b8/calibrated.ms.12m.uvaver"
field_ids = [0, 18, 25, 94, 101, 133, 134]

# use CASA ms tools to get columns of DATA, UVW, TIME, FIELD, UVdist, etc. 
# All the information saved into d with a dict. 
ms.open(vis)
ms.select(
        {
            'field_id':0
            }
        )
spw_info = ms.getspectralwindowinfo()
nchan    = spw_info["0"]["NumChan"]
npol     = spw_info["0"]["NumCorr"]
d = ms.getdata(['data', 'antenna1', 'antenna2', 'field_id', 'time', 'weight','u', 'v', 'flag', 'uvdist'])
ms.close()

# use CASA table tool get the frequency
tb.open(vis+"/SPECTRAL_WINDOW")
freqs = tb.getcol("CHAN_FREQ")
rfreq = tb.getcol("REF_FREQUENCY")
tb.close

flags  = np.squeeze(d['flag'])
data   = np.squeeze(d['data'])
time   = d['time']
uu     = d['u']
vv     = d['v']
ant1   = d['antenna1']
ant2   = d['antenna2']
weight = d['weight']
uvdist = d['uvdist']

'''

'''

if npol == 1:
    Re   = data.real
    Im   = data.imag
    wgts = weight
else:
    # polarization aveaging
    re_xx = data[0,:].real
    im_xx = data[0,:].imag
    re_yy = data[1,:].real
    im_yy = data[1,:].imag
    
    weight_xx = weight[0,:]
    weight_yy = weight[1,:]

    flags = flags[0,:] * flags[1,:]
    
    # - weighted averages
    with np.errstate(divide='ignore', invalid='ignore'):
        Re = np.where((weight_xx + weight_yy) != 0, (re_xx*weight_xx + re_yy*weight_yy) / (weight_xx + weight_yy), 0.)
        Im = np.where((weight_xx + weight_yy) != 0, (im_xx*weight_xx + im_yy*weight_yy) / (weight_xx + weight_yy), 0.)
    
        Re_xx = np.where(weight_xx != 0, re_xx * weight_xx, 0.) 
        Im_xx = np.where(weight_xx != 0, im_xx * weight_xx, 0.) 
        Re_yy = np.where(weight_yy != 0, re_yy * weight_yy, 0.) 
        Im_yy = np.where(weight_yy != 0, im_yy * weight_yy, 0.)
    
    wgts = (weight_xx + weight_yy)

# toss out the autocorrelation placeholders
xc = np.where(ant1 != ant2)[0]
if nchan==1:
    data_real = Re[np.newaxis, xc]
    data_imag = Im[np.newaxis, xc]
    
    Re_xx = Re_xx[np.newaxis, xc]
    Im_xx = Im_xx[np.newaxis, xc]
    Re_yy = Re_yy[np.newaxis, xc]
    Im_yy = Im_yy[np.newaxis, xc]

    flags     = flags[xc]
    uvdist    = uvdist[xc]
else:
    data_real = Re[:, xc]
    data_imag = Im[:, xc]
    # if the majority of points in any channel are flagged, it probably means someone flagged an entire channel - spit warning
    if np.mean(flags.all(axis=0)) > 0.5:
        print("WARNING: Over half of the (u,v) points in at least one channel are marked as flagged. If you didn't expect this, it is likely due to having an entire channel flagged in the ms. Please double check this and be careful if model fitting or using diff mode.")

    # collapse flags to single channel, because weights are not currently channelized
    flags  = flags.any(axis=0)
    uvdist = uvdist.any(axis=0)

# calculating the complex visibility
data_real = np.squeeze(data_real)
data_imag = np.squeeze(data_imag)
data_VIS = data_real + data_imag*1.0j

Re_xx  = np.squeeze(Re_xx)
Im_xx  = np.squeeze(Im_xx)
XX_VIS = Re_xx + Im_xx*1.0j

Re_yy = np.squeeze(Re_yy)
Im_yy  = np.squeeze(Im_yy)
YY_VIS = Re_yy + Im_yy*1.0j

# Remove the flagged data
data_VIS = data_VIS[np.logical_not(flags)]
XX_VIS   = XX_VIS[np.logical_not(flags)]
YY_VIS   = YY_VIS[np.logical_not(flags)]
uvdist   = uvdist[np.logical_not(flags)]

Stokes_I = np.abs(data_VIS)
XX = np.abs(XX_VIS) 
YY = np.abs(YY_VIS)
R_pol = (XX - YY)/Stokes_I


'''
# Fits Stokes-I
def FIT_I(uvdist, A, B):
    return A
params, params_covariance = curve_fit(FIT_I, uvdist, Stokes_I)

# Fits The real part
def FIT_REAL(uvdist, A, B):
    return A * np.sin(uvdist * B)
params, params_covariance = curve_fit(FIT_REAL, uvdist, data_VIS.real)

plt.clf()
plt.cla()
plt.plot(uvdist, data, '.', label='Stokes I')
plt.plot(uvdist, test_f(uvdist, params[0]), label='Fitted curve')
plt.xlabel("UVdist")
plt.ylabel("Flux Intensity (Jy)")
plt.legend(loc='best')
plt.show()
'''

#def FIT_I(uvdist, A):
#    fit_i = [A] * len(uvdist)
#    return fit_i
#params, params_covariance = curve_fit(FIT_I, uvdist, Stokes_I)


#####################################
############### Plots ###############

plt.clf()
plt.cla()
# plt.plot(uvdist, data_VIS.real, '.')        # Visibility real part to uvdist
# plt.plot(uvdist, data_VIS.imag, 'x')        # Visibility imaginary part to uvdist
# plt.plot(uvdist, Stokes_I, '.')            # Stokes I to UVdist
# plt.plot(uvdist, FIT_I(uvdist, params[0]))
plt.plot(uvdist, XX-YY, '.')

plt.xlabel("UVdist")
plt.ylabel("Flux Intensity (Jy)")
# plt.legend(['Stokes I', f'Fitted data={params[0]}'])
plt.title('XX-YY vs UV distance field 0')
plt.show()
plt.savefig('XXmYY_uvdist-field0.pdf')
