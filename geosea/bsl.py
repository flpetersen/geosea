#-------------------------------------------------------------------------------
#       Calculate Baselines data
#-------------------------------------------------------------------------------

import pandas as pd

from .search_df import *
from .read.utils.extract_df import extract_df
from .calc import *
from .read.read_id import *
from .read.read_data import *
from .read.utils.sw import *

GMT_DATEFORMAT = '%Y-%m-%dT%H:%M'
MATLAB_DATEFORMAT = '%Y-%m-%d %H:%M'


def bsl(ID=None, st_series=None, bsl_series=None, outlier_flag=False, pathname=None, starttime=None, endtime=None, writefile=True, dateformat=None):
    """Calculates baselines for all possible pairs.

    It needs:
    ID ... 1-dim array with all available beacon IDs
    bsl_series ... an 1-dim list with pandas.DataFrame with baseline
        measurements: ID of other station ('range_ID'), traveltime ('range')
        and turn around time ('TAT') with corresponding times of measurement
        for each beacon (same order as items in ID)
    ssp_all ... an 1-dim list with pandas.DataFrame with sound speed ('ssp')
        with corresponding times of measurement for each beacon (same order
        as items in ID)
    minmax ... half time window length for searching for sound speed at
        beacon 2
    outlier_flag (optional) ... if set to True all baselines with lengths
        +/-10m are removed
    pathname (optional) ... location of files created with read() (default
        is None)
    starttime (optional) ... no measurement before this time is used (format
        'YYYY-MM-DD hh:mm:ss')
    endtime (optional) ... no measurement after this time is used (format
        'YYYY-MM-DD hh:mm:ss')
    writefile (optional) ... if True files containing all baseline parameters
        will be created in current directory, if False data will just be
        returned (default True)
    dateformat = (optional) ... MATLAB_DATEFORMAT = '%Y-%m-%d %H:%M'
                                 GMT_DATEFORMAT = '%Y-%m-%dT%H:%M' (Default)
                                 

    It returns:
    ID_pair ... a 2-dim list with IDs of beacon pairs
        ([[ID1,ID2],[ID1,ID3],...])
    final_bsls ... an 1-dim list with pandas.DataFrame with ID of beacon 1
        ('ID'), ID of beacon 2 ('range_ID'), calculated baseline lengths in
        metres ('bsl'), one way traveltime in seconds ('tt'), sound speed at
        beacon 1 ('ssp1') in metres per second, sound speed at beacon 2
        ('ssp2') in metres per second, measured traveltime in milliseconds
        ('range'), turn around time in milliseconds ('TAT') with
        corresponding times of measurement for each beacon pair (same order
        as list items in ID_pair)
    """

    cal_bsl_series = []

    ID_pair = []
    st_svleroy = []
    list_df_bsl = []
    
    if dateformat is None:
        dateformat = 'GMT_DATEFORMAT'
        
#-------------------------------------------------------------------------------
#       Identify Beacon IDs
#-------------------------------------------------------------------------------

    if pathname is None:
        pathname = ''
        
    if ID is None:
        ID = read_id(pathname=pathname)
        ifiles = glob.glob(pathname + 'Data_*_*_*.csv')

#-------------------------------------------------------------------------------
#       Load BSL Data
#-------------------------------------------------------------------------------

    if bsl_series is None:
        if starttime is not None:
            bsl_series = []
            for beacon in ID:
                bsl_series.append(read_data(beacon,'BSL',pathname=pathname,starttime=starttime,endtime=endtime))
        else:
            bsl_series = []
            for beacon in ID:
                bsl_series.append(read_data(beacon,'BSL',pathname=pathname))
            
