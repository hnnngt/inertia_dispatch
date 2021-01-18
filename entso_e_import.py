# -------------
# data import
# -------------
# set path
pathEntso = 'ActualGenerationOutputPerUnit/'

converterEntso = pandas.read_csv(pathData + 'ENTSO_EIRGRID.csv',
                                 sep=';')

# create a list of files within the folder
listFilesEntso = os.listdir(pathData + pathEntso)

# data import
for l in range(0,len(listFilesEntso)):
    dataEntsoTmp = pandas.read_csv(pathData + pathEntso + listFilesEntso[l],
                                   encoding='utf_16',
                                   sep='\t')

    if l == 0:
        dataEntso = dataEntsoTmp
    else:
        dataEntso =  dataEntso.append(dataEntsoTmp, ignore_index=True)

# --------------
# data reduction
# --------------
# reduce data to EirGrid
dataEntsoIe = dataEntso[dataEntso['MapCode'] == 'IE']
dataEntsoNie = dataEntso[dataEntso['MapCode'] == 'NIE']
dataEntsoEirGrid = dataEntsoIe.append(dataEntsoNie, ignore_index=True)
dataEntsoEirGrid = dataEntsoEirGrid[['DateTime', 'MapCode', 'PowerSystemResourceName', 'ProductionTypeName', 'ActualGenerationOutput', 'InstalledGenCapacity']]

# adapt time info
for idx in dataEntsoEirGrid['DateTime'].index:
    dataEntsoEirGrid.loc[idx, 'DateTime'] = dataEntsoEirGrid.loc[idx, 'DateTime'][0:19]

# -------------------
# export data
# -------------------

dataEntsoEirGrid.to_csv(pathData + 'Entso_e_data' + '.csv', sep=';')

# print message
print('import ENTSO-E data successfull')
