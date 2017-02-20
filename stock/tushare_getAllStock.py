#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-

from __future__ import division
import _index
from energy.db.emongo import emongo

import tushare as ts

class getAllStock():
    def run(self):
        df = ts.get_industry_classified()

        JsonList = []
        for i in df.index:
            JsonList.append(df.loc[i].to_dict())

        emg = emongo()
        sdb = emg.getCollectionNames("AllStockClass")
        sdb.remove()
        sdb.insert(JsonList)
        emg.Close()

def main():
    gas = getAllStock()
    gas.run()

if __name__ == "__main__":
    main()
