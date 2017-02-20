#!/usr/bin/python2
# -*- coding: utf-8 -*-
#  QTaLib
#
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#   talib 函数集合.
#

from talib import abstract
import numpy as np

class QTaLib():
    def __init__(self):
        self._FunName = ""
        self._KLine = None

    def SetFunName(self, n):
        """
            SetFunName 设置函数名称
        Parameters
        ----------
            n:String
        """
        self._FunName = n

    def SetKline(self, k):
        """
            SetKline 设置k线数据
        Parameters
        ----------
            k:DataFrame
        """
        self._KLine = k

    def Run(self):
        """
            Run 执行
        Return
        ------
            narray
        """
        inputs = {
            'open': self._KLine.open.values,
            'high': self._KLine.high.values,
            'low': self._KLine.low.values,
            'close': self._KLine.close.values,
            'volume': self._KLine.volume.values
        }
        try:
            fun = abstract.Function(self._FunName)
        except:
            return None
        res = fun(inputs)
        if type(res) is list:
            for o in range(len(res)):
                res[o][np.isnan(res[o])] = 0
        else:
            res[np.isnan(res)] = 0
        return res
