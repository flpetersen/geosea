#-------------------------------------------------------------------------------
#       Calculate Pressure Differences of Seafloor Geodetic Network
#-------------------------------------------------------------------------------

import pandas as pd

from .read_id import *
from .read_data import *
from .read_tides import *

GMT_DATEFORMAT = '%Y-%m-%dT%H:%M'
MATLAB_DATEFORMAT = '%Y-%m-%d %H:%M'


def vert_bsl(ID=None, tidesfile=None, pathname=None, starttime=None,dateformat=None, writevariable=False):
    """ Calculates vertical pressure differences by subtracting pressure from each other.

    It needs:

    ID     (optional) ... list of station IDs
    tides  (optional) ... filename of global or regional Tidemodel. Format:
        YYYY-MM-DDTHH:MM   XXXXX.X)

    starttime (optional) ... no measurement before this time is used ( format
        'YYYY-MM-DD hh:mm:ss')

    It returns:
    List of vertical motion differences in cm

    """
    # convert tide data from kPa to dbar and subtract the mean
    if tidesfile is not None:
        df_tides = read_tides(tidesfile)
        tides = df_tides
        tides_mean = tides - tides.mean()
        
    if pathname is None:
        pathname = ''
        
    if dateformat is None:
        dateformat = 'GMT_DATEFORMAT'
        
    if ID is None:
        ID = read_id(pathname=pathname)
        ifiles = glob.glob(pathname + 'Data_*_*_*.csv')


    # read pressure data from file and convert Kpa to dbar
    prs_corr = []
    prs_all = []
    for id in ID:

        if starttime is None:
            df_prs = ((read_data(id, 'prs',pathname=pathname)-100)/10)

        else:
            df_prs = ((read_data(id, 'prs',starttime=starttime,pathname=pathname)-100)/10)

        # subtract mean and append to a list of pandas.DataFrame
        df_prs = df_prs - df_prs.mean()

        if tidesfile is None:
            prs_corr.append(df_prs)

        else:
        # add Index of reference station to DataFrame and interpolate the pressure in between
            df_tide_newindex=tides_mean.reindex(df_prs.index).append(tides_mean).sort_index()
            
            tide_interpolate = df_tide_newindex.interpolate(method ='slinear')
            prs_corr.append(pd.DataFrame({"prs": df_prs.prs.subtract(tide_interpolate.tide).dropna()}))
        offset = []

    # Loop over all Statsions
    for i ,df_prs1 in enumerate(prs_corr):

        for j , df_prs2 in enumerate(prs_corr):
            if i != j:
                df_prs1.rename(columns={"prs": "prs1"})
                df_prs2.rename(columns={"prs": "prs2"})
                
                print('Vertical Presure Difference Calculation for: ' + str(ID[i]) + ' <-> ' + str(ID[j]))
          
                # add Index of reference station to DataFrame and interpolate the pressure in between
                df_prs1_newindex=df_prs1.reindex(df_prs2.index).append(df_prs1).sort_index()
                
                prs_interpolate = df_prs1_newindex.interpolate(method ='slinear')
                
                prs_diff = df_prs2.sub(prs_interpolate).rename(columns={"prs": "prs_diff"}).dropna()
                
                
                #prs_diff = pd.DataFrame({"prs_diff": df_prs2.prs2.subtract(prs_interpolate.prs1).dropna()})

                # calculation of rolling mean to smoth dataset ans remove high tide frequancies
                #prs_diff_mean = prs_diff.rolling(freq=rolling_freq,window=1).median().dropna()
                
                if dateformat == 'MATLAB_DATEFORMAT':
                    prs_diff.to_csv( pathname + str(ID[i]) + '-' + str(ID[j]) + '-PRS-DIFF.dat', header=True, date_format=MATLAB_DATEFORMAT)
                else:
                    prs_diff.to_csv( pathname + str(ID[i]) + '-' + str(ID[j]) + '-PRS-DIFF.dat', header=True, date_format=GMT_DATEFORMAT)
                
                prs_all.append(prs_diff)
                
    if writevariable:
        return(prs_all)
    else:
        return()
        
# end def vert_bsl (ID, tidesfile=None, starttime=None):

