
![PyPI - License](https://img.shields.io/pypi/l/geosea?style=plastic)
![PyPI - Version](https://img.shields.io/pypi/v/geosea?style=plastic)


# Project Description


Geosea is an open tool box for seafloor geodetic data processing of dircet-path ranging. It supplies a variety of functions to process acoustic baselines and analyze ground movement. 


# Dependencies


sciPy: miscellaneous statistical functions

matplotlib: for plotting

pandas: data structures and data analysis tool

numPy: 1.7.1 or higher

obspy: for date and time types


# Import of GeoSEA Module

import geosea 

# Functions


**Read raw csw files into an pandas DataFrame:**

geosea.read(sal=None ,phi=None, starttime=None, endtime=None, pathname=None, writefile=True, writevariable=True, dateformat=None)

Calculates the sound velocity from temperature in °C, pressure in kPa and constant salinity in PSU. 

**Complete Baseline processing of horizontal and vertical changes in time:**

geosea.bsl(ID=None, st_series=None, bsl_series=None, outlier_flag=False, pathname=None, starttime=None, endtime=None, writefile=True, dateformat=None)



Parameters:
            SAL                     constant salinity value in PSU
            phi                     Latitude for Leroy formular in XX.X°         
            pathname                Pathname of raw CSV Data files
            outlier_flag            Cuts outlier mesurements automatically (Default = None)
            writefile               Save output data to csv data format (Defulat = True)
            dateformat              GMT_DATEFORMAT or MATLAB_DATEFORMAT
            
            
            






