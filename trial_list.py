from QuasarPol_Class import QuasarPol
import numpy as np
from datetime import date
import time
import os

with open('target_list.txt', 'r') as file:
    targets = file.readlines()

for target in targets:
    target = target.strip()
    result = QuasarPol(target, True, 'Dual', 100)
    
    PA_table = result.get_ParaAngle()
    if len(PA_table) != 0:
        print(f"---------\n {target} has {len(np.unique(PA_table['proposal_id]))} data.")
        f_PA = result.filter_data(10, 15)

        if len(f_PA) != 0:
            print(f"{target} has {len(np.unique(f_PA['Project code]))} data satisfy th constrain.")
            print(f"Downloading {len(np.unique(f_PA['Project code]))} for {target}")
            today = str(date.today()).replace('-', '')
            target_for_path = target.replace('-', 'm').replace('+', 'p')
            download_path = f'{storage}/{target}.{today}'
            os.system(f'mkdir {download_path}')
            os.system(f'rm -rf {download_path}/*')
            result.download(filtered=False, save_directory=download_path)
            result.untar()
            try:
                result.run_pipeline()
            except:
                print("Occured Error running pipeline.")
                pass
        else:
            print(f"{target} has no data pass filter.")
    else:
        print(f"No result for {target}")
