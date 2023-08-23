from QuasarPol_Class import QuasarPol
import time

data = QuasarPol('J1924-2914', False, 'Full', 1000)

data.directory = '/home/pinhsien/Research/Data'
print(data.directory)

data.untar()
