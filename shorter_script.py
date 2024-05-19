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

def XXYY_DATA(visibility, field):
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
        for i in range(len(StokeI['spw'][spw])):
            params, params_covariance = curve_fit(PointSource_FITTING, uvdist, StokesI['spw'][spw][i])
            
            if spw not in StokesI['spw']:
                Fitted_I['spw'][spw] = []
            FittedI['spw'][spw].append(params[0])

    return StokesI, FittedI




'''
def fit_I(visibility, field):
    fitted_I = {"spw":{}}
    
    # make directory "fitting_result" to save the result of fitting.
    l = subprocess.run("ls", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    l = l.stdout.decode()
    l = l.split('\n')
    if "fitting_result" not in l:
        os.system("mkdir fitting_result")
    
    name = visibility.replace("/", ".")
    # read the ms and use the uvmodelfit in CASA
    for f in field:
        ms.open(visibility)
        ms.select({'field_id':f})
        spw_info = ms.getspectralwindowinfo()
        for s in range(len(spw_info)):
            # Use uvmodelfit to fit the Stokes I
            ##  use the field 0 fitting result to initial the flux fitting 
            uvmodelfit(
                    visibility, 
                    field=f'{f}', 
                    spw=f'{s}', 
                    niter=10, 
                    comptype='P', 
                    sourcepar=[1.0, 0.0, 0.0], 
                    outfile=f'fitting_result/{name}.fit.field{f}.spw{s}.cl'
                    )
            cl.open(f'fitting_result/{name}.fit.field{f}.spw{s}.cl')
            fit = cl.getcomponent(0)
            cl.close()
            if s not in fitted_I["spw"]:
                fitted_I["spw"][s] = []
            fitted_I["spw"][s].append(fit['flux']['value'][0])
        ms.close()
    return fitted_I
'''
def XXmYY_FITTING(uvdist, A):
    fit_xxmyy = [A] * len(uvdist)
    return fit_xxmyy

def fit_XXmYY(visibility, field):
    fitted_XXmYY = {"spw":{}}
    for f in field:
        print('field:', f)
        ms.open(visibility)
        ms.select({'field_id':f})
        spw_info = ms.getspectralwindowinfo()
        for s in range(len(spw_info)):
            print('spectural window:', s)
            ms.selectinit(datadescid=s)
            d = ms.getdata(['data', 'antenna1', 'antenna2', 'weight', 'flag', 'uvdist'])
            ms.selectinit(reset=True)       # reset=True to reset to unselected state

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
            
            # Calculate the flux density
            XX = np.abs(XX_VIS)
            YY = np.abs(YY_VIS)
            XXmYY = XX-YY

            #fit XX-YY to uvdist
            params, params_covariance = curve_fit(XXmYY_FITTING, uvdist, XXmYY)
            print('Fitted XX-YY=', params[0])
            if s not in fitted_XXmYY['spw']:
                fitted_XXmYY["spw"][s] = []
            fitted_XXmYY["spw"][s].append(params[0])
        ms.close()
    return fitted_XXmYY


def get_ParAngle(visibility, field):    

    ParAngle = {'spw':{}}
    
    # make a directory to save the ascii file from the plotms
    l = subprocess.run("ls", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    l = l.stdout.decode()
    l = l.split('\n')
    if "plotms_result" not in l:
        os.system("mkdir plotms_result")

    name = visibility.replace("/", ".")
    
    # Read the spectral window info from ms
    for f in field:
        ms.open(visibility)
        ms.select({'field_id':f})
        spw_info = ms.getspectralwindowinfo()
        for s in range(len(spw_info)):
            parangle = []
            # use plotms to get and the information of ParAngle
            # and export the result to ASCII format
            plotms(
                visibility,
                xaxis='Time',
                yaxis='ParAngle',
                selectdata=True,
                field=f'{f}',
                spw=f'{s}',
                plotfile=f'plotms_result/{name}.plot.field{f}.spw{s}.txt'
                )
            # read the ascii file to and obtain the averaging ParAngle of each integration
            txtfile  = open(f'plotms_result/{name}.plot.field{f}.spw{s}.txt', 'r')
            for line in txtfile:
                line = line.strip()
                datacol = line.split()
                if len(datacol) == 14:
                    parangle.append(datacol[1])
            
            parangle = [float(num) for num in parangle]
            if s not in ParAngle['spw']:
                ParAngle['spw'][s] = []
            ParAngle['spw'][s].append(mean(parangle))
        ms.close()

    # Convert the parallactic angle in astropy angle object and wrap the angle between -180 to 180 degree
    for i in range(len(ParAngle['spw'])):
        ParAngle['spw'][i] = Angle(ParAngle['spw'][i] * u.deg)
        ParAngle['spw'][i].wrap_at('180d', inplace=True)
    return ParAngle

def Rpol_PA_FITTING(Parallactic_Angle, P, a, c):
    '''
    P: the polarization percentage
    a: (polarization position angle in the sky frame) - (E-vector)
    
    return the function model for the polarization ratio to the parallactic angle
    '''
    return P * np.cos(2 * (a - np.array(Parallactic_Angle))) + c


def fit_Pol_PA(fitted_I, fitted_XXmYY, ParAngle):
    '''
    fitted_I: dict
        I: int
    fitted_XXmYY: dict
        XX-YY: integer
    ParAngle: dict
        Parallactic angles are the astropy object in the dictionary
    '''
    # check the length (number of field) is the same
    if len(fitted_I) != len(fitted_XXmYY) != len(ParaAngle):
        return 
    # calculate the polarization ratio (XX-YY)/I 
    Rpol = {'spw':{}}
    fit_params = {'spw':{}}
    fit_covari = {'spw':{}}
    for i in range(len(fitted_I['spw'])):
        if all(i not in d for d in [Rpol['spw'], fit_params['spw'], fit_covari['spw']]):
            Rpol['spw'][i] = []
            fit_params['spw'][i] = []
            fit_covari['spw'][i] = []
        # Calculate the polarization ratio (XX-YY)/I
        Rpol['spw'][i] = [x / y for x, y in zip(fitted_I['spw'][i], fitted_XXmYY['spw'][i])]
        
        #  Fit the polarization ratio to the parallactic angle
        params, params_covariance = curve_fit(Rpol_PA_FITTING, ParAngle['spw'][i].rad, Rpol['spw'][i])
        
        fit_params['spw'][i] = params
        fit_covari['spw'][i] = params_covariance
    return Rpol, fit_params, fit_covari


XXYY = XXYY_DATA(vis, field_ids)
Stokes_I = Fitting(XXYY)

# FitStokeI     = fit_I(vis, field_ids)
# FitXXmYY      = fit_XXmYY(vis, field_ids)
# ParAngle_list = get_ParAngle(vis, field_ids)

# test = fit_Pol_PA(FitStokeI, FitXXmYY, ParAngle_list)
