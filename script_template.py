from QuasarPol_Class import QuasarPol
from datetime import date, datetime

target = 'J1924-2914'               # your target
calibration = False                 # you're free to modify in True or False
polarization = 'False'              # polarization type can be 'Single', 'Dual', 'Full'
data_length = 20000                 # Integer
min_change_in_PA = -33.54           # Parallactic angle change lower bound
Max_change_in_PA = -33.53           # Parallactic angle change upper bound

storage = '/run/media/pinhsien/Storage24TB/DATA'            # yout storage directory

result = QuasarPol(target, calibration, polarization, data_length)

# The .get_tables() and the .get_ParaAngle() steps can be passed when using script.

PA_filter = result.filter_data(min_change_in_PA, Max_change_in_PA)
# The filter step is to obtain the lower bound and upper bound varibles.

# Can sort the data like the the below.
today = str(date.today()).replace('-', '')
target_name = target.replace('+', 'p').replace('-', 'm')
download_path = f'{storage}/{target_name}.{today}'

result.download(filtered=True, save_directory=download_path)
result.untar()
# result.run_script()