#-------------------------------------------------------------------------------
#       Load Station Data
#-------------------------------------------------------------------------------

    if st_series is None:
        if starttime is not None:
            print('Read Data from: ' + starttime)
            print('---------------------------------------------------------------------')
            st_series = []
            for beacon in ID:
                df_ssp = read_data(beacon,'ssp',pathname=pathname,starttime=starttime,endtime=endtime)
                df_prs = read_data(beacon,'prs',pathname=pathname,starttime=starttime,endtime=endtime)
                df_hrt = read_data(beacon,'hrt',pathname=pathname,starttime=starttime,endtime=endtime)
                df_tpr = read_data(beacon,'tpr',pathname=pathname,starttime=starttime,endtime=endtime)
                df_inc = read_data(beacon,'inc',pathname=pathname,starttime=starttime,endtime=endtime)
                df_bat = read_data(beacon,'bat',pathname=pathname,starttime=starttime,endtime=endtime)
                df_pag = read_data(beacon,'pag',pathname=pathname,starttime=starttime,endtime=endtime)
                df_sv_hrt = read_data(beacon,'SV_HRT',pathname=pathname,starttime=starttime,endtime=endtime)
                df_sv_tpr = read_data(beacon,'SV_TPR',pathname=pathname,starttime=starttime,endtime=endtime)
                df_sal = read_data(beacon,'SAL',pathname=pathname,starttime=starttime,endtime=endtime)
                st_series.append(pd.concat([df_ssp, df_prs, df_hrt, df_tpr, df_inc, df_bat, df_pag, df_sv_hrt, df_sv_tpr,df_sal],axis = 1))
                
        else:
            print('Read Data')
            print('---------------------------------------------------------------------')
            st_series = []
            for beacon in ID:
                df_ssp = read_data(beacon,'ssp',pathname=pathname)
                df_prs = read_data(beacon,'prs',pathname=pathname)
                df_hrt = read_data(beacon,'hrt',pathname=pathname)
                df_tpr = read_data(beacon,'tpr',pathname=pathname)
                df_inc = read_data(beacon,'inc',pathname=pathname)
                df_bat = read_data(beacon,'bat',pathname=pathname)
                df_pag = read_data(beacon,'pag',pathname=pathname)
                df_sv_hrt = read_data(beacon,'SV_HRT',pathname=pathname)
                df_sv_tpr = read_data(beacon,'SV_TPR',pathname=pathname)
                df_sal = read_data(beacon,'SAL',pathname=pathname)
                st_series.append(pd.concat([df_ssp, df_prs, df_hrt, df_tpr, df_inc, df_bat, df_pag, df_sv_hrt, df_sv_tpr,df_sal],axis = 1))
                         
