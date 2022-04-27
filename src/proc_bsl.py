#-------------------------------------------------------------------------------
#       Complete processing
#-------------------------------------------------------------------------------

from .read import *
from .vert_bsl import *
from .bsl import *

from .sw import *

def proc_bsl (SAL,pathname=None,starttime=None, endtime=None,outlier_flag=None,writefile=True,dateformat=None):
    """ Complete Baseline processing of GeoSEA Raw data.

    It needs:
    SAL ...    constant salinity value in PSU
    pathname   Pathname of raw CSV Data files;
    starttime (optional) ... no measurement before this time is used (format
        'YYYY-MM-DD hh:mm:ss')
    endtime (optional) ... no measurement after this time is used (format
        'YYYY-MM-DD hh:mm:ss')

    It returns:
    bsl ... list of pandas.DataFrame with calculated Baselines

    """
    
    if dateformat is None:
          dateformat = 'GMT_DATEFORMAT'
    
    if pathname is None:
        pathname = ''
    
    ID,st_series,bsl_series = read(starttime=starttime, endtime=endtime,pathname=pathname,writefile=writefile)
    
    st_series_leroy = []
    st_series_wilson = []
    result = []
    for i, id in enumerate(ID):
        st_series_wilson.append(sv_wilson(st_series[i],SAL))
    
    bsl_horizonal = bsl(ID,bsl_series,st_series_wilson,outlier_flag,writefile,dateformat=dateformat)
    
    bsl_vertical = vert_bsl(ID)
    m=0
    
    #for i, id1 in range(len(bsl_horizonal)):
    for i, id1 in enumerate(ID):
        for j, id2 in enumerate(ID):
            if id1 != id2:

                bsl_all = bsl_horizonal[m].join([bsl_vertical[m]], how='outer').sort_index()
            
                bsl_all.to_csv( pathname + str(ID[i]) + '-' + str(ID[j]) + '.dat', header=False, date_format='%Y-%m-%dT%H:%M')
            
                result.append(bsl_all)
            
                m=m+1
        
    return(result)
