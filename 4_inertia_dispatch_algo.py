# ---------------------
# import packages
# ---------------------

import os
import pandas
import datetime
import pickle

# ---------------------
# define function
# ---------------------

# function to find the intersection between two lines
def line_intersect(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2):
    d = (by2 - by1) * (ax2 - ax1) - (bx2 - bx1) * (ay2 - ay1)
    if d:
        uA = ((bx2 - bx1) * (ay1 - by1) - (by2 - by1) * (ax1 - bx1)) / d
        uB = ((ax2 - ax1) * (ay1 - by1) - (ay2 - ay1) * (ax1 - bx1)) / d
    else:
        return

    if (0 <= uA <= 1 and 0 <= uB <= 1):
        x = ax1 + uA * (ax2 - ax1)
        y = ay1 + uA * (ay2 - ay1)
    else:
        return

    return x, y

# function to start the intersection process
def intersec_process(buyDataFrame, sellDataFrame):
    # extract price and quantity data
    priceBuyTmp = buyDataFrame['Price'].tolist()
    quantSumBuyTmp = buyDataFrame['Accumulated Difference'].tolist()
    priceSellTmp = sellDataFrame['Price'].tolist()
    quantSumSellTmp = sellDataFrame['Accumulated Difference'].tolist()

    # create empty lists
    marketBalanceTimeTmp = []
    marketBalancePriceTmp = []
    marketBalanceQuantityTmp = []

    # buy loop
    for i in range(len(priceBuyTmp)-1):
        # sell loop
        for j in range(len(priceSellTmp)-1):
            # buy data
            a = quantSumBuyTmp[i]
            b = priceBuyTmp[i]
            c = quantSumBuyTmp[i+1]
            d = priceBuyTmp[i+1]
            # sell data
            e = quantSumSellTmp[j]
            f = priceSellTmp[j]
            g = quantSumSellTmp[j+1]
            h = priceSellTmp[j+1]

            # call function
            pt = line_intersect(a,b,c,d,e,f,g,h)

            # if return is not None store value in respective list
            if pt is not None:
                marketBalanceTimeTmp.append(key)
                marketBalancePriceTmp.append(pt[1])
                marketBalanceQuantityTmp.append(pt[0])
            else:
                None

    return marketBalanceTimeTmp, marketBalancePriceTmp, marketBalanceQuantityTmp
# ---------------------
# data import
# ---------------------
# set path to folder where the imported is stored
path = 'set path'

# load result files
dicBuy = pickle.load(open(path + "bid_buy_data_calc.pickle", "rb"))
dicSell = pickle.load(open(path + "bid_sell_data_calc.pickle", "rb"))

# ---------------------
# stockholm methodology algorithm
# ---------------------

# set H_min
sysInertiaMin = 23000

# initiate result lists
# before application of algorithm
marketBalanceTimeBeforeAlgo = []
marketBalancePriceBeforeAlgo = []
marketBalanceQuantityBeforeAlgo = []
kinEnergyBeforeAlgo = []
# after application of algorithm
marketBalanceTimeAfterAlgo = []
marketBalancePriceAfterAlgo = []
marketBalanceQuantityAfterAlgo = []
kinEnergyAfterAlgo = []
# dictionary to store the merit order after the application of the algorithm
dicSellAfter = {}


