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
#from pyalgotrade.technical import stoch
from pyalgotrade.technical import ma
from pyalgotrade.talibext import indicator
from pyalgotrade.technical import atr

import pandas as pd
import sys

class pyAlgoSMASTOCH(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, bBandsPeriod):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.setDebugMode(False)
        self.__instrument = instrument
        self.__feed = feed
        self.__position = None
        #self.__stochK = stoch.StochasticOscillator(feed[instrument], 5, 3)
        self.__mafast = ma.EMA(feed[instrument].getCloseDataSeries(), 5)
        self.__maslow = ma.EMA(feed[instrument].getCloseDataSeries(), 30)

        self.__atr = atr.ATR(feed[instrument], 15)

        self.__col = ["buyPrice","buyTime","sellPrice","sellTime", "returns"]
        self.__msdf = pd.DataFrame(columns=self.__col)
        self.__buyPrice = 0
        self.__buyTime = None
        self.setUseAdjustedValues(True)

    def EchoDF(self):
        return self.__msdf

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        #self.info("BUY at $%.2f"%(execInfo.getPrice()))
        self.__buyPrice = execInfo.getPrice()
        self.__buyTime = execInfo.getDateTime()

    def onEnterCanceled(self, position):
        #self.info("onEnterCanceled")
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        #self.info("SELL at $%.2f"%(execInfo.getPrice()))
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
        if self.__atr is None:
            return
        barDs = self.getFeed().getDataSeries(self.__instrument)
        atr_21 = self.__atr[-21:]
        if len(atr_21) < 20:
            return
        #print atr_21[:-1]
        maxatr = max(atr_21[:-1])
        nowatr = self.__atr[-1]
        stochk, stochd = indicator.STOCH(barDs, 100, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        #print stochk[-1],"--",stochd[-1]
        #print "stochk:%s  mfast:%s mslow:%s nowatr:%s maxatr:%s"%(stochk[-1], self.__mafast[-1], self.__maslow[-1], nowatr, maxatr)

        if self.__position is None:
            if stochk[-1] < 20 and self.__mafast[-1] < self.__maslow[-1] :
                # Enter a buy market order for 10 shares. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, 10, True)
                #print dir(self.__position)

        # Check if we have to exit the position.
        elif stochk[-1] > 75  and  nowatr < maxatr and not self.__position.exitActive():
            self.__position.exitMarket()


def main(i, code):
    #code = "000592"
    dbfeed = Feed(code, bar.Frequency.DAY, 1024)
    dbfeed.loadBars()

    myStrategy = pyAlgoSMASTOCH(dbfeed, code, bBandsPeriod=i)
    ms = eal()
    ms.setDebug(True)
    ms.protfolio(myStrategy)

if __name__ == "__main__":
    code = sys.argv[1]
    #for m in range(10,60,5):
    m = 40
    main(m, code)
