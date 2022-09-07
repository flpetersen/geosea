"""GeoSEA read CSV module."""
import glob # Unix style pathname pattern expansion

import numpy as np # fundamental package for scientific computing

import pandas as pd # Pandas toolbox
from obspy.geodetics.base import gps2dist_azimuth

### Import GeoSEA Modules ###

from .read_data import read_data
from .read_id import read_id

from .utils.extract_df import extract_df
from .utils.sw import sv_wilson
from .utils.sw import sv_leroy

# Global date format for export
GMT_DATEFORMAT = '%Y-%m-%dT%H:%M'
MATLAB_DATEFORMAT = '%Y-%m-%d %H:%M'


class Network(object):
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name



def read(sal=None,phi=None,starttime=None, endtime=None, pathname=None, writefile=True, writevariable=True, dateformat=None):
    """ Reads data from *csv files.

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
    ID ... an 1-dim list with station IDs
    st_series ... an 1-dim list with pandas.DataFrame with columns:
        temperature ('hrt'), pressure ('prs'), sound speed ('ssp'), temperature
        from pressure ('tpr'), inclinometer data ('pitch','roll'), battery ('bat','vlt')
        and pages ('pag') with corresponding times of measurement for each beacon
        (same order as items in ID)
    bsl_series ... an 1-dim list with pandas.DataFrame with baseline
        measurements: ID of other station ('range_ID'), traveltime ('range')
        and turn around time ('TAT') with corresponding times of measurement
        for each beacon (same order as items in ID)

    It further writes human readable files for pressure, inclinometer
    data, battery, and pages, respectively.
    """

    ID = []

    if pathname is None:
        pathname = ''

    if sal is None:
        sal = 32

    if dateformat is None:
        dateformat = GMT_DATEFORMAT

    if dateformat == 'MATLAB_DATEFORMAT':
        dateformat = MATLAB_DATEFORMAT


    ID = read_id(pathname=pathname)
    ifiles = glob.glob(pathname + 'Data_*_*_*.csv')

#-------------------------------------------------------------------------------
#       Open and merge all Raw Files
#-------------------------------------------------------------------------------
    st_series = []
    bsl_series = []

    # pre-define column names (needed because of different number of columns
    # per row in input files)
    my_cols = ["A","B","C","D","E","F","G","H","I","J","K"]

    for j,station in enumerate(ID):

        print('\nData Processing for Station: ' + station)
        print('---------------------------------------------------------------------')
        print('Open Files:')

        # create empty pandas.DataFrame for storing of data from file
        all_data = pd.DataFrame()
        for i,data in enumerate(ifiles):
            stationname = data.split('_', 3)
            if station in stationname:
                print(data)
                # reads data from csv-file using pandas
                # my_cols ... pre-defined column names
                # skiprow=13 ... skips first 13 rows
                # index_col=0 ... uses first column as index
                # final dataframe has columns 'B'-'J' (0-9) and index column
                # with ['PAG','BSL',...]
                curfile = pd.read_csv(data,names=my_cols,skiprows=13,index_col=0,low_memory=False)
                # append curfile to DataFrame, needs to be stored to all_data
                # otherwise no permanent change
                #all_data = all_data.append(curfile)
                all_data = pd.concat([all_data, curfile])
        #print curfile
            # end if station in stationname:
        print('   ')
        # end for i,data in enumerate(ifiles):

        # remove duplicates, again has to be stored to all_data otherwise no
        # permanent change
        all_data = all_data.drop_duplicates()

        # transform date column 'B' to time format used by pandas
        all_data['B'] = pd.to_datetime(all_data['B'])

        if starttime is not None:
            # remove all entries before starttime
            all_data = all_data.loc[all_data['B'] >= starttime]
        # end if starttime is not None:

        if endtime is not None:
            # remove all entries after endtime
            all_data = all_data.loc[all_data['B'] <= endtime]
        # end if endtime is not None:

        ######## Sort Files to Sensor

        # position of date in following column_lists
        date_pos = 0

        sv_fr = 0
#-------------------------------------------------------------------------------
#       Travel Time measurement
#-------------------------------------------------------------------------------
        index = 'BSL'
        column_list = ['B','F','G','H']
        # columns contain date, ID of other station, traveltime measurement in
        # milliseconds and turn around time in milliseconds
        label_list = ['date','range_ID','range','TAT']
        # data types for columns except date
        dtype = ['d','f','f']
        df_bsl = extract_df(all_data,index,column_list,label_list,dtype,date_pos)

        if writefile:
            # writes data to file
            df_bsl.to_csv( pathname + str(station) +'-'+ index+'.dat',sep='\t', header=True, date_format=dateformat)
                
