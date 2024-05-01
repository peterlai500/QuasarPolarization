# 03/07

# fitting script

# import uvmultifit as uvm

import numpy as np
vis       = "/home/pinhsien/Research/Baobab_2016data/sgrastar_b8/calibrated.ms.12m.uvaver"
field_id  = [0, 18, 25, 94, 101, 133, 134]
fit_field = []
fit_time  = []

# use CASA ms tools to get columns of DATA, UVW, TIME, FIELD, etc.
ms.open(vis)
ms.select(
        {
            'field_id':field_id
            }
        )
d = ms.getdata(['data', 'field_id', 'time', 'weight'])
ms.close()



# polarization

data   = np.squeeze(d['data'])
weight = np.squeeze(d['weight'])

