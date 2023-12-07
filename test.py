from QuasarPol_Class import QuasarPol
from datetime import date, datetime
import numpy as np

target        = 'J1924-2914'
calibration   = False
polarization  = 'Dual'
data_length   = 20000
earliest_date = "27-09-2022"
latest_date   = "30-09-2023"
min_change    = -1
Max_change    = 1

storage = '/run/media/pinhsien/Storage24TB/DATA'

result = QuasarPol(target, calibration, polarization, data_length)

step = 3

if step >= 0:
    data = result.get_tables()
    print(f'There are {len(data)} resleased {target} data in archive.')
if step >= 1:
    PA_filtered = result.filter_data(earliest_date, latest_date, min_change, Max_change)
    print(f'Total {len(np.unique(PA_filtered["proposal_id"]))} observations satisfy the condition.')
if step >= 2:
    today = str(date.today()).replace('-','')
    target_name = target.replace('+', 'p').replace('-', 'm')
    path = f'{storage}/{target_name}.{today}'
    result.download(filtered=True, save_directory=path)
    result.untar()
if step >= 3:
    result.run_script()
