# ------------------
# package import
# ------------------

import pandas
import datetime
import pickle
import matplotlib.pyplot as plt
from matplotlib import dates as mdt
from matplotlib import rc
import numpy as np

# ----------------
# define function
# ----------------

# date subset function
def date_subset(dfResBeforeAlgoVar, dfResAfterAlgoVar, dayVar, dateMinVar):
    # set start and end date
    startDate = dateMinVar + pandas.tseries.offsets.Day(dayVar)
    endDate = dateMinVar + pandas.tseries.offsets.Day(dayVar) + pandas.tseries.offsets.Hour(23)

    # create logical index
    afterStartDate = dfResBeforeAlgoVar['Time'] >= startDate
    beforeEndDate = dfResBeforeAlgoVar['Time'] <= endDate
    betweenTwoDates = afterStartDate & beforeEndDate

    # get subset
    subsetBeforeAlgoVar = dfResBeforeAlgoVar.loc[betweenTwoDates]
    subsetAfterAlgoVar = dfResAfterAlgoVar.loc[betweenTwoDates]

    subsetBeforeAlgoVar = subsetBeforeAlgoVar.sort_values(by='Time', ascending=True)
    subsetAfterAlgoVar = subsetAfterAlgoVar.sort_values(by='Time', ascending=True)

    return subsetBeforeAlgoVar, subsetAfterAlgoVar

# calculate the system costs
def calc_system_cots(subsetBeforeAlgoVar, subsetAfterAlgoVar):
    # temporal empty list to store system costs
    sysCostBeforeTmp = []
    sysCostAfterTmp = []

    # get time info
    timeTmp = subsetBeforeAlgoVar['Time'].iloc[12].date()

    # subset of energy and price data
    priceBeforeTmp = subsetBeforeAlgoVar['Price'].tolist()
    priceAfterTmp = subsetAfterAlgoVar['Price'].tolist()
    quantityBeforeTmp = subsetBeforeAlgoVar['Quantity'].tolist()
    quantityAfterTmp = subsetAfterAlgoVar['Quantity'].tolist()

    # loop to calcualte system costs of subset per hour
    for i in range(len(priceBeforeTmp)):
        sysCostBeforeTmp.append(abs(priceBeforeTmp[i] * quantityBeforeTmp[i]/1000))
        sysCostAfterTmp.append(abs(priceAfterTmp[i] * quantityAfterTmp[i]/1000))

    # calculate the sum of costs per day
    sumCostBefore = sum(sysCostBeforeTmp)
    sumCostAfter = sum(sysCostAfterTmp)
    sysCostDiffTmp = sumCostAfter - sumCostBefore

    return sumCostBefore, sumCostAfter, sysCostDiffTmp, timeTmp

# ----------------
# data import
# ----------------

# set path to the folder where the results are stored
path = 'path'

# import results
dfResultsBefore = pandas.read_csv(path + 'results_before.csv', sep=';', index_col=0, parse_dates=['Time'])
dfResultsAfter = pandas.read_csv(path + 'results_after.csv', sep=';', index_col=0, parse_dates=['Time'])

# -------------------
# date subset
# -------------------
# find min and maximum values of the time series
dateMin = min(dfResultsBefore['Time'])
dateMax = max(dfResultsBefore['Time'])
# full number of days
noDays = (dateMax - dateMin).days

sysCostBefore = []
sysCostAfter = []
sysCostTime = []
sysCostDiff = []

# create the start and end date for the first step of the loop
for idxDay in range(noDays+1):
    subsetBeforeAlgo, subsetAfterAlgo = date_subset(dfResultsBefore, dfResultsAfter, idxDay, dateMin)

    costBefore, costAfter, costDiff, time = calc_system_cots(subsetBeforeAlgo, subsetAfterAlgo)

    sysCostBefore.append(costBefore)
    sysCostAfter.append(costAfter)
    sysCostTime.append(time)
    sysCostDiff.append(costDiff)

# plot system costs
rc('font',**{'family':'serif','sans-serif':['Helvetica'], 'size':14})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=True)
fig, ax = plt.subplots()
plt.bar(sysCostTime, sysCostBefore, alpha=0.6, label='Costs (BA)')
plt.bar(sysCostTime, sysCostDiff, alpha=0.6, bottom=sysCostBefore, label='Costs (AA)')
ax.legend(loc='upper right')
ax.set_xlabel('Date')
myFmt = mdt.DateFormatter('%d/%m')
ax.xaxis.set_major_formatter(myFmt)
start, end = ax.get_xlim()
ax.xaxis.set_ticks(np.arange(start, end, ((end-start)/7)))
ax.set_ylabel('System Costs [TEUR/d]')
ax.grid()
#fig.set_size_inches(8, 4.5)
fig.tight_layout()
fig.savefig('path', format='pdf')
