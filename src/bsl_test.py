


#-------------------------------------------------------------------------------
#       Calculate Baselines data
#-------------------------------------------------------------------------------

import pandas as pd


from .read.read import *

from .read.utils.sql import *



class Beacon:

    def __init__(self, id):
        self.id = id




def bsl_test(name, pathname):
    """Calculates baselines for all possible pairs.

    """


    df = sql2df(name, pathname)

    # get
    dfn = df.reset_index()

    id = dfn['node_id'].unique().tolist()


    station1=Beacon(id[0])

    print(station1.id)


    #-------------------------------------------------------------------------------
    #       Start Baseline Calculation
    #-------------------------------------------------------------------------------



