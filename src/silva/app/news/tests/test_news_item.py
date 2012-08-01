
import unittest

from zope.interface.verify import verifyObject

from Products.Silva.ftesting import public_settings
from Products.Silva.testing import assertTriggersEvents

from silva.core.interfaces import IPublicationWorkflow
from silva.app.news.interfaces import INewsItem, INewsItemVersion
from silva.app.news.testing import FunctionalLayer


class NewsItemTestCase(unittest.TestCase):
    """Test the NewsItem content type.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_item(self):
        factory = self.root.manage_addProduct['silva.app.news']
        with assertTriggersEvents('ContentCreatedEvent'):
            factory.manage_addNewsItem('item', 'News Item')
        item = self.root._getOb('item', None)
        self.assertTrue(verifyObject(INewsItem, item))
        version = item.get_editable()
        self.assertTrue(verifyObject(INewsItemVersion, version))

    def test_rendering(self):
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addNewsItem('item', 'News Item')
        IPublicationWorkflow(self.root.item).publish()

        with self.layer.get_browser(public_settings) as browser:
            self.assertEqual(browser.open('/root/item'), 200)
            self.assertIn('News Item', browser.inspect.title)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NewsItemTestCase))
    return suite
