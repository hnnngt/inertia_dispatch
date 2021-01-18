# ---------------------
# file import section
# ---------------------

# set pathes
# path to bid files location
pathFolderBidFiles = 'beta/BidFiles/'

# set path to registered unit file
fileRegUnits = 'Reg_Units_Modified.csv'

# set path to where market results are located
pathFolderMarketResults = 'beta/MarketResults/'

# data import section
# import data of registered units
dataRegUnits = pandas.read_csv(pathData + fileRegUnits, sep=';')

# market result import
# create a list of files to be imported
listFilesMarketResults = os.listdir(pathData + pathFolderMarketResults)

#create empty list where auction date and exchange rate is stored
auctionDateMarketResults = []
exchangeRateMarketResults = []
tradingHourMarketResults = []
netPositionMarketResults = []

# import loop
for i in listFilesMarketResults:
    # full path to each individual file in pathFolder
    fullPathMarketResults = pathData + pathFolderMarketResults + i

    # open file
    fileMarketResultsTmp = open(fullPathMarketResults)

    # read all lines of file
    fileMarketResultsTmp = fileMarketResultsTmp.readlines()

    # extract line three of the imported file and sperate the cells
    lineThreeTmp = fileMarketResultsTmp[2].split(';')

    # extract the second cell
    auctionDateTmp = lineThreeTmp[1]

    # convert string to datetime
    auctionDateTmp = datetime.datetime.strptime(auctionDateTmp, '%Y-%m-%dT%H:%M:%SZ\n')

    # add temporal data to final list
    auctionDateMarketResults.append(auctionDateTmp)

    # extract line five of imported file and seperate cells
    lineFiveTmp = fileMarketResultsTmp[4].split(';')

    # extract exchange rate and convert info to float
    exchangeRateTmp = float(lineFiveTmp[2].replace(',', '.'))

    # append temporal info to final list
    exchangeRateMarketResults.append(exchangeRateTmp)

    # get time info ni
    netPositionTimeNi = fileMarketResultsTmp[16].split(';')

    # get value line ni
    netPostitionValueNi = fileMarketResultsTmp[17].split(';')

    # get value line ni
    netPostitionValueRoi = fileMarketResultsTmp[38].split(';')

    #set index value
    colIdx = 0

    while netPositionTimeNi[colIdx] != None:

        # save time info
        tradingHourMarketResults.append(datetime.datetime.strptime(netPositionTimeNi[colIdx], '%Y-%m-%dT%H:%M:%SZ'))

        # save net position value
        netPositionMarketResults.append(float(netPostitionValueNi[colIdx].replace(',', '.')) + float(netPostitionValueRoi[colIdx].replace(',', '.')))

        # index + 1
        colIdx += 1

        if colIdx == len(netPositionTimeNi)-1:
            break



# create a list of all bid files
listBidFiles = os.listdir(pathData + pathFolderBidFiles)

# create dictionaries to store all final results. One for buy bids and one for sell bids
dicBidDataSell = {}
dicBidDataBuy = {}

# loop import
for i in listBidFiles:
    # full path to each individual file in pathFolder
    fullBidFilePath = pathData + pathFolderBidFiles + i

    # import data as data frame
    dataTmp = pandas.read_csv(fullBidFilePath,
                              header=None,
                              sep='\n')

    # seperate data frame based on seperator
    dataTmp = dataTmp[0].str.split(';', expand=True)

    # replace empty cells with the string 'nan'
    dataTmp.replace('', 'nan', inplace=True)

