#!/usr/bin/python2
# -*- coding: utf-8 -*-
#  buildReturnJson
#
#  生成返回值的JSON
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-

import _index

from energy.libs.buildReturnJson import buildReturnJson as brj

from pyalgotrade.stratanalyzer import returns
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.stratanalyzer import drawdown
from pyalgotrade.stratanalyzer import trades
from pyalgotrade.utils import stats

import pandas as pd


class eAlgoLib():

    def protfolio(self, myStrategy):
        retAnalyzer = returns.Returns()
        sharpeRatioAnalyzer = sharpe.SharpeRatio()
        drawDownAnalyzer = drawdown.DrawDown()
        tradesAnalyzer = trades.Trades()

        myStrategy.attachAnalyzer(retAnalyzer)
        myStrategy.attachAnalyzer(sharpeRatioAnalyzer)
        myStrategy.attachAnalyzer(drawDownAnalyzer)

        myStrategy.attachAnalyzer(tradesAnalyzer)

        myStrategy.run()
        dfjson = myStrategy.EchoDF()
        finalProt = myStrategy.getResult()

        brjObject = brj()

#交易过程

        brjObject.db(dfjson)
## ...
        brjObject.formats("markPoint")
        brjObject.name("df")
        brjObject.buildData()

        brjObject.db(dfjson)
## ...
        brjObject.formats("table")
        brjObject.name("交易细则")
        brjObject.buildData()

        base = {}
#总资产
        base[ "Final portfolio value: "] = "$%.2f" % finalProt
#累计收益率
        base["Anual return: "] = "%.2f %%" % (retAnalyzer.getCumulativeReturns()[-1] * 100)
#    平均收益率
        base["Average daily return:"]=" %.2f %%" % (stats.mean(retAnalyzer.getReturns()) * 100)
#方差收益率
        base["Std. dev. daily return:"]=" %.4f" % (stats.stddev(retAnalyzer.getReturns()))
#夏普比率
        base["Sharpe ratio: "]="%.2f" % (sharpeRatioAnalyzer.getSharpeRatio(0))
#最大回撤
        base["DrawDown :"]=" %.2f" % (drawDownAnalyzer.getMaxDrawDown())
        dfbase = pd.DataFrame(base,index=["val"])

        baseJson = dfbase.T.reset_index().to_json(orient="split")

        brjObject.db(baseJson)
        brjObject.formats("table")
        brjObject.name("base")
        brjObject.buildData()

        AllTrades = {}
#总交易笔数
        AllTrades["Total trades:"]=" %d" % (tradesAnalyzer.getCount())
        if tradesAnalyzer.getCount() > 0:
            profits = tradesAnalyzer.getAll()
            AllTrades["Avg. profit:"]=" $%2.f" % (profits.mean())
            AllTrades["Profits std. dev.:"]=" $%2.f" % (profits.std())
            AllTrades["Max. profit: "]="$%2.f" % (profits.max())
            AllTrades["Min. profit:"]=" $%2.f" % (profits.min())
            returns_trade = tradesAnalyzer.getAllReturns()
            AllTrades["Avg. return:"]=" %2.f %%" % (returns_trade.mean() * 100)
            AllTrades["Returns std. dev.: "]="%2.f %%" % (returns_trade.std() * 100)
            AllTrades["Max. return: "]="%2.f %%" % (returns_trade.max() * 100)
            AllTrades["Min. return: "]="%2.f %%" % (returns_trade.min() * 100)

        df = pd.DataFrame(AllTrades,index=["val"])
        baseJson = df.T.reset_index().to_json(orient="split")

        brjObject.db(baseJson)
        brjObject.formats("table")
        brjObject.name("AllTrades")
        brjObject.buildData()

#盈利笔数
        proTrades = {}
        proTrades["Profitable trades: "]="%d" % (tradesAnalyzer.getProfitableCount())
        if tradesAnalyzer.getProfitableCount() > 0:
            profits = tradesAnalyzer.getProfits()
            proTrades["Avg. profit: "]="$%2.f" % (profits.mean())
            proTrades["Profits std. dev.: "]="$%2.f" % (profits.std())
            proTrades["Max. profit:"]=" $%2.f" % (profits.max())
            proTrades["Min. profit:"]=" $%2.f" % (profits.min())
            returns_trade = tradesAnalyzer.getPositiveReturns()
            proTrades["Avg. return: "]="%2.f %%" % (returns_trade.mean() * 100)
            proTrades["Returns std. dev.:"]=" %2.f %%" % (returns_trade.std() * 100)
            proTrades["Max. return: "]="%2.f %%" % (returns_trade.max() * 100)
            proTrades["Min. return: "]="%2.f %%" % (returns_trade.min() * 100)

        df = pd.DataFrame(proTrades, index=["val"])
        baseJson = df.T.reset_index().to_json(orient="split")

        brjObject.db(baseJson)
        brjObject.formats("table")
        brjObject.name("proTrades")
        brjObject.buildData()
#亏损笔数
        unproTrades = {}
        unproTrades["Unprofitable trades:"]=" %d" % (tradesAnalyzer.getUnprofitableCount())
        if tradesAnalyzer.getUnprofitableCount() > 0:
            losses = tradesAnalyzer.getLosses()
            unproTrades["Avg. loss:"]=" $%2.f" % (losses.mean())
            unproTrades["Losses std. dev.:"]=" $%2.f" % (losses.std())
            unproTrades["Max. loss: "]="$%2.f" % (losses.min())
            unproTrades["Min. loss: "]="$%2.f" % (losses.max())
            returns_trade = tradesAnalyzer.getNegativeReturns()
            unproTrades["Avg. return: "]="%2.f %%" % (returns_trade.mean() * 100)
            unproTrades["Returns std. dev.: "]="%2.f %%" % (returns_trade.std() * 100)
            unproTrades["Max. return: "]="%2.f %%" % (returns_trade.max() * 100)
            unproTrades["Min. return: "]="%2.f %%" % (returns_trade.min() * 100)

        df = pd.DataFrame(unproTrades, index=["val"])
        baseJson = df.T.reset_index().to_json(orient="split")

        brjObject.db(baseJson)
        brjObject.formats("table")
        brjObject.name("unproTrades")
        brjObject.buildData()

        brjJson = brjObject.getResult()

        print brjJson
