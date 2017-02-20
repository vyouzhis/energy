#!/usr/bin/python2
# -*- coding: utf-8 -*-
# emongo
#
# use etomc2 mongo
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#    python like mongo
#

import pymongo
class emongo():
    def __init__(self):
        self._IP="127.0.0.1"
        self._Port=27017
        self._conn = None

    def getCollectionNames(self, name):
        self._conn = pymongo.MongoClient(self._IP, port=self._Port)
        sdb = self._conn.etomc2[name]
        return sdb

    def Close(self):
        self._conn.close()
