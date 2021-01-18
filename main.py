# ------------------------
# set scenario parameters
# ------------------------

# set path to where the data is stored
pathData = ''

# set demanded stored kinetic energy by the TSO in MWs
kinEnergyTso = 23000

# set inertia share from power consumers in percentage
inertiaPowerConsumers = 20

# set inertia constants for different fuel sources in s
# min and max literature value
inertiaConstantBiomass = [2, 2]
inertiaConstantHardCoal = [4, 4.25]
inertiaConstantDistillate = [3.5, 3.5]
inertiaConstantFossilGas = [3.5, 6.25]
inertiaConstantHydro = [1, 4.5]
inertiaConstantFossilOil = [3.5, 3.5]
inertiaConstantFossilPeat = [3.7, 3.7]
inertiaConstantPumpStorage = [5.5, 6.35]

# set H_dem for synthetic inertia calcualtion in s
inertiaConstantDemand = 6

# switch whether synthetic inertia by WT should be considered
# 1 = synthetic inertia by wind turbines is enabled
# 0 = synthetic inertia by wind turbines is disabled
syntheticInertiaWind = 1

# -----------------
# package import
# -----------------

import pandas
import os
import pickle
import datetime
import math
from scipy.interpolate import interp1d


# ------------------
# import section
# ------------------

# run script to import registered units
exec(open("reg_units_import.py").read())

# run script to import entso-e data
exec(open("entso_e_import.py").read())

# run script to import entso-e data
exec(open("bid_file_import.py").read())

# if synthetic ienrtia by wind turbines shall be inclided, the data is imported
if syntheticInertiaWind == 1:
    exec(open("wind_import.py").read())
else:
    None

# run script to process entso-e data
exec(open("process_bid_file_data.py").read())

# run script to execute the inertia dispatch algorithm
exec(open("inertia_dispatch.py").read())
