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
from pyalgotrade.technical import ma
from pyalgotrade.technical import rsi
from pyalgotrade.technical import cross

import pandas as pd
import sys

class pyAlgoRSI(strategy.BacktestingStrategy):

    def __init__(self, feed, instrument, entrySMA, exitSMA, rsiPeriod, overBoughtThreshold, overSoldThreshold):
        super(pyAlgoRSI, self).__init__(feed)
        self.__instrument = instrument
        # We'll use adjusted close values, if available, instead of regular close values.
        if feed.barsHaveAdjClose():
            self.setUseAdjustedValues(True)
        self.__priceDS = feed[instrument].getPriceDataSeries()
        self.__entrySMA = ma.SMA(self.__priceDS, entrySMA)
        self.__exitSMA = ma.SMA(self.__priceDS, exitSMA)
        self.__rsi = rsi.RSI(self.__priceDS, rsiPeriod)
        self.__overBoughtThreshold = overBoughtThreshold
        self.__overSoldThreshold = overSoldThreshold
        self.__longPos = None
        self.__shortPos = None
        self.__col = ["buyPrice","buyTime","sellPrice","sellTime", "returns"]
        self.__msdf = pd.DataFrame(columns=self.__col)


    def EchoDF(self):
#        return self.__msdf.to_json(orient="split")
        return self.__msdf

    def getEntrySMA(self):
        return self.__entrySMA

    def getExitSMA(self):
        return self.__exitSMA

    def getRSI(self):
        return self.__rsi

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        #self.info("BUY at $%.2f"%(execInfo.getPrice()))
        self.__buyPrice = execInfo.getPrice()
        self.__buyTime = execInfo.getDateTime()

    def onEnterCanceled(self, position):
        #self.info("onEnterCanceled")
        if self.__longPos == position:
            self.__longPos = None
        elif self.__shortPos == position:
            self.__shortPos = None
        else:
            assert(False)

    def onExitOk(self, position):
        if self.__longPos == position:
            self.__longPos = None
        elif self.__shortPos == position:
            self.__shortPos = None
        else:
            assert(False)

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
        position.exitMarket()

    def onBars(self, bars):
        # Wait for enough bars to be available to calculate SMA and RSI.
        if self.__exitSMA[-1] is None or self.__entrySMA[-1] is None or self.__rsi[-1] is None:
            return

        bar = bars[self.__instrument]
        if self.__longPos is not None:
            if self.exitLongSignal():
                self.__longPos.exitMarket()
        elif self.__shortPos is not None:
            if self.exitShortSignal():
                self.__shortPos.exitMarket()
        else:
            if self.enterLongSignal(bar):
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                self.__longPos = self.enterLong(self.__instrument, shares, True)
            elif self.enterShortSignal(bar):
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                self.__shortPos = self.enterShort(self.__instrument, shares, True)

    def enterLongSignal(self, bar):
        return bar.getPrice() > self.__entrySMA[-1] and self.__rsi[-1] <= self.__overSoldThreshold

    def exitLongSignal(self):
        return cross.cross_above(self.__priceDS, self.__exitSMA) and not self.__longPos.exitActive()

    def enterShortSignal(self, bar):
        return bar.getPrice() < self.__entrySMA[-1] and self.__rsi[-1] >= self.__overBoughtThreshold

    def exitShortSignal(self):
        return cross.cross_below(self.__priceDS, self.__exitSMA) and not self.__shortPos.exitActive()

def main(i, code):
    #code = "000592"
    dbfeed = Feed(code, bar.Frequency.DAY, 1024)
    dbfeed.loadBars()

    entrySMA = 200
    exitSMA = 5
    rsiPeriod = 2
    overBoughtThreshold = 90
    overSoldThreshold = 10

    myStrategy = pyAlgoRSI(dbfeed, code, entrySMA, exitSMA, rsiPeriod, overBoughtThreshold, overSoldThreshold)
    ms = eal()
    ms.setDebug(True)
    ms.protfolio(myStrategy)

if __name__ == "__main__":
    code = sys.argv[1]
    #for m in range(10,60,5):
    m = 40
    main(m, code)
