#!/usr/bin/python2
# -*- coding: utf-8 -*-
# kPrice
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#     获取股票的基本信息，包括K线，代码等
#
import pandas as pd
import talib

import _index
from energy.db.emongo import emongo

class kPrice():
    def __init__(self):
        self.__conn = emongo()
        self.__sdb = self.__conn.getCollectionNames("stockDB")

    def close(self):
        self.__conn.Close()

    def getAllKLine(self,code):
        """
            获取某一个时间的K 线
        Parameters
        ---------
            code:String 代码
        Return
        -------
            DataFrame
        """
        klres = list(self.__sdb.find({code: {'$exists':1}},{code:1,'_id':0}))

        if len(klres) == 0:
            return None
        KL = klres[0][code]

        mdf = pd.DataFrame(KL)
        mdf = mdf.sort_values(by="date")
        return mdf

    def talibMa(self, df, tp):
        """
            获得不同的 Moving average
        Parameters
            df:DataFrame  K line
            tp:int  k number
        Return:
            list
        """
        inputs = {
            'open': df.open.values,
            'high': df.high.values,
            'low': df.low.values,
            'close': df.close.values,
            'volume': df.volume.values
        }
        tma = talib.abstract.MA(inputs, timeperiod=tp)
        return tma

    def getOrderDateKLine(self, code, oby, lmt):
        """
            获取某一个时间的K 线
        Parameters
        ---------
            code:String 代码
            oby:date 时间
            lmt:int 数量
        Return
        -------
            DataFrame
        """

        mdf = self.getAllKLine(code)

        return mdf.sort_values(by=oby).tail(lmt)

    def HS300Time(self,nextTime = None):
        """
            以HS300Time 为标准时间
        Parameters
        ---------
            nextTime:date  开始时间值
        Return
        -------
            Series
        """
        kl = kPrice()
        hs300 = kl.getAllKLine("hs300")
        hs300 = hs300.sort_values(by="date")
        if nextTime is None:
            return hs300.date
        else:
            return hs300[hs300.date >= nextTime].date
