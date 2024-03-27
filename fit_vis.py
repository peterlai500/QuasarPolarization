# 03/07

# fitting script

# import uvmultifit as uvm

vis = '/home/pinhsien/Research/Baobab_2016data/sgrastar_b8/calibrated.ms.12m.uvaver'
'''
myfit = uvm.uvmultifit(
                        vis, 
                        spw='0', 
                        column='data',
                        field='0'
                        scans=[10],
                        field='0',
                        model=['delta'],
                        var=['p[0], p[1], p[2]'],
                        p_ini=[0.0, 0.0, 1.0],
                        write='model',
                        outfile='B8_7m_fitting.uvfit'
                       )


'''
myfit = uvmodelfit(
                    vis,
                    field='18',
                    spw='',
                    selectdata=True,
                    scan='',
                    niter=10,
                    comptype='P',
                    sourcepar=[1.0, 0.0, 0.0],
                    varypar=[False, True, True],
                    outfile='sgrastar_b8.12m_fit.cl'
                  )


cl.open('sgrastar_b8.12m_fit.cl')
fit = cl.getcomponent(0)
