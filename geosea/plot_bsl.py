
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from .read.read_id import read_id
from .read.read_data import read_data
from .read.read_bsl import read_bsl


def plot_bsl(ID = None, pathname=None, starttime=None):

    if pathname is None:
        pathname = ''

    if ID == None:
        ID = read_id(pathname=pathname)
  

    for beacon1 in ID:
        for beacon2 in ID:
            if beacon1 != beacon2:

                df = read_bsl(beacon1,beacon2)

                

                start_date = str(df.index.year[0]) + '-' + str(df.index.month[0]) + '-28'

                end_date = str(df.index.year[-1]) + '-' + str(df.index.month[-1]) + '-01'

                print(start_date)

                mean = df[df.index <= start_date].bsl_tpr.mean()
                df2 = pd.DataFrame([{'mean':mean,'mean':mean}],index=[df[df.index <= start_date].index[0],df[df.index <= start_date].index[-1]] )

                mean2 = df[df.index <= start_date].bsl_tpr.mean()

                mean3 = df[df.index >= '2022-08-25'].bsl_tpr.mean()

                plot_mean = (mean2 + mean3)/2

                bsl_mean = plot_mean/10000*2

                print(beacon1, beacon2,plot_mean)

                #df3 = pd.DataFrame([{'mean':mean2,'mean':mean3}],index=[df[df.index <= '2021-11-08'].index[0],df[df.index <= '2021-11-08'].index[-1]] )
                #df3 = pd.DataFrame([{'mean':mean2}],index=[df[df.index <= '2022-04-08'].index[0]] ).append(pd.DataFrame([{'mean':mean3}],index=[df[df.index <= '2022-04-08'].index[-1]]))
                df3 = pd.DataFrame([{'mean':mean2}],index=[df[df.index <= '2022-04-08'].index[0]])
                pd.concat([df3, pd.DataFrame([{'mean':mean3}],index=[df[df.index <= '2022-04-08'].index[-1]])])
                

                fig = plt.figure(figsize=(12, 3))
                ax = fig.add_subplot(111)
                ax.plot(df.bsl_tpr,'.',ms=2)

                #ax.plot(df2,lw=3)
                #ax.plot(df3,lw=3)
                ax.set_ylim(plot_mean-bsl_mean, plot_mean+bsl_mean)

                # plot Figure and Save as PDF
                plt.grid(True)
                plt.title(str(beacon1) + ' - ' + str(beacon2))

                plt.savefig(str(beacon1) + '-' + str(beacon2) + '.pdf', bbox_inches='tight')

