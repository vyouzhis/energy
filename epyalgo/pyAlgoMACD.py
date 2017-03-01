#!/usr/bin/python2
# -*- coding: utf-8 -*-
#  home
#
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#  测试　pyalgotrade 回测
#
import _index
from energy.libs.MongoStock import Feed
from energy.libs.eAlgoLib import eAlgoLib as eal

from pyalgotrade import strategy
from pyalgotrade import bar
from pyalgotrade.technical import macd
from pyalgotrade.technical import ma

import pandas as pd
import sys

class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, bBandsPeriod):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.setDebugMode(False)
        self.__instrument = instrument
        self.__feed = feed
        self.__position = None
        fastEMA=12
        slowEMA=26
        signalEMA=9
        self.__macd = macd.MACD(feed[instrument].getCloseDataSeries(),
                               fastEMA,slowEMA,signalEMA, 15)
        self.__fastma = ma.EMA(feed[instrument].getCloseDataSeries(),fastEMA)
        self.__slowma = ma.EMA(feed[instrument].getCloseDataSeries(),slowEMA)

        self.__col = ["buyPrice","buyTime","sellPrice","sellTime", "returns"]
        self.__msdf = pd.DataFrame(columns=self.__col)
        self.__buyPrice = 0
        self.__buyTime = None
        self.setUseAdjustedValues(True)

    def EchoDF(self):
        return self.__msdf

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("BUY at $%.2f"%(execInfo.getPrice()))
        self.__buyPrice = execInfo.getPrice()
        self.__buyTime = execInfo.getDateTime()
#        self.__position = None

    def onEnterCanceled(self, position):
        self.info("onEnterCanceled")
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.2f"%(execInfo.getPrice()))
        self.__position = None

        pdser = pd.Series([self.__buyPrice, str(self.__buyTime)[:10],
                           execInfo.getPrice(),str(execInfo.getDateTime())[:10], (execInfo.getPrice() -self.__buyPrice)],index=self.__col )
        self.__msdf = self.__msdf.append(pdser,ignore_index=True)
        self.__buyPrice = 0
        self.__buyTime = None

    def onExitCanceled(self, position):
        self.info("onExitCanceled")
        self.__position.exitMarket()

    def onBars(self, bars):
        if self.__macd[-1] is None:
            return
        #bar = bars[self.__instrument]
        macds = self.__macd[-1]
 #       hists = self.__macd.getHistogram()[-1]
 #       sigs = self.__macd.getSignal()[-1]
        fast = self.__fastma[-1]
        slow = self.__slowma[-1]
        #self.info("macd:%s fast:%s slow:%s date:%s" % (macds,fast,slow,bar.getDateTime()))

        if self.__position is None:
            if macds >=0 and fast>=slow:
                # Enter a buy market order for 10 shares. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, 10, True)
                #print dir(self.__position)

        # Check if we have to exit the position.
        elif macds<0 and fast<slow and not self.__position.exitActive():
            self.__position.exitMarket()

def main(i, code):
    #code = "000592"
    dbfeed = Feed(code, bar.Frequency.DAY, 1024)
    dbfeed.loadBars()

    myStrategy = MyStrategy(dbfeed, code, bBandsPeriod=i)
    ms = eal()
    ms.setDebug(True)
    ms.protfolio(myStrategy)

if __name__ == "__main__":
    code = sys.argv[1]
    #for m in range(10,60,5):
    m = 40
    main(m, code)
