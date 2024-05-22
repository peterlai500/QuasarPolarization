import os
import numpy as np
import matplotlib.pyplot as plt
from statistics import mean
from scipy.optimize import curve_fit

from astropy.coordinates import Angle
from astropy import units as u

vis = "sgrastar_b8/calibrated.ms.12m.uvaver"
field_ids = [0, 18, 25, 94, 101, 133, 134]

def ChanAverage(visibility):
    ms.open(visibility)
    spw_info = ms.getspectralwindowinfo()
    ms.close()

    if spw_info['0']['NumChan'] != 1:
        mstransform(
                vis         = visibility,
                outputvis   = f"{vis}.chanaver",
                chanaverage = True,
                chanbin     = spw_info['0']['NumChan']
                )
        outputvis   = f"{vis}.chanaver"
    return outputvis


def PointSource_FITTING(uvdist, A):
    fitting = [A] * len(uvdist)
    return fitting

def read_DATA(visibility, field):
    XX_data = {"spw":{}}
    YY_data = {"spw":{}}
    UVdist  = {"spw":{}}
    data_dict = []
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

            flags = flags[0,:] * flags[1,:]
             
            # toss out the autocorrelation placeholders
            xc = np.where(ant1 != ant2)[0]

            Re_xx  = re_xx[np.newaxis, xc]
            Im_xx  = im_xx[np.newaxis, xc]
            Re_yy  = re_yy[np.newaxis, xc]
            Im_yy  = im_yy[np.newaxis, xc]
            uvdist = uvdist[xc] 
            flags  = flags[xc]

            Re_xx  = np.squeeze(Re_xx)
            Im_xx  = np.squeeze(Im_xx)
            Re_yy  = np.squeeze(Re_yy)
            Im_yy  = np.squeeze(Im_yy)
            
            # Remove the flagged data
            Re_xx  = Re_xx[np.logical_not(flags)]
            Im_xx  = Im_xx[np.logical_not(flags)]
            Re_yy  = Re_yy[np.logical_not(flags)]
            Im_yy  = Im_yy[np.logical_not(flags)]
            uvdist = uvdist[np.logical_not(flags)]
            
            # Combining Real part and Imag part
            XX_VIS = Re_xx + Im_xx*1.0j
            YY_VIS = Re_yy + Im_yy*1.0j
            print(f"Flux amplitude: XX = {np.mean(abs(XX_VIS))}\tYY = {np.mean(abs(YY_VIS))}\n")
            data_dict = [XX_data, YY_data, UVdist]
            for data in data_dict:
                if s not in data['spw']:
                    data['spw'][s] = []
            data_dict[0]['spw'][s].append(XX_VIS)
            data_dict[1]['spw'][s].append(YY_VIS)
            data_dict[2]['spw'][s].append(uvdist)

    return data_dict



def Fit_I(XXYYdata):
    XX     = XXYYdata[0]
    YY     = XXYYdata[1]
    uvdist = XXYYdata[2]

    StokesI = {'spw':{}}
    FittedI = {'spw':{}}

    # Stokes I = (XX + YY)/2
    for spw in range(len(XX['spw'])):
        for i in range(len(XX['spw'][spw])):
            stokes_i = abs( XX['spw'][spw][i] + YY['spw'][spw][i] ) / 2
            if spw not in StokesI['spw']:
                StokesI['spw'][spw] = []
            
            StokesI['spw'][spw].append(stokes_i)
            print(f'Fitting field {i} spw {spw} Stokes I')
            params, params_covariance = curve_fit(PointSource_FITTING, uvdist['spw'][spw][i], StokesI['spw'][spw][i])
            print(f'result: I = {params[0]}\n')
            if spw not in FittedI['spw']:
                FittedI['spw'][spw] = []
            FittedI['spw'][spw].append(params[0])

    return StokesI, FittedI

