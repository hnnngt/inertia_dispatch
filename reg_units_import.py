# -------------------
# import section
# -------------------

# set paths to files

# path to List-of-Registered-Units.xlsx
# file can be downloaded from https://www.sem-o.com/documents/general-publications/List-of-Registered-Units.xlsx
fileRegUnits = 'List-of-Registered-Units.xlsx'

# path to Registered-Capacity-April-2020.xlsx
# file can be downloaded from https://www.sem-o.com/documents/general-publications/List-of-Registered-Units.xlsx
fileRegCapacities = 'Registered-Capacity-April-2020.xlsx'

# path to PUBLIC GEN DATA 2017-18.xlsx
# file can be downloaded from https://www.semcommittee.com/publication/sem-17-056-baringa-sem-plexos-forecast-model-2017-18
filePublicGenData = 'PUBLIC GEN DATA 2017-18.xlsx'

# import data of registered units
dataRegUnits = pandas.read_excel(pathData + fileRegUnits, header=3)
# import data of registered capacities
dataRegCap = pandas.read_excel(pathData + fileRegCapacities)
# import data of public generator data from SEM Committe
dataPubGen = pandas.read_excel(pathData + filePublicGenData, sheet_name=1, header=2)

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

# -------------------
# merge installed capacity data, updated fuel names and inertia data and list of registered units
# -------------------
dataRegUnits['Installed Capacity'] = listCap
dataRegUnits['Installed Capacity'] = dataRegUnits['Installed Capacity'].round(2)

# -------------------
# export data
# -------------------

dataRegUnits.to_csv(pathData + 'Reg_Units_Modified' + '.csv', sep=';')

# print message
print('import registered units successfull')