# ---------------------
# data restructuring section; data is structured into single lists; inertia allocation and final restructuring into a dictionary
# ---------------------

    # create empty lists to store data temporarly
    listResourceName = []
    listPrice = []
    listQuantity = []
    listTime = []
    listCapacity = []
    listOrderId = []
    listOrderType = []
    listFuelType = []

    for idx1 in dataTmp.index:

        # find the necessary information regarding the resource name and the currency of the the bid. If the bid was made in GBP, an exhange rate is applied to convert the bid into EURO
        if dataTmp[0][idx1] == 'Auction date time':

            # get auction date info
            auctionDateTmp = dataTmp[1][idx1]

            # convert str to datetime.datetime
            auctionDateTmp = datetime.datetime.strptime(auctionDateTmp, '%Y-%m-%dT%H:%M:%SZ')

            # find exchange rate for respective auction date
            for idx2 in range(len(auctionDateMarketResults)):
                if auctionDateMarketResults[idx2] == auctionDateTmp:
                    exchangeRateTmp = exchangeRateMarketResults[idx2]
                else:
                    None

        elif dataTmp[0][idx1] == 'PO':
            # set temporal resource Name
            resourceNameTmp = dataTmp[2][idx1]
            # find inertia and capacity info from registered unit list
            for idx2 in dataRegUnits.index:
                # if resouce name is found in both files
                if resourceNameTmp == dataRegUnits['Resource Name'][idx2]:
                    capacityTmp =  dataRegUnits['Installed Capacity'][idx2]
                    fuelTypeTmp = dataRegUnits['Fuel Type'][idx2]
                # if name is not found in loop due to index
                elif resourceNameTmp != dataRegUnits['Resource Name'][idx2]:
                    None
                # if no match was found
                else:
                    capacityTmp = 0

            # set exchange rate if necessary
            if dataTmp[5][idx1] == 'GBP':
                exchangeRate = exchangeRateTmp

            else:
                exchangeRate = 1

        # get order ID in case order is a simple order (SL)
        elif dataTmp[0][idx1] == 'SL':
            orderIdTmp = dataTmp[1][idx1]
            orderTypeTmp = 'SL'
            activationIndex = 1

        # get order IDin case order is a complex order (SC)
        elif dataTmp[0][idx1] == 'SC':
            orderIdTmp = dataTmp[1][idx1]
            orderTypeTmp = 'SC'
            activationIndex = float(dataTmp[18][idx1])

        # get the price information
        elif dataTmp[0][idx1] == 'PR':

            # create empty temporal list to store prices
            listPriceTmp = []
            colIdx = 5

            # get the prices and store them into a temporal list until the cell contains a nan
            while dataTmp[colIdx][idx1] is not None:
                listPriceTmp.append(dataTmp[colIdx][idx1])
                colIdx += 1

                # break condition if price list ends with length of columns
                if colIdx == dataTmp.shape[1]:
                    break

        # get quantities from dataTmp and necessary time information
        elif dataTmp[0][idx1] == 'VL' and activationIndex == 1 and dataTmp[3][idx1] == 'Y':
            # get time information
            time = datetime.datetime.strptime(dataTmp[1][idx1], '%Y-%m-%dT%H:%M:%SZ')

            # store resource name, time information, quantity and price in lists
            for idx2 in range(5,len(listPriceTmp) + 5):
                if str(dataTmp[idx2][idx1]) != 'nan':
                    # time
                    listTime.append(time)
                    # resource name
                    listResourceName.append(resourceNameTmp)
                    # order ID
                    listOrderId.append(orderIdTmp)
                    # order type
                    listOrderType.append(orderTypeTmp)
                    # fuel type
                    listFuelType.append(fuelTypeTmp)
                    # generator capacity
                    listCapacity.append(capacityTmp)
                    # bidding price
                    listPrice.append(float(listPriceTmp[idx2-5].replace(',','.'))/exchangeRate)
                    # quantity
                    listQuantity.append(float(dataTmp[idx2][idx1].replace(',','.')))
                else:
                    None

    # section to find gaps in quantity bis from sell to buy without zeros bids
    # store previous lists into a data frame
    dfTmp = pandas.DataFrame({'Time': listTime,
                              'Name': listResourceName,
                              'Order ID': listOrderId,
                              'Order Type': listOrderType,
                              'Capacity': listCapacity,
                              'Price': listPrice,
                              'Quantity': listQuantity,
                              'Fuel Type': listFuelType})

    # create empty lists to store results at the end of the loop
    listTime = []
    listResourceName = []
    listOrderId = []
    listOrderType = []
    listCapacity = []
    listPrice = []
    listQuantity = []
    listFuelType = []

    # get order id
    orderIdEss = list(set(dfTmp['Order ID']))

    # for loop
    for idx1 in orderIdEss:
        # extract data
        dfTmpEss = dfTmp.loc[dfTmp['Order ID'] == idx1]

        # reindex data frame
        dfTmpEss.reset_index(inplace=True, drop='index')

        # for loop
        for idx2 in range(len(dfTmpEss)-1):
            if dfTmpEss['Quantity'][idx2] < 0 and dfTmpEss['Quantity'][idx2+1] > 0 and str(dfTmpEss['Time'][idx2]) == str(dfTmpEss['Time'][idx2+1]):
                # orig data
                listResourceName.append(dfTmpEss['Name'][idx2])
                listPrice.append(dfTmpEss['Price'][idx2])
                listQuantity.append(dfTmpEss['Quantity'][idx2])
                listTime.append(dfTmpEss['Time'][idx2])
                listCapacity.append(dfTmpEss['Capacity'][idx2])
                listOrderId.append(dfTmpEss['Order ID'][idx2])
                listOrderType.append(dfTmpEss['Order Type'][idx2])
                listFuelType.append(dfTmpEss['Fuel Type'][idx2])
                # include quantity zero bid
                listResourceName.append(dfTmpEss['Name'][idx2])
                listPrice.append(dfTmpEss['Price'][idx2])
                listQuantity.append(0)
                listTime.append(dfTmpEss['Time'][idx2])
                listCapacity.append(dfTmpEss['Capacity'][idx2])
                listOrderId.append(dfTmpEss['Order ID'][idx2])
                listOrderType.append(dfTmpEss['Order Type'][idx2])
                listFuelType.append(dfTmpEss['Fuel Type'][idx2])
                listResourceName.append(dfTmpEss['Name'][idx2])
                listPrice.append(dfTmpEss['Price'][idx2])
                listQuantity.append(0)
                listTime.append(dfTmpEss['Time'][idx2])
                listCapacity.append(dfTmpEss['Capacity'][idx2])
                listOrderId.append(dfTmpEss['Order ID'][idx2])
                listOrderType.append(dfTmpEss['Order Type'][idx2])
                listFuelType.append(dfTmpEss['Fuel Type'][idx2])
            elif dfTmpEss['Quantity'][idx2] > 0 and dfTmpEss['Quantity'][idx2+1] < 0 and str(dfTmpEss['Time'][idx2]) == str(dfTmpEss['Time'][idx2+1]):
                # orig data
                listResourceName.append(dfTmpEss['Name'][idx2])
                listPrice.append(dfTmpEss['Price'][idx2])
                listQuantity.append(dfTmpEss['Quantity'][idx2])
                listTime.append(dfTmpEss['Time'][idx2])
                listCapacity.append(dfTmpEss['Capacity'][idx2])
                listOrderId.append(dfTmpEss['Order ID'][idx2])
                listOrderType.append(dfTmpEss['Order Type'][idx2])
                listFuelType.append(dfTmpEss['Fuel Type'][idx2])
                # include quantity zero bid
                listResourceName.append(dfTmpEss['Name'][idx2])
                listPrice.append(dfTmpEss['Price'][idx2])
                listQuantity.append(0)
                listTime.append(dfTmpEss['Time'][idx2])
                listCapacity.append(dfTmpEss['Capacity'][idx2])
                listOrderId.append(dfTmpEss['Order ID'][idx2])
                listOrderType.append(dfTmpEss['Order Type'][idx2])
                listFuelType.append(dfTmpEss['Fuel Type'][idx2])
                listResourceName.append(dfTmpEss['Name'][idx2])
                listPrice.append(dfTmpEss['Price'][idx2])
                listQuantity.append(0)
                listTime.append(dfTmpEss['Time'][idx2])
                listCapacity.append(dfTmpEss['Capacity'][idx2])
                listOrderId.append(dfTmpEss['Order ID'][idx2])
                listOrderType.append(dfTmpEss['Order Type'][idx2])
                listFuelType.append(dfTmpEss['Fuel Type'][idx2])
            else:
                listResourceName.append(dfTmpEss['Name'][idx2])
                listPrice.append(dfTmpEss['Price'][idx2])
                listQuantity.append(dfTmpEss['Quantity'][idx2])
                listTime.append(dfTmpEss['Time'][idx2])
                listCapacity.append(dfTmpEss['Capacity'][idx2])
                listOrderId.append(dfTmpEss['Order ID'][idx2])
                listOrderType.append(dfTmpEss['Order Type'][idx2])
                listFuelType.append(dfTmpEss['Fuel Type'][idx2])
            # if the second to last idx store the last values
            if idx2 == len(dfTmpEss)-1:
                listResourceName.append(dfTmpEss['Name'][idx2+1])
                listPrice.append(dfTmpEss['Price'][idx2+1])
                listQuantity.append(dfTmpEss['Quantity'][idx2+1])
                listTime.append(dfTmpEss['Time'][idx2+1])
                listCapacity.append(dfTmpEss['Capacity'][idx2+1])
                listOrderId.append(dfTmpEss['Order ID'][idx2+1])
                listOrderType.append(dfTmpEss['Order Type'][idx2+1])
                listFuelType.append(dfTmpEss['Fuel Type'][idx2+1])
            else:
                None

    # create empty lists to store data temporarly. Either for buy and sell orders seperatly
    # buy lists
    listBuyResourceName = []
    listBuyPrice = []
    listBuyQuantity = []
    listBuyTime = []
    listBuyCapacity = []
    listBuyOrderId = []
    listBuyOrderType = []
    listBuyFuelType = []

    #sell lists
    listSellResourceName = []
    listSellPrice = []
    listSellQuantity = []
    listSellTime = []
    listSellCapacity = []
    listSellOrderId = []
    listSellOrderType = []
    listSellFuelType = []

    # seperate buy and sell orders and store data into lists
    for idx1 in range(len(listQuantity)-1):
        if listQuantity[idx1] < 0:
            listSellResourceName.append(listResourceName[idx1])
            listSellPrice.append(listPrice[idx1])
            listSellQuantity.append(listQuantity[idx1])
            listSellTime.append(listTime[idx1])
            listSellCapacity.append(listCapacity[idx1])
            listSellOrderId.append(listOrderId[idx1])
            listSellOrderType.append(listOrderType[idx1])
            listSellFuelType.append(listFuelType[idx1])
        elif listQuantity[idx1] > 0:
            listBuyResourceName.append(listResourceName[idx1])
            listBuyPrice.append(listPrice[idx1])
            listBuyQuantity.append(listQuantity[idx1])
            listBuyTime.append(listTime[idx1])
            listBuyCapacity.append(listCapacity[idx1])
            listBuyOrderId.append(listOrderId[idx1])
            listBuyOrderType.append(listOrderType[idx1])
            listBuyFuelType.append(listFuelType[idx1])
        else:
            # for all zero bids
            # if the very first bid is zero in first row with bids
            if idx1 == 0:
                idx2 = idx1 + 1
                # go forwards in indexing until you get a number
                while idx2 <= len(listQuantity)-1:
                    if listQuantity[idx2] == 0:
                        idx2 += 1
                    else:
                        # if forward number is below zero
                        if listQuantity[idx2] < 0:
                            listSellResourceName.append(listResourceName[idx1])
                            listSellPrice.append(listPrice[idx1])
                            listSellQuantity.append(listQuantity[idx1])
                            listSellTime.append(listTime[idx1])
                            listSellCapacity.append(listCapacity[idx1])
                            listSellOrderId.append(listOrderId[idx1])
                            listSellOrderType.append(listOrderType[idx1])
                            listSellFuelType.append(listFuelType[idx1])
                        # if forward number is above zero
                        else:
                            listBuyResourceName.append(listResourceName[idx1])
                            listBuyPrice.append(listPrice[idx1])
                            listBuyQuantity.append(listQuantity[idx1])
                            listBuyTime.append(listTime[idx1])
                            listBuyCapacity.append(listCapacity[idx1])
                            listBuyOrderId.append(listOrderId[idx1])
                            listBuyOrderType.append(listOrderType[idx1])
                            listBuyFuelType.append(listFuelType[idx1])
                        break
            elif idx1 == 1:
                idx2 = idx1 + 1
                # go forwards in indexing until you get a number
                while idx2 <= len(listQuantity)-1:
                    if listQuantity[idx2] == 0:
                        idx2 += 1
                    else:
                        # if forward number is below zero
                        if listQuantity[idx2] < 0:
                            listSellResourceName.append(listResourceName[idx1])
                            listSellPrice.append(listPrice[idx1])
                            listSellQuantity.append(listQuantity[idx1])
                            listSellTime.append(listTime[idx1])
                            listSellCapacity.append(listCapacity[idx1])
                            listSellOrderId.append(listOrderId[idx1])
                            listSellOrderType.append(listOrderType[idx1])
                            listSellFuelType.append(listFuelType[idx1])
                        # if forward number is above zero
                        else:
                            listBuyResourceName.append(listResourceName[idx1])
                            listBuyPrice.append(listPrice[idx1])
                            listBuyQuantity.append(listQuantity[idx1])
                            listBuyTime.append(listTime[idx1])
                            listBuyCapacity.append(listCapacity[idx1])
                            listBuyOrderId.append(listOrderId[idx1])
                            listBuyOrderType.append(listOrderType[idx1])
                            listBuyFuelType.append(listFuelType[idx1])
                        break
            # for every other row
            else:
                # calculate the time difference of the idx time and the previos time step
                # if difference is not zero, do the same as in the above section (with the while loop)
                if listTime[idx1].hour - listTime[idx1-1].hour != 0:
                    idx2 = idx1 + 1
                    while idx2 <= len(listQuantity)-1:
                        if listQuantity[idx2] == 0:
                            idx2 += 1
                        else:
                            if listQuantity[idx2] < 0:
                                listSellResourceName.append(listResourceName[idx1])
                                listSellPrice.append(listPrice[idx1])
                                listSellQuantity.append(listQuantity[idx1])
                                listSellTime.append(listTime[idx1])
                                listSellCapacity.append(listCapacity[idx1])
                                listSellOrderId.append(listOrderId[idx1])
                                listSellOrderType.append(listOrderType[idx1])
                                listSellFuelType.append(listFuelType[idx1])
                            else:
                                listBuyResourceName.append(listResourceName[idx1])
                                listBuyPrice.append(listPrice[idx1])
                                listBuyQuantity.append(listQuantity[idx1])
                                listBuyTime.append(listTime[idx1])
                                listBuyCapacity.append(listCapacity[idx1])
                                listBuyOrderId.append(listOrderId[idx1])
                                listBuyOrderType.append(listOrderType[idx1])
                                listBuyFuelType.append(listFuelType[idx1])
                            break
                elif listTime[idx1].hour - listTime[idx1-2].hour != 0:
                    idx2 = idx1 + 1
                    while idx2 <= len(listQuantity)-1:
                        if listQuantity[idx2] == 0:
                            idx2 += 1
                        else:
                            if listQuantity[idx2] < 0:
                                listSellResourceName.append(listResourceName[idx1])
                                listSellPrice.append(listPrice[idx1])
                                listSellQuantity.append(listQuantity[idx1])
                                listSellTime.append(listTime[idx1])
                                listSellCapacity.append(listCapacity[idx1])
                                listSellOrderId.append(listOrderId[idx1])
                                listSellOrderType.append(listOrderType[idx1])
                                listSellFuelType.append(listFuelType[idx1])
                            else:
                                listBuyResourceName.append(listResourceName[idx1])
                                listBuyPrice.append(listPrice[idx1])
                                listBuyQuantity.append(listQuantity[idx1])
                                listBuyTime.append(listTime[idx1])
                                listBuyCapacity.append(listCapacity[idx1])
                                listBuyOrderId.append(listOrderId[idx1])
                                listBuyOrderType.append(listOrderType[idx1])
                                listBuyFuelType.append(listFuelType[idx1])
                            break
                # look at the previous values
                else:
                    # if previous value is below zero
                    if listQuantity[idx1 - 1] > 0:
                        listBuyResourceName.append(listResourceName[idx1])
                        listBuyPrice.append(listPrice[idx1])
                        listBuyQuantity.append(listQuantity[idx1])
                        listBuyTime.append(listTime[idx1])
                        listBuyCapacity.append(listCapacity[idx1])
                        listBuyOrderId.append(listOrderId[idx1])
                        listBuyOrderType.append(listOrderType[idx1])
                        listBuyFuelType.append(listFuelType[idx1])
                    elif listQuantity[idx1 - 2] > 0 and listQuantity[idx1 + 1] < 0 and listTime[idx1].hour - listTime[idx1 + 1].hour == 0:
                        listSellResourceName.append(listResourceName[idx1])
                        listSellPrice.append(listPrice[idx1])
                        listSellQuantity.append(listQuantity[idx1])
                        listSellTime.append(listTime[idx1])
                        listSellCapacity.append(listCapacity[idx1])
                        listSellOrderId.append(listOrderId[idx1])
                        listSellOrderType.append(listOrderType[idx1])
                        listSellFuelType.append(listFuelType[idx1])
                    # if previous value is above zero
                    else:
                        listBuyResourceName.append(listResourceName[idx1])
                        listBuyPrice.append(listPrice[idx1])
                        listBuyQuantity.append(listQuantity[idx1])
                        listBuyTime.append(listTime[idx1])
                        listBuyCapacity.append(listCapacity[idx1])
                        listBuyOrderId.append(listOrderId[idx1])
                        listBuyOrderType.append(listOrderType[idx1])
                        listBuyFuelType.append(listFuelType[idx1])

    # combine lists to data frame in order to sort by time info
    sellDataFrame = pandas.DataFrame({'Time': listSellTime,
                                      'Name': listSellResourceName,
                                      'Order ID': listSellOrderId,
                                      'Order Type': listSellOrderType,
                                      'Quantity': listSellQuantity,
                                      'Price': listSellPrice,
                                      'Capacity': listSellCapacity,
                                      'Fuel Type': listSellFuelType}).sort_values(by=['Time'])

    buyDataFrame = pandas.DataFrame({'Time': listBuyTime,
                                     'Name': listBuyResourceName,
                                     'Order ID': listBuyOrderId,
                                     'Order Type': listBuyOrderType,
                                     'Quantity': listBuyQuantity,
                                     'Price': listBuyPrice,
                                     'Capacity': listBuyCapacity,
                                     'Fuel Type': listBuyFuelType}).sort_values(by=['Time'])

    # create a time series which will later be used as keys in the final dictionary
    timeSeries = pandas.date_range(start=min(sellDataFrame['Time']),
                                   end=max(sellDataFrame['Time']),
                                   freq='H')

    # sell data
    # allocate and store data frame data based on trading period
    for idx1 in range(len(timeSeries)):
        # for every idx1 create a new empty temporal dictionary
        dicBidDataSellTmp = {str(timeSeries[idx1]): None}

        # for loop to allocate data from data frame
        for idx2 in sellDataFrame.index:
            if timeSeries[idx1] == sellDataFrame['Time'][idx2] and dicBidDataSellTmp[str(timeSeries[idx1])] is None:
                dicBidDataSellTmp[str(timeSeries[idx1])] = sellDataFrame.loc[[idx2]]
            elif timeSeries[idx1] == sellDataFrame['Time'][idx2] and dicBidDataSellTmp[str(timeSeries[idx1])] is not None:
                dicBidDataSellTmp[str(timeSeries[idx1])] = dicBidDataSellTmp[str(timeSeries[idx1])].append(sellDataFrame.loc[[idx2]])
            else:
                None

        # add temporal dict to final dictionry
        dicBidDataSell.update(dicBidDataSellTmp)

    # buy data
    # allocate and store data frame data based on trading period
    for idx1 in range(len(timeSeries)):
        # for every idx1 create a new empty temporal dictionary
        dicBidDataBuyTmp = {str(timeSeries[idx1]): None}

        # for loop to allocate data from data frame
        for idx2 in buyDataFrame.index:
            if timeSeries[idx1] == buyDataFrame['Time'][idx2] and dicBidDataBuyTmp[str(timeSeries[idx1])] is None:
                dicBidDataBuyTmp[str(timeSeries[idx1])] = buyDataFrame.loc[[idx2]]
            elif timeSeries[idx1] == buyDataFrame['Time'][idx2] and dicBidDataBuyTmp[str(timeSeries[idx1])] is not None:
                dicBidDataBuyTmp[str(timeSeries[idx1])] = dicBidDataBuyTmp[str(timeSeries[idx1])].append(buyDataFrame.loc[[idx2]])
            else:
                None

        # add temporal dict to final dictionry
        dicBidDataBuy.update(dicBidDataBuyTmp)

        # add net position volume

