#!/usr/bin/python2
# -*- coding: utf-8 -*-
#  buildReturnJson
#
#  生成返回值的JSON
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#
#
# {
#    "RawMa": "0",  // 0 关闭原来的MA5 MA10 MA20, 1 保留
#    "data": [
#        {
#            "format": "line",　　//  图像 line 线
#            "yIndex": "0",　　//  刻度方位，０　左边，１右边
#            "isExt": "0",　　//  ０　下面副图区，１主图区
#            "db": "list",　　　　 // 数组
#            "date": "list",  // 时间数组，可为空
#            "name": "db name" //　名字
#        },
#        {
#             "format": "bar",　　//  图像 bar 线
#            "yIndex": "0",　　//  刻度方位，０　左边，１右边
#            "isExt": "0",　　//  ０　下面副图区，１主图区
#            "db": "list",　　　　 // 数组
#            "date": "list",  // 时间数组，可为空
#            "name": "db name" //　名字
#        },
#        {
#            "format": "markPoint",　　// 在k 线上面标识
#            "yIndex": "0",　　//  刻度方位，０　左边，１右边
#            "isExt": "1",　　//  ０　下面副图区，１主图区
#            "db": "list",　　　　 // 数组
#            "date": "list",  // 时间数组，可为空
#            "name": "db name" //　名字
#        },
#        {
#            "format": "table", // table 显示，主要在讨论区
#            "db": "pandas json",　//  pandas 格式 json
#            "name": "db name"　// 名字
#        }
#    ],
#    "tips":{}  //定时调用的时候，引发提醒
#}

import json

class buildReturnJson():

    def __init__(self):
        self._rawma = 1
        self._data = []
        self._format = "table"
        self._yIndex = 0
        self._db = None
        self._name = None
        self._date = None
        self._index = 0
        self._isExt = 0

    def Index(self, i):
        self._index = i

    def isExt(self, e):
        self._isExt = e

    def RawMa(self, v):
        """
            RawMa
        Parameters
        ----------
            v:int  0 隐藏原来的平均线,1 显示原来的平均线
        """
        self._rawma = v

    def formats(self,f="table"):
        """
            format　设置格式
        Parameters
        ----------
            f:String 　 table　line bar
        """
        self._format = f

    def yIndex(self, y):
        self._yIndex = y

    def date(self, l):
        """
            date 时间数组
        Parameters
        ----------
            l:list
        """
        self._date = l

    def db(self, o):
        """
            db 设置数据，list 或者 json 结构
        Parameters
        ----------
            o:Object
        """
        self._db = o

    def name(self, n):
        """
            name 设置名字
        Parameters
        ----------
            n:String
        """
        self._name = n

    def buildData(self):
        """
            buildData 生成节点数据
        Parameters
        ---------
        """
        data = {}
        data["format"] = self._format
        data["yIndex"] = self._yIndex
        data["isExt"] = self._isExt
        data["db"] = self._db

        if self._date is not None:
            data["date"] = self._date

        data["name"] = self._name
        self._data.append(data)

    def getResult(self):
        """
            getResult 返回结果
        Return
        ------
            json
        """
        rj = {}
        rj["rawma"] = self._rawma
        rj["data"] = self._data

        return json.dumps(rj)
