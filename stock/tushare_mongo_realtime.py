#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-

import tushare as ts
import sys

def realtime():
    stock = []
    if(len(sys.argv) > 1):
        for i in range(1,len(sys.argv)):
            stock.append(sys.argv[i])
    else:

        stock.append("sh")
        stock.append("sz")
        stock.append("hs300")
        stock.append("sz50")

    df = ts.get_realtime_quotes(stock)
    JsonList = []
    for i in df.index:
        mydf = df.loc[i]
        mydf["date"] = str(i)
        JsonList.append(mydf.to_dict())

    print JsonList

def main():
    realtime()

if __name__ == "__main__":
    main()
