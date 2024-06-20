from QuasarPol_Class import QuasarPol

from datetime import date, datetime

import subprocess
import os

target = 'J1924-2914'               # your target
calibration = False                 # you're free to modify in True or False
polarization = 'Dual'               # polarization type can be 'Single', 'Dual', 'Full'
data_length = 20000                 # Integer
min_change_in_PA = -60              # Parallactic angle change lower bound
Max_change_in_PA = 60               # Parallactic angle change upper bound
mindate = "01-01-2018"
maxdate = "30-06-2018"

storage = '/run/media/pinhsien/PinHsien2022Dec/DATA_QuasarPol'     # yout storage directory

result = QuasarPol(target, calibration, polarization, data_length)

# The .get_tables() and the .get_ParaAngle() steps can be passed when using script.

PA_filter = result.filter_data(mindate, maxdate, min_change_in_PA, Max_change_in_PA)
# The filter step is to obtain the lower bound and upper bound varibles.

# Can sort the data like the the below.
today = str(date.today()).replace('-', '')
target_name = target.replace('+', 'p').replace('-', 'm')
download_path = f'{storage}/{target_name}.{today}'

l = subprocess.run("ls", cwd=f"{storage}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
l = l.stdout.decode()
l = l.split('\n')

if download_path not in l:
    os.system(f"mkdir {download_path}")

result.download(filtered=True, save_directory=download_path)

result.untar()
# result.run_script()
