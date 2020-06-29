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
# plot function
def execute_plot(subsetBeforeAlgoVar, subsetAfterAlgoVar):
    # set latex font
    rc('font',**{'family':'serif','sans-serif':['Helvetica'], 'size':14})
    ## for Palatino and other serif fonts use:
    #rc('font',**{'family':'serif','serif':['Palatino']})
    rc('text', usetex=True)
    #plt.rc('font', family='serif')
    fig, ax = plt.subplots()
    plt.plot(subsetBeforeAlgoVar['Time'], subsetBeforeAlgoVar['Inertia'], label='Kinetic Energy (BA)', alpha=0.6, linewidth = 1.3)
    plt.plot(subsetAfterAlgoVar['Time'], subsetAfterAlgoVar['Inertia'], label='Kinetic Energy  (AA)', alpha=0.6, linewidth = 1.3)
    ax.legend(loc='lower right')
    ax.set_xlabel('Time')
    myFmt = mdt.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(myFmt)
    start, end = ax.get_xlim()
    ax.xaxis.set_ticks(np.arange(start, end, ((end-start)/8)))
    ax.margins(x=0)
    ax.set_ylabel('Kinetic Energy [MWs]')
    plt.title(str(max(subsetBeforeAlgoVar['Time']).date()))
    ax.grid()
    #fig.set_size_inches(8, 4.5)
    fig.tight_layout()
    fig.savefig('path/' + str(max(subsetBeforeAlgoVar['Time']).date()) + '.pdf', format='pdf')

# date subset function
def date_subset(dfResBeforeAlgoVar, dfResAfterAlgoVar, dayVar, dateMinVar):
    # set start and end date
    startDate = dateMinVar + pandas.tseries.offsets.Day(dayVar)
    endDate = dateMinVar + pandas.tseries.offsets.Day(dayVar+1) - pandas.tseries.offsets.Hour(1)

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


# create the start and end date for the first step of the loop
for idxDay in range(noDays+1):
    subsetBeforeAlgo, subsetAfterAlgo = date_subset(dfResultsBefore, dfResultsAfter, idxDay, dateMin)
# -------------------
# execute plot sequence
# -------------------

    execute_plot(subsetBeforeAlgo, subsetAfterAlgo)
