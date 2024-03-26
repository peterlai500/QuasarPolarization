import numpy as np

cc = 29979245800.0          # speed of light (cm/s)
def visibility(filename, inclination, pa):
    
    ```
    filename: the filename of the calibrated visibility
    ```

    # Use CASA table tools to get columns of UVW, DATA, WEIGHT, etc.
    tb.open(filename)
    data   = tb.getcol("DATA")
    uvw    = tb.getcol("UVW")
    weight = tb.getcol("WEIGHT")
    ant1   = tb.getcol("ANTENNA1")
    ant2   = tb.getcol("ANTENNA2")
    flags  = tb.getcol("FLAG")
    tb.close()

    #  print(np.shape(data) )

    # Use CASA ms tools to get the channel/spw info
    ms.open(filename)
    spw_info = ms.getspectralwindowinfo()
    nchan    = spw_info["0"]["NumChan"]
    npol     = spw_info["0"]["NumCorr"]
    ms.close()
    # print(spw_info["0"]["NumChan"])
    # print(spw_info["1"]["NumChan"])
    # print(spw_info["2"]["NumChan"])
    # print(spw_info["3"]["NumChan"])

    # Use CASA table tools to get frequencies
    tb.open(filename+"/SPECTRAL_WINDOW")
    freqs = tb.getcol("CHAN_FREQ")
    rfreq = tb.getcol("REF_FREQUENCY")
    tb.close()

    # break out the u, v spatial frequencies, convert from m to lambda
    # print('uvw', np.shape(uvw) )

    uutmp = uvw[0,:] *rfreq[0]/(cc/100)
    vvtmp = uvw[1,:] *rfreq[0]/(cc/100)

    # deprojection
    uu = (uutmp*np.cos(pa*np.pi/180.0)-vvtmp*np.sin(pa*np.pi/180.0))*np.cos(inclination*np.pi/180.0)
    vv = uutmp*np.sin(pa*np.pi/180.0)+vvtmp*np.cos(pa*np.pi/180.0)

    # check to see whether the polarizations are already averaged
    data   = np.squeeze(data)
    weight = np.squeeze(weight)
    flags  = np.squeeze(flags)

    if npol==1:
        Re = data.real
        Im = data.imag
        wgts = weight

    else:
        # polarization averaging
        Re_xx = data[0,:].real
        Re_yy = data[1,:].real
        Im_xx = data[0,:].imag
        Im_yy = data[1,:].imag
        weight_xx = weight[0,:]
        weight_yy = weight[1,:]
        #weight_xx = 1.
        #weight_yy = 1.
        flags = flags[0,:]*flags[1,:]

        # - weighted averages
        with np.errstate(divide='ignore', invalid='ignore'):
            Re = np.where((weight_xx + weight_yy) != 0, (Re_xx*weight_xx + Re_yy*weight_yy) / (weight_xx + weight_yy), 0.)
            Im = np.where((weight_xx + weight_yy) != 0, (Im_xx*weight_xx + Im_yy*weight_yy) / (weight_xx + weight_yy), 0.)
        wgts = (weight_xx + weight_yy)

    # toss out the autocorrelation placeholders
    xc = np.where(ant1 != ant2)[0]

    # check if there's only a single channel
    if nchan==1:
        data_real = Re[np.newaxis, xc]
        data_imag = Im[np.newaxis, xc]
        flags = flags[xc]
    else:
        data_real = Re[:,xc]
        data_imag = Im[:,xc]
        flags = flags[:,xc]

        # if the majority of points in any channel are flagged, it probably means someone flagged an entire channel - spit warning
        if np.mean(flags.all(axis=0)) > 0.5:
            print("WARNING: Over half of the (u,v) points in at least one channel are marked as flagged. If you didn't expect this, it is likely due to having an entire channel flagged in the ms. Please double check this and be careful if model fitting or using diff mode.")

        # collapse flags to single channel, because weights are not currently channelized
        flags = flags.any(axis=0)

    #data_wgts = wgts[xc]
    data_uu = -1 * uu[xc]
    data_vv = vv[xc]

    ### visibility
    #data_VV = data_real+data_imag*1.0j

    data_real = np.squeeze(data_real)
    data_imag = np.squeeze(data_imag)

    # now remove all flagged data (we assume the user doesn't want to interpolate for these points)
    # commenting this out for now, but leaving infrastructure in place if desired later
    #data_wgts = data_wgts[np.logical_not(flags)]
    #data_uu = data_uu[np.logical_not(flags)]
    #data_vv = data_vv[np.logical_not(flags)]
    #data_VV = data_VV[:,np.logical_not(flags)]

    # remove all flagged data
    data_uu = data_uu[np.logical_not(flags)]
    data_vv = data_vv[np.logical_not(flags)]
    data_real = data_real[np.logical_not(flags)]
    data_imag = data_imag[np.logical_not(flags)]

    #uuvv_klambda   = np.zeros(xc.shape[0])
    #uv_theta       = np.zeros(xc.shape[0])
    uuvv_klambda   = np.zeros(data_uu.shape[0])
    uv_theta       = np.zeros(data_uu.shape[0])
    index_uv_theta  = np.array([-999])

    #for num in range(xc.shape[0]):
    for num in range(data_uu.shape[0]):

        uuvv_klambda[num] = np.sqrt(data_uu[num] * data_uu[num] + data_vv[num] * data_vv[num]) / 1000.

        index_uv_theta = np.append(index_uv_theta, num)

    index_uv_theta      = np.delete(index_uv_theta, [0])
    uuvv_klambda_sector = uuvv_klambda[index_uv_theta]
    data_real_sector    = data_real[index_uv_theta] * 1000
    data_imag_sector    = data_imag[index_uv_theta] * 1000

    return index_uv_theta, uuvv_klambda_sector, data_real_sector, data_imag_sector





filename = '/home/pinhsien/Research/Baobab_2016data/sgrastar_b8/calibrated.ms.7m.uvaver'

B8_7m = visibility('/home/pinhsien/Research/Baobab_2016data/sgrastar_b8/calibrated.ms.7m.uvaver',0,0)
