import os
import sys
import tarfile
import subprocess
import xml.etree.ElementTree as ET
import fileinput

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
        # ALMA_table    = self.get_tables(legacy_columns=True)
        ALMA_location = Observer.at_site("ALMA")
        
        Init_PA     = []
        End_PA      = []
        Delta_PA    = []
        Obs_date    = []
        End_date    = []
        
        proposal_id = ObsCore_table['proposal_id']
        Uids        = ObsCore_table['member_ous_uid']
        Group_id    = ObsCore_table['group_ous_uid']
        
        for i in range(len(Uids)):
            
            # Get source coordinate
            Ra = ObsCore_table['s_ra'][i]
            Dec = ObsCore_table['s_dec'][i]
            target_coord = SkyCoord(ra=Ra*u.deg, dec=Dec*u.deg)

            # Get the time information
            start_time = ObsCore_table['t_min'][i]
            start_time = Time(start_time,format='mjd').utc.iso
            start_time = datetime.fromisoformat(start_time)
            obs_date = start_time.date()
            obs_date = obs_date.strftime("%d-%m-%Y")
            Obs_date.append(obs_date)

            end_time = ObsCore_table['t_max'][i]
            end_time = Time(end_time, format='mjd').utc.iso
            end_time = datetime.fromisoformat(end_time)
            end_date = end_time.date()
            end_date = end_date.strftime("%d-%m-%Y")
            End_date.append(end_date)

            # Initial Parallactic Angle calculation and create list
            init_PA = Angle(ALMA_location.parallactic_angle(start_time, target_coord), u.deg)
            Init_PA.append(init_PA)
            
            # End Parallactic Angle
            end_PA = Angle(ALMA_location.parallactic_angle(end_time, target_coord), u.deg)
            End_PA.append(end_PA)
            
            delta_PA = end_PA - init_PA
            '''
            if abs(delta_PA / u.deg) > 180:
                delta_PA = (delta_PA / u.deg + 360) * u.deg
            '''
            Delta_PA.append(delta_PA)
        
        ParaAngle = QTable([proposal_id, Group_id, Uids, Obs_date, End_date, Delta_PA, Init_PA, End_PA], 
                           names=('proposal_id', 'group_ous_uid', 'member_ous_uid', 'Obs_date', 'End_date', 'Change_PA', 'Init_PA', 'End_PA'))

        return ParaAngle





    def filter_data(self, min_obs_date, Max_obs_date, min_change_in_PA, Max_change_in_PA):
        
        '''
        Filter the parallactic angle from self.get_ParaAngle by the change of PA.
        
        Parameters
        ----------
        min_obs_date : string
        Max_obs_date : string
            format : "%d-%m-%Y"
            Constrain the observation data after the date.

        min_change_in_PA : float or int (unit: degree)
        Max_change_in_PA : float or int (unit: degree)
            The unit of can be ignore.
        
        Returns
        -------
        Filtered data table
        
        '''
        self.min_PA   = min_change_in_PA
        self.max_PA   = Max_change_in_PA
        self.min_date = min_obs_date
        self.max_date = Max_obs_date
        ParaAngle = self.get_ParaAngle()

        Init_PA     = []
        End_PA      = []
        Delta_PA    = []
        Obs_date    = []
        End_date    = []
        proposal_id = []
        Uids        = []
        Group_id    = []

        min_obs_date = datetime.strptime(min_obs_date, "%d-%m-%Y").date()
        Max_obs_date = datetime.strptime(Max_obs_date, "%d-%m-%Y").date()
        
        for i in range(len(ParaAngle)):
            data_date = ParaAngle['Obs_date'][i]
            data_date = datetime.strptime(data_date, "%d-%m-%Y").date()

            if (min_change_in_PA < ParaAngle['Change_PA'][i] / u.deg < Max_change_in_PA) and (min_obs_date < data_date < Max_obs_date):
                proposal_id.append(ParaAngle['proposal_id'][i])
                Uids.append(ParaAngle['member_ous_uid'][i])
                Group_id.append(ParaAngle['group_ous_uid'][i])
                Obs_date.append(ParaAngle['Obs_date'][i])
                End_date.append(ParaAngle['End_date'][i])
                Delta_PA.append(ParaAngle['Change_PA'][i])
                Init_PA.append(ParaAngle['Init_PA'][i])
                End_PA.append(ParaAngle['End_PA'][i])
        
        Filtered_PA = QTable([proposal_id, Group_id, Uids, Obs_date, End_date, Delta_PA, Init_PA, End_PA],
                             names=['proposal_id', 'group_ous_uid', 'member_ous_uid', 'Obs_date', 'End_date', 'Change_PA', 'Init_PA','End_PA'])

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
            PA_table = self.filter_data(self.min_date, self.max_date, self.min_PA, self.max_PA)
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
        variable_name_to_modify = "DOSPLIT"
        new_value = True
        
        untar_directory = self.directory

        f_PA = self.filter_data(self.min_PA, self.max_PA)

        proposal_id = np.unique(f_PA['proposal_id'])
        group_id    = np.unique(f_PA['group_ous_uid'])
        member_ous_id = np.unique(f_PA['member_ous_uid'])
        print(f'Files at the {untar_directory} directory')
        
        for Proposal_ID in proposal_id:
            science_goal_path = f'{untar_directory}/{Proposal_ID}'
            output = subprocess.run("ls", cwd=science_goal_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = output.stdout.decode()
            output = output.split('\n')
            output.pop()

            for science_goal_id in output:
                science_goal_path = f"{science_goal_path}/{science_goal_id}"

                for Group_ID in group_id:
                    for Member_ID in member_ous_id:
                        Group_ID  = Group_ID.replace('/', '_').replace(':', '_')
                        Member_ID = Member_ID.replace('/', '_').replace(':', '_')
                        member_path = f'{science_goal_path}/group.{Group_ID}/member.{Member_ID}'
                        self.data_path = member_path

                        for science_id in output:
                            script_path = f'{member_path}/script'
                            script_files = subprocess.run("ls", cwd=script_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            script_files = script_files.stdout.decode()
                            script_files = script_files.split('\n')
                            script_files.pop()
    
                            xml_file = [file for file in script_files if version_xml in file]
                            script_py = [file for file in script_files if pipeline in file]
                            tree = ET.parse(f'{script_path}/{xml_file[0]}')
                            root = tree.getroot()
                            casaversion_element = root.find('.//casaversion')
                            if casaversion_element is not None:
                                casaversion = casaversion_element.get('name')
                                print(f'CASA version: {casaversion}')
                            else:
                                print('No found compatible version')
                            version = casaversion.replace('.', '')[:3]
                            pipeline_cmd = f"casa{version} --pipeline -c {script_path}/{script_py[0]}"
                            print(f'Run script in {script_path}')

                            try:
                                with open(f"{script_path}/{script_py[0]}", "r") as file:
                                    lines = file.readlines()

                                for i, line in enumerate(lines):
                                    if variable_name_to_modify in line:
                                        if "DOSPLIT = False" == line:
                                            lines[i] = f"{variable_name_to_modify} = {new_value}\n"
                                            break
                                        else:
                                            lines.insert(0, f"{variable_name_to_modify} = {new_value}\n")
                                            break

                                with open(f"{script_path}/{script_py[0]}", "w") as file:
                                    file.writelines(lines)
                            except ImportError:
                                print("Error: The script file could not be imported.")

                            try:
                                subprocess.call(['/bin/bash', '-i', '-c', pipeline_cmd], cwd=script_path)
                            except subprocess.CalledProcessError as e:
                                print(f"Error running command: {e}")


    def fitting(self):
        # Go into the calibrated direcrory
        calibrated_dire = f'{self.data_path}/calibrated/'
        print(f"Looking for the calibrated files in the {calibrated_dire}")
        ms_files = subprocess.run('ls *.ms.split.cal -d', cwd=calibrated_dire, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ms_files = ms_files.stdout.decode()
        ms_files = ms_files.split('\n')
        ms_files.pop()
        for file in ms_files:
            print(files)
            '''
            obs = listobs(vis=files, 
                          field=self.source,
                          intent='CALIBRATE_BANDPASS#ON_SOURCE',
                          verbose=False)
            print(f"There are {obs['nfields']} of {self.source}")
            '''
        # listobs(vis='',) 
