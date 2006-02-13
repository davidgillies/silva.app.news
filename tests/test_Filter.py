# Copyright (c) 2002-2006 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.13 $
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
 
import SilvaTestCase

from DateTime import DateTime

def add_helper(object, typename, id, title):
    getattr(object.manage_addProduct['Silva'], 'manage_add%s' % typename)(id, title)
    return getattr(object, id)

def add_helper_news(object, typename, id, title):
    getattr(object.manage_addProduct['SilvaNews'], 'manage_add%s' % typename)(id, title)
    item = getattr(object, id)
    return item

class NewsFilterBaseTestCase(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        self.sroot = self.root
        
        self.service_news = service_news = self.sroot.service_news
        service_news.add_subject('test', 'Test')
        service_news.add_subject('test2', 'Test 2')
        service_news.add_target_audience('test', 'Test')
        service_news.add_target_audience('test2', 'Test 2')

        self.service_catalog = self.sroot.service_catalog

        self.source1 = add_helper_news(self.sroot, 'NewsPublication', 'source1', 'Folder 1')

        self.item1_1 = add_helper_news(self.source1, 'PlainArticle', 'art1', 'Article 1')
        self.item1_1.set_next_version_publication_datetime(DateTime())
        getattr(self.item1_1, '0').set_subjects(['test'])
        getattr(self.item1_1, '0').set_target_audiences(['test'])
        self.item1_1.approve_version()
        self.item1_1._update_publication_status()
        getattr(self.item1_1, '0').set_display_datetime(DateTime())

        self.item1_2 = add_helper_news(self.source1, 'PlainArticle', 'art2', 'Article 2')
        self.item1_2.set_next_version_publication_datetime(DateTime())
        getattr(self.item1_2, '0').set_subjects(['test2'])
        getattr(self.item1_2, '0').set_target_audiences(['test2'])
        self.item1_2.approve_version()
        self.item1_2._update_publication_status()
        getattr(self.item1_2, '0').set_display_datetime(DateTime())

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
        getattr(self.item1_3, '0').set_display_datetime(DateTime())

        self.newsfilter = add_helper_news(self.sroot, 'NewsFilter', 'newsfilter', 'NewsFilter')

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
        self.newsfilter.set_subjects(['test'])
        self.newsfilter.set_target_audiences(['test'])
        self.newsfilter.add_source('/root/source1', 1)
        self.newsfilter.add_source('/root/source2', 1)
        self.newsfilter.add_source('/root/somefolder/source3', 1)
        res = ['%s - %s' % (i.id, i.object_path) for i in self.service_catalog({})]
        resids = [i.object_path[-1] for i in self.newsfilter.search_items('test')]
        self.assert_('art1' in resids)
        self.assert_('art2' not in resids)
        self.assert_('art3' not in resids)
        self.assert_(len(resids) == 1)

    def test_display_datetime(self):
        self.newsfilter.set_subjects(['test', 'test2'])
        self.newsfilter.set_target_audiences(['test', 'test2'])
        self.newsfilter.add_source('/root/source1', 1)
        self.newsfilter.add_source('/root/somefolder/source3', 1)
        items = self.newsfilter.get_last_items(2)
        itemids = [item.object_path[-1] for item in items]
        self.assertEquals(itemids, ['art1', 'art2'])
        # normal code would never set the display datetime on the viewable,
        # I guess
        self.item1_2.get_viewable().set_display_datetime(DateTime() + 1)
        items = self.newsfilter.get_last_items(2)
        itemids = [item.object_path[-1] for item in items]
        self.assertEquals(itemids, ['art2', 'art1'])

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(NewsFilterTestCase))
        return suite
