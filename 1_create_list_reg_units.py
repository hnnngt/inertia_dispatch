# -------------------
# import packages
# ------------------

import pandas

# -------------------
# import section
# -------------------

# set paths to files

# path to List-of-Registered-Units.xlsx
# file can be downloaded from https://www.sem-o.com/documents/general-publications/List-of-Registered-Units.xlsx
fileRegUnits = 'set path/List-of-Registered-Units.xlsx'

# path to Registered-Capacity-April-2020.xlsx
# file can be downloaded from https://www.sem-o.com/documents/general-publications/List-of-Registered-Units.xlsx
fileRegCapacities = 'set path/Registered-Capacity-April-2020.xlsx'

# path to PUBLIC GEN DATA 2017-18.xlsx
# file can be downloaded from https://www.semcommittee.com/publication/sem-17-056-baringa-sem-plexos-forecast-model-2017-18
filePublicGenData = 'set path/PUBLIC GEN DATA 2017-18.xlsx'

# import data of registered units
dataRegUnits = pandas.read_excel(fileRegUnits, header=3)
# import data of registered capacities
dataRegCap = pandas.read_excel(fileRegCapacities)
# import data of public generator data from SEM Committe
dataPubGen = pandas.read_excel(filePublicGenData, sheet_name=1, header=2)

# ---------------
# data extension
# ---------------

# loop to extend data with installed capacities

# create empty capacity list
listCap = [0] * len(dataRegUnits)

# for loop
for idx1 in dataRegUnits.index:
    for idx2 in dataRegCap.index:
        if dataRegUnits['Resource Name'][idx1] == dataRegCap['Resource Name'][idx2]:
            listCap[idx1] = dataRegCap['Registered Capacity / Dispatchable Capacity'][idx2]/85*100 # conversion from reatead power to rated apparent power
        else:
            None

# loop to extend data; additional information regarding fuel sources or type of generator

#create empty fuel name list
listFuelType = [None] * len(dataRegUnits)

# for loop to get data
for idx1 in dataRegUnits.index:
    for idx2 in dataPubGen.index:
        if dataRegUnits['Resource Name'][idx1] == dataPubGen['SEM Unit ID'][idx2]:
            listFuelType[idx1] = dataPubGen['Fuel for Generation and No Load'][idx2]
        else:
            None


# -----------------
# rename fuel types
# -----------------

for idx1 in dataRegUnits.index:
    if dataRegUnits['Fuel Type'][idx1] == 'BIOMASS':
        dataRegUnits['Fuel Type'][idx1] = 'biomass'
    elif dataRegUnits['Fuel Type'][idx1] == 'COAL':
        dataRegUnits['Fuel Type'][idx1] = 'coal'
    elif dataRegUnits['Fuel Type'][idx1] == 'DISTILLATE':
        dataRegUnits['Fuel Type'][idx1] = 'distillate'
    elif dataRegUnits['Fuel Type'][idx1] == 'GAS':
        dataRegUnits['Fuel Type'][idx1] = 'gas'
    elif dataRegUnits['Fuel Type'][idx1] == 'HYDRO':
        dataRegUnits['Fuel Type'][idx1] = 'hydro'
    elif dataRegUnits['Fuel Type'][idx1] == 'MULTI_FUEL':
        dataRegUnits['Fuel Type'][idx1] = 'gas'
    elif dataRegUnits['Fuel Type'][idx1] == 'OIL':
        dataRegUnits['Fuel Type'][idx1] = 'oil'
    elif dataRegUnits['Fuel Type'][idx1] == 'PEAT':
        dataRegUnits['Fuel Type'][idx1] = 'peat'
    elif dataRegUnits['Fuel Type'][idx1] == 'PUMP_STORAGE':
        dataRegUnits['Fuel Type'][idx1] = 'pump_storage'
    elif dataRegUnits['Fuel Type'][idx1] == 'WIND':
        dataRegUnits['Fuel Type'][idx1] = 'wind'
    elif dataRegUnits['Fuel Type'][idx1] == 'SOLAR':
        dataRegUnits['Fuel Type'][idx1] = 'solar'
    else:
        dataRegUnits['Fuel Type'][idx1] = 'nan'

# ---------------------------
# process inertia information
# ---------------------------

# set up a dictionry containing inertia constant [s] per fuel type
inertiaDic = {'biomass': 2  ,
              'coal': 4,
              'distillate': 3.5,
              'gas': 3.5,
              'hydro': 1,
              'oil': 3.5,
              'peat': 3.7,
              'pump_storage': 5.5}

# create empty list to store inertia constants
listInertia = [0] * len(dataRegUnits)

#for loop to allocate inertia constants based on fuel type
for idx1 in dataRegUnits.index:
    for key in inertiaDic:
        if dataRegUnits['Fuel Type'][idx1] == key:
            listInertia[idx1] = inertiaDic[key]
        else:
            None

# -------------------
# merge installed capacity data, updated fuel names and inertia data and list of registered units
# -------------------
dataRegUnits['Installed Capacity'] = listCap
dataRegUnits['Installed Capacity'] = dataRegUnits['Installed Capacity'].round(2)
dataRegUnits['Additional Fuel Information'] = listFuelType
dataRegUnits['Inertia Constant'] = listInertia
# -------------------
# export data
# -------------------

# export data to csv
pathExport = 'path to where the processed data shall be saved'
dataRegUnits.to_csv(path + 'file name' + '.csv', sep=';')
