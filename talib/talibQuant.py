#!/usr/bin/python2
# -*- coding: utf-8 -*-
#  trader_quant_obv
#
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#   talib Quant.
#

import sys
import json

import _index
from energy.db.kPrice import kPrice
from energy.libs.buildReturnJson import buildReturnJson as brj
from energy.libs.QTaLib import QTaLib

class talibQuant():
    def __init__(self):
        self._Code = ""
        self._o = ""

    def SetCode(self, c):
        self._Code = c

    def SetO(self, o):
        self._o = o

    def run(self):
        kp = kPrice()
        kline = kp.getAllKLine(self._Code)

        qtl = QTaLib()
        qtl.SetFunName(self._o)
        qtl.SetKline(kline)

        qRes = qtl.Run()

        brjObject = brj()

        OneList = ["ATR", "EMA", "OBV","ROC","RSI","SMA","WMA"]

        nlist = {}

        if o in OneList:
            real = qRes

            brjObject.db(json.dumps(real.tolist()))
            brjObject.formats("line")
            brjObject.name(o)
            brjObject.buildData()

        if self._o == "BBANDS":
            upperband, middleband, lowerband = qRes
            brjObject.RawMa(0)

            brjObject.db(json.dumps(upperband.tolist()))
            brjObject.formats("line")
            brjObject.isExt(1)
#            brjObject.yIndex(1)
            brjObject.name("Upper Band")
            brjObject.buildData()

            brjObject.db(json.dumps(middleband.tolist()))
            brjObject.formats("line")
            brjObject.isExt(1)
 #           brjObject.yIndex(1)
            brjObject.name("5-day SMA")
            brjObject.buildData()

            brjObject.db(json.dumps(lowerband.tolist()))
            brjObject.formats("line")
            brjObject.isExt(1)
  #          brjObject.yIndex(1)
            brjObject.name("Lower Band")
            brjObject.buildData()

        if self._o == "MACD":

            macd, macdsignal, macdhist = qRes
            nlist["macd"] = macd
            nlist["macdsignal"] = macdsignal
            for k in nlist:
                brjObject.db(json.dumps(nlist[k].tolist()))
                brjObject.formats("line")
                brjObject.name(k)
                brjObject.buildData()

            brjObject.db(json.dumps(macdhist.tolist()))
            brjObject.formats("bar")
            brjObject.yIndex(1)
            brjObject.name("macdhist")
            brjObject.buildData()

        if self._o == "STOCH":
            slowk, slowd = qRes

            brjObject.db(json.dumps(slowk.tolist()))
            brjObject.formats("line")
            brjObject.name("slowk")
            brjObject.buildData()

            brjObject.db(json.dumps(slowd.tolist()))
            brjObject.formats("bar")
            brjObject.yIndex(1)
            brjObject.name("slowd")
            brjObject.buildData()
        brjJson = brjObject.getResult()

        print brjJson


def main(c, o):
    obv = talibQuant()
    obv.SetCode(c)
    obv.SetO(o)
    obv.run()

if __name__ == "__main__":
    if(len(sys.argv) == 3):
        code = sys.argv[2]
        o = sys.argv[1]
        main(code, o)
    else:
        print "2"
