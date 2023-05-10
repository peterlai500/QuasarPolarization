from astroquery.alma import Alma
alma=Alma()

from astropy import units as u
from astropy.coordinates import Angle, SkyCoord
from astropy.table import QTable
from astropy.time import Time
from astropy.io import fits

from astroplan import Observer

import numpy as np



class QuasarPol:
    
    def __init__(self, source, sci_obs, table_length):
        '''
        constructor of the class
        '''
        self.science = sci_obs
        self.len = table_length
        self.source = source
    
    
    def __del__(self):
        '''
        Destrucror of th class
        '''
    
    
    def get_tables(self, *, legacy_columns=False):
        
        '''
        Tool to get data tables.
        
        Parameters
        ----------
        legacy_columns : bool
            True to return the columns from the obsolete ALMA advanced query,
            otherwise return the current columns based on ObsCore model.
        
        Returns
        -------
        
        Table with results.
        '''
        
        self.ALMA_table = alma.query(payload=dict(source_name_alma=self.source),
                                     science=self.science,
                                     legacy_columns=True, 
                                     maxrec=self.len
                                    )
        
        self.ObsCore_table = alma.query(payload=dict(source_name_alma=self.source),
                                        science=self.science,
                                        maxrec=self.len
                                       )
        
        if legacy_columns == True:    
            return self.ALMA_table
        else:
            return self.ObsCore_table
    
    
    
    def get_ParaAngle(self):
        
        '''
        
        To get parallactic angle and see informations
        
        Returns
        -------
        
        Table with "observation ID", "member observation unit set ID", 
        initial and final PAs.
        
        '''
        
        self.get_tables()
        ALMA = Observer.at_site("ALMA")
        
        Init_PA = []
        End_PA = []
        Obs_ids = self.ObsCore_table['obs_id']
        Uids = self.ObsCore_table['member_ous_uid']
        
        for i in range(len(Uids)):
            
            ALMA = Observer.at_site("ALMA")
            
            # Get source coordinate
            Ra = self.ALMA_table['RA'][i]
            Dec = self.ALMA_table['Dec'][i]
            target_coord = SkyCoord(ra=Ra*u.deg, dec=Dec*u.deg)
            
            # Get date
            date = self.ALMA_table['Observation date'][i]
            [day, month, year] = date.split('-')
            obs_date = year + '-' + month + '-' + day
            
            # Get observation time information
            start_time = self.ObsCore_table['t_min'][i]
            duration_time = self.ObsCore_table['t_exptime'][i]
            end_time = start_time + duration_time
            
            # Transform into the format we can understand (UTC)
            hours = int(start_time / 3600)
            remaining_seconds = start_time % 3600
            minutes = int(remaining_seconds / 60)
            seconds = remaining_seconds - minutes * 60
            
            obs_start_time = str(hours)+':'+str(minutes)+':'+str(seconds)
            
            # combine time and date
            obs_init_Datetime = Time(obs_date + ' ' + obs_start_time)
            
            # Initial Parallactic Angle calculation and create list
            init_PA = Angle(ALMA.parallactic_angle(obs_init_Datetime, target_coord), u.deg)
            Init_PA.append(init_PA)
            
            # Final Parallactic Angle Part
            hours = int(end_time / 3600)
            remaining_seconds = end_time % 3600
            minutes = int(remaining_seconds / 60)
            seconds = remaining_seconds - minutes * 60
            
            obs_end_time = str(hours)+':'+str(minutes)+':'+str(seconds)
            obs_end_Datetime = Time(obs_date + ' ' + obs_end_time)
            
            end_PA = Angle(ALMA.parallactic_angle(obs_end_Datetime, target_coord), u.deg)
            End_PA.append(end_PA)
        
        ParaAngle = QTable([Obs_ids, Uids, Init_PA, End_PA], 
                           names=('obs_id', 'member_ous_uid', 'Initial Parallactic Angle','Final Parallactic Angle'))
        
        return ParaAngle
    
    
    
    def download(self, *, save_directory=alma.cache_location):
        
        '''
        To save files in specific diretory
        
        
        Parameters
        ----------
        save_directory : string
            The directory the files save to. If None will save to alma query cache 
            directory, '~/.astropy/cache/astroquery/Alma/'.
        '''
        
        PA_table = self.get_ParaAngle()
        uids = np.unique(PA_table['member_ous_uid'])
        
        
        for ids in uids:
            
            # Get data info
            data_info = alma.get_data_info(uids)
            
            # Extract the URLs from the data_info table
            link_list = [row['access_url'] for row in data_info if row['access_url']]
            alma.cache_location = save_directory
            
            # Download files if there are valid URLs
            if link_list:
                alma.download_files(link_list)
            else:
                print("No valid URLs found for download.")
