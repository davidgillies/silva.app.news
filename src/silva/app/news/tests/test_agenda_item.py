
import unittest

from zope.interface.verify import verifyObject

from Products.Silva.ftesting import public_settings

from silva.core.interfaces import IPublicationWorkflow
from silva.app.news.interfaces import IAgendaItem, IAgendaItemVersion
from silva.app.news.testing import FunctionalLayer


class AgendaItemTestCase(unittest.TestCase):
    """Test the AgendaItem content type.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_item(self):
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addAgendaItem('event', 'Testing event')
        event = self.root._getOb('event', None)
        self.assertTrue(verifyObject(IAgendaItem, event))
        version = event.get_editable()
        self.assertTrue(verifyObject(IAgendaItemVersion, version))

    def test_rendering(self):
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addNewsItem('event', 'Testing event')
        IPublicationWorkflow(self.root.event).publish()

        with self.layer.get_browser(public_settings) as browser:
            self.assertEqual(browser.open('/root/event'), 200)
            self.assertIn('Testing event', browser.inspect.title)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AgendaItemTestCase))
    return suite
