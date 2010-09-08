# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.testing import SilvaLayer
from DateTime import DateTime
import transaction
import Products.SilvaNews
import unittest


class SilvaNewsLayer(SilvaLayer):

    def _install_application(self, app):
        super(SilvaNewsLayer, self)._install_application(app)
        app.root.service_extensions.install('SilvaNews')
        transaction.commit()


class SilvaNewsTestCase(unittest.TestCase):

    layer = SilvaNewsLayer(Products.SilvaNews, zcml_file='configure.zcml')

    def setUp(self):
        self.root = self.layer.get_application()
        self.service_news = self.root.service_news
        self.catalog = self.root.service_catalog

    def add_news_publication(self, object, id, title, **kw):
        factory = object.manage_addProduct['SilvaNews']
        factory.manage_addNewsPublication(id, title, **kw)
        return getattr(object, id)

    def add_plain_article(self, object, id, title, **kw):
        factory = object.manage_addProduct['SilvaNews']
        factory.manage_addPlainArticle(id, title, **kw)
        return getattr(object, id)

    def add_news_viewer(self, object, id, title, **kw):
        factory = object.manage_addProduct['SilvaNews']
        factory.manage_addNewsViewer(id, title, **kw)
        return getattr(object, id)

    def add_news_filter(self, object, id, title, **kw):
        factory = object.manage_addProduct['SilvaNews']
        factory.manage_addNewsFilter(id, title, **kw)
        return getattr(object, id)

    def add_agenda_filter(self, object, id, title, **kw):
        factory = object.manage_addProduct['SilvaNews']
        factory.manage_addAgendaFilter(id, title, **kw)
        return getattr(object, id)

    def add_published_agenda_item(self, object, id, title, sdt, edt, **kw):
        factory = object.manage_addProduct['SilvaNews']
        factory.manage_addPlainAgendaItem(id, title, **kw)
        obj = getattr(object, id)
        ver = obj.get_editable()
        ver.set_start_datetime(sdt)
        ver.set_end_datetime(edt)
        ver.set_subjects(['sub'])
        ver.set_target_audiences(['ta'])
        obj.set_next_version_publication_datetime(DateTime())
        obj.approve_version()
        obj._update_publication_status()
        ver.set_display_datetime(DateTime())
        return getattr(object, id)

class NewsBaseTestCase(SilvaNewsTestCase):
    def setUp(self):
        super(NewsBaseTestCase, self).setUp()
        self.sm = self.root.service_metadata
        service_news = self.service_news = self.root.service_news
        service_news.add_subject('sub', 'Subject')
        service_news.add_subject('sub2', 'Subject 2')
        service_news.add_target_audience('ta', 'TA')
        service_news.add_target_audience('ta2', 'TA 2')

        self.source1 = self.add_news_publication(self.root, 'source1', 'News Pub 1')
        self.item1_1 = self.add_plain_article(self.source1, 'art1', 'Article 1')
        self.item1_1.set_next_version_publication_datetime(DateTime())
        getattr(self.item1_1, '0').set_subjects(['sub'])
        getattr(self.item1_1, '0').set_target_audiences(['ta'])
        self.item1_1.approve_version()
        self.item1_1._update_publication_status()
        getattr(self.item1_1, '0').set_display_datetime(DateTime())

        self.item1_2 = self.add_plain_article(self.source1, 'art2', 'Article 2')
        self.item1_2.set_next_version_publication_datetime(DateTime())
        getattr(self.item1_2, '0').set_subjects(['sub2'])
        getattr(self.item1_2, '0').set_target_audiences(['ta2'])
        self.item1_2.approve_version()
        self.item1_2._update_publication_status()
        getattr(self.item1_2, '0').set_display_datetime(DateTime())

        self.source2 = self.add_news_publication(self.root, 'source2', 'News Pub 2')
        binding = self.sm.getMetadata(self.source2)
        binding.setValues('snn-np-settings',{'is_private':'yes'},reindex=1)

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('somefolder', 'Some Folder')
        self.folder = getattr(self.root, 'somefolder')
        self.source3 = self.add_news_publication(self.folder, 'source3', 'Folder ')
        binding = self.sm.getMetadata(self.source3)
        binding.setValues('snn-np-settings',{'is_private':'yes'},reindex=1)

        self.item3_3 = self.add_plain_article(self.source3, 'art3', 'Article 3')
        self.item3_3.set_next_version_publication_datetime(DateTime())
        getattr(self.item3_3, '0').set_subjects(['sub'])
        getattr(self.item3_3, '0').set_target_audiences(['ta'])
        self.item3_3.approve_version()
        self.item3_3._update_publication_status()
        getattr(self.item3_3, '0').set_display_datetime(DateTime())

        self.newsfilter = self.add_news_filter(self.root, 'newsfilter', 'NewsFilter')
        self.newsfilter.set_subjects(['sub', 'sub2'])
        self.newsfilter.set_target_audiences(['ta', 'ta2'])

        self.newsviewer = self.add_news_viewer(self.root, 'newsviewer', 'NewsViewer')
        self.newsviewer.set_filters(['/root/newsfilter'])
