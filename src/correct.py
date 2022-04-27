#-------------------------------------------------------------------------------
#       Correction for Baseline calculation
#-------------------------------------------------------------------------------
import pandas as pd
import numpy as np

from .read_data import *
from .sw import *


### Global Variables ###
GMT_DATEFORMAT = '%Y-%m-%dT%H:%M'
MATLAB_DATEFORMAT = '%Y-%m-%d %H:%M'

def correct_inc (ID,pathname=None,writefile=True,dateformat=None,starttime=None, endtime=None):

    if pathname is None:
        pathname = ''
        
    if dateformat is None:
        dateformat = GMT_DATEFORMAT
        
    df_inc = read_data(ID,'inc',pathname=pathname)
    
    df_tilt = np.sqrt((df_inc.roll**2)+(df_inc.pitch**2)).name
    df_tilt.
    
    polynomial  = np.polyfit(df_tilt.values,list(range(1,df_tilt.size+1)),3)
    
    poly_curve = np.polyval(polynomial,list(range(1,df_tilt.size+1)))
    
    df_poly_curve = pd.DataFrame(poly_curve,index=df_tilt.index,columns=['polycurve'])
    
    df = pd.concat([df_poly_curve, df_tilt ], axis=1)
