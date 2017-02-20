#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-

import json
import lxml.html
import pandas as pd
import sys

from tushare.stock import news_vars as nv
from tushare.stock import cons as ct

import _index
from energy.db.emongo import emongo
from energy.db.dblist import dblist

class Notice():
    def __init__(self):
        self._code = ""
        self._init = 0

    def Init(self):
        self._init = 1

    def run(self):

        if self._init == 1:
            emg = emongo()
            szNotic = emg.getCollectionNames("StockNotices")
            szNotic.remove()
            emg.Close()

        dbl = dblist()
        clist = dbl.getAllCodeList()
        dbl.Close()

        for c in clist:
            cd = c["code"]
            self.getData(cd)

    def get_notices(self,codes=None, page=1):
        '''
        个股信息地雷
        Parameters
        --------
            code:股票代码
            date:信息公布日期

        Return
        --------
            DataFrame，属性列表：
            title:信息标题
            type:信息类型
            date:公告日期
            url:信息内容URL
        '''
        #print codes
        if codes is None:
            return None
        if codes.decode().isdigit():
# 0开头自动补sz，6开头补sh，3开头补sz，否则无效
            if codes.startswith('0'):
                self._code = 'sz' + codes
            elif codes.startswith('6'):
                self._code = 'sh' + codes
            elif codes.startswith('3'):
                self._code = 'sz' + codes
        url = "http://vip.stock.finance.sina.com.cn/corp/view/vCB_BulletinGather.php?stock_str=%s&page=%d"%(self._code, page)
        #print url
        html = lxml.html.parse(url)
        if not html:
            print "html is not found"
            return
        res = html.getroot().xpath('//table[@class=\"body_table\"]/tbody/tr')
        data = []
        for td in res:
            title = td.xpath('th/a/text()')
            if len(title) > 0:
                title = title[0]
            else:
                continue
            ctype = td.xpath('td[1]/text()')
            if len(ctype) > 0:
                ctype = ctype[0]
            else:
                continue
            date = td.xpath('td[2]/text()')
            if len(date) > 0:
                date = date[0]
            else:
                continue
            url = '%s%s%s'%(ct.P_TYPE['http'], ct.DOMAINS['vsf'], td.xpath('th/a/@href')[0])
            data.append([title, ctype, date, url])
        df = pd.DataFrame(data, columns=nv.NOTICE_INFO_CLS)

        return df

    def find(self, df):
        xe = u'回购部分'
        xdf = df[df.title.apply(lambda x: x.find(xe)) != -1]
        if xdf.title.count() > 0:
            print xdf.title

    def getData(self, code):
        ndf = pd.DataFrame()
        n = 1
        emg = emongo()
        szNotic = emg.getCollectionNames("StockNotices")
        d={}
        notices = list(szNotic.find({code:{"$exists":1}},{code:1,"_id":1}))
        if len(notices) == 0:
            while 1:
                df = self.get_notices(code, n)
                if n == 1:
                    ndf = df
                    n+=1
                    continue
                if df.empty == False:
                    ndf = ndf.append(df)
                    n+=1
                else:
                    break
            if ndf.empty:
                return
            d[code] = json.loads(ndf.to_json(orient="records"))

            szNotic.insert(d)
            emg.Close()
        else:
            print code," is update"
            ndf = self.get_notices(code, n)
            if ndf.empty == True:
                print "ndf is empty"
                emg.Close()
                return

            _id =  notices[0]["_id"]
            cdata = notices[0][code]
            ndf = ndf.append(pd.DataFrame(cdata))
            ndf = ndf.drop_duplicates()
            d[code] = json.loads(ndf.to_json(orient="records"))
            szNotic.update({"_id":{"$eq":_id}}, {"$set":  d })
            emg.Close()

def main():
    if len(sys.argv) == 2:
        stock = sys.argv[1]
        print "get one stock:",stock
        notice = Notice()
        #notice.Init()
        notice.getData(stock)
    else:
        notice = Notice()
        #notice.Init()
        notice.run()

if __name__ == "__main__":
    main()