#-------------------------------------------------------------------------------
#       Sound speed and temperature for Fetch Stations
#-------------------------------------------------------------------------------
        if 'SVT' in all_data.index:
            index = 'SVT'
            print('SVT - Sound Speed and Temperature Sensor !')
            column_list = ['B','F']
            # columns contain date and sound speed measurement in metres per second
            label_list = ['date','hrt']
            # data types for columns except date
            dtype = ['f','f']
            df_svt = extract_df(all_data,index,column_list,label_list,dtype,date_pos)
        
            # removes sound speed measurements which are not in water
            #df_svt = df_svt.loc[df_svt['SSP']!=9996.]
            index = 'HRT'
            if writefile:
                # writes data to file
                write2csv(df_svt, station, index, dateformat, pathname)
            # end if writefile:
        
#-------------------------------------------------------------------------------
#       Sound Speed
#-------------------------------------------------------------------------------
        if 'SSP' in all_data.index:
            index = 'SSP'
            column_list = ['B','E']
            # columns contain date and sound speed measurement in metres per second
            label_list = ['date','ssp']
            # data types for columns except date
            dtype = ['f']
            df_ssp = extract_df(all_data,index,column_list,label_list,dtype,date_pos)

            # removes sound speed measurements which are not in water
            df_ssp = df_ssp.loc[df_ssp['ssp']!=9996.]

            if writefile:
                write2csv(df_ssp, station, index, dateformat, pathname)

            
#-------------------------------------------------------------------------------
#       Temperature
#-------------------------------------------------------------------------------
        if 'TMP' in all_data.index:
            index = 'TMP'
            # columns contain date and temperature in degree Celsius
            label_list = ['date','tmp']
            df_tp = extract_df(all_data,index,column_list,label_list,dtype,date_pos)
        
        if 'HRT' in all_data.index:
            index = 'HRT'
            column_list = ['B','E']
            # same label_list as 'TMP'
            label_list = ['date','hrt']
            df_hrt = extract_df(all_data,index,column_list,label_list,dtype,date_pos)

            if writefile:
                write2csv(df_hrt, station, index, dateformat, pathname)

#-------------------------------------------------------------------------------
#       Pressure and Temperature data
#-------------------------------------------------------------------------------
        index = 'PRS'
        index1 = 'TPR'
        column_list = ['B','E']
        column_list2 = ['B','F']
        # columns contain date and pressure in kPa
        label_list = ['date','prs']
        label_list2 = ['date','tpr']
        df_tpr = extract_df(all_data,index,column_list2,label_list2,dtype,date_pos)
        df_prs = extract_df(all_data,index,column_list,label_list,dtype,date_pos)
        dtype = ['f']

        if writefile:
            write2csv(df_prs, station, index, dateformat, pathname)
            write2csv(df_tpr, station, index1, dateformat, pathname)

#-------------------------------------------------------------------------------
#       Recorded pages in Bytes
#-------------------------------------------------------------------------------
        index = 'PAG'
        column_list = ['B','E']
        # columns contain date and page number
        label_list = ['date','pag']
        #  data types for columns except date
        dtype = ['d']
        df_pag = extract_df(all_data,index,column_list,label_list,dtype,date_pos)

        if writefile:
            # writes data to file
            write2csv(df_pag, station, index, dateformat, pathname)

        # tranform page numbers to Bytes
        df_pag['size'] = df_pag['pag']*512/1000

        # total size of downloaded data in kB last entry in column 'pag'
        pag_size = df_pag['size'].iloc[-1]/1024

#-------------------------------------------------------------------------------
#       Battery Power
#-------------------------------------------------------------------------------
        index = 'BAT'
        column_list = ['B','E','F']
        # columns contain date, battery consumption in per cent and voltage in
        # volt
        label_list = ['date','bat','vlt']
        #  data types for columns except date
        dtype = ['d','f']
        df_bat = extract_df(all_data,index,column_list,label_list,dtype,date_pos)

        if writefile:
            write2csv(df_bat, station,index,dateformat,pathname)

