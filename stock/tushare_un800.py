#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-

import tushare as ts
import json
import pandas as pd
import _index
from energy.db.emongo import emongo

class UN800():
    def run(self):
        df500 = ts.get_zz500s()
        df300 = ts.get_hs300s()

        df800 = pd.DataFrame(df500)
        df800 = df800.append(df300,ignore_index=True)
        df800.sort_values(by="code")

        un800 = json.loads(df800.to_json(orient="records"))

        emg = emongo()
        szCode = emg.getCollectionNames("un800")
        szCode.remove()
        szCode.insert(un800)
        emg.Close()

def main():
    un = UN800()
    un.run()

if __name__ == "__main__":
    main()
