from QuasarPol_Class import QuasarPol
from datetime import date
import time
import os

mystep = 4

st = time.time()

target = 'J1733-1304'
storage = '/data2/users/pinhsien/DATA'
PA_min, PA_max = 2, 5

result = QuasarPol(target, False , 'Dual', 100)
    
if mystep > 0:
    step = 'Query'
    PA_table = result.get_ParaAngle()
    print(f'Querying {target} data length : {len(PA_table)}.')

if mystep > 1:
    if len(PA_table) > 0:
        step += ', filter'
        f_PA = result.filter_data(PA_min, PA_max)
        print(f'Filtered {target} data length : {len(f_PA)}.') 
        if len(f_PA) == 0: 
            print(f'No data satify the condition.')

if mystep > 2:
    step += ', download'
    today = str(date.today()).replace('-', '')
    target_for_path = target.replace('-', 'm')
    download_path = f'{storage}/{today}'
    os.system(f'mkdir {download_path}')
    os.system(f'rm -rf {download_path}/*')
    result.download(filtered=True, save_directory=download_path)

if mystep > 3:
    step += ', untar'
    result.untar()

et = time.time()
rt = et - st
print(f'{step} : {rt:.0f} seconds.')