#-------------------------------------------------------------------------------
#       Start Baseline Calculation
#-------------------------------------------------------------------------------
    for i, beacon_1 in enumerate(ID):
        for j, beacon_2 in enumerate(ID):
            if beacon_1 != beacon_2:
                
                print('')
                print('Baseline Calculation for: ' + str(beacon_1) + ' <-> ' + str(beacon_2))
                print('---------------------------------------------------------------------')
                ID_pair.append([beacon_1,beacon_2])
                # create new pandas.DataFrame holding baseline measurements
                # between beacon_1 and beacon_2 which are not 0.0 milli seconds
                
                df_bsl = bsl_series[i].loc[(bsl_series[i]['range_ID']==int(beacon_2)) & (bsl_series[i]['range']!=0.0)]
                
                if not df_bsl.empty and not st_series[i].empty and not st_series[j].empty:
                    # set new column 'ID' of beacon 1
                    #df_bsl['ID']=int(beacon_1)
                    # alternative version:
                    
                    df_bsl,SV_1_err_count = search_df(df_bsl,st_series[i],'ssp',0.0,'ssp1',0)
                    df_bsl,SV_1_err_count = search_df(df_bsl,st_series[i],'sv_hrt',0.0,'sv_hrt1',10)
                    df_bsl,SV_1_err_count = search_df(df_bsl,st_series[i],'sv_tpr',0.0,'sv_tpr1',11)
                    
                    df_bsl,SV_1_err_count = search_df(df_bsl,st_series[i],'prs',0.0,'prs1',1)
                    
                    df_bsl,SV_1_err_count = search_df(df_bsl,st_series[i],'hrt',0.0,'hrt1',2)
                    df_bsl,SV_1_err_count = search_df(df_bsl,st_series[i],'tpr',0.0,'tpr1',3)
                    df_bsl,SV_1_err_count = search_df(df_bsl,st_series[i],'sal',0.0,'sal1',12)
                 
                    df_bsl,SV_2_err_count = search_df(df_bsl,st_series[j],'ssp',0.0,'ssp2',0)
                    df_bsl,SV_2_err_count = search_df(df_bsl,st_series[j],'sv_hrt',0.0,'sv_hrt2',10)
                    df_bsl,SV_2_err_count = search_df(df_bsl,st_series[j],'sv_tpr',0.0,'sv_tpr2',11)
                    
                    df_bsl,SV_2_err_count = search_df(df_bsl,st_series[j],'prs',0.0,'prs2',1)
                    
                    df_bsl,SV_2_err_count = search_df(df_bsl,st_series[j],'hrt',0.0,'hrt2',2)
                    df_bsl,SV_2_err_count = search_df(df_bsl,st_series[j],'tpr',0.0,'tpr2',3)
                    df_bsl,SV_2_err_count = search_df(df_bsl,st_series[j],'sal',0.0,'sal2',12)

                    df_bsl.loc[:,'ID'] = int(beacon_1)
                    
                    #st_series_2 = st_series[j].rename(columns={"ssp":"ssp2","prs":"prs2","hrt":"hrt2","tpr":"tpr2","pitch":"pitch2","roll":"roll2","bat":"bat2","vlt":"vlt2","pag":"pag2","size":"size2","svl_hrt":"svl_hrt2","svl_tpr":"svl_tpr2","sal":"sal2"})
                    
                    #st_series_1 = st_series[i].rename(columns={"ssp":"ssp1","prs":"prs1","hrt":"hrt1","tpr":"tpr1","pitch":"pitch1","roll":"roll1","bat":"bat1","vlt":"vlt1","pag":"pag1","size":"size1","svl_hrt":"svl_hrt1","svl_tpr":"svl_tpr1","sal":"sal1"})
                    
  
                    #st_series_2.to_csv('st_series2')
                    #st_series_1.to_csv('st_series1')
                   
                    #df_bsl_st = df_bsl.join([st_series_1, st_series_2], how='outer').sort_index()

                    # define criteria that ssp1 and ssp2 have to be not NaN
                    # for row selection allow also single sided baseline
                    # calculation
    #---------------------------------------------------------------------------------------
    #            SSP
                    criteria_ssp = (df_bsl.loc[:,'ssp1']!=0.0) & (df_bsl.loc[:,'ssp2']!=0.0)
                    ssp2_check = (df_bsl.loc[:,'ssp2'] == 0.0) & (df_bsl.loc[:,'ssp1']!=0.0)
                    ssp1_check = (df_bsl.loc[:,'ssp1'] == 0.0) & (df_bsl.loc[:,'ssp2']!=0.0)
                   
                    df_bsl.loc[criteria_ssp,'tt'] = ((df_bsl[criteria_ssp]['range']-df_bsl[criteria_ssp]['TAT'])/2)/1000
                    df_bsl.loc[ssp2_check,'tt'] = ((df_bsl[ssp2_check]['range']-df_bsl[ssp2_check]['TAT'])/2)/1000
                    df_bsl.loc[ssp1_check,'tt'] = ((df_bsl[ssp1_check]['range']-df_bsl[ssp1_check]['TAT'])/2)/1000
                    
                    df_bsl.loc[criteria_ssp,'bsl'] = baseline_calc_hmean(df_bsl[criteria_ssp]['ssp1'],df_bsl[criteria_ssp]['ssp2'],df_bsl[criteria_ssp]['range'],df_bsl[criteria_ssp]['TAT'])
                    
                    df_bsl.loc[ssp1_check,'bsl'] = baseline_calc_hmean(df_bsl[ssp1_check]['ssp2'],df_bsl[ssp1_check]['ssp2'],df_bsl[ssp1_check]['range'],df_bsl[ssp1_check]['TAT'])

                    df_bsl.loc[ssp2_check,'bsl'] = baseline_calc_hmean(df_bsl[ssp2_check]['ssp1'],df_bsl[ssp2_check]['ssp1'],df_bsl[ssp2_check]['range'],df_bsl[ssp2_check]['TAT'])
                    
                    bsl_sucess = len(df_bsl.loc[pd.notnull(df_bsl['bsl'])])
                    
