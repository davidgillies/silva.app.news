import unittest
from Products.SilvaNews.tests.SilvaNewsTestCase import NewsBaseTestCase


class TestViewerPublicViews(NewsBaseTestCase):

    def setUp(self):
        super(TestViewerPublicViews, self).setUp()
        self.browser = self.layer.get_browser()

    def test_index(self):
        status = self.browser.open('http://localhost/root/newsviewer')
        self.assertEquals(200, status)

    def test_archive(self):
        status = self.browser.open('http://localhost/root/newsviewer/archives')
        self.assertEquals(200, status)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestViewerPublicViews))
    return suite

