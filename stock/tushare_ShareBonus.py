#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-


import json
import sys
import pandas as pd

import lxml.html
from lxml import etree
from pandas.compat import StringIO

import _index
from energy.db.emongo import emongo
from energy.db.dblist import dblist

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

def _get_ShareBonus_data(code):
    """
        获取沪深上市公司分红内容
    Parameters
    ---------
    code:string 代码

    Return
    -------
    DataFrame
        date,分红时间
        bonus,送股(股)
        tran,转增(股)
        divid,派息(税前)(元)(每10股)
        progress,进度
        gxdate,除权除息日
        regdate,股权登记日
    """
    url = "http://money.finance.sina.com.cn/corp/go.php/vISSUE_ShareBonus/stockid/%s.phtml"%(code)
    try:
        request = Request(url)
        text = urlopen(request, timeout=10).read()
        text = text.decode('GBK')

        text = text.replace('--', '')
        html = lxml.html.parse(StringIO(text))
        res = html.xpath("//table[@id='sharebonus_1']")

        sarr = [etree.tostring(node) for node in res]
        sarr = ''.join(sarr)

        df = pd.read_html(sarr)[0]
        CASHFLOW_COLS=['date','bonus','tran','divid','progress','gxdate','regdate','i','j','k','u']
        df.columns = CASHFLOW_COLS
        df.pop('u')
        df.pop('i')
        df.pop('j')
        df.pop('k')
        return df
    except Exception as e:
        print(e)


def getAllShareBonus():

        dbl = dblist()
        allCodeList = dbl.getAllCodeList()
        dbl.Close()

        emg = emongo()
        conn = emg.getCollectionNames("ShareBonus")
        conn.remove()

        for post in allCodeList:
            code = post["code"]
            df = _get_ShareBonus_data(code)
            cjson = df.to_json(orient="records")
            j = json.loads(cjson)
            dt = {}
            dt[str(code)] = j

            conn.insert(dt)
        emg.Close()

def main():
    if len(sys.argv) == 2:
        stock = sys.argv[1]
        print "get one stock:",stock

        emg = emongo()
        conn = emg.getCollectionNames("ShareBonus")
        df = _get_ShareBonus_data(stock)
        cjson = df.to_json(orient="records")
        j = json.loads(cjson)
        dt = {}
        dt[str(stock)] = j
        conn.insert(dt)
        emg.Close()
    else:
        print "get all stock"
        getAllShareBonus()

if __name__ == "__main__":
    main()
