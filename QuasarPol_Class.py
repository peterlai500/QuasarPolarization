from astroquery.alma import Alma
alma=Alma()

from astropy import units as u
from astropy.coordinates import Angle, SkyCoord
from astropy.time import Time

from astropy.io import fits

from astroplan import Observer

class QuasarPol:
    
    def almaquery(source):
        result_ObsCorelist = alma.query(payload=dict(source_name_alme=source),
                                        science=False)

        result_Almalist = alma.query(payload=dict(source_name_alme=source),
                                        science=False,
                                        lagacy_columns=True)

