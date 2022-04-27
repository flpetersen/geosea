
# Project Description


Geosea is an open tool box for seafloor geodetic data processing of dircet-path ranging. It supplies a variety of functions to process acoustic baselines and analyze ground movement. 



# Dependencies
#

sciPy: miscellaneous statistical functions

matplotlib: for plotting

pandas: data structures and data analysis tool

numPy: 1.7.1 or higher

obspy: for date and time types


# Import of GeoSEA Module

import geosea 

# Functions

geosea.proc_bsl (SAL,phi,pathname=None,outlier_flag=None,writefile=True)

Read raw csw files into an pandas DataFrame. 

Calculates the sound velocity from temperature in °C, pressure in kPa and constant salinity in PSU. 

Complete Baseline processing of horizontal and vertical changes in time. 

Parameters:
            SAL                 constant salinity value in PSU
            phi                   Latitude for Leroy formular in XX.X
            pathname        Pathname of raw CSV Data files
            outlier_flag      Cuts outlier mesurements automatically (Default = None)
            writefile           Save output data to csv data format (Defulat = True)
            
            
            






