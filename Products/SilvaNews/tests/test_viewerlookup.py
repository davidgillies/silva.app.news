import unittest
from Products.SilvaNews.tests.SilvaNewsTestCase import SilvaNewsTestCase
from Products.SilvaNews.traverser import set_parent
from Products.SilvaNews.interfaces import INewsViewer


class TestLookupViewer(SilvaNewsTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.news_publication = self.add_news_publication(
            self.root, "newspub", "News")
        self.news_publication.manage_delObjects(['index'])
        self.news_viewer = self.add_news_viewer(
            self.news_publication, 'index', 'News')
        self.news_item = self.add_published_news_item(
            self.news_publication, "news_item", "Item")

    def test_find_default_viewer(self):
        looked_up_viewer = INewsViewer(self.news_item, None)
        self.assertEqual(self.news_viewer, looked_up_viewer)

    def test_find_viewer_with_viewer_proxing(self):
        root_viewer = self.add_news_viewer(
            self.root, 'root_viewer', 'Root news viewer')
        proxied = set_parent(root_viewer, self.news_item)
        looked_up_viewer = INewsViewer(proxied, None)
        self.assertEqual(root_viewer, looked_up_viewer)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLookupViewer))
    return suite
