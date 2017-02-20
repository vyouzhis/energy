#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-

import pymongo
import tushare as ts
import json

import _index
from energy.db.emongo import emongo

class pyToMongo():
    def run(self, year, month):


        stockDB = {}

        print "basics"
        basicDf = ts.get_stock_basics()
        basicDf.rename(columns=lambda x: x.replace('esp', 'eps'), inplace=True)
        stockDB["basics"] = json.loads(basicDf.to_json(orient="index"))

        print "report"
        reportDf = ts.get_report_data(year,month)
        if reportDf is None:
            print "report is None %d, %d"%(year, month)
            return
        else:
            repJson = self.toJson(reportDf)
            stockDB["report"] = repJson
#        print stockDB

        print "profit"
        profitDf = ts.get_profit_data(year,month)
        if profitDf is None:
            print "profitDf is None %d, %d"%(year, month)
        else:
            proJson = self.toJson(profitDf)
            stockDB["profit"] = proJson

        print "operation"
        operationDf = ts.get_operation_data(year,month)
        if operationDf is None:
            print "operationDf is None %d, %d"%(year, month)
        else:
            operJson = self.toJson(operationDf)
            stockDB["operation"] = operJson

        print "growth"
        growthDf = ts.get_growth_data(year,month)
        if growthDf is None:
            print "growthDf is None %d, %d"%(year, month)
        else:
            growJson = self.toJson(growthDf)
            stockDB["growth"] = growJson

        print "debtpaying"
        debtpayingDf = ts.get_debtpaying_data(year,month)
        if debtpayingDf is None:
            print "debtpayingDf is None %d, %d"%(year, month)
        else:
            debJson = self.toJson(debtpayingDf)
            stockDB["debtpaying"] = debJson

        print "cashflow"
        cashflowDf = ts.get_cashflow_data(year,month)
        if cashflowDf is None:
            print "cashflowDf is None %d, %d"%(year, month)
        else:
            cashj = self.toJson(cashflowDf)
            stockDB["cashflow"] = cashj

        DT = {}
        k = str(year)+str(month)
        DT["Info"] = stockDB
        DT["ym"] = k

        emg = emongo()
        sdb = emg.getCollectionNames("stockInfo")

        sdb.insert(DT)
        emg.Close()

    def toJson(self,dfData):
        index = dfData.set_index(["code"]).index
        dfData.index = index
        cl = dfData.drop_duplicates("code")
        cl.pop("code")
        cjson = cl.to_json(orient="index")
        j = json.loads(cjson)
        return j

def main():
    pytm = pyToMongo()
    emg = emongo()
    sdb = emg.getCollectionNames("stockInfo")
    ymk = sdb.find({},{"ym":1,"_id":0}).sort("ym", pymongo.DESCENDING).limit(1)
    if ymk.count() == 0:
        pytm.run(2013, 1)
    else:
        for ym in ymk:
            y = int(ym['ym'][:4])
            m = int(ym['ym'][4:])
            if m < 4:
                m += 1
            else:
                y+=1
                m = 1
            print y,"_",m
            pytm.run(y, m)
    emg.Close()

if __name__ == "__main__":
    for i in range(5):
        main()
