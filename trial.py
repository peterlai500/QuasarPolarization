from QuasarPol_Class import QuasarPol
import time

target = QuasarPol('J1924-2914', False, 'Full', 1000)
st = time.time()
data_table = target.get_tables()
et = time.time()
rt = et - st
print(f'Query {target.source} time: {rt:.6f}\nFull data table is {len(data_table)} long')

PA_table = target.get_ParaAngle()

st = time.time()
f_PA = target.filter_data(2.182, 2.2)
et = time.time()
rt = et - st
print(f"Filter time: {rt:.6f} seconds.\n Length of filtered data: {len(f_PA)}")

st = time.time()
target.download(filtered=True,save_directory='/home/pinhsien/Research/Data')
et = time.time()
rt = et - st
print(f"Download time: {rt:.6f} seconds")

st = time.time()
target.untar()
et = time.time()
rt = et - st
