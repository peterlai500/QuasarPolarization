from QuasarPol_Class import QuasarPol
import time

mystep = 2

target = QuasarPol('J1924-2914', False, 'Full', 1000)
data_table = target.get_tables()
PA_table = target.get_ParaAngle()
f_PA = target.filter_data(2.182, 2.2)

if mystep == 1:
    target.download(filtered=True, save_directory='/home/pinhsien/Research/Data')

elif mystep == 2:
    print('Start untar')
    target.directory = '/home/pinhsien/Research/Data'
    target.untar()
    print('Done')

elif mystep == 3:
    
    target.run_pipeline()
    

