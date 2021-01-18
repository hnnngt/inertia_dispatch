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

def wind_speed_height(windSpeed,heightStation):
    windSpeedNewHeight = windSpeed*((math.log(80/0.03)/math.log(heightStation/0.03)))
    return windSpeedNewHeight

# create interpolate 1-D functions
windPowerInterpol = interp1d(windVsPower['wind'],
                             windVsPower['power PU'])
speedPowerInterpol = interp1d(speedPuVspower['Ppu'],
                              speedPuVspower['SpeedPu'])
speedVarHInterpol = interp1d(speedPuVsVarH['speed PU'],
                             speedPuVsVarH['var H'])

# set up scenarios
scenKinEnergy = [kinEnergyTso * (1-inertiaPowerConsumers/100), kinEnergyTso]
scenKinEnergyName = ['kinEnerLow', 'kinEnerHigh']
scenSynWind = [syntheticInertiaWind, 0]
scenSynWindName = ['SI', 'nonSI']
scenInertia = pandas.DataFrame({'biomass': inertiaConstantBiomass,
                                'hardCoal': inertiaConstantHardCoal,
                                'distillate': inertiaConstantDistillate,
                                'fossilGas': inertiaConstantFossilGas,
                                'hydro': inertiaConstantHydro,
                                'fossilOil': inertiaConstantFossilOil,
                                'fossilPeat': inertiaConstantFossilPeat,
                                'pumpStorage': inertiaConstantPumpStorage})
scenInertiaName = ['inertiaMin', 'inertiaMax']

