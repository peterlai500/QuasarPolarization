from QuasarPol_Class import QuasarPol
from datetime import date
import time

mystep = 1

st = time.time()

storage = '/run/media/pinhsien/Storage24TB/DATA'
PA_min, PA_max = 5, 10

with open('target_list.txt', 'r') as file:
    targets = file.readlines()

for target in targets:

    target = target.strip()
    result = QuasarPol(target, False , 'Dual', 200)
    
    if mystep > 0:
        step = 'Query'
        PA_table = result.get_ParaAngle()
        print(f'Querying {target}, data length : {len(PA_table)}.')

    elif mystep > 1:
        if len(PA_table) > 0:
            try:
                step = step + 'and filter'
                f_PA = result.filtered_PA(PA_min. PA_max)
                print(f'Filtered {target} data length : {len(f_PA)}.')
            except:
                 print('Filter Error')
            
            if len(f_PA) == 0: 
                print(f'No data satify the condition.')

    elif mystep > 2:
        try:
            download_path = f'{storage}/{date.today()}'
            os.system(f'mkdir {download_path}')
            os.system(f'rm -rf {download_path}/*')
            result.download(True, download_path)
        except:
            print('Download Error')
    
    elif mystep > 3:

        result.untar()




et = time.time()
rt = et - st
print(f'Querying  : {rt:.0f} seconds.')
