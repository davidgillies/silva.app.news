# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from datetime import datetime
import unittest

from silva.app.news.indexing import IntegerRangesIndex


class Doc(object):

    def __init__(self, ranges):
        self.ranges = ranges

    def ranges(self):
        return self.ranges


def utc_datetime_to_timestamp(dt):
    return int(dt.strftime("%s"))


class IntegerRangesIndexTestCase(unittest.TestCase):

    def setUp(self):
        self.index = IntegerRangesIndex('ranges')

    def _get_range(self, range_id):
        return self.index._IntegerRangesIndex__get_range(range_id)

    def test_indexing_a_document(self):
        now = utc_datetime_to_timestamp(datetime.now())
        r1 = (now, now + 60,)
        r2 = (now + 120, now + 240,)
        ranges = [r1, r2,]
        doc = Doc(ranges)
        docid = 1

        self.index.index_object(docid, doc)

        self.assertEquals(set(ranges),
            set(map(self._get_range, self.index._unindex[docid])))

        self.assertEquals(r1,
            self._get_range(self.index._since_index[now]))
        self.assertEquals(r2,
            self._get_range(self.index._since_index[now + 120]))

        self.assertEquals(r1,
            self._get_range(self.index._until_index[now + 60]))
        self.assertEquals(r2,
            self._get_range(self.index._until_index[now + 240]))

    def test_reindexing_a_document_removing_an_item(self):
        now = utc_datetime_to_timestamp(datetime.now())
        r1 = (now, now + 60,)
        r2 = (now + 120, now + 240,)
        r3 = (now, now + 3600)
        ranges = [r1, r2, r3]
        ranges2 = [r2, r3]
        doc1 = Doc(ranges)
        doc2 = Doc(ranges2)
        docid = 1

        # index document with ranges
        self.index.index_object(docid, doc1)

        self.assertEquals(3, len(self.index._unindex.get(docid)))
        self.assertEquals(set(ranges),
            set(map(self._get_range, self.index._unindex[docid])))

        # reindex document with ranges2
        self.index.index_object(docid, doc2)

        self.assertEquals(2, len(self.index._unindex.get(docid)))
        self.assertEquals(set(ranges2),
            set(map(self._get_range, self.index._unindex[docid])))

    def test_length(self):
        now = utc_datetime_to_timestamp(datetime.now())
        r1 = (now, now + 60,)
        r2 = (now + 120, now + 240,)
        r3 = (now, now + 3600)
        ranges = [r1, r2, r3]
        ranges2 = [r2, r3]
        doc1 = Doc(ranges)
        doc2 = Doc(ranges2)
        # adding 2 documents
        self.index.index_object(1, doc1)
        self.assertEquals(1, len(self.index))
        self.index.index_object(2, doc2)
        self.assertEquals(2, len(self.index))

        # adding an already indexed documents
        # nothing should change
        self.index.index_object(1, doc1)
        self.assertEquals(2, len(self.index))
        self.index.index_object(2, doc2)
        self.assertEquals(2, len(self.index))

        # unindexing documents
        self.index.unindex_object(2)
        self.assertEquals(1, len(self.index))
        self.index.unindex_object(1)
        self.assertEquals(0, len(self.index))

    def test_unofficial_size(self):
        now = utc_datetime_to_timestamp(datetime.now())
        r1 = (now, now + 60,)
        r2 = (now + 120, now + 240,)
        r3 = (now, now + 3600)
        ranges = [r1, r2, r3]
        ranges2 = [r2, r3]
        doc1 = Doc(ranges)
        doc2 = Doc(ranges2)
        # adding 2 documents
        self.index.index_object(1, doc1)
        self.index.index_object(2, doc2)
        self.assertEquals(2, self.index.numObjects())
        self.assertEquals(3, self.index.indexSize())
        doc1.ranges = [r2]
        self.index.index_object(1, doc1)
        self.assertEquals(2, self.index.numObjects())
        self.assertEquals(2, self.index.indexSize())
        self.index.unindex_object(1)
        self.index.unindex_object(2)
        self.assertEquals(0, self.index.numObjects())
        self.assertEquals(0, self.index.indexSize())

    def test_unindex_object(self):
        now = utc_datetime_to_timestamp(datetime.now())
        r1 = (now, now + 60,)
        r2 = (now + 120, now + 240,)
        ranges = [r1, r2,]
        doc = Doc(ranges)
        docid = 1

        self.index.index_object(docid, doc)
        indexed_ranges_ids = self.index._unindex[docid]
        self.index.unindex_object(docid)

        for range_id in indexed_ranges_ids:
            range_ = self._get_range(range_id)
            self.assertEquals(None, range_)


class QueryIntegerRangesIndexTestCase(unittest.TestCase):

    def setUp(self):
        self.index = IntegerRangesIndex('ranges')
        self.now = utc_datetime_to_timestamp(datetime.now())
        r1 = (self.now, self.now + 60)
        r2 = (self.now + 120, self.now + 240,)
        r3 = (self.now, self.now + 3600)
        r4 = (self.now, self.now + 180)
        r5 = (self.now - 120, self.now)
        doc1 = Doc([r1])
        doc2 = Doc([r2])
        doc3 = Doc([r3])
        doc4 = Doc([r4])
        doc5 = Doc([r5])
        doc0 = Doc([r1,r2,r3,r4,r5])
        self.index.index_object(1, doc1)
        self.index.index_object(2, doc2)
        self.index.index_object(3, doc3)
        self.index.index_object(4, doc4)
        self.index.index_object(5, doc5)
        self.index.index_object(0, doc0)

    def query(self, start, end):
        ret = self.index._apply_index(
            {'ranges': {'query': (start, end,)}})
        if ret is None:
            return None
        return set(ret[0])

    def test_apply_index(self):
        now = self.now

        self.assertEquals(self.query(now, now + 10), set([0,1,3,4,5]))
        self.assertEquals(self.query(now - 10000, now - 1000), set())
        self.assertEquals(self.query(now - 100, now - 1), set([0, 5]))
        self.assertEquals(self.query(now - 120, now + 3600), set([0,1,2,3,4,5]))
        self.assertEquals(self.query(now + 200, now + 210), set([0,2,3]))

    def test_apply_ranges_limits_32bits(self):
        past = utc_datetime_to_timestamp(datetime(1901, 12, 01, 10, 22))
        future = utc_datetime_to_timestamp(datetime(2040, 01, 02, 10, 22))

        self.assertEquals(self.query(past, past + 10), set())
        self.assertEquals(self.query(future, future + 10), set())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IntegerRangesIndexTestCase))
    suite.addTest(unittest.makeSuite(QueryIntegerRangesIndexTestCase))
    return suite
