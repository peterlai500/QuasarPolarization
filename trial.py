from QuasarPol_Class import QuasarPol
import time

mystep = 3
st = time.time()

target = QuasarPol('J1924-2914', False, 'Full', 1000)
data_table = target.get_tables()
PA_table = target.get_ParaAngle()
f_PA = target.filter_data(2.182, 2.2)
target.directory = '/home/pinhsien/Research/Data'

if mystep == 1:
    target.download(filtered=True, save_directory='/home/pinhsien/Research/Data')
elif mystep == 2:
    print('Start untar')
    target.untar()
    print('Done')

elif mystep == 3:
    print('Start run pipeline script')
    target.run_pipeline()
    print('DONE')

elif mystep == 4:
    print('Start check casa version')

et = time.time()
rt = et - st
print(f'Runtime : {rt:.0f} seconds.')
