import os
import numpy as np
from scipy.optimize import curve_fit


vis = "sgrastar_b8/calibrated.ms.12m.uvaver"
field_ids = [0, 18, 25, 94, 101, 133, 134]

def fit_I(vis, field):
    # All the information saved into d with a dict
    fitted_I = {"spw":{}}
    
    # make directory "fitting_result" to save the result of fitting.
    l = subprocess.run("ls", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    l = l.stdout.decode()
    l = l.split('\n')
    if "fitting_result" not in l:
        os.system("mkdir fitting_result")
    
    name = vis.replace("/", ".")
    
    # read the ms and use the uvmodelfit in CASA
    for f in field:
        ms.open(vis)
        ms.select({'field_id':f})
        spw_info = ms.getspectralwindowinfo()
        for s in range(len(spw_info)):
            # Use uvmodelfit to fit the Stokes I
            uvmodelfit(
                    vis, 
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

def XXmYY_FITTING(uvdist, A):
    fit_xxmyy = [A] * len(uvdist)
    return fit_xxmyy

def fit_XXmYY(vis, field):
    fitted_XXmYY = {"spw":{}}
    for f in field:
        print('field:', f)
        ms.open(vis)
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


def get_ParAngle():
    pass

def calc_PolRatio(StokesI, XXmYY):
    R = {"spw":{}}
    for s in range(len(StokesI["spw"])):
        print("spectral window:"s)

        

        if s not in R["spw"]:
            R["spw"][s] = []
        R["spw"][s].append(fit['flux']['value'][0])

    pass

FitStokeI = fit_I(vis, field_ids)
FitXXmYY = fit_XXmYY(vis, field_ids)
