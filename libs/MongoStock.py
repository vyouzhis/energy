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

import time
import _index
from energy.db.kPrice import kPrice

class MonSQLDatabase(dbfeed.Database):
    def __init__(self):
        self.__df = None

    def getBars(self, instrument, timezone=None, fromDateTime=None, toDateTime=None):
        kp = kPrice()
        kline = kp.getAllKLine(instrument+"_hfq")
        kline =  kline.tail(300)
        ret = []

        for row in kline.itertuples():
            dateTime = row.date
            TimeStamp = time.mktime(time.strptime(dateTime,'%Y-%m-%d'))
            OdateTime = dt.timestamp_to_datetime(TimeStamp)
            #print float(row.high)
            #print "close:%s adjclose:%s high:%s low:%s date:%s "%(row.close, row.AdjClose,row.high,row.low, row.date)
            ret.append(bar.BasicBar(OdateTime, row.open, row.high,
                                    row.low, row.close, row.volume,
                                    row.close,
                                    bar.Frequency.DAY))

        self.__df = kline

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
        return self.__monSQLdb.getDF()

    def loadBars(self, timezone=None, fromDateTime=None, toDateTime=None):
        bars = self.__monSQLdb.getBars(self.__instrument,timezone, fromDateTime, toDateTime)
        self.addBarsFromSequence(self.__instrument, bars)
