import os
import numpy as np
import matplotlib.pyplot as plt
from statistics import mean
from scipy.optimize import curve_fit

from astropy.coordinates import Angle
from astropy import units as u

vis = "sgrastar_b8/calibrated.ms.12m.uvaver"
field_ids = [0, 18, 25, 94, 101, 133, 134]

def PointSource_FITTING(uvdist, A):
    fitting = [A] * len(uvdist)
    return fitting

def read_DATA(visibility, field):
    XX_data = {"spw":{}}
    YY_data = {"spw":{}}

    for f in field:
        ms.open(visibility)
        ms.select({
            'field_id':f
            })
        spw_info = ms.getspectralwindowinfo()       # for reading the number of spectral windows in specific field
        ms.close()
        for s in range(len(spw_info)):
            # Read the data
            print(f'producing XX & YY for field {f} spw {s}')
            ms.open(visibility)
            ms.select({
                'field_id':f
                })
            ms.selectinit(datadescid=s)
            d = ms.getdata(['data', 'antenna1', 'antenna2', 'weight', 'flag', 'uvdist'])
            ms.selectinit(reset=True)           # reset=True to reset to unselected state
            ms.close()

            # modify the data into proper format
            flags  = np.squeeze(d['flag'])
            data   = np.squeeze(d['data'])
            ant1   = d['antenna1']
            ant2   = d['antenna2']
            weight = d['weight']
            uvdist = d['uvdist']

            # polarization averaging
            re_xx = data[0,:].real
            im_xx = data[0,:].imag
            re_yy = data[1,:].real
            im_yy = data[1,:].imag

            weight_xx = weight[0,:]
            weight_yy = weight[1,:]

            flags = flags[0,:] * flags[1,:]

            # - weighted averages
            with np.errstate(divide='ignore', invalid='ignore'):
                Re_xx = np.where(weight_xx != 0, re_xx * weight_xx, 0.)
                Im_xx = np.where(weight_xx != 0, im_xx * weight_xx, 0.)
                Re_yy = np.where(weight_yy != 0, re_yy * weight_yy, 0.)
                Im_yy = np.where(weight_yy != 0, im_yy * weight_yy, 0.)
            wgts = (weight_xx + weight_yy)

            # toss out the autocorrelation placeholders
            xc = np.where(ant1 != ant2)[0]
            Re_xx  = Re_xx[np.newaxis, xc]
            Im_xx  = Im_xx[np.newaxis, xc]
            Re_yy  = Re_yy[np.newaxis, xc]
            Im_yy  = Im_yy[np.newaxis, xc]
            flags  = flags[xc]
            uvdist = uvdist[xc]

            Re_xx  = np.squeeze(Re_xx)
            Im_xx  = np.squeeze(Im_xx)
            XX_VIS = Re_xx + Im_xx*1.0j

            Re_yy = np.squeeze(Re_yy)
            Im_yy  = np.squeeze(Im_yy)
            YY_VIS = Re_yy + Im_yy*1.0j

            # Remove the flagged data
            XX_VIS   = XX_VIS[np.logical_not(flags)]
            YY_VIS   = YY_VIS[np.logical_not(flags)]
            uvdist   = uvdist[np.logical_not(flags)]

            # Calculate the amplitude
            XX = np.abs(XX_VIS)
            YY = np.abs(YY_VIS)

            if s not in XX_data['spw']:
                XX_data['spw'][s] = []
            if s not in YY_data['spw']:
                YY_data['spw'][s] = []
            XX_data['spw'][s].append(XX)
            YY_data['spw'][s].append(YY)

    return XX_data, YY_data, uvdist

def Fit_I(XXYYdata):
    XX = XXYYdata[0]
    YY = XXYYdata[1]
    uvdist = XXYYdata[2]

    StokesI = {'spw':{}}
    FittedI = {'spw':{}}
    # Stokes I = (XX + YY)/2
    for spw in range(len(XX['spw'])):
        for i in range(len(XX['spw'][spw])):
            stokes_i = ( XX['spw'][spw][i] + YY['spw'][spw][i] ) / 2

            if spw not in StokesI['spw']:
                StokesI['spw'][spw] = []
            StokesI['spw'][spw].append(stokes_i)

    for spw in range(len(StokesI['spw'])):
        for i in range(len(StokesI['spw'][spw])):
            params, params_covariance = curve_fit(PointSource_FITTING, uvdist, StokesI['spw'][spw][i])

            if spw not in StokesI['spw']:
                Fitted_I['spw'][spw] = []
            FittedI['spw'][spw].append(params[0])

    return StokesI, FittedI

data = read_DATA(vis, field_ids)
# I = Fit_I(data)