def FitRpol(XXYYdata, StokesI):
    XX       = XXYYdata[0]
    YY       = XXYYdata[1]
    uvdist   = XXYYdata[2]
    stokes_i = StokesI[1]
    
    Rpol    = {'spw':{}}
    fitRpol = {'spw':{}}
    
    for spw in range(len(XX['spw'])):
        for i in range(len(XX['spw'][spw])):
            stokes_i = (XX['spw'][spw][i] + YY['spw'][spw][i]) / 2
            XXmYY    = XX['spw'][spw][i] - YY['spw'][spw][i]
            rpol     = (XXmYY / stokes_i)
            if spw not in Rpol['spw']:
                Rpol['spw'][spw] = []
            Rpol['spw'][spw].append(rpol)
            print(f'Fitting (XX-YY)/I field {i} spw {spw}') 
            params, params_covariance = curve_fit(PointSource_FITTING, uvdist['spw'][spw][i], rpol)
            print(f'result: (XX-YY)/I = {params[0]}')
            if spw not in fitRpol['spw']:
                fitRpol['spw'][spw] = []
            fitRpol['spw'][spw].append(params[0])
    return Rpol, fitRpol


def get_ParAngle(visibility, field):

    ParAngle = {'spw':{}}

    # make a directory to save the ascii file from the plotms
    l = subprocess.run("ls", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    l = l.stdout.decode()
    l = l.split('\n')

    name = visibility.replace("/", ".")

    if "plotms_result" not in l:
        os.system("mkdir plotms_result")
    else:
        os.system(f"rm -rf plotms_result/{name}*")

    # Read the spectral window info from ms
    for f in field:
        ms.open(visibility)
        ms.select({'field_id':f})
        spw_info = ms.getspectralwindowinfo()
        ms.close()
        for s in range(len(spw_info)):
            parangle = []
            # use plotms to get and the information of ParAngle
            # and export the result to ASCII format
            plotms(
                visibility,
                xaxis      = 'Time',
                yaxis      = 'ParAngle',
                selectdata = True,
                field      = str(f),
                spw        = str(s),
                plotfile   = f'plotms_result/{name}.plot.field{f}.spw{s}.txt'
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

def Fit_RpolPA(Rpol, ParAngle):
    rpol = Rpol[1]
    pa   = ParAngle
    if len(rpol) != len(pa):
        return
    fit_params = {'spw':{}}
    fit_covari = {'spw':{}}
    for spw_id in range(len(rpol['spw'])):
        if all(spw_id not in d for d in [fit_params['spw'], fit_covari['spw']]):
            fit_params['spw'][spw_id] = []
            fit_covari['spw'][spw_id] = []

        print(f'Curve fitting (XX-YY)/I for spw {spw_id}\n')
        params, params_covariance = curve_fit(Rpol_PA_FITTING, pa['spw'][spw_id].rad, rpol['spw'][spw_id])

        fit_params['spw'][spw_id] = params
        fit_covari['spw'][spw_id] = params_covariance
    return fit_params, fit_covari

def plot_fitting(Rpol, ParAngle, Fitting, save=True):
    rpol   = Rpol[1]
    PA     = ParAngle
    params = Fitting[0]

    l = subprocess.run("ls", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    l = l.stdout.decode()
    l = l.split('\n')

    if "images" not in l:
        os.system("mkdir images")
    
    pa = np.linspace(-0.5*np.pi, 0.5*np.pi, 360)
    for spw in range(len(rpol['spw'])):
        plt.clf()
        plt.cla()
        plt.plot(PA['spw'][spw].rad, rpol['spw'][spw], '.')
        plt.plot(pa, Rpol_PA_FITTING(pa, params['spw'][spw][0], params['spw'][spw][1], params['spw'][spw][2]))
        plt.xlabel('Parallactic Angle (rad)')
        plt.ylabel(r'$\frac{XX-YY}{I}$')
#       plt.title(r'$\frac{XX-YY}{I}$ vs ParAngle at spw {}'.format(spw))
        plt.legend(["data","model"])
        plt.show()
        if save == True:
            plt.savefig(f'images/Rpol-PA_fitting_spw{spw}.pdf')

vis = "sgrastar_b8/calibrated.ms.12m.uvaver"
field_ids = [0, 18, 25, 94, 101, 133, 134]

XXYYdata      = read_DATA(vis, field_ids)
StokesI       = Fit_I(XXYYdata)
Rpol          = FitRpol(XXYYdata, StokesI)
ParAngle_list = get_ParAngle(vis, field_ids)
Fitting       = Fit_RpolPA(Rpol, ParAngle_list)
plot_fitting(Rpol, ParAngle_list, Fitting, save=True)
