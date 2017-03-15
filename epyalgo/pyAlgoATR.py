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
from pyalgotrade.technical import atr

import pandas as pd
import sys

class pyAlgoATR(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, bBandsPeriod):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.setDebugMode(False)
        self.__instrument = instrument
        self.__feed = feed
        self.__position = None
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
        if self.__atr[-1] is None or self.__atr[-15] is None:
            return
        preAtr = self.__atr[-15]
        nowAtr = self.__atr[-1]
        per = nowAtr * 0.75

        if self.__position is None:
            if per > preAtr:
                sharesToBuy = int(self.getBroker().getCash(False) / bar.getClose())
                self.__position = self.enterLong(self.__instrument, sharesToBuy, True)
                # Enter a buy market order for 10 shares. The order is good till canceled.
    #            self.__position = self.enterLong(self.__instrument, 10, True)
                #print dir(self.__position)

        # Check if we have to exit the position.
        elif per < preAtr and not self.__position.exitActive():
            self.__position.exitMarket()

def main(i, code):
    #code = "000592"
    dbfeed = Feed(code, bar.Frequency.DAY, 1024)
    dbfeed.loadBars()

    myStrategy = pyAlgoATR(dbfeed, code, bBandsPeriod=i)
    ms = eal()
    ms.protfolio(myStrategy)

if __name__ == "__main__":
    code = sys.argv[1]
    #for m in range(10,60,5):
    m = 40
    main(m, code)
