# ------------------
# package import
# ------------------

import pandas
import datetime
import pickle
import matplotlib.pyplot as plt
from matplotlib import rc

# ----------------
# data import
# ----------------

# set path to the folder where the results are stored
path = 'path'

# open pickle data and import results
dicSellBefore = pickle.load(open(path + "bid_sell_data_calc.pickle", "rb"))
dicBuyBefore = pickle.load(open(path + "bid_buy_data_calc.pickle", "rb"))
dicSellAfter = pickle.load(open(path + "bid_sell_data_after_algo.pickle", "rb"))

# -------------------
# execute plot sequence
# -------------------

for key in dicSellBefore:
    # extract data from dictionary
    dfSellBefore = dicSellBefore[key]
    dfSellAfter = dicSellAfter[key]
    dfBuyBefore = dicBuyBefore[key]

    # extract price and quantity buy data
    priceBuyBefore = dfBuyBefore['Price']
    quantityBuyBefore = dfBuyBefore['Accumulated Difference']

    # extract price and quantity sell data before application of the algorithm
    priceSellBefore = dfSellBefore['Price']
    quantitySellBefore = dfSellBefore['Accumulated Difference']

    # extract price and quantity sell data after application of the algorithm
    priceSellAfter = dfSellAfter['Price']
    quantitySellAfter = dfSellAfter['Accumulated Difference']

    # data visualisation
    fig, ax = plt.subplots()
    # set latex font
    rc('font',**{'family':'serif','sans-serif':['Helvetica'], 'size':14})
    ## for Palatino and other serif fonts use:
    #rc('font',**{'family':'serif','serif':['Palatino']})
    rc('text', usetex=True)
    #plt.rc('font', family='serif')
    plt.plot(quantityBuyBefore, priceBuyBefore, label='Demand', alpha=0.6, linewidth = 1.3)
    plt.plot(quantitySellBefore, priceSellBefore, label='Supply (BA)', alpha=0.6, linewidth = 1.3)
    plt.plot(quantitySellAfter, priceSellAfter, label='Supply (AA)', alpha=0.6, linewidth = 1.3)
    ax.legend(loc='upper center')
    ax.set_xlabel('Traded Energy [MWh]')
    ax.set_ylabel('Price [EUR/MWh]')
    plt.title(key)
    #ax.set_ylim(0,250)
    ax.grid()
    #fig.set_size_inches(8, 4.5)
    fig.tight_layout()
    plt.savefig('path' + str(key).replace(' ', '_') + '.pdf', format='pdf')
