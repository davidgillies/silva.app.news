# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.9 $

import unittest
import Zope
Zope.startup()

from DateTime import DateTime
from Products.ZCatalog.ZCatalog import ZCatalog
from Testing import makerequest

from Products.SilvaNews.ServiceNews import DuplicateError, NotEmptyError
from Products.Silva.tests.test_SilvaObject import hack_create_user
from Products.SilvaNews.install import install

def add_helper(object, typename, id, title):
    getattr(object.manage_addProduct['Silva'], 'manage_add%s' % typename)(id, title)
    return getattr(object, id)

def add_helper_news(object, typename, id, title):
    getattr(object.manage_addProduct['SilvaNews'], 'manage_add%s' % typename)(id, title)
    return getattr(object, id)

def setup_catalog(context, columns, indexes):
    catalog = context.service_catalog

    existing_columns = catalog.schema()
    existing_indexes = catalog.indexes()

    for column_name in columns:
        if column_name in existing_columns:
            continue
        catalog.addColumn(column_name)

    for field_name, field_type in indexes:
        if field_name in existing_indexes:
            continue
        catalog.addIndex(field_name, field_type)

class NewsViewerBaseTestCase(unittest.TestCase):
    def setUp(self):
        get_transaction().begin()
        self.connection = Zope.DB.open()
        self.root = makerequest.makerequest(self.connection.root()['Application'])
        self.root.REQUEST['URL1'] = ''
        self.REQUEST = self.root.REQUEST
        self.REQUEST.set = lambda a, b: None
        hack_create_user(self.root)

        self.root.manage_addProduct['Silva'].manage_addRoot(
            'root', 'Root')
        self.sroot = self.root.root

        install(self.sroot)
        
        service_news = self.service_news = self.sroot.service_news
        service_news.add_subject('test')
        service_news.add_subject('test2')
        service_news.add_target_audience('test')
        service_news.add_target_audience('test2')

        self.service_catalog = self.sroot.service_catalog
        
        self.source1 = add_helper_news(self.sroot, 'NewsPublication', 'source1', 'Folder 1')

        self.item1_1 = add_helper_news(self.source1, 'PlainArticle', 'art1', 'Article 1')
        self.item1_1.set_next_version_publication_datetime(DateTime())
        getattr(self.item1_1, '0').set_subjects(['test'])
        getattr(self.item1_1, '0').set_target_audiences(['test'])
        self.item1_1.approve_version()
        self.item1_1._update_publication_status()

        self.item1_2 = add_helper_news(self.source1, 'PlainArticle', 'art2', 'Article 2')
        self.item1_2.set_next_version_publication_datetime(DateTime())
        getattr(self.item1_2, '0').set_subjects(['test2'])
        getattr(self.item1_2, '0').set_target_audiences(['test2'])
        self.item1_2.approve_version()
        self.item1_2._update_publication_status()

        self.source2 = add_helper_news(self.sroot, 'NewsPublication', 'source2', 'Folder 2')
        self.source2.set_private(1)

        self.folder = add_helper(self.sroot, 'Folder', 'somefolder', 'Some Folder')
        self.source3 = add_helper_news(self.folder, 'NewsPublication', 'source3', 'Folder 3')
        self.source3.set_private(1)

        self.item1_3 = add_helper_news(self.source3, 'PlainArticle', 'art3', 'Article 3')
        self.item1_3.set_next_version_publication_datetime(DateTime())
        getattr(self.item1_3, '0').set_subjects(['test'])
        getattr(self.item1_3, '0').set_target_audiences(['test'])
        self.item1_3.approve_version()
        self.item1_3._update_publication_status()

        self.newsfilter = add_helper_news(self.sroot, 'NewsFilter', 'newsfilter', 'NewsFilter')
        self.newsfilter.add_source('/root/source1', 1)

        self.newsviewer = add_helper_news(self.newsfilter, 'NewsViewer', 'newsviewer', 'NewsViewer')
        self.newsviewer.set_filter('/root/newsfilter', 1)

    def tearDown(self):
        get_transaction().abort()
        self.connection.close()

class NewsViewerTestCase(NewsViewerBaseTestCase):
    """Test the NewsViewer interface.
    """
    def test_filters(self):
        self.assert_(self.newsviewer.filters() == ['/root/newsfilter'])
        self.newsviewer.set_filter('/root/newsfilter', 0)
        self.assert_(self.newsviewer.filters() == [])

    def test_findfilters(self):
        self.assert_(self.newsviewer.findfilters() == ['/root/newsfilter'])

    def test_findfilters_pairs(self):
        self.assert_(self.newsviewer.findfilters_pairs() == [('NewsFilter (/root/newsfilter)', '/root/newsfilter')])

    def test_verify_filters(self):
        self.assert_(self.newsviewer.filters() == ['/root/newsfilter'])
        self.sroot.manage_delObjects('newsfilter')
        self.assert_(self.newsviewer.filters() == [])

    def test_get_items(self):
        iops = [i.object_path for i in self.newsviewer.get_items()]
        self.assert_(('', 'root', 'source1', 'art1') in iops)
        self.assert_(('', 'root', 'source1', 'art2') in iops)
        self.assert_(len(iops) == 2)

        self.newsfilter.set_excluded_item(('', 'root', 'source1', 'art2'), 1)
        iops = [i.object_path for i in self.newsviewer.get_items()]
        self.assert_(('', 'root', 'source1', 'art1') in iops)
        self.assert_(not ('', 'root', 'source1', 'art2') in iops)
        self.assert_(len(iops) == 1)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NewsViewerTestCase, 'test'))
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