#---------------------------------------------------------------------------------------
    #            SV_HRT
    
                    # for row selection allow also single sided baseline
                    # calculation
                    criteria_sv_hrt = (df_bsl['sv_hrt1']!=0.0) & (df_bsl['sv_hrt2']!=0.0)
                    # one side baseline calculation
                    sv_hrt2_check = (df_bsl['sv_hrt2'].isnull()) & (df_bsl['sv_hrt1'].notnull())
                    
                    sv_hrt1_check = (df_bsl['sv_hrt1'].isnull()) & (df_bsl['sv_hrt2']!=0.0)
                    
                    df_bsl.loc[criteria_sv_hrt,'tt'] = ((df_bsl[criteria_sv_hrt]['range']-df_bsl[criteria_sv_hrt]['TAT'])/2)/1000
                    df_bsl.loc[sv_hrt2_check,'tt'] = ((df_bsl[sv_hrt2_check]['range']-df_bsl[sv_hrt2_check]['TAT'])/2)/1000
                    df_bsl.loc[sv_hrt1_check,'tt'] = ((df_bsl[sv_hrt1_check]['range']-df_bsl[sv_hrt1_check]['TAT'])/2)/1000
                    
                    df_bsl.loc[criteria_sv_hrt,'bsl_hrt'] = baseline_calc_hmean(df_bsl[criteria_sv_hrt]['sv_hrt1'],df_bsl[criteria_sv_hrt]['sv_hrt2'],df_bsl[criteria_sv_hrt]['range'],df_bsl[criteria_sv_hrt]['TAT'])
                    
                    df_bsl.loc[sv_hrt1_check,'bsl_hrt'] = baseline_calc_hmean(df_bsl[sv_hrt1_check]['sv_hrt2'],df_bsl[sv_hrt1_check]['sv_hrt2'],df_bsl[sv_hrt1_check]['range'],df_bsl[sv_hrt1_check]['TAT'])

                    df_bsl.loc[sv_hrt2_check,'bsl_hrt'] = baseline_calc_hmean(df_bsl[sv_hrt2_check]['sv_hrt1'],df_bsl[sv_hrt2_check]['sv_hrt1'],df_bsl[sv_hrt2_check]['range'],df_bsl[sv_hrt2_check]['TAT'])
                    
                    bsl_hrt_sucess = len(df_bsl.loc[pd.notnull(df_bsl['bsl_hrt'])])
    #---------------------------------------------------------------------------------------
    #            SV_TPR
    
                    criteria_sv_tpr = (df_bsl['sv_tpr1']!=0.0) & (df_bsl['sv_tpr2']!=0.0)
                    sv_tpr2_check = (df_bsl['sv_tpr2'].isnull()) & (df_bsl['sv_tpr1'].notnull())
                    sv_tpr1_check = (df_bsl['sv_tpr1'].isnull()) & (df_bsl['sv_tpr2']!=0.0)
                    
                    df_bsl.loc[criteria_sv_tpr,'tt'] = ((df_bsl[criteria_sv_tpr]['range']-df_bsl[criteria_sv_tpr]['TAT'])/2)/1000
                    df_bsl.loc[sv_tpr2_check,'tt'] = ((df_bsl[sv_tpr2_check]['range']-df_bsl[sv_tpr2_check]['TAT'])/2)/1000
                    df_bsl.loc[sv_tpr1_check,'tt'] = ((df_bsl[sv_tpr1_check]['range']-df_bsl[sv_tpr1_check]['TAT'])/2)/1000
                    
                    df_bsl.loc[criteria_sv_hrt,'bsl_tpr'] = baseline_calc_hmean(df_bsl[criteria_sv_tpr]['sv_tpr1'],df_bsl[criteria_sv_tpr]['sv_tpr2'],df_bsl[criteria_sv_tpr]['range'],df_bsl[criteria_sv_tpr]['TAT'])
                    
                    df_bsl.loc[sv_tpr1_check,'bsl_tpr'] = baseline_calc_hmean(df_bsl[sv_tpr1_check]['sv_tpr2'],df_bsl[sv_tpr1_check]['sv_tpr2'],df_bsl[sv_tpr1_check]['range'],df_bsl[sv_tpr1_check]['TAT'])

                    df_bsl.loc[sv_tpr2_check,'bsl_tpr'] = baseline_calc_hmean(df_bsl[sv_tpr2_check]['sv_tpr1'],df_bsl[sv_tpr2_check]['sv_tpr1'],df_bsl[sv_tpr2_check]['range'],df_bsl[sv_tpr2_check]['TAT'])
                    
                    bsl_tpr_sucess = len(df_bsl.loc[pd.notnull(df_bsl['bsl_tpr'])])
    #---------------------------------------------------------------------------------------
    #            PRS_DIFF
                    
                    criteria_prs_diff = (df_bsl['prs1']!=0.0) & (df_bsl['prs2']!=0.0)
                    df_bsl.loc[criteria_prs_diff,'prs_diff'] = calc_prs_diff(df_bsl[criteria_prs_diff]['prs1'],df_bsl[criteria_prs_diff]['prs2'])
                    
                    #diff = 1
                    #try:
                    #    df_bsl = pd.concat([df_bsl,prs_diff],axis=1)
                    #except:
                    #    diff = 0
                    
                    # count entries of df_bsl for which 'bsl' is not NaN

                elif len(df_bsl) <= 5:
                    bsl_sucess = 0
                    bsl_hrt_sucess = 0
                    bsl_tpr_sucess = 0
                    
                    print(str(len(df_bsl)) + '\t Ranges found')
                    print(str(bsl_sucess) + '\t Successfull Calculated Baselines from SSP')
                    print(str(bsl_hrt_sucess) + '\t Successfull Calculated Baselines from HRT')
                    print(str(bsl_tpr_sucess) + '\t Successfull Calculated Baselines from TPR')
                    
                    continue
                    
                else:
                    bsl_sucess = 0
                    bsl_hrt_sucess = 0
                    bsl_tpr_sucess = 0
                    
                    print(str(len(df_bsl)) + '\t Ranges found')
                    print(str(bsl_sucess) + '\t Successfull Calculated Baselines from SSP')
                    print(str(bsl_hrt_sucess) + '\t Successfull Calculated Baselines from HRT')
                    print(str(bsl_tpr_sucess) + '\t Successfull Calculated Baselines from TPR')
                    
                    continue
                    
                #end if not df_bsl.empty:

                df_bsl = extract_df(df_bsl,column_list=['ID','range_ID','range','TAT','tt','hrt1','hrt2','prs1','prs2','prs_diff','tpr1','tpr2','sal1','sal2','ssp1','ssp2','bsl','sv_hrt1','sv_hrt2','bsl_hrt','sv_tpr1','sv_tpr2','bsl_tpr'])

                                        
                if writefile:
                    if dateformat == 'MATLAB_DATEFORMAT':
                        df_bsl.to_csv(pathname + beacon_1 +'-'+ beacon_2 +'-BSL.dat', header=True, date_format=MATLAB_DATEFORMAT)
                    else:
                        df_bsl.to_csv(pathname + beacon_1 +'-'+ beacon_2 +'-BSL.dat', header=True, date_format=GMT_DATEFORMAT)
                    
                    

                    # end if suffix == None:
                # end if writefile:

                print(str(len(df_bsl)) + '\t Ranges found')
                print(str(bsl_sucess) + '\t Successfull Calculated Baselines from SSP')
                print(str(bsl_hrt_sucess) + '\t Successfull Calculated Baselines from HRT')
                print(str(bsl_tpr_sucess) + '\t Successfull Calculated Baselines from TPR')
                if len(df_bsl) != 0:
                    print(' ')
                    print(str(SV_1_err_count) + '\t No SV Record in -> ' + str(beacon_1))
                    print(str(SV_2_err_count) + '\t No SV Record in -> ' + str(beacon_2))
                print(' \n')
                
                list_df_bsl.append(df_bsl)
                #  append to data formats of other stations
     
                cal_bsl_series.append(df_bsl)


            # end if beacon_1 != beacon_2:

        # end for j, beacon_2 in enumerate(ID):

    # end for i, beacon_1 in enumerate(ID):

    if outlier_flag == True:
        final_bsls = []
        for i in range(len(cal_bsl_series)):
            
                ### cut off unrealistic Ranges and Baselines ###

                # This part removes all baselines with lengths +/-10m

            print('Cut Off unrealistic Ranges and Baselines for: ' + str(ID_pair[i][0]) + ' <-> ' + str(ID_pair[i][1]))
            # calculate mean range exculding NaN value
            mean_bsl = cal_bsl_series[i].median(axis=0,skipna=True)['bsl']
            print("BSL: " + str(mean_bsl))
            mean_bsl_hrt = cal_bsl_series[i].median(axis=0,skipna=True)['bsl_hrt']
            print("BSL HRT: " + str(mean_bsl_hrt))
            mean_bsl_tpr = cal_bsl_series[i].median(axis=0,skipna=True)['bsl_tpr']
            print("BSL TPR: " + str(mean_bsl_tpr))
            
            # keep only those baselines within mean_bsl +/-1 m
            
            df_bsl_remean = cal_bsl_series[i].loc[ (cal_bsl_series[i]['bsl']>mean_bsl-1) & (cal_bsl_series[i]['bsl']<mean_bsl+1)]
            
            df_bsl_hrt_remean = df_bsl_remean.loc[ (df_bsl_remean['bsl_hrt']>mean_bsl_hrt-1) & (df_bsl_remean['bsl_hrt']<mean_bsl_hrt+1)]
            
            df_bsl = df_bsl_hrt_remean.loc[ (df_bsl_hrt_remean['bsl_tpr']>mean_bsl_tpr-1) & (df_bsl_hrt_remean['bsl_tpr']<mean_bsl_tpr+1)]
            
            print("Pair: {0:s} <-> {1:s}".format(ID_pair[i][0],ID_pair[i][1]))
            print("{0:d} baselines from {1:d} kept.".format(len(df_bsl),len(cal_bsl_series[i])))
    #        else:
     #           df_bsl = cal_bsl_series[i]
            

            # re-arange order of columns
            df_bsl = extract_df(df_bsl,column_list=['ID','range_ID','range','TAT','tt','hrt1','hrt2','prs1','prs2','prs_diff','tpr1','tpr2','sal1','sal2','ssp1','ssp2','bsl','sv_hrt1','sv_hrt2','bsl_hrt','sv_tpr1','sv_tpr2','bsl_tpr'])
            final_bsls.append(df_bsl)
            
            list_df_bsl = final_bsls
            
            if writefile:
                if dateformat == 'MATLAB_DATEFORMAT':
                    final_bsls[i].to_csv( pathname + ID_pair[i][0] +'-'+ ID_pair[i][1] +'-BSL.dat', header=True, date_format=MATLAB_DATEFORMAT)
                else:
                    final_bsls[i].to_csv( pathname +  ID_pair[i][0] +'-'+ ID_pair[i][1] + '-BSL.dat', header=True, date_format=GMT_DATEFORMAT)
          
                # end if suffix is None:
            # end if writefile:
        # end for i in range(len(cal_bsl_series):

        if not writefile:
            print('\n')
            print('Data has not been stored in files!')
        # end if not writefile:

    return(list_df_bsl)
# end def sort_bsl( ... ):
