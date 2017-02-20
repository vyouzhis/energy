#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-

import tushare as ts
from tushare.stock import cons as ct
from tushare.stock import news_vars as nv
import pandas as pd
from datetime import datetime
import lxml.html
from lxml import etree
import re
import json
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

from time import localtime, strftime, time
import _index
from energy.db.emongo import emongo

class SinaNews():
    def _random(self, n=16):
        from random import randint
        start = 10 ** (n - 1)
        end = (10 ** n) - 1
        return str(randint(start, end))

    def get_latest_news(self,top=None, page=3):
        """
            获取即时财经新闻

        Parameters
        --------
            top:数值，显示最新消息的条数，默认为80条

        Return
        --------
            DataFrame
                classify :新闻类别
                title :新闻标题
                time :发布时间
                url :新闻链接
        """
        LATEST_URL = '%sroll.news.%s/interface/%s?col=43&spec=&type=&ch=03&k=&offset_page=0&offset_num=0&num=%s&asc=&page=%d&r=0.%s'
        top = ct.PAGE_NUM[2] if top is None else top
        try:
            request = Request(LATEST_URL % (ct.P_TYPE['http'], ct.DOMAINS['sina'],
                                                    ct.PAGES['lnews'], top,page,
                                                    self._random()))
            #print LATEST_URL % (ct.P_TYPE['http'], ct.DOMAINS['sina'],ct.PAGES['lnews'], top,page, self._random())

            data_str = urlopen(request, timeout=10).read()
            data_str = data_str.decode('GBK')
            data_str = data_str.split('=')[1][:-1]
            data_str = eval(data_str, type('Dummy', (dict,),
                                        dict(__getitem__ = lambda s, n:n))())
            data_str = json.dumps(data_str)
            data_str = json.loads(data_str)
            data_str = data_str['list']
            """
            data = []
            for r in data_str:
                rt = datetime.fromtimestamp(r['time'])
                rtstr = datetime.strftime(rt, "%m-%d %H:%M")
                arow = [r['channel']['title'], r['title'], rtstr, r['url']]
                data.append(arow)
            """
            df = pd.DataFrame(data_str, columns=nv.LATEST_COLS_C)
            return df
        except Exception as er:
            print(str(er))

    def run(self):
        #self.get_latest_news()
        df = self.get_latest_news(50, 10)
        print df.title
        """
        ndf = df[~(df.url.str.match(".*jsy", as_indexer=True))]

        contTime = strftime("%m-%d %H:%M", localtime(time()-3660))

        ndf = df[df.time > contTime]

        emg = emongo()
        szCode = emg.getCollectionNames("AllStockClass")

        codeList = list(szCode.find({},{"_id":0, "name":1,"code":1}))

        newTalk = {}
        for post in codeList:
            name = post['name'].replace("*", "").strip()
            re_name = ".*"+name
            nadf = ndf[ndf.title.str.match(re_name, as_indexer=True)]
            if len(nadf):
                newTalk[post['code']] = nadf.to_dict(orient="list")

        print newTalk
        #print json.dumps(newTalk)
        """

def main():
    news = SinaNews()
    news.run()

if __name__ == "__main__":
    main()


