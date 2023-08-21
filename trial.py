import QuasarPol_Class
import time

target = QuasarPol_Class.QuasarPol('J1924-2914', False, 'Full')
data_table = target.get_tables(legacy_columns=True)
print('length of data_table', len(data_table))
PA_table = target.get_ParaAngle()

start_time = time.time()
Filter_PA = target.filter_data(10)
end_time = time.time()
runtime = end_time - start_time

print(f"Runtime: {runtime:.6f} seconds")
print('length of Filtered_PA',len(Filter_PA))
