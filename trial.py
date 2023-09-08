from QuasarPol_Class import QuasarPol
import time

mystep = 0

st = time.time()

target = QuasarPol('J1924-2914', False, 'Dual', 1000)
storage = '/run/media/pinhsien/Storage24TB/DATA'

if mystep == 0:
    print('Query date from ALMA data archive')
    data_table = target.get_tables()
    PA_table = target.get_ParaAngle()
    print(f'Table length is {len(data)}')
elif mystep == 2:
    print('Filter data')
    f_PA = target.filter_data(10,20)
elif mystep == 3:
    target.download(filtered=True, save_directory=storage)
    print('Start untar')
    target.untar()
    print('Done')
elif mystep == 4:
    print('Start untar')
    target.untar()
    print('Done')

elif mystep == 5:
    print('Start run pipeline script')
    target.run_pipeline()
    print('DONE')

elif mystep == 6:
    print('Start check casa version')

    print('DONE')
else:
    pass
et = time.time()
rt = et - st
print(f'Runtime : {rt:.0f} seconds.')
