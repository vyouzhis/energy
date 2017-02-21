#!/usr/bin/python2
# -*- coding: utf-8 -*-
#  tushare_to_mongo
#
#
# vim:fileencoding=utf-8:sw=4:et
#
#   从tushare获取Ｋ线数据
#

import sys,json
import pandas as pd
import tushare as ts
from time import localtime, strftime, time
from datetime import datetime
import pymongo
import multiprocessing
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

import _index
from energy.db.emongo import emongo
from energy.db.dblist import dblist

class TTM():
    def __init__(self):
        self._code = None
        self._stock_name = None
        self._Type = None
        self._id = 0
        self._df = None
        self._InitNum = 20

    def setType(self, t=None):
        self._Type = t

    def setCode(self, c):
        self._code = c

    def CodeInit(self):
        self._stock_name = self._code

        if self._code == 'sh':
#上证指数
            self._code = 'sh000001'
            self._stock_name = "sh"
        elif self._code == 'sz':
#深证指数
            self._code = 'sz399001'
            self._stock_name = "sz"
        elif self._code == 'zx':
#中小板指数
            self._code = 'sz399005'
            self._stock_name = "zx"
        elif self._code == 'cy':
#创业板指数
            self._code = 'sz399006'
            self._stock_name = "cy"
        elif self._code == '300':
#沪深300
            self._code = 'sh000300'
            self._stock_name = "hs300"


        if self._Type is not None:
            self._stock_name += "_hfq"

    def IsExists(self):
        TodayTime = strftime("%Y-%m-%d", localtime(time()))

        self.CodeInit()

        emg = emongo()
        sdb = emg.getCollectionNames("stockDB")

        StockData = sdb.find({self._stock_name:{"$exists":1}},{self._stock_name:1, "_id":1}).limit(1)

        sdate = None
        ie = list(StockData)
        if len(ie)==0:
            self._InitNum = 900
        else:

            self._df = pd.DataFrame(ie[0][self._stock_name])
            self._id = ie[0]['_id']

            tdf = self._df.tail(1)
            sdate =  tdf.date.values[0]
            if sdate == TodayTime:
                print "ok date, ",TodayTime
                return

        if self._Type is not None:
            print sdate
# hfq
            stime = self.getBaseDate(sdate)
            if stime is None:
                return
            print self._code,"---",stime
            df = ts.get_h_data(self._code, autype=self._Type, start=stime)
            #print df
            if df is None:
                return
            if df.empty:
                return

            df = df.reset_index()
            df.date = df["date"].astype(str)
        else:
            df = self.getSinaKline()

            if df is None:
                return

            if df.empty:
                return
        #print df
        if df.close.count() == 0:
            return

        stockDB = {}

        if self._InitNum == 900:
            cjson = df.sort_values(by="date").to_json(orient="records")
            j = json.loads(cjson)

            stockDB[self._stock_name] = j
            sdb.insert(stockDB)
        else:
            self._df = self._df.append(df.head(20))
            self._df = self._df.drop_duplicates()
            cjson = self._df.sort_values(by="date").to_json(orient="records")
            j = json.loads(cjson)
            stockDB[self._stock_name] = j

            sdb.update({"_id":{"$eq":self._id}}, {"$set":  stockDB })

        emg.Close()

    def getBaseDate(self, st):

        if self._InitNum == 20:
            ot = int(datetime.strptime(st, '%Y-%m-%d').strftime("%s"))
            StartTime = strftime("%Y-%m-%d", localtime(ot-86400*20))
            return StartTime

        emg = emongo()
        sdb = emg.getCollectionNames("stockInfo")
        df = sdb.find({"Info.basics."+self._code:{"$exists":1}},{"Info.basics."+self._code+".timeToMarket":1,"_id":0}).sort("ym", pymongo.DESCENDING).limit(1)
        il = list(df)
        if len(il)==0:
            emg.Close()
            return None

        baseTime = None

        baseTime = str(il[0]["Info"]["basics"][self._code]["timeToMarket"])

        if baseTime is None:
            return None

        emg.Close()
        baseTime = baseTime[0:4]+"-"+baseTime[4:6]+"-"+baseTime[6:]

        return baseTime

    def getSinaKline(self):

        stockNumber = self._code
        if len(stockNumber) == 8:
#8位长度的代码必须以sh或者sz开头，后面6位是数字
            if (stockNumber.startswith('sh') or stockNumber.startswith('sz')) and stockNumber[2:8].decode().isdecimal():
                self._code = stockNumber
        elif len(stockNumber) == 6:
# 6位长度的代码必须全是数字
            if stockNumber.decode().isdigit():
# 0开头自动补sz，6开头补sh，3开头补sz，否则无效
                if stockNumber.startswith('0'):
                    self._code = 'sz' + stockNumber
                elif stockNumber.startswith('6'):
                    self._code = 'sh' + stockNumber
                elif stockNumber.startswith('3'):
                    self._code = 'sz' + stockNumber

        url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php"
        url +="/CN_MarketData.getKLineData?symbol=%s&scale=240&datalen=%d"%(self._code, self._InitNum)
        try:
            request = Request(url)
            text = urlopen(request, timeout=10).read()
            text = text.replace("\"", "")

            text = text.replace(",",",\"")
            text = text.replace(":","\":")
            text = text.replace("{","{\"")

            text = text.replace("day\":","day\":\"")
            text = text.replace(",\"open","\",\"open")

            text = text.replace("},\"{",  "},{")
            djson = json.loads(text)
            df = pd.DataFrame(djson)
            df.rename(columns=lambda x: x.replace('day', 'date'), inplace=True)
            df.rename(columns=lambda x: x.replace('ma_price5', 'ma5'), inplace=True)
            df.rename(columns=lambda x: x.replace('ma_price10', 'ma10'), inplace=True)
            df.rename(columns=lambda x: x.replace('ma_price30', 'ma30'), inplace=True)
            #print df
            return df
        except Exception as e:
            print(e)

class getAllStock():
    def getas(self, t=None):

        dbl = dblist()
        codeList = dbl.getAllCodeList()
        dbl.Close()
        print t, " is start"
        i = 0
        for post in codeList:
            code = post["code"]

            ttm = TTM()
            ttm.setCode(code)
            ttm.setType(t)
            ttm.IsExists()
            print "now next is:",i
            i+=1

        print t," is end"


def runStock(types=None):
    gas = getAllStock()
    gas.getas(types)

def main():
    if len(sys.argv) == 2:
        code = sys.argv[1]
        if code == "I":
            hs = ["zx","sh","sz","cy","300"]
            for cds in hs:
                ttm = TTM()
                ttm.setCode(cds)
                ttm.IsExists()
            return

        gas = getAllStock()
        gas.getas()
    elif len(sys.argv) == 3:
        code = sys.argv[1]
        ttm = TTM()
        ttm.setCode(code)
        t = sys.argv[2]
        if int(t) == 1:
            ttm.setType("hfq")
        ttm.IsExists()
    else:
        print "get all stock"
        runStock()
        runStock("hfq")
        """
        try:
            h = multiprocessing.Process(target = runStock, args = ("hfq",))
            h.start()
            n = multiprocessing.Process(target = runStock, args = ())
            n.start()
        except:
            print "Error: unable to start thread"
        """
        print "end"


if __name__ == "__main__":
    main()
