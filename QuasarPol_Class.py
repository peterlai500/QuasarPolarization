import os
import sys
import tarfile
import subprocess
import xml.etree.ElementTree as ET

from astroquery.alma import Alma
alma=Alma()

from astropy import units as u
from astropy.coordinates import Angle, SkyCoord
from astropy.table import QTable
from astropy.time import Time
from astropy.io import fits

from astroplan import Observer

import numpy as np
import time
from datetime import datetime

alma.archice_url = 'https://almascience.nao.ac.jp/aq/'

class QuasarPol:
    
    def __init__(self, source, sci_obs, pol, table_length):
        '''
        constructor of the class
        
        Parameters
        ---------
        sci_obs : bool
            True to return only science datasets, 
            False to return only calibration, None to return both.
        pol : str ('Single', 'Dual', 'Full')
            Types of polarisation products provides
            'Single' : Return only XX or YY
            'Dual' : Return datasets contain both XX and YY
            'Full' : Return datasets contain all types of polarisation, i.e., XX, YY, XY, and YX.
        table_length : int
        '''
        self.science = sci_obs
        self.len = table_length
        self.source = source
        self.pol = pol
    
    
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

        if legacy_columns == True:
            ALMA = []
            ALMA = alma.query(payload=dict(source_name_alma=self.source, polarisation_type=self.pol),
                              science=self.science,
                              legacy_columns=True, 
                              maxrec=self.len
                             )
            return ALMA

        else:
            ObsCore_format = []
            ObsCore_format = alma.query(payload=dict(source_name_alma=self.source, polarisation_type=self.pol),
                                        science=self.science,
                                        maxrec=self.len
                                       )
            return ObsCore_format





    def get_ParaAngle(self):
        
        '''
        
        To get parallactic angle and see informations
        
        Returns
        -------
        
        Table with "observation ID", "member observation unit set ID", 
        initial and final PAs.
        
        '''

        ObsCore_table = self.get_tables()
        ALMA_table = self.get_tables(legacy_columns=True)
        ALMA_location = Observer.at_site("ALMA")
        
        Init_PA = []
        End_PA = []
        Delta_PA = []
        Obs_date = []
        Obs_ids = ObsCore_table['obs_id']
        Uids = ObsCore_table['member_ous_uid']
        
        for i in range(len(Uids)):
            
            # Get source coordinate
            Ra = ALMA_table['RA'][i]
            Dec = ALMA_table['Dec'][i]
            target_coord = SkyCoord(ra=Ra*u.deg, dec=Dec*u.deg)

            # Get date
            date = ALMA_table['Observation date'][i]
            [day, month, year] = date.split('-')
            Obs_date.append(date)
            
            # Get the time information
            start_time = ObsCore_table['t_min'][i]
            start_time = Time(start_time,format='mjd').utc.iso
            start_time = datetime.fromisoformat(start_time)

            end_time   = ObsCore_table['t_max'][i]
            end_time = Time(end_time, format='mjd').utc.iso
            end_time = datetime.fromisoformat(end_time)

            # Initial Parallactic Angle calculation and create list
            init_PA = ALMA_location.parallactic_angle(start_time, target_coord)
            Init_PA.append(init_PA)
            
            # End Parallactic Angle
            end_PA = ALMA_location.parallactic_angle(end_time, target_coord)
            End_PA.append(end_PA)
            
            delta_PA = end_PA - init_PA
            '''
            if abs(delta_PA / u.deg) > 180:
                delta_PA = (delta_PA / u.deg + 360) * u.deg
            '''
            Delta_PA.append(abs(delta_PA))
        
        ParaAngle = QTable([Obs_ids, Uids, Obs_date, Delta_PA, Init_PA, End_PA], 
                           names=('obs_id', 'member_ous_uid', 'Obs_Date', 'Change_PA', 'Init_PA','End_PA'))

        return ParaAngle





    def filter_data(self, min_change_in_PA, Max_change_in_PA):
        
        '''
        Filter the parallactic angle from self.get_ParaAngle by the change of PA.
        
        Parameters
        ----------
        min_change_in_PA : float or int (unit: degree)
            The unit of parallactic angle (eg, degree) can be ignore.
        
        Returns
        -------
        Filtered data table
        
        '''
        self.min_PA = min_change_in_PA
        self.max_PA = Max_change_in_PA

        ParaAngle = self.get_ParaAngle()

        obs_id = []
        member_id = []
        obs_date = []
        change = []
        init = []
        end = []
        
        for i in range(len(ParaAngle)):
            if Max_change_in_PA > ParaAngle['Change_PA'][i] / u.deg > min_change_in_PA:

                member_id.append(ParaAngle['member_ous_uid'][i])
                obs_date.append(ParaAngle['Obs_Date'][i])
                change.append(ParaAngle['Change_PA'][i])
                init.append(ParaAngle['Init_PA'][i])
                end.append(ParaAngle['End_PA'][i])
        
        Filtered_PA = QTable([member_id, obs_date, change, init, end],
                             names=['member_ous_uid', 'Obs_date', 'Change_PA', 'Init_PA','End_PA'])

        return Filtered_PA





    def download(self, *,filtered=True, save_directory=alma.cache_location):
        
        '''
        To save files in specific diretory
        
        
        Parameters
        ----------
        save_directory : string
            The directory the files save to. If None will save to alma query cache 
            directory, '~/.astropy/cache/astroquery/Alma/'.
        
        filtered : bool
            Whether to use the filtered PA tables. Defult value is True
        '''
        
        self.directory = save_directory

        if filtered is True:
            PA_table = self.filter_data(self.min_PA, self.max_PA)
        else:
             PA_table = self.get_ParaAngle()
        uids = np.unique(PA_table['member_ous_uid'])
        
        print('Files will save to', save_directory)
        
        for ids in uids:
            
            print('Currently download', ids)
            
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

    


    def untar(self):

        '''
        directly untar all the files downloaded
        '''

        tar_directory = self.directory
        file_list = os.listdir(tar_directory)
        tar_files = [file for file in file_list if file.endswith('.tar') or file.startswith('uid')]

        for tar_file in tar_files:
            tar_file_path = os.path.join(tar_directory, tar_file)
            print('Untaring :',tar_file_path)
            st = time.time()
            with tarfile.open(tar_file_path, 'r') as tar:
                tar.extractall(path=tar_directory)
            print('Done')
        subprocess.run('rm -rf *.pickle', cwd=tar_directory, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print('Untar finished')





    def run_script(self):
        '''
        This code will identify the CASA version and run casa pipeline automatically.
        '''

        version_xml = '.pipeline_manifest.xml'
        pipeline = '.scriptForPI.py'
        
        bash_cmd = 'ls -d */'

        untar_directory = self.directory
        folders = subprocess.run(bash_cmd, cwd=untar_directory, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        folders = folders.stdout.decode()
        folders = folders.split('\n')
        folders.pop()

        # Into proposal_id/
        for project_id in folders:
            path = f'{untar_directory}/{project_id}'
            science_goals = subprocess.run(bash_cmd, cwd=path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            science_goals = science_goals.stdout.decode()
            science_goals = science_goals.split('\n')
            science_goals.pop()
            
            # Into science_goal.ouss_id/
            for science_goal in science_goals:
                science_dire = f'{path}{science_goal}'
                groups = subprocess.run(bash_cmd, cwd=science_dire, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                groups = groups.stdout.decode()
                groups = groups.split('\n')
                groups.pop()

                # Into member.ouss_id/
                for group in groups:
                    group_dire = f'{science_dire}{group}'
                    members = subprocess.run(bash_cmd, cwd=group_dire, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    members = members.stdout.decode()
                    members = members.split('\n')
                    members.pop()
                    
                    for member in members:
                        member_dire = f'{group_dire}{member}'
                        data_set = subprocess.run(bash_cmd, cwd=member_dire, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        data_set = data_set.stdout.decode()
                        data_set = data_set.split('\n')
                        data_set.pop()
                            
                        script_dire = f'{member_dire}{data_set[-1]}'
                        script = subprocess.run('ls', cwd=script_dire, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        script = script.stdout.decode()
                        script = script.split('\n')
                        script.pop()
                        
                        xml_file = [file for file in script if version_xml in file]
                        script_file = [file for file in script if pipeline in file]

                        # Use XML get CASA version
                        xml_file_path = f'{script_dire}/{xml_file[0]}'
                        tree = ET.parse(xml_file_path)
                        root = tree.getroot()
                        casaversion_element = root.find('.//casaversion')
                        
                        if casaversion_element is not None:
                            casaversion = casaversion_element.get('name')
                            print('casa version: ', casaversion)
                            version = casaversion.split('.')
                            casa = casaversion.replace('.', '')
                            casa = casa.replace(casa[-1], '')
                            casaversion = casaversion.replace('.', '')[0:3]
                            casa_cmd = f'casa{casaversion} --pipeline -c {script_dire}/{script_file[0]}'
                            print(f'Run script in {script_dire}')

                            try:
                                os.system("export LD_PRELOAD='/usr/lib64/libfreetype.so'")
                                subprocess.call(['/bin/bash', '-i', '-c', casa_cmd], cwd=script_dire)

                            except:
                                os.system(f'rm -rf {member_dire}/calibrated/')
                                if casaversion[0] == '6':
                                    casa_cmd = 'casa641 --pipeline -c {script_dire}/{script_file[0]}'
                                    subprocess.call(['/bin/bash', '-i', '-c', casa_cmd], cwd=script_dire)
                                elif casaversion == '540':
                                    casa_cmd = 'casa561 --pipeline -c {script_dire}/{script_file[0]}'
                                    subprocess.call(['/bin/bash', '-i', '-c', casa_cmd], cwd=script_dire)
                                elif casaversion == '470':
                                    casa_cmd = 'casa472 --pipeline -c {script_dire}/{script_file[0]}'
                                    subprocess.call(['/bin/bash', '-i', '-c', casa_cmd], cwd=script_dire)
                                elif casaversion == '472':
                                    casa_cmd = 'casa470 --pipeline -c {script_dire}/{script_file[0]}'
                                    subprocess.call(['/bin/bash', '-i', '-c', casa_cmd], cwd=script_dire)
                                elif casaversion[:2] == 45:
                                    casa_cmd = 'casa453 --pipeline -c {script_dire}/{script_file[0]}'
                                    subprocess.call(['/bin/bash', '-i', '-c', casa_cmd], cwd=script_dire)
                        
                        else:
                            print('casa version element not found.')
    def Imaging(self):
        pass