for key in dicSell:
    
    # extract data for test
    dfBuyTmp = dicBuy[key]
    dfSellTmp = dicSell[key]

    # call function to find the intersection of sell and buy bids
    timeTmp, priceTmp, quantityTmp = intersec_process(dfBuyTmp, dfSellTmp)

    # calculate sysInertiaAct
    # extract all sell bids belowe or equalt to balance quanity

    # get all indexes of rows which meet the condition
    indexBalance = dfSellTmp[dfSellTmp['Accumulated Difference'] <= quantityTmp[0]].index

    # get the last index where balance is achieved
    indexMarketBalanceSell = indexBalance[-1]

    # add one to index in order to get all bids within market balance
    indexMarketBalanceSell += 1

    # subset of full sell data frame. Only values of below balance point + 1
    dfSellBalance = dfSellTmp.loc[0:indexMarketBalanceSell]

    # in order to calculate the stored kinetic energy, only those generators acutally delivering are considered, i.e. quantity > 0
    dfSellBalanceSubset = dfSellBalance[dfSellBalance['Quantity'] > 0]

    # get only essence of dfSellTmp, i.e. remove duplicates
    dfSellBalanceSubset = dfSellBalanceSubset.drop_duplicates(subset='Order ID', inplace=False, ignore_index=False)

    # calcualte amount of stored energy in rotating parts
    inertiaAct = []

    # loop to calculate the stored kinetic energy per unit
    for idx in dfSellBalanceSubset.index:
        inertiaAct.append(dfSellBalanceSubset['Capacity'][idx] * dfSellBalanceSubset['Inertia'][idx])

    # calculate the overall system stored kinetic energy
    sysInertiaAct = sum(inertiaAct)

    # store results before the algorithm starts to possibly change the merit order
    marketBalanceTimeBeforeAlgo.append(timeTmp[0])
    marketBalancePriceBeforeAlgo.append(priceTmp[0])
    marketBalanceQuantityBeforeAlgo.append(quantityTmp[0])
    kinEnergyBeforeAlgo.append(sysInertiaAct)

    if sysInertiaAct < sysInertiaMin:


        while sysInertiaAct < sysInertiaMin:

            # apply stockholm algorithm

            #extract all sell bids from units without inertia
            dfSellNoInertia = dfSellBalance[dfSellBalance['Inertia'] == 0]

            # sort extract by price
            dfSellNoInertia = dfSellNoInertia.sort_values(by='Price', ascending=True)

            #get the index of the most expensive sell bid without inertia
            indexSellNoInertia = dfSellNoInertia.index

            try:
                # remove the before found index from the dataframe
                dfSellTmp = dfSellTmp.drop(indexSellNoInertia[-1])
            except IndexError:
                marketBalanceTimeAfterAlgo.append(timeTmp[0])
                marketBalancePriceAfterAlgo.append(None)
                marketBalanceQuantityAfterAlgo.append(None)
                kinEnergyAfterAlgo.append(None)

                dicSellAfter[key] = dfSellTmp
                break

            # reset index
            dfSellTmp.reset_index(inplace=True, drop='index')

            # recalculate acumulated quanity
            idx = 0

            while idx <= len(dfSellTmp)-1:
                if idx == 0:
                    dfSellTmp['Accumulated Difference'][idx] = dfSellTmp['Quantity Difference'][idx]
                    idx += 1
                else:
                    dfSellTmp['Accumulated Difference'][idx] = dfSellTmp['Accumulated Difference'][idx-1] + dfSellTmp['Quantity Difference'][idx]
                    idx += 1

            # call function to find the intersection of the sell and buy bids
            timeTmp, priceTmp, quantityTmp = intersec_process(dfBuyTmp, dfSellTmp)

            # calculate stored system kinetic energy
            # extract all sell bids belowe or equalt to balance quanity
            # get all indexes of rows which meet the condition
            indexBalance = dfSellTmp[dfSellTmp['Accumulated Difference'] <= quantityTmp[0]].index

            # get the last index where balance is achieved
            indexMarketBalanceSell = indexBalance[-1]

            # add one to index in order to get all bids within market balance
            indexMarketBalanceSell += 1

            # subset of full sell data frame. Only values of below balance point + 1
            dfSellBalance = dfSellTmp.loc[0:indexMarketBalanceSell]

            # in order to calculate the stored kinetic energy, only those generators acutally delivering are considered, i.e. quantity > 0
            dfSellBalanceSubset = dfSellBalance[dfSellBalance['Quantity'] > 0]

            # get only essence of dfSellTmp, i.e. remove duplicates
            dfSellBalanceSubset = dfSellBalanceSubset.drop_duplicates(subset='Order ID', inplace=False, ignore_index=False)

            # calcualte amount of stored energy in rotating parts
            inertiaAct = []

            # loop to calculate the stored kinetic energy per unit
            for idx in dfSellBalanceSubset.index:
                inertiaAct.append(dfSellBalanceSubset['Capacity'][idx] * dfSellBalanceSubset['Inertia'][idx])

            # calculate the overall system stored kinetic energy
            sysInertiaAct = sum(inertiaAct)

            if sysInertiaAct < sysInertiaMin:
                None
            else:
                marketBalanceTimeAfterAlgo.append(timeTmp[0])
                marketBalancePriceAfterAlgo.append(priceTmp[0])
                marketBalanceQuantityAfterAlgo.append(quantityTmp[0])
                kinEnergyAfterAlgo.append(sysInertiaAct)

                dicSellAfter[key] = dfSellTmp


    else:
        # store results after application of the algorithm even no changes were made due to sufficient amount of stored kinetic energy
        marketBalanceTimeAfterAlgo.append(timeTmp[0])
        marketBalancePriceAfterAlgo.append(priceTmp[0])
        marketBalanceQuantityAfterAlgo.append(quantityTmp[0])
        kinEnergyAfterAlgo.append(sysInertiaAct)

        dicSellAfter[key] = dfSellTmp

dfResultBeforeAlgo = pandas.DataFrame({'Time': marketBalanceTimeBeforeAlgo,
                                       'Price': marketBalancePriceBeforeAlgo,
                                       'Quantity': marketBalanceQuantityBeforeAlgo,
                                       'Inertia': kinEnergyBeforeAlgo})

dfResultAfterAlgo = pandas.DataFrame({'Time': marketBalanceTimeAfterAlgo,
                                       'Price': marketBalancePriceAfterAlgo,
                                       'Quantity': marketBalanceQuantityAfterAlgo,
                                       'Inertia': kinEnergyAfterAlgo})

dfResultBeforeAlgo.to_csv('path/results_before.csv', sep=';')

dfResultAfterAlgo.to_csv('path/results_after.csv', sep=';')


pickleSellData = open('path/bid_sell_data_after_algo.pickle', 'wb')
pickle.dump(dicSellAfter, pickleSellData, protocol=pickle.HIGHEST_PROTOCOL)
