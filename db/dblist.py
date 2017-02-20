#!/usr/bin/python2
# -*- coding: utf-8 -*-
# dblist
#
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#   取数据内容
#
import _index
from energy.db.emongo import emongo

import pandas as pd

class dblist():
    def __init__(self):
        self.__conn = emongo()

    def Close(self):
        self.__conn.Close()

    def getCodeList(self, collection):
        szCode = self.__conn.getCollectionNames(collection)
        codeList = list(szCode.find({},{"code":1,"_id":0}))

        return codeList

    def getUn800(self):
        """
            获取上证 800 股票
        Parameters
        ---------
        Return
        -------
            list
        """
        codeList = self.getCodeList("un800")

        return codeList

    def getAllCodeList(self):
        """
            获取沪深所有 股票
        Parameters
        ---------
        Return
        -------
            list
        """
        codeList = self.getCodeList("AllStockClass")

        return codeList

    def getIndustryCode(self, code):
        """
            获取该股票的行业代码
        Parameters
        ---------
            code:string  代码
        Return
        -------
            list
        """
        sdb = self.__conn.getCollectionNames("AllStockClass")
        CodeIndu = sdb.find({"code":{"$eq":code}},{"_id":0}).limit(1)
        if CodeIndu.count() == 0:
            return
        clist = None
        for ci in CodeIndu:
            cname = ci['c_name']

            clist = list(sdb.find({"c_name":{"$eq":cname}},{"_id":0,"code":1,"name":1}))

        return clist

    def getInfo(self,ym, ctype, c):
        """
            getInfo 获取 stockinfo 信息
        Parameters
        ---------
            ym:int  年份月份
            ctype:String 类型
            c:String  code
        Return
        -------
            DataFrame

        """
        info = self.__conn.getCollectionNames("stockinfo")

        BasicsList = info.find({"ym":{"$eq":ym}},{"Info."+ctype+"."+c:1,"_id":0, "ym":1}).limit(1)
        if BasicsList.count() != 0:
            bl = BasicsList[0]['Info'][ctype]
            df = pd.DataFrame(data=bl)
            return df.T
        else:
            return None
