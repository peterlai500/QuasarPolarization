from QuasarPol_Class import QuasarPol
from datetime import date
import time

mystep = 2

st = time.time()

target = 'J1924-2914'
storage = '/run/media/pinhsien/Storage24TB/DATA'
PA_min, PA_max = 5, 10

result = QuasarPol(target, False , 'Dual', 500)
    
if mystep > 0:
    step = 'Query'
    PA_table = result.get_ParaAngle()
    print(f'Querying {target}, data length : {len(PA_table)}.')

if mystep > 1:
    if len(PA_table) > 0:
        step = step + 'and filter'
        f_PA = result.filter_data(PA_min, PA_max)
        print(f'Filtered {target} data length : {len(f_PA)}.')
        if len(f_PA) == 0:
            print(f'No data satify the condition.')

if mystep > 2:
    try:
        step  = step + 'and download'
        today = str(date.today()).replace('-', '')
        target_for_path = target.replace('-', 'm')
        download_path = f'{storage}/{today}'
        os.system(f'mkdir {download_path}')
        os.system(f'rm -rf {download_path}/*')
        result.download(True, download_path)
    except:
        print('Download Error or no data to download')
        pass

if mystep > 3:
    try:
        step = step + 'and untar'
        result.untar()
    except:
        print('Untar error or no file to untar')
        pass

et = time.time()
rt = et - st
print(f'{step} : {rt:.0f} seconds.')
