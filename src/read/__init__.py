# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#  Purpose: Convenience imports for geosea
#   Author: Florian Petersen
#           Katrin Hannemann
#
# GEOMAR Helmholtz Centre for Ocean Research Kiel, Germany
#
# Version: 2021.1.2.1                August 2020
#
# -----------------------------------------------------------------------------
"""
GeoSEA: A Python Toolbox for seafloor geodesy
======================================================

GeoSEA is an open-source project to provide a pursuning Python tool for
seafloor gedetic data processing.
"""

from __future__ import absolute_import
import warnings

from .read import *
from .read_id import *
from .read_data import *
from .read_bsl import *
from .read_meta import *
from .read_tides import *
from .read_airpressure import *

global GMT_DATEFORMAT # Output date format
global IN_DATEFORMAT # Input date format
global PROJECTS # GeoSEA projects

# Global date format for export
GMT_DATEFORMAT = '%Y-%m-%dT%H:%M'
IN_DATEFORMAT = '%Y/%m/%d %H:%M:%S'


