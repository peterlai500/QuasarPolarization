from QuasarPol_Class import QuasarPol
from datetime import date, datetime
import numpy as np

target        = "J1924-2914"
calibration   = False
polarization  = "Dual"
data_length   = 20000
earliest_date = "10-02-2016"
latest_date   = "01-04-2016"
min_change    = 90
Max_change    = 180

storage = '/run/media/pinhsien/Storage24TB/DATA'

result = QuasarPol(target, calibration, polarization, data_length)

step = 2

if step >= 0:       # make sure the data is exist
    data = result.get_tables()
    print(f'There are {len(data)} resleased {target} data in archive.')

if step >= 1:       # check the filter result
    PA_filtered = result.filter_data(earliest_date, latest_date, min_change, Max_change)
    print(f'Total {len(np.unique(PA_filtered["proposal_id"]))} observations satisfy the condition.')

if step >= 2:       # download and the data
    today = str(date.today()).replace('-','')
    target_name = target.replace('+', 'p').replace('-', 'm')
    path = f'{storage}/{target_name}.{today}'
    result.download(filtered=True, save_directory=path)
    result.untar()

if step >= 3:       # run the calibration pipeline
    result.run_script()