#-------------------------------------------------------------------------------
#       Inclinometer
#-------------------------------------------------------------------------------
        index = 'INC'
        # columns contain date, pitch and roll in radians
        label_list = ['date','pitch','roll']
        #  data types for columns except date
        dtype = ['f','f']
        df_inc = extract_df(all_data,index,column_list,label_list,dtype,date_pos)

        # transform radians to degrees
        df_inc['pitch'] = df_inc['pitch']*180/np.pi
        df_inc['roll'] = df_inc['roll']*180/np.pi

        if writefile:
            # writes data to file
            df_inc.to_csv( pathname + str(station) +'-'+ index+'.dat',sep='\t', header=True, date_format=dateformat)
            df_inc = read_data(str(station),'INC', pathname=pathname)
            df_inc = df_inc.reset_index().drop_duplicates(subset='date').set_index('date')
            df_inc.to_csv( pathname + str(station) +'-'+ index+'.dat',sep='\t', header=True, date_format=dateformat)
        # end writefile:

        # Standard output
        print('Found: ' + str(len(df_bsl)) + '\t Baseline Records')
        print('Found: ' + str(len(df_prs)) + '\t Pressure Records')
        if sv_fr == 1:
            print('Found: ' + str(len(df_svt)) + '\t Sound Speed Records')
            print('Found: ' + str(len(df_svt)) + '\t Temperature Records')
        else:
            print('Found: ' + str(len(df_ssp)) + '\t Sound Speed Records')
            print('Found: ' + str(len(df_hrt)) + '\t HiRes Temperature Records')
        print('Found: ' + str(len(df_inc)) + '\t Inclination Records')
        print('Found: ' + str(len(df_bat)) + '\t Battery Records')
        print('Found: ' + str(pag_size) + '\t MB Data')
#-------------------------------------------------------------------------------
#       Theoretical Sound Velocity
#-------------------------------------------------------------------------------
        
    # concatenate pandas data formats in one data format for temperature,
        # pressure, sound speed, inclinometer, battery, and pages
        if sv_fr == 1:
            df = pd.concat([df_svt, df_prs, df_inc, df_bat, df_pag], axis=1)
        else:
            df = pd.concat([df_ssp, df_prs, df_hrt, df_tpr, df_inc, df_bat, df_pag], axis=1)
    # append this to data formats of other stations
        
        df_wilson = sv_wilson(df,int(sal))
                
        if writefile:
            # writes data to file
            df_wilson['sv_hrt'].to_csv( pathname + str(station) +'-'+ 'SV_HRT' + '.dat',sep='\t', header=True, date_format=dateformat)
            df_sv_hrt = read_data(str(station),'SV_HRT', pathname=pathname)
            df_sv_hrt = df_sv_hrt.reset_index().drop_duplicates(subset='date').set_index('date')
            df_sv_hrt.to_csv( pathname + str(station) +'-'+ 'SV_HRT'+'.dat',sep='\t', header=True, date_format=dateformat)
            
            df_wilson['sv_tpr'].to_csv( pathname + str(station) +'-'+ 'SV_TPR' + '.dat',sep='\t', header=True, date_format=dateformat)
            df_sv_tpr = read_data(str(station),'SV_TPR', pathname=pathname)
            df_sv_tpr = df_sv_tpr.reset_index().drop_duplicates(subset='date').set_index('date')
            df_sv_tpr.to_csv( pathname + str(station) +'-'+ 'SV_TPR'+'.dat',sep='\t', header=True, date_format=dateformat)
            
            df_wilson['sal'].to_csv( pathname + str(station) +'-'+ 'SAL' + '.dat',sep='\t', header=True, date_format=dateformat)
            df_sal = read_data(str(station),'sal', pathname=pathname)
            df_sal = df_sal.reset_index().drop_duplicates(subset='date').set_index('date')
            df_sal.to_csv( pathname + str(station) +'-'+ 'sal'+'.dat',sep='\t', header=True, date_format=dateformat)
            
        if phi is not None:
            df = sv_leroy(df,sal,phi)
            
            if writefile:
                index = 'SVL_HRT'
                write2csv(df['sv_hrt'], station, index, dateformat, pathname)
            
                index = 'SV_TPR'
                write2csv(df['sv_tpr'], station, index, dateformat, pathname)

        
        if sv_fr == 1:
            df = pd.concat([df_svt, df_prs, df_inc, df_bat, df_pag], axis=1)
        else:
            df = pd.concat([df_ssp, df_prs, df_hrt, df_tpr, df_inc, df_bat, df_pag, df_sv_hrt, df_sv_tpr, df_sal], axis=1)
        
        
        st_series.append(df)

        # baseline data not included in pandas.concat as it holds multiple
        # entries per day for different baselines
        bsl_series.append(df_bsl)
    # end for j,station in enumerate(ID):

    if not writefile:
        print('\n')
        print('Data has not been stored in files!')
    # end if not writefile:

    if writevariable:
        return(ID,st_series,bsl_series)
    else:
        print('Data has not been stored in files!')
        return()
        
# end def read(starttime, pathname=None):


def write2csv (df, station, index, dateformat, pathname):
                
        df.to_csv( pathname + str(station) +'-'+ index+'.dat',sep='\t', header=True, date_format=dateformat)
        df = read_data(str(station), index, pathname=pathname)
        df = df.reset_index().drop_duplicates(subset='date').set_index('date')
        df.to_csv( pathname + str(station) +'-'+ index+'.dat',sep='\t', header=True, date_format=dateformat)
