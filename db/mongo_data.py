#!/usr/bin/python2
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-

from pyalgotrade.barfeed import dbfeed
from pyalgotrade.barfeed import membf
from pyalgotrade import bar
from pyalgotrade.utils import dt

import pandas as pd

import time

from energy.db import emongo

class MonSQLDatabase(dbfeed.Database):
    def __init__(self):
        self.__df = None

    def getBars(self, instrument, timezone=None, fromDateTime=None, toDateTime=None):
        """
            生成Bar 数据
        Parameters
        ------
            instrument:string
                        股票代码
            timezone:string
            fromDateTime:string
            toDateTime:string
        return
            数组
        """
        emg = emongo()
        stockdb = emg.getCollectionNames("stockDB")
        ret = []
        KL = []
        for post in stockdb.find({instrument: {'$exists':1}},{instrument:1,'_id':0}):
            KL = KL+post[instrument]

        Date = []
        Open = []
        High = []
        Low = []
        Close = []
        Volume = []
        Adj_Close = []

        for val in KL:

            dateTime = val['date']
            dateTime = dateTime[:10]
            #print dateTime
            TimeStamp = time.mktime(time.strptime(dateTime,'%Y-%m-%d'))
            OdateTime = dt.timestamp_to_datetime(TimeStamp)
#                print("%s"%dateTimes)
            if type(val) is list:
                val = val[0]

            ret.append(bar.BasicBar(OdateTime, val['open'], val['high'], val['low'], val['close'], val['volume'], val['close'], bar.Frequency.DAY))

            Date.append(TimeStamp)
            Open.append(val['open'])
            High.append(val['high'])
            Low.append(val['low'])
            Close.append(val['close'])
            Volume.append(val['volume'])
            Adj_Close.append(val['close'])

        self.__df = pd.DataFrame({'Date' : Date, 'Open' : Open,
                'High' : High,'Close' : Close,
                'Low' : Low,'Volume' : Volume,
                'Adj Close':Adj_Close})

        emg.Close()

        return ret

    def getDF(self):

        return self.__df


class Feed(membf.BarFeed):
    def __init__(self, instrument, frequency, maxLen=None):
        super(Feed, self).__init__(frequency, maxLen)
        self.__instrument = instrument
        self.__monSQLdb = MonSQLDatabase()

    def barsHaveAdjClose(self):
        return True

    def getDatabase(self):
        return self.__monSQLdb

    def getDF(self):
        """
            getDF
        Parameters
        --------
        return
        -------
            DataFrame

        """
        return self.__monSQLdb.getDF()

    def loadBars(self, timezone=None, fromDateTime=None, toDateTime=None):
        bars = self.__monSQLdb.getBars(self.__instrument,timezone, fromDateTime, toDateTime)
        self.addBarsFromSequence(self.__instrument, bars)
