# 03/07

# fitting script

# import uvmultifit as uvm

import numpy as np

vis       = "/home/pinhsien/Research/Baobab_2016data/sgrastar_b8/calibrated.ms.12m.uvaver"
field_ids = [0, 18, 25, 94, 101, 133, 134]

# Try to read data in respectively to each field
def select_field(filename, fields):
    ms.open(filename)
    for FieldID in fields:
        ms.select({'field':FieldID})
        field_data = ms.getdata(['data', 'antenna1', 'antenna2', 'field_id', 'time', 'weight', 'flag'])
        
    return d



# use CASA ms tools to get columns of DATA, UVW, TIME, FIELD, etc.
ms.open(vis)
ms.select(
        {
            'field_id':field_id
            }
        )
spw_info = ms.getspectralwindowinfo()
nchan    = spw_info["0"]["NumChan"]
npol     = spw_info["0"]["NumCorr"]
d = ms.getdata(['data', 'antenna1', 'antenna2', 'field_id', 'time', 'weight', 'flag'])
ms.close()

data   = np.squeeze(d['data'])
ant1   = d['antenna1']
ant2   = d['antenna2']
weight = d['weight']
flags  = np.squeeze(d['flag'])

# use CASA table tool get the frequency
tb.open(vis+"/SPECTRAL_WINDOW")
freqs = tb.getcol("CHAN_FREQ")
rfreq = tb.getcol("REF_FREQUENCY")
tb.close

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
    wgts = (weight_xx + weight_yy)

# toss out the autocorrelation placeholders
xc = np.where(ant1 != ant2)[0]

