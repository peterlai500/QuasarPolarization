import os
import numpy as np
from scipy.optimize import curve_fit


vis = "sgrastar_b8/calibrated.ms.12m.uvaver"
field_ids = [0, 18, 25, 94, 101, 133, 134]

fitted_data = {"spw":{}}

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

def fit_XXmYY(vis, field):
    fitted_XXmYY = {"spw":{}}
    for f in field:
        ms.open(vis)
        ms.select({'field':f})
        spw_info = ms.getspectralwindowinfo()
        for s in range(len(spw_info)):
            nchan = spw_info["0"]["NumChan"]
            npol  = spw_info["0"]["NumCorr"]
            d = ms.getdata(['data', 'antenna1', 'antenna2', 'weight', 'flag'])
            
            # modify the data into proper format
            flags  = np.squeeze(d['flag'])
            data   = np.squeeze(d['data'])
            ant1   = d['antenna1']
            ant2   = d['antenna2']
            weight = d['weight']
            
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
            Re_xx = Re_xx[np.newaxis, xc]
            Im_xx = Im_xx[np.newaxis, xc]
            Re_yy = Re_yy[np.newaxis, xc]
            Im_yy = Im_yy[np.newaxis, xc]

            flags = flags[xc]


    pass




# FitStokeI = fit_I(vis, field_ids)