for idxKinEnergy in range(0, len(scenKinEnergy)):
    for idxInertia in range(0, len(scenInertia)):
        for idxSynWind in range(0, len(scenSynWind)):

            # ---------------------
            # stockholm methodology algorithm
            # ---------------------

            # initiate result lists
            # before application of algorithm
            marketBalanceTimeBeforeAlgo = []
            marketBalancePriceBeforeAlgo = []
            marketBalanceQuantityBeforeAlgo = []
            kinEnergyBeforeAlgo = []
            kinEnergyEntsoBeforeAlgo = []
            kinEnergyRemainBeforeAlgo = []
            # after application of algorithm
            marketBalanceTimeAfterAlgo = []
            marketBalancePriceAfterAlgo = []
            marketBalanceQuantityAfterAlgo = []
            kinEnergyAfterAlgo = []
            kinEnergyEntsoAfterAlgo = []
            kinEnergyRemainAfterAlgo = []
            # dictionary to store the merit order after the application of the algorithm
            dicSellAfter = {}

            # create scenario name
            scenNameFull = scenKinEnergyName[idxKinEnergy] + '_' + scenInertiaName[idxInertia] + '_' + scenSynWindName[idxSynWind]
            print('Scenario: ' + scenNameFull)

            for key in dicBuyFinal:

                print('Trading Period: ' + str(key))
                # extract data for test
                dfBuyTmp = dicBuyFinal[key]
                dfSellTmp = dicSellFinal[key]
                # ----------------------
                # allocate inertia const
                # ----------------------

                dfBuyTmp = dfBuyTmp.reset_index()
                dfSellTmp = dfSellTmp.reset_index()

                listInertiaConst = [0] * len(dfSellTmp)
                # allocate inertia constant
                for idxInertiaAllocate in dfSellTmp.index:
                    if dfSellTmp.loc[idxInertiaAllocate, 'Fuel Type'] == 'BIOMASS':
                        listInertiaConst[idxInertiaAllocate] = scenInertia.loc[idxInertia, 'biomass']
                    elif dfSellTmp.loc[idxInertiaAllocate, 'Fuel Type'] == 'COAL':
                        listInertiaConst[idxInertiaAllocate] = scenInertia.loc[idxInertia, 'hardCoal']
                    elif dfSellTmp.loc[idxInertiaAllocate, 'Fuel Type'] == 'DISTILLATE':
                        listInertiaConst[idxInertiaAllocate] = scenInertia.loc[idxInertia, 'distillate']
                    elif dfSellTmp.loc[idxInertiaAllocate, 'Fuel Type'] == 'GAS':
                        listInertiaConst[idxInertiaAllocate] = scenInertia.loc[idxInertia, 'fossilGas']
                    elif dfSellTmp.loc[idxInertiaAllocate, 'Fuel Type'] == 'HYDRO':
                        listInertiaConst[idxInertiaAllocate] = scenInertia.loc[idxInertia, 'hydro']
                    elif dfSellTmp.loc[idxInertiaAllocate, 'Fuel Type'] == 'MULTI_FUEL':
                        listInertiaConst[idxInertiaAllocate] = scenInertia.loc[idxInertia, 'fossilGas']
                    elif dfSellTmp.loc[idxInertiaAllocate, 'Fuel Type'] == 'oil':
                        listInertiaConst[idxInertiaAllocate] = scenInertia.loc[idxInertia, 'fossilOil']
                    elif dfSellTmp.loc[idxInertiaAllocate, 'Fuel Type'] == 'PEAT':
                        listInertiaConst[idxInertiaAllocate] = scenInertia.loc[idxInertia, 'fossilPeat']
                    elif dfSellTmp.loc[idxInertiaAllocate, 'Fuel Type'] == 'PUMP_STORAGE':
                        listInertiaConst[idxInertiaAllocate] = scenInertia.loc[idxInertia, 'pumpStorage']
                    else:
                        None

                # add inertia const to sell df
                dfSellTmp['Inertia'] = listInertiaConst

                # calculate potential stored kinetic energy
                listKinEnergy = [0] * len(dfSellTmp)

                # calculate stored kinetic energy
                for idxKinEnergySell in dfSellTmp.index:
                    listKinEnergy[idxKinEnergySell] = dfSellTmp.loc[idxKinEnergySell, 'Inertia'] * dfSellTmp.loc[idxKinEnergySell, 'Capacity']

                # add inertia const to sell df
                dfSellTmp['Kinetic Energy'] = listKinEnergy

                # -----------------------------------------
                # calculate remaining needed kinetic energy
                # -----------------------------------------

                # data subset
                dataEntsoEirGridSubset = dataEntsoEirGrid[dataEntsoEirGrid['DateTime'] == key]
                dataEntsoEirGridSubset = dataEntsoEirGridSubset.reset_index()

                # create list to inertia constant
                listInertia = [0] * len(dataEntsoEirGridSubset)

                # loop to allocate inertia constant
                for idxEntso in dataEntsoEirGridSubset.index:
                    if dataEntsoEirGridSubset.loc[idxEntso, 'ProductionTypeName'] == 'Fossil Hard coal':
                        listInertia[idxEntso] = scenInertia.loc[idxInertia, 'hardCoal']
                    elif dataEntsoEirGridSubset.loc[idxEntso, 'ProductionTypeName'] == 'Fossil Gas':
                        listInertia[idxEntso] = scenInertia.loc[idxInertia, 'fossilGas']
                    elif dataEntsoEirGridSubset.loc[idxEntso, 'ProductionTypeName'] == 'Fossil Oil':
                        listInertia[idxEntso] = scenInertia.loc[idxInertia, 'fossilOil']
                    elif dataEntsoEirGridSubset.loc[idxEntso, 'ProductionTypeName'] == 'Fossil Peat':
                        listInertia[idxEntso] = scenInertia.loc[idxInertia, 'fossilPeat']
                    elif dataEntsoEirGridSubset.loc[idxEntso, 'ProductionTypeName'] == 'Hydro Pumped Storage':
                        listInertia[idxEntso] = scenInertia.loc[idxInertia, 'pumpStorage']
                    elif dataEntsoEirGridSubset.loc[idxEntso, 'ProductionTypeName'] == 'Hydro Run-of-river and poundage':
                        listInertia[idxEntso] = scenInertia.loc[idxInertia, 'hydro']
                    elif dataEntsoEirGridSubset.loc[idxEntso, 'ProductionTypeName'] == 'Other':
                        listInertia[idxEntso] = scenInertia.loc[idxInertia, 'distillate']
                    else:
                        None

                # add inertia constant to data frame
                dataEntsoEirGridSubset['InertiaConstant'] = listInertia

                # create list to store kinetic energy
                listKinEnergy = [0] * len(dataEntsoEirGridSubset)

                # calculate the potential stored kinetic energy
                for idxEntsoKinEn in dataEntsoEirGridSubset.index:
                    if dataEntsoEirGridSubset['ActualGenerationOutput'][idxEntsoKinEn] > 0:
                        listKinEnergy[idxEntsoKinEn] = dataEntsoEirGridSubset['InstalledGenCapacity'][idxEntsoKinEn] * dataEntsoEirGridSubset['InertiaConstant'][idxEntsoKinEn]
                    else:
                        None

                # append list kinetic energy constant to data frame
                dataEntsoEirGridSubset['KineticEnergy'] = listKinEnergy

                # list names
                namesResourceEirGridSubset = [None] * len(dataEntsoEirGridSubset)

                for idxEirGridSubset in dataEntsoEirGridSubset.index:
                    for idxConverter in converterEntso.index:
                        if dataEntsoEirGridSubset['PowerSystemResourceName'][idxEirGridSubset] == converterEntso['Name ENTSO-E'][idxConverter]:
                            namesResourceEirGridSubset[idxEirGridSubset] = converterEntso['Resource Name'][idxConverter]
                        else:
                            None

                dataEntsoEirGridSubset['ResourceName'] = namesResourceEirGridSubset

                # go through sell and entso data and set kin energy to zero
                for idx1 in dataEntsoEirGridSubset.index:
                    for idx2 in dfSellTmp.index:
                        if dataEntsoEirGridSubset['ResourceName'][idx1] == dfSellTmp['Name'][idx2]:
                            dataEntsoEirGridSubset.loc[idx1, 'KineticEnergy'] = 0
                        else:
                            None

                kinEnergRem = scenKinEnergy[idxKinEnergy] - sum(dataEntsoEirGridSubset['KineticEnergy'])

                if kinEnergRem < 0:
                    kinEnergRem = 0
                else:
                    None

                # section to calculate the inertia provision from WT
                # subset of wind data
                windDataTmp = windData[windData['Time'] == key]
                windDataTmp = windDataTmp[['Time', 'Station No', 'Wind Speed']]
                windDataTmp = windDataTmp.reset_index()

                # calculate potential stored kinetic energy, if condition is True
                if scenSynWind[idxSynWind] == 1:
                    # calculate synthetic inertia from wind power plants
                    for idx in dfSellTmp.index:
                        for idx2 in listWindFarms.index:
                            if dfSellTmp['Name'][idx] == listWindFarms['Resource Name'][idx2]:
                                for idx3 in windWeatherAllocation.index:
                                    if listWindFarms['County'][idx2] == windWeatherAllocation['assigned County'][idx3]:
                                        for idx4 in windDataTmp.index:
                                            if windDataTmp['Time'][idx4] == datetime.datetime.strptime(key, '%Y-%m-%d %H:%M:%S') and windDataTmp['Station No'][idx4] == windWeatherAllocation['stno'][idx3]:
                                                # calculate wind speed in 80m height
                                                windSpeed80 = wind_speed_height(
                                                                windDataTmp['Wind Speed'][idx4], windWeatherAllocation['measurement height [m]'][idx3])
                                                if windSpeed80 < 3:
                                                    dfSellTmp.loc[idx, 'Kinetic Energy'] = 0

                                                elif windSpeed80 > 25:
                                                    dfSellTmp.loc[idx, 'Kinetic Energy'] = 0

                                                else:
                                                    try :


                                                        #print('Wind: ' + str(windSpeed80))
                                                        # calculate var H of wind turbine
                                                        varH =  speedVarHInterpol(speedPowerInterpol(windPowerInterpol(windSpeed80)))
                                                        #print('Var H: ' + str(varH))
                                                        #print('Power: ' + str(listWindFarms['Registered Capacity / Dispatchable Capacity'][idx2]))
                                                        # calculate stored kinetic energy
                                                        kinEnergyWT = inertiaConstantDemand * varH * listWindFarms['Registered Capacity / Dispatchable Capacity'][idx2]

                                                        # write stored kinetic energy into
                                                        dfSellTmp.loc[idx, 'Kinetic Energy'] = kinEnergyWT

                                                    except ValueError:
                                                        dfSellTmp.loc[idx, 'Kinetic Energy'] = 0


                                            else:
                                                None
                                    else:
                                        None
                            else:
                                None

                        else:
                            None

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
                #inertiaAct = []

                # find wind
                '''
                print(str(key))
                for idx in dfSellBalanceSubset.index:
                    if dfSellBalanceSubset['Fuel Type'][idx] == 'wind':
                        print('wind')
                        print(str(dfSellBalanceSubset['Kinetic Energy'][idx]))
                    else:
                        None

                '''




                # loop to calculate the stored kinetic energy per unit
                '''
                for idx in dfSellBalanceSubset.index:
                    inertiaAct.append(dfSellBalanceSubset['Capacity'][idx] * dfSellBalanceSubset['Inertia'][idx])
                '''
                # calculate the overall system stored kinetic energy
                #sysInertiaAct = sum(inertiaAct)
                sysInertiaAct = sum(dfSellBalanceSubset['Kinetic Energy'])

                # store results before the algorithm starts to possibly change the merit order
                marketBalanceTimeBeforeAlgo.append(timeTmp[0])
                marketBalancePriceBeforeAlgo.append(round(priceTmp[0],2))
                marketBalanceQuantityBeforeAlgo.append(round(quantityTmp[0],2))
                kinEnergyBeforeAlgo.append(round(sysInertiaAct,2))
                kinEnergyEntsoBeforeAlgo.append(round(sum(dataEntsoEirGridSubset['KineticEnergy']), 2))
                kinEnergyRemainBeforeAlgo.append(round(kinEnergRem, 2))

                if sysInertiaAct <= kinEnergRem:

                    while sysInertiaAct <= kinEnergRem:

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
                            kinEnergyEntsoAfterAlgo.append(round(sum(dataEntsoEirGridSubset['KineticEnergy']), 2))
                            kinEnergyRemainAfterAlgo.append(round(kinEnergRem, 2))

                            dicSellAfter[key] = dfSellTmp
                            break

                        # reset index
                        dfSellTmp.reset_index(inplace=True, drop='index')

                        # recalculate acumulated quanity
                        idx = 0

                        while idx <= len(dfSellTmp)-1:
                            if idx == 0:
                                dfSellTmp.loc[idx, 'Accumulated Difference'] = dfSellTmp['Quantity Difference'][idx]
                                idx += 1
                            else:
                                dfSellTmp.loc[idx, 'Accumulated Difference'] = dfSellTmp['Accumulated Difference'][idx-1] + dfSellTmp['Quantity Difference'][idx]
                                idx += 1

                        # call function to find the intersection of the sell and buy bids
                        timeTmp, priceTmp, quantityTmp = intersec_process(dfBuyTmp, dfSellTmp)

                        # calculate stored system kinetic energy
                        # extract all sell bids belowe or equalt to balance quanity
                        # get all indexes of rows which meet the condition
                        try:
                            indexBalance = dfSellTmp[dfSellTmp['Accumulated Difference'] <= quantityTmp[0]].index
                        except:
                            marketBalanceTimeAfterAlgo.append(timeTmp[0])
                            marketBalancePriceAfterAlgo.append(None)
                            marketBalanceQuantityAfterAlgo.append(None)
                            kinEnergyAfterAlgo.append(None)
                            kinEnergyEntsoAfterAlgo.append(round(sum(dataEntsoEirGridSubset['KineticEnergy']), 2))
                            kinEnergyRemainAfterAlgo.append(round(kinEnergRem, 2))

                            dicSellAfter[key] = dfSellTmp
                            break

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
                        # inertiaAct = []

                        # loop to calculate the stored kinetic energy per unit
                        '''
                        for idx in dfSellBalanceSubset.index:
                            inertiaAct.append(dfSellBalanceSubset['Capacity'][idx] * dfSellBalanceSubset['Inertia'][idx])
                        '''
                        # calculate the overall system stored kinetic energy
                        #sysInertiaAct = sum(inertiaAct)
                        sysInertiaAct = sum(dfSellBalanceSubset['Kinetic Energy'])

                        if sysInertiaAct <= kinEnergRem:
                            None
                        else:
                            marketBalanceTimeAfterAlgo.append(timeTmp[0])
                            marketBalancePriceAfterAlgo.append(round(priceTmp[0],2))
                            marketBalanceQuantityAfterAlgo.append(round(quantityTmp[0],2))
                            kinEnergyAfterAlgo.append(round(sysInertiaAct,2))
                            kinEnergyEntsoAfterAlgo.append(round(sum(dataEntsoEirGridSubset['KineticEnergy']), 2))
                            kinEnergyRemainAfterAlgo.append(round(kinEnergRem, 2))


                            dicSellAfter[key] = dfSellTmp


                else:
                    # store results after application of the algorithm even no changes were made due to sufficient amount of stored kinetic energy
                    marketBalanceTimeAfterAlgo.append(timeTmp[0])
                    marketBalancePriceAfterAlgo.append(round(priceTmp[0],2))
                    marketBalanceQuantityAfterAlgo.append(round(quantityTmp[0],2))
                    kinEnergyAfterAlgo.append(round(sysInertiaAct,2))
                    kinEnergyEntsoAfterAlgo.append(round(sum(dataEntsoEirGridSubset['KineticEnergy']), 2))
                    kinEnergyRemainAfterAlgo.append(round(kinEnergRem, 2))

                    dicSellAfter[key] = dfSellTmp

                dfResultBeforeAlgo = pandas.DataFrame({'Time': marketBalanceTimeBeforeAlgo,
                                                       'Price [EUR/MWh]': marketBalancePriceBeforeAlgo,
                                                       'Quantity [MWh]': marketBalanceQuantityBeforeAlgo,
                                                       'Inertia Day Ahead Act [MWs]': kinEnergyBeforeAlgo,
                                                       'Inertia ENTSO [MWs]': kinEnergyEntsoBeforeAlgo,
                                                       'Inertia Day Ahead Demand [MWs]':
                                                       kinEnergyRemainBeforeAlgo})

                dfResultAfterAlgo = pandas.DataFrame({'Time': marketBalanceTimeAfterAlgo,
                                                       'Price [EUR/MWh]': marketBalancePriceAfterAlgo,
                                                       'Quantity [MWh]': marketBalanceQuantityAfterAlgo,
                                                       'Inertia Day Ahead Act [MWs]': kinEnergyAfterAlgo,
                                                       'Inertia ENTSO [MWs]': kinEnergyEntsoAfterAlgo,
                                                       'Inertia Day Ahead Demand [MWs]':
                                                       kinEnergyRemainAfterAlgo})

                dfResultBeforeAlgo.to_csv(pathData + 'beta/Results/' + scenNameFull + '_Before.csv', sep=';')

                dfResultAfterAlgo.to_csv(pathData + 'beta/Results/' + scenNameFull + '_After.csv', sep=';')

                pickleSellDataAfter = open(pathData + 'beta/Results/' + scenNameFull + '_bid_sell_data_after_algo.pickle', 'wb')
                pickle.dump(dicSellAfter, pickleSellDataAfter, protocol=pickle.HIGHEST_PROTOCOL)

                pickleSellDataBefore = open(pathData + 'beta/Results/' + scenNameFull + '_bid_sell_data_before_algo.pickle', 'wb')
                pickle.dump(dicSellFinal, pickleSellDataBefore, protocol=pickle.HIGHEST_PROTOCOL)

# print message
print('inertia dispatch analysis successfull')
