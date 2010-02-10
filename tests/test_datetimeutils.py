import unittest
from Products.SilvaNews.datetimeutils import *


class TestDateTime(unittest.TestCase):

    def test_datetime_set_local_timezone(self):
        dt = datetime(2010, 2, 1, 10, 20, 03)
        dtltz = datetime_with_timezone(dt)
        self.assertEquals(local_timezone, dtltz.tzinfo)
        self.assertEquals(10, dtltz.hour)
        self.assertEquals(20, dtltz.minute)
        self.assertEquals(3, dtltz.second)

    def test_utc_with_Datetime_tzinfo(self):
        now = DateTime()
        utcnow = utc_datetime(now)
        self.assertEquals(UTC, utcnow.tzinfo)

    def test_utc_with_Datetime(self):
        nowDT = utc_datetime(DateTime(2010, 2, 1, 10, 20, 03))
        nowdt = utc_datetime(datetime(2010, 2, 1, 10, 20, 03))
        self.assertEquals(nowdt, nowDT)
        self.assertEquals(str(nowdt), str(nowDT))

    def test_dt_stamp(self):
        """ the same datetime in different time zone should have
        the same unix timestamp
        """
        dt = datetime(2010, 2, 1, 10, 20, 03)
        ldt = datetime_with_timezone(datetime(2010, 2, 1, 10, 20, 03))
        stamp = 1265016003
        nowDT = utc_datetime(DateTime(2010, 2, 1, 10, 20, 03))
        nowdt = utc_datetime(datetime(2010, 2, 1, 10, 20, 03))
        self.assertEquals(stamp, utc_datetime_to_unixtimestamp(dt))
        self.assertEquals(stamp, utc_datetime_to_unixtimestamp(nowdt))
        self.assertEquals(stamp, utc_datetime_to_unixtimestamp(nowDT))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDateTime))
    return suite
