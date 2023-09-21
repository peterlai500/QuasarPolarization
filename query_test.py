from astroquery.alma import Alma
alma = Alma()

from QuasarPol_Class import QuasarPol
'''
data = alma.query(payload=dict(source_name_alma='J2253+1608'),
                  science=False
                 )
print(len(data))
'''

result = QuasarPol('J2253+1608', False , "Dual", 50)

data = result.get_tables()

print(len(data))


