from QuasarPol_Class import QuasarPol
from datetime import date
import time
import os
import numpy as np

mystep = 4

st = time.time()

target = '3C273'
storage = '/run/media/pinhsien/Storage24TB/DATA'
PA_min, PA_max = -20, -19

result = QuasarPol(target, True, 'Dual', 100)

if mystep > 0:
    step = 'Query'
    PA_table = result.get_ParaAngle()
    print(f'Querying {target} data length : {len(PA_table)}.')

if mystep > 1:
    if len(PA_table) > 0:
        step += ', filter'
        f_PA = result.filter_data(PA_min, PA_max)
        print(f'Filtered {target} data length : {len(np.unique(f_PA["member_ous_uid"]))}.') 
        if len(f_PA) == 0: 
            print(f'No data satify the condition.')

if mystep > 2:
    step += ', download'
    today = str(date.today()).replace('-', '')
    target_for_path = target.replace('-', 'm').replace('+', 'p')
    download_path = f'{storage}/{target}.{today}'
    os.system(f'mkdir {download_path}')
    os.system(f'rm -rf {download_path}/*')
    result.download(filtered=False, save_directory=download_path)

if mystep > 3:
    step += ', untar'
    result.untar()

if mystep == 4:
    result.run_pipeline()

et = time.time()
rt = et - st
print(f'{step} : {rt:.0f} seconds.')
