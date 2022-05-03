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

from .proc_bsl import *
from .search_df import *

from .range_sv import *
from .replace import *
from .vert_bsl import *
from .bsl import *
from .bsl_test import *

from .compare_df import *

from .calc import *
from .correct import *

global GMT_DATEFORMAT # Output date format
global IN_DATEFORMAT # Input date format
global PROJECTS # GeoSEA projects

# Global date format for export
GMT_DATEFORMAT = '%Y-%m-%dT%H:%M'
IN_DATEFORMAT = '%Y/%m/%d %H:%M:%S'


