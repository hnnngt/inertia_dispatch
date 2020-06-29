# ------------------
# package import
# ------------------

import pandas
import numpy
import math

# ------------------
# define function
# ------------------
def calc_cost_per_inertia(resultBeforeVar, resultAfterVar):

    # empty lists
    sysCost = []
    inertia = []
    costPerKinEn = []

    for idx in resultAfterVar.index:
        # calculate system costs
        sysCostTmp = resultAfterVar['Price'][idx].tolist()*resultAfterVar['Quantity'][idx].tolist()-resultBeforeVar['Price'][idx].tolist()*resultBeforeVar['Quantity'][idx].tolist()
        # calculate stored kinetic energy
        inertiaTmp = ((resultAfterVar['Inertia'][idx].tolist()*2*1000000)/(4*math.pi*math.pi*50*50))-((resultBeforeVar['Inertia'][idx].tolist()*2*1000000)/(4*math.pi*math.pi*50*50))

        # store temporal results in list
        sysCost.append(sysCostTmp)
        inertia.append(inertiaTmp)

        # calculate costs
        try:
            costPerKinEn.append(sysCostTmp/inertiaTmp)
        except ZeroDivisionError:
            costPerKinEn.append(0)

    return sysCost, inertia, costPerKinEn

# ------------------
# data import
# ------------------
# data before application of algorithm
resultsBefAlgo = pandas.read_csv('path/results_before.csv', sep=';')
resultsAftAlgo = pandas.read_csv('path/results_after.csv', sep=';')

# ------------------
# data assessment
# ------------------
#drop na values
resultsBefAlgo.dropna(axis='index', inplace=True)
resultsAftAlgo.dropna(axis='index', inplace=True)

# subset of before data
tmpData = resultsBefAlgo.loc[resultsBefAlgo.index]
resultsBefAlgo = tmpData

# execute function
sysCost, kinEnergy, costPerKinEn = calc_cost_per_inertia(resultsBefAlgo, resultsAftAlgo)

# print results
print('Costs [EUR/kg m^2]: ' + str(sum(costPerKinEn)/len(costPerKinEn)))