# inclide net position from market results
for key in  dicBidDataBuy:
    for idx1 in range(len(tradingHourMarketResults)):
        if key == str(tradingHourMarketResults[idx1]) and netPositionMarketResults[idx1] < 0:
            dicBidDataSell[key] = dicBidDataSell[key].append(pandas.DataFrame({'Time': [tradingHourMarketResults[idx1]],
                                                         'Name': ['Net Position'],
                                                         'Order ID': [12345],
                                                         'Order Type': ['NP'],
                                                         'Quantity': [netPositionMarketResults[idx1]],
                                                         'Price': [-500],
                                                         'Capacity': [0],
                                                         'Fuel Type': ['Net Position']}))
            dicBidDataSell[key] = dicBidDataSell[key].append(pandas.DataFrame({'Time': [tradingHourMarketResults[idx1]],
                                                         'Name': ['Net Position'],
                                                         'Order ID': [12345],
                                                         'Order Type': ['NP'],
                                                         'Quantity': [netPositionMarketResults[idx1]],
                                                         'Price': [3000],
                                                         'Capacity': [0],
                                                         'Fuel Type': ['Net Position']}))
        elif key == str(tradingHourMarketResults[idx1]) and netPositionMarketResults[idx1] > 0:
            dicBidDataBuy[key] = dicBidDataBuy[key].append(pandas.DataFrame({'Time': [tradingHourMarketResults[idx1]],
                                                         'Name': ['Net Position'],
                                                         'Order ID': [12345],
                                                         'Order Type': ['NP'],
                                                         'Quantity': [netPositionMarketResults[idx1]],
                                                         'Price': [-500],
                                                         'Capacity': [0],
                                                         'Fuel Type': ['Net Position']}))
            dicBidDataBuy[key] = dicBidDataBuy[key].append(pandas.DataFrame({'Time': [tradingHourMarketResults[idx1]],
                                                         'Name': ['Net Position'],
                                                         'Order ID': [12345],
                                                         'Order Type': ['NP'],
                                                         'Quantity': [netPositionMarketResults[idx1]],
                                                         'Price': [3000],
                                                         'Capacity': [0],
                                                         'Fuel Type': ['Net Position']}))

# store data
# sell data
pickleSellData = open(pathData + 'beta/Results/bid_sell_data.pickle', 'wb')
pickle.dump(dicBidDataSell, pickleSellData, protocol=pickle.HIGHEST_PROTOCOL)
# buy data
pickleBuyData = open(pathData + 'beta/Results/bid_buy_data.pickle', 'wb')
pickle.dump(dicBidDataBuy, pickleBuyData, protocol=pickle.HIGHEST_PROTOCOL)

# print message
print('import bid files successfull')
