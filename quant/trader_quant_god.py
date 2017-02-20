#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and un800
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#    alpaca trade stock
#      黄金分割线的实战运用主要集中在两个方面，一个是利用股价回调和反弹的幅度来预测股价运行趋势，另一个则是判断股价的回调支撑区和反弹压力区。
#

import pandas as pd
import sys
from time import localtime, strftime, time
import datetime

import _index
from energy.db.kPrice import kPrice

from energy.libs.buildReturnJson import buildReturnJson as brj

def getStockKline(code):

    month = ["01","04","07","10"]
    _mon = strftime("%m", localtime(time()))
    _year = int(strftime("%Y", localtime(time())))
    args = []
    for y in range(_year-1, _year+1):
        for m in month:
            if m == _mon and _year == y:
                break
            a = [y,m]
            args.append(a)
#    col = ["code","god","price","date","nextUP","nextDown","percent"]
    goddf = None

    for m in args[-4:]:
        #print m[0], m[1]
        gdf = runGod(code, m[0], m[1])
        if gdf.code.count() == 0:
            continue

        if goddf is None:
            goddf = gdf
        else:
            goddf =  pd.concat([goddf,gdf])

    if goddf is None:
        return

    if goddf.code.count() > 0:
        print goddf.set_index(["quarter"]).to_json(orient="split")

def runGod(rcode, year, mon):

    godTime = "%s-%s-01"%(year,mon)
    hfqTime = int(datetime.datetime.strptime(godTime, '%Y-%m-%d').strftime("%s"))
    col = ["code","god","price","date","nextUP","nextDown","percent"]
    goddf = pd.DataFrame(columns=col)
    clist = getCode(rcode)

    for c in clist:
        code = str(c['code'])+"_hfq"
        godse = GodStock(code, hfqTime)
        gdf = pd.DataFrame(godse, columns=col)
        gdf["quarter"] = str(year)+str(mon)
        goddf = goddf.append(gdf,ignore_index=True)

    del goddf["god"]
    return goddf
    #if goddf.code.count() > 0:
    #    print goddf.sort_values(by="code").to_json(orient="index")

def getCode(code):

    clist = []
    cl = {}
    cl["code"] = str(code)
    clist.append(cl)

    return clist

def GodStock(code, hfqTime):
    gs = [0.191,0.382,0.5,0.618,0.809]
    godBaseList = [0.019,0.038,0.05,0.0618,0.0809,0.191,0.382,0.5,0.618,0.809]
    dpress = 0.854
    kp = kPrice()
    kline = kp.getOrderDateKLine(code, hfqTime, 12)
    if kline is None:
        return
    i = 0

    iniClose = 0
    iniDate = ""
    gsInit = 0
    percent = 0
    n = 1
    lp = []
    for k in kline.itertuples():
        if i == 0:
            i+=1
            iniClose = k.close
            iniDate = strftime("%Y-%m-%d", localtime(k.date))
            continue

        if i >= len(gs):
            i=1
            n+=1
            gsInit = gs[i-1]+n
            #gpprice = (gs[i-2]+n)*iniClose
            #percent = ((k.close - gpprice)/ k.close)*100
            #iniClose = k.close
            #iniDate = strftime("%Y-%m-%d", localtime(k.date))

        h = (gs[i-1]+n)*iniClose - k.close
        if h < 0:
            if (i-1)==0 and n == 1:
                lp.append([code,0, iniClose, iniDate,(gs[i-1]+n)*iniClose, iniClose*dpress,0])
            i += 1

            gdate = strftime("%Y-%m-%d", localtime(k.date))
            gsprice = (gs[i-1]+n)*iniClose
            gpprice = (gs[i-2]+n)*iniClose
            percent = ((k.close - gpprice)/ k.close)*100
            lp.append([code,gs[i-1]+n, k.close, gdate,gsprice , k.close*dpress, percent])
#    print lp
    if len(lp) == 0:
        return None
    else:
        return lp


class QuantGod():
    def __init__(self):
        self._GodList = [0.019,0.038,0.05,0.0618,0.0809,0.191,0.382]
        self._Code = ""
        self._GodSplit=[30,60,90]
        self._col = ["basePrice", "godPrice","god"]

        self._sdate = ""

        self._brjObject = brj()
        self._brjName = ""

    def SetCode(self,c):
        self._Code = c

    def SetDate(self, d):
        self._sdate = d

    def Split(self, price, pn):

        df = pd.DataFrame(columns=self._col)
        for g in self._GodList:
            pg = g
            if pn == 1:
                pg = 0 - g
            gk = price*(1+pg)
            pdser = pd.Series([price, gk, pg],index=self._col)
            df = df.append(pdser,ignore_index=True)
        json = df.to_json(orient="split")
        self._brjObject.db(json)
        self._brjObject.formats("table")
        self._brjObject.name(self._brjName)
        self._brjObject.buildData()

    def Run(self):

        kp = kPrice()
        kline = kp.getAllKLine(self._Code)
        if kline is None:
            return

        if self._sdate == "":
            kl = kline.tail(1)
        else:
            kl = kline[kline.date == self._sdate]

        self._brjName = str(kl.date.values[0]) + " 起点"
        self.par(kl.close.values[0])

        for m in self._GodSplit:
            self._brjName = str(m)+" 天平均线"
            kgl = kline[kline.index > kl.index.values[0]-m]
            pgl = kgl.head(m).close.values.mean()
            self.par(pgl)

        bjson = self._brjObject.getResult()
        print bjson

    def par(self, kl):

        for n in range(0,2):

            self.Split(kl, n)

def main():

    if(len(sys.argv) >= 2):
        code = sys.argv[1]
        qg = QuantGod()
        qg.SetCode(code)

        if len(sys.argv) == 3:
            date = sys.argv[2]
            qg.SetDate(date)

        qg.Run()

    else:
        print "3"

if __name__ == "__main__":
    main()
