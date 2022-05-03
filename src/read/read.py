"""
GeoSEA read CSV module.

To Do:


30 Aptil 2022 - implement SQL database to store the station and baseline data properly. 
28 April 2022 - ps.DataFrames manipulation has been enhanced. New pd.DataFrame structure!!
- automatically read SQL Databases


"""

import glob # Unix style pathname pattern expansion

import numpy as np # fundamental package for scientific computing
import pandas as pd # Pandas toolbox
from pathlib import Path


### Import GeoSEA Modules ###

from .read_data import read_data
from .read_id import read_id

from .utils.extract_df import extract_df
from .utils.sw import sv_wilson
from .utils.sw import sv_leroy

from .utils.sql import df2sql
from .utils.sql import sql2df

# Global date format for export
GMT_DATEFORMAT = '%Y-%m-%dT%H:%M'
MATLAB_DATEFORMAT = '%Y-%m-%d %H:%M'


class Network(object):

    name = str()
    num_stations = 0

    def __init__(self, x, y):
        self.name = x
        self.num_stations = y

    def get_name(self):
        return self.name



def read(network_name, sal=None,phi=None,starttime=None, endtime=None, pathname=None):
    """ Reads data from *csv files and stores seafloor geodetic network data in a SQL Database (*.sqlite) 

    Note that the *csv files have to be unique for each station!
    It needs:

    SAL (optional) ... constant salinity value in PSU to calculate the theoretical
        sound velocity
    phi (optional) ... if phi is not None the Leroy formular is used
    starttime (optional) ... no measurement before this time is used (format
        'YYYY-MM-DD hh:mm:ss')
    endtime (optional) ... no measurement after this time is used (format
        'YYYY-MM-DD hh:mm:ss')
    pathname (optional) ... location of input files (default .)
    writefile (optional) ... if True files containing all read-in parameters
        will be created in current directory, if False data will just be
        returned (default True)
    dateformat = (optional) ... MATLAB_DATEFORMAT = '%Y-%m-%d %H:%M'
                                 GMT_DATEFORMAT = '%Y-%m-%dT%H:%M' (Default)

    It returns:
    pd.DataFarme
    
    """

    ID = []

    if pathname is None:
        pathname = ''

    if sal is None:
        sal = 32

    ID = read_id(pathname=pathname)
    ifiles = glob.glob(pathname + 'Data_*_*_*.csv')

#-------------------------------------------------------------------------------
#       Open and merge all Raw Files
#-------------------------------------------------------------------------------
    st_series = []
    bsl_series = []
    
    # pre-define column names (needed because of different number of columns
    # per row in input files)



    if Path(pathname + network_name + '.sqlite').is_file():

        df = pd.DataFrame()

        df = sql2df(network_name, pathname)

        return(df)
        
    else:
        df = pd.DataFrame()
        for station in ID:
            
            print('\nData Processing for Station: ' + station)
            print('---------------------------------------------------------------------')
            print('Open Files:')

            # Initial Pandas DataFrame
            
            # create empty pandas.DataFrame for storing of data from file
            all_data = pd.DataFrame()
            
            for data in ifiles:
                stationname = data.split('_', 3)
                if station in stationname:
                    print(data)

                    # reads data from csv-file using pandas
                    curfile = pd.read_csv(data,names=list('abcdefghijk'),skiprows=13,low_memory=False)
                    curfile['d']=station

                    # concatenate all csv files into one DataFrame
                    df = pd.concat([df, curfile.drop('c',axis=1).rename(columns={'a':'sensor','d':'node_id','b':'rec_time','e':'value_1','f':'value_2','g':'tt','h':'tat'})])

                    
                    
                    df  = df[df['sensor'].ne('SNS') & df['sensor'].ne('BAS')& df['sensor'].ne('SLG')& df['sensor'].ne('TIM')].drop(['i','j','k'],axis=1)

            # Standard output
            print('Found: ' + str(len(df[df['sensor'].eq('BSL') & df['node_id'].eq(station)])) + '\t Baseline Records')
            print('Found: ' + str(len(df[df['sensor'].eq('PRS') & df['node_id'].eq(station)])) + '\t Pressure Records')
            print('Found: ' + str(len(df[df['sensor'].eq('SSP') & df['node_id'].eq(station)])) + '\t Sound Speed Records')
            print('Found: ' + str(len(df[df['sensor'].eq('HRT') & df['node_id'].eq(station)])) + '\t HiRes Temperature Records')
            print('Found: ' + str(len(df[df['sensor'].eq('INC') & df['node_id'].eq(station)])) + '\t Inclination Records')
            print('Found: ' + str(len(df[df['sensor'].eq('BAT') & df['node_id'].eq(station)])) + '\t Battery Records')
            print('Found: ' + str(len(df[df['sensor'].eq('PAG') & df['node_id'].eq(station)])) + '\t MB Data')
        # convert record time to datetime format
        df['rec_time'] = pd.to_datetime(df['rec_time'])
        # set multiindex to station ID and record time
        df.set_index(['node_id', 'rec_time'], inplace=True)

        # store DF in SQL database

        df2sql(df, network_name, pathname)
    
        return(df)

    # import DataFrame into a SQL Database




