# ---------------------
# import packages
# ---------------------

import os
import pandas
import pickle

# ---------------------
# file import section
# ---------------------

# set path to folder where the pickle results from the bid import file are located
path = ''

# import data
dicBuy = pickle.load(open(path + "bid_buy_data.pickle", "rb"))
dicSell = pickle.load(open(path + "bid_sell_data.pickle", "rb"))

# empty dics for final data
dicBuyFinal = {}
dicSellFinal = {}

# buy section
for key in dicBuy:

    # store data frame temporarly
    dfTmp = dicBuy[key]

    # get all resource names of the temporal data frame
    resourceNameFull = dfTmp['Order ID']

    # remove duplicates from list
    resourceNamesEss = list(set(resourceNameFull))

    # for loop to extract data and calculate the difference
    for idx1 in range(len(resourceNamesEss)):
        # extract data frame based on resource name
        dfExTmp = dfTmp.loc[dfTmp['Order ID'] == resourceNamesEss[idx1]]

        # sort data
        dfExTmp = dfExTmp.sort_values(by=['Price', 'Quantity'], ascending=[False, True])

        # reindex the dataframe
        dfExTmp.reset_index(inplace=True, drop='index')

        # create empty list for calculated diferences between bits
        listQuantityDiffTmp = []

        for idx2 in dfExTmp.index:
            # if it is the first value of the extracted data frame, quantity is equal to quantity diff
            if not listQuantityDiffTmp:
                listQuantityDiffTmp.append(dfExTmp['Quantity'][idx2])
            # if not, calculate the difference
            else:
                listQuantityDiffTmp.append(dfExTmp['Quantity'][idx2] - dfExTmp['Quantity'][idx2-1])

        # add calcualted list as columns to extracted data frame
        dfExTmp.insert(5, 'Quantity Difference', listQuantityDiffTmp, True)

        # add data frame to final dictionary
        if idx1 == 0:
            dicBuyFinal[key] = dfExTmp
        else:
            dicBuyFinal[key] = dicBuyFinal[key].append(dfExTmp)

    # sort values
    dicBuyFinal[key] = dicBuyFinal[key].sort_values(by=['Price', 'Quantity'], ascending=[False, True])

    # assign new index
    dicBuyFinal[key].reset_index(inplace=True, drop='index')

    # get temporal data frame to calcualte accumulated difference per step
    dfBuyTmp = dicBuyFinal[key]

    # set counter to zero
    idx2 = 0

    # while loop
    while idx2 <= len(dfBuyTmp)-1:
        if idx2 == 0:
            quantAccBuy = [dfBuyTmp['Quantity Difference'][idx2]]
            idx2 += 1

        else:
            quantAccBuy.append(quantAccBuy[idx2-1] + dfBuyTmp['Quantity Difference'][idx2])
            idx2 += 1

    # add accumualted difference list to df
    dfBuyTmp.insert(6, 'Accumulated Difference', quantAccBuy, True)

    dicBuyFinal[key] = dfBuyTmp

    # assign new index
    dicBuyFinal[key].reset_index(inplace=True, drop='index')


# sell section
for key in dicSell:

    # store data frame temporarly
    dfTmp = dicSell[key]

    dfTmp['Quantity'] = dfTmp['Quantity'] * -1

    # get all resource names of the temporal data frame
    resourceNameFull = dfTmp['Order ID']

    # remove duplicates from list
    resourceNamesEss = list(set(resourceNameFull))

    # for loop to extract data and calculate the difference
    for idx1 in range(len(resourceNamesEss)):
        # extract data frame based on resource name
        dfExTmp = dfTmp.loc[dfTmp['Order ID'] == resourceNamesEss[idx1]]

        # sort data
        dfExTmp = dfExTmp.sort_values(by=['Price', 'Quantity'], ascending=[True, True])

        # reindex the dataframe
        dfExTmp.reset_index(inplace=True, drop='index')

        # create empty list for calculated diferences between bits
        listQuantityDiffTmp = []

        for idx2 in dfExTmp.index:
            # if it is the first value of the extracted data frame, quantity is equal to quantity diff
            if not listQuantityDiffTmp:
                listQuantityDiffTmp.append(dfExTmp['Quantity'][idx2])
            # if not, calculate the difference
            else:
                listQuantityDiffTmp.append(dfExTmp['Quantity'][idx2] - dfExTmp['Quantity'][idx2-1])

        # add calcualted list as columns to extracted data frame
        dfExTmp.insert(5, 'Quantity Difference', listQuantityDiffTmp, True)

        # add data frame to final dictionary
        if idx1 == 0:
            dicSellFinal[key] = dfExTmp
        else:
            dicSellFinal[key] = dicSellFinal[key].append(dfExTmp)

    # sort values
    dicSellFinal[key] = dicSellFinal[key].sort_values(by=['Price', 'Quantity'], ascending=[True, True])

    # assign new index
    dicSellFinal[key].reset_index(inplace=True, drop='index')

    # get temporal data frame to calcualte accumulated difference per step
    dfSellTmp = dicSellFinal[key]

    # set counter to zero
    idx2 = 0

    # while loop
    while idx2 <= len(dfSellTmp)-1:
        if idx2 == 0:
            quantAccSell = [dfSellTmp['Quantity Difference'][idx2]]
            idx2 += 1

        else:
            quantAccSell.append(quantAccSell[idx2-1] + dfSellTmp['Quantity Difference'][idx2])
            idx2 += 1

    # add accumualted difference list to df
    dfSellTmp.insert(6, 'Accumulated Difference', quantAccSell, True)

    dicSellFinal[key] = dfSellTmp

    # assign new index
    dicSellFinal[key].reset_index(inplace=True, drop='index')


# store data
# sell data
pickleSellData = open('path/bid_sell_data_calc.pickle', 'wb')
pickle.dump(dicSellFinal, pickleSellData, protocol=pickle.HIGHEST_PROTOCOL)
# buy data
pickleBuyData = open('path/bid_buy_data_calc.pickle', 'wb')
pickle.dump(dicBuyFinal, pickleBuyData, protocol=pickle.HIGHEST_PROTOCOL)
