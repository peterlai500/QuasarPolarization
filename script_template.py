from QuasarPol_Class import QuasarPol

target = ''             # your target
calibration = False     # you're free to modify in True or False
polarization = ''       # polarization type can be 'Single', 'Dual', 'Full'
data_length = 5000      # Integer
PA_min = 40             # Parallactic angle change lower bound
PA_max = 50             # Parallactic angle change upper bound

storage = ''            # yout storage directory

result = QuasarPol(target, calibration, polarization, data_length)

# The .get_tables() and the .get_ParaAngle() steps can be passed when using script.

PA_filter = result.filter_data(min_change_in_PA, Max_change_in_PA)
# The filter step is to obtain the lower bound and upper bound varibles.

result.download(filtered=False, save_directory=storage)
result.untar()
result.run_script()
