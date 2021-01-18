# ------------------
# functions
# ------------------

# create function to convert wind speed in knots to m/s
def knots2Meters(knots):
    speedSecondsPerMeters = 0.514444 * knots
    return speedSecondsPerMeters


# -------------------
# import section
# -------------------

# set path to folder where weather data is stored
pathWindData = 'Weather/'

# create a list of all weather files
listWeatherFieles = os.listdir(pathData + pathWindData)

# create empty list to store imported and processed data
windSpeedTotal = []
stationNoTotal = []

# for loop to import weather data and calculate the 1 hour mean wind speed
for idx in listWeatherFieles:
    # import weather data
    dataWeatherRaw = pandas.read_csv(pathData + pathWindData + idx, sep = ',',low_memory=False)

    # group data to calculate the mean wind speed per hour
    groupedData = dataWeatherRaw.groupby(by = ['year',
                                               'month',
                                               'day',
                                               'hour'])

    # calculate mean wind speed [knots] for every hour
    meanSpeedPerHour = groupedData['speed'].mean()

    # convert from knots into meters per second
    windSpeed = []
    for i in meanSpeedPerHour:
        windSpeed.append(knots2Meters(i))

    # create time series in hourly resolution
    # get start time of data frame
    startTime = dataWeatherRaw['date'].iloc[0]

    # get the number of days in a month
    noDays = dataWeatherRaw['day'].iloc[-1]

    # create time series
    timeSeries = pandas.date_range(start=startTime,
                                   periods=noDays*24,
                                   freq='H')
    timeSeries = pandas.Series(timeSeries)

    # append data to final list
    # append wind data
    windSpeedTotal = windSpeedTotal + windSpeed

    # append time series
    if 'timeSeriesTotal' in locals():
        timeSeriesTotal = timeSeriesTotal.append(timeSeries)

    else:
        timeSeriesTotal = timeSeries

    # get station no
    stationNo = dataWeatherRaw['stno'].iloc[0]
    stationNo = [stationNo] * 24 * noDays
    stationNoTotal = stationNoTotal + stationNo

windData = pandas.DataFrame({'Time': timeSeriesTotal,
                             'Station No': stationNoTotal,
                             'Wind Speed': windSpeedTotal})

windData.to_csv(pathData + 'wind_speed.csv',
                sep=';')

# import file fille needed to combine date
windWeatherAllocation = pandas.read_csv(pathData + 'wind_weather.csv',
                                        sep=';')

# import list of wind farm
listWindFarms = pandas.read_csv(pathData + 'list_wind_farms.csv',
                                engine='python',
                                sep=';',
                                decimal=',')

listWindFarms = listWindFarms.drop(['Unnamed: 8'], axis=1)

# import wt specific data
# import wind vs power PU characteristic of WT
windVsPower = pandas.read_csv(pathData + 'wind_vs_powerpu.csv',
                              sep=',',
                              names=['wind', 'power PU'])

# import speed PU vs power PU characteristic of WT
speedPuVspower = pandas.read_csv(pathData + 'speedpu_vs_powerpu.csv',
                                 sep=';',
                                 decimal=',')

# import speed PU vs var H characteristic of WT
speedPuVsVarH = pandas.read_csv(pathData + 'speed_vs_varh.csv',
                                sep=',',
                                names=['speed PU', 'var H'])

# print message
print('import wind data successfull')
