import unittest
from datetime import datetime

# from Products.Silva.tests.test_xmlimport import SilvaXMLTestCase
from silva.app.news.tests.SilvaNewsTestCase import FunctionalLayer

# XXX import error
# class TestImport(SilvaXMLTestCase):
class TestImport(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        super(TestImport, self).setUp()

    def test_import_news_filter(self):
        self.import_file('import_newsfilter.xml', globs=globals())
        self.assertTrue(hasattr(self.root, 'export'))
        self.assertTrue(hasattr(self.root.export, 'filter'))
        self.assertTrue(hasattr(self.root.export, 'newspub'))
        self.assertEquals([self.root.export.newspub],
                          self.root.export.filter.get_sources())
        self.assertEquals('News Filter', self.root.export.filter.get_title())

    def test_import_agenda_filter(self):
        self.import_file('import_agendafilter.xml', globs=globals())
        self.assertTrue(hasattr(self.root, 'export'))
        self.assertTrue(hasattr(self.root.export, 'filter'))
        self.assertTrue(hasattr(self.root.export, 'newspub'))
        self.assertEquals([self.root.export.newspub],
                          self.root.export.filter.get_sources())
        self.assertEquals('Agenda Filter', self.root.export.filter.get_title())

    def test_import_news_viewer(self):
        self.import_file('import_newsviewer.xml', globs=globals())
        self.assertTrue(hasattr(self.root.export, 'viewer'))
        self.assertEquals([self.root.export.newspub],
                          self.root.export.filter.get_sources())
        self.assertEquals([self.root.export.filter],
                          self.root.export.viewer.get_filters())
        self.assertEquals('News Viewer', self.root.export.viewer.get_title())

    def test_import_news_item(self):
        self.import_file('import_newsitem.xml', globs=globals())
        self.assertTrue(hasattr(self.root.export, 'newspub'))
        self.assertTrue(hasattr(self.root.export.newspub, 'news'))
        news = self.root.export.newspub.news
        version = news.get_editable()
        self.assertEquals(['all'], version.get_subjects())
        self.assertEquals(['generic'], version.get_target_audiences())
        self.assertEquals(
            datetime(2010, 9, 30, 10, 0, 0),
            version.get_display_datetime())

    def test_import_agenda_item(self):
        self.import_file('import_agendaitem.xml', globs=globals())
        self.assertTrue(hasattr(self.root.export, 'newspub'))
        self.assertTrue(hasattr(self.root.export.newspub, 'event'))
        version = self.root.export.newspub.event.get_viewable()

        self.assertEquals('Europe/Amsterdam', version.get_timezone_name())
        timezone = version.get_timezone()
        self.assertEquals(datetime(2010, 9, 1, 10, 0, 0, tzinfo=timezone),
            version.get_start_datetime())
        self.assertEquals('Rotterdam', version.get_location())
        self.assertTrue(version.is_all_day())
        self.assertEquals(['all'], version.get_subjects())
        self.assertEquals(['generic'], version.get_target_audiences())
        self.assertEquals('FREQ=DAILY;UNTIL=20100910T123212Z',
            version.get_recurrence())
        self.assertEquals('Europe/Amsterdam', version.get_timezone_name())
        self.assertEquals(
            datetime(2010, 9, 30, 10, 0, 0),
            version.get_display_datetime())


def test_suite():
    suite = unittest.TestSuite()
    # suite.addTest(unittest.makeSuite(TestImport))
    return suite
