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
from Products.Silva.install import install as silva_install

def set(key, value):
    pass

def add_helper(object, typename, id, title):
    getattr(object.manage_addProduct['Silva'], 'manage_add%s' % typename)(id, title)
    return getattr(object, id)

def add_helper_news(object, typename, id, title):
    getattr(object.manage_addProduct['SilvaNews'], 'manage_add%s' % typename)(id, title)
    return getattr(object, id)

class NewsFilterBaseTestCase(unittest.TestCase):
    def setUp(self):
        get_transaction().begin()
        self.connection = Zope.DB.open()
        self.root = makerequest.makerequest(
            self.connection.root()['Application'])
        self.root.REQUEST['URL1'] = ''
        self.REQUEST = self.root.REQUEST
        self.REQUEST.set = set
        hack_create_user(self.root)

        self.root.manage_addProduct['Silva'].manage_addRoot(
            'root', 'Root')
        self.sroot = self.root.root

        install(self.sroot)

        self.service_news = service_news = self.sroot.service_news
        service_news.add_subject('test')
        service_news.add_subject('test2')
        service_news.add_target_audience('test')
        service_news.add_target_audience('test2')

        #self.root.manage_addProduct['ZCatalog'].manage_addZCatalog('service_catalog', 'ZCat')
        #self.service_catalog = getattr(self.root, 'service_catalog')
        #columns = ['is_private', 'object_path', 'fulltext', 'version_status', 'path', 'subjects', 'target_audiences',
        #            'publication_datetime']
        #indexes = [('meta_type', 'FieldIndex'), ('is_private', 'FieldIndex'), ('parent_path', 'FieldIndex'),
        #            ('version_status', 'FieldIndex'), ('subjects', 'KeywordIndex'), ('target_audiences', 'KeywordIndex'),
        #            ('creation_datetime', 'FieldIndex'), ('publication_datetime', 'FieldIndex'), ('fulltext', 'TextIndex'),
        #            ('path', 'PathIndex')]
        #setup_catalog(self.root, columns, indexes)

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

    def tearDown(self):
        get_transaction().abort()
        self.connection.close()

class NewsFilterTestCase(NewsFilterBaseTestCase):
    """Test the NewsFilter interface.
    """

    def test_find_sources(self):
        res = self.newsfilter.find_sources()
        self.assert_('source1' in [i.id for i in res])
        self.assert_('source2' in [i.id for i in res])
        self.assert_('source3' not in [i.id for i in res])
        self.assert_(len(res) == 2)

    def test_sources(self):
        self.assert_(self.newsfilter.sources() == [])
        self.newsfilter.add_source('/root/source1', 1)
        self.assert_(self.newsfilter.sources() == ['/root/source1'])
        self.newsfilter.add_source('/root/source2', 1)
        self.assert_('/root/source1' in self.newsfilter.sources())
        self.assert_('/root/source2' in self.newsfilter.sources())
        self.assert_(len(self.newsfilter.sources()) == 2)
        self.newsfilter.add_source('/root/banaan', 1)
        self.assert_('/root/banaan' not in self.newsfilter.sources())
        self.assert_(len(self.newsfilter.sources()) == 2)
        self.newsfilter.add_source('/root/somefolder/source3', 1)
        self.assert_('/root/somefolder/source3' not in self.newsfilter.sources())
        self.assert_(len(self.newsfilter.sources()) == 2)
        self.newsfilter.add_source('/root/source2', 0)
        self.assert_(self.newsfilter.sources() == ['/root/source1'])

    def test_items(self):
        self.newsfilter.set_subjects(['test'])
        self.newsfilter.set_target_audiences(['test'])
        self.newsfilter.add_source('/root/source1', 1)
        self.newsfilter.add_source('/root/somefolder/source3', 1)
        res = self.newsfilter.get_all_items()
        pps = ['/'.join(i.object_path) for i in res]
        self.assert_('/root/source1/art1' in pps)
        self.assert_(not '/root/source1/art2' in pps)
        self.assert_(not '/root/source1/somefolder/art3' in pps)
        self.assert_(len(pps) == 1)
        self.newsfilter.set_excluded_item(('', 'root', 'source1', 'art1'), 1)
        self.assert_(self.newsfilter.excluded_items() == [('', 'root', 'source1', 'art1')])
        self.assert_([i.object_path for i in self.newsfilter.get_last_items(10)] == [])

    def test_synchronize_with_service(self):
        self.newsfilter.set_subjects(['test'])
        self.newsfilter.synchronize_with_service()
        self.assert_(self.newsfilter.subjects() == ['test'])
        self.service_news.remove_subject('test')
        self.newsfilter.synchronize_with_service()
        self.assert_(self.newsfilter.subjects() == [])

    def test_search_items(self):
        self.newsfilter.add_source('/root/source1', 1)
        self.newsfilter.add_source('/root/source2', 1)
        self.newsfilter.add_source('/root/somefolder/source3', 1)
        res = ['%s - %s' % (i.id, i.object_path) for i in self.service_catalog({})]
        resids = [i.object_path[-1] for i in self.newsfilter.search_items('test')]
        self.assert_('art1' in resids)
        self.assert_('art2' not in resids)
        self.assert_('art3' not in resids)
        self.assert_(len(resids) == 1)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NewsFilterTestCase, 'test'))
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
