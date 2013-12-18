# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.component import queryUtility, getUtility
from zope.interface.verify import verifyObject

from Products.Silva.testing import tests
from silva.core.services.interfaces import IMetadataService

from silva.app.news.interfaces import IServiceNews, IAgendaFilter
from silva.app.news.Tree import DuplicateIdError, IReadableRoot
from silva.app.news.testing import FunctionalLayer


class ServiceNewsTestCase(unittest.TestCase):
    """Test the ServiceNews interface.
    """
    layer = FunctionalLayer

    def setUp(self):
        super(ServiceNewsTestCase, self).setUp()
        self.root = self.layer.get_application()

    def test_implementation(self):
        service = queryUtility(IServiceNews)
        self.assertTrue(verifyObject(IServiceNews, service))
        self.assertTrue('service_news' in self.root.objectIds())
        self.assertEqual(self.root.service_news, service)

    def test_find_all_filters(self):
        """Find all the news filters.
        """
        service = getUtility(IServiceNews)
        # By default there are no filters.
        tests.assertContentItemsEqual(
            list(service.get_all_filters()),
            [])

        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addAgendaFilter('agenda_filter', 'Agenda Filter')
        factory.manage_addNewsFilter('news_filter', 'News Filter')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('info', 'Info')
        factory = self.root.info.manage_addProduct['silva.app.news']
        factory.manage_addAgendaFilter('agenda_filter', 'Agenda Filter')

        # We should now find all the agenda and news filters we added
        tests.assertContentItemsEqual(
            list(service.get_all_filters()),
            [self.root.news_filter, self.root.agenda_filter,
             self.root.info.agenda_filter])

        # We should now find all the agenda and news filters we added
        tests.assertContentItemsEqual(
            list(service.get_all_filters(IAgendaFilter)),
            [self.root.agenda_filter,
             self.root.info.agenda_filter])

    def test_find_all_sources(self):
        """Find all the sources that are global.
        """
        service = getUtility(IServiceNews)
        # By default there are no sources.
        tests.assertContentItemsEqual(
            list(service.get_all_sources()),
            [])

        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'News')

        # We should now see the soure we added.
        tests.assertContentItemsEqual(
            list(service.get_all_sources()),
            [self.root.news])

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('section', 'Section')
        factory = self.root.section.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'Section News')

        # We should now see all the sources we added.
        tests.assertContentItemsEqual(
            list(service.get_all_sources()),
            [self.root.news, self.root.section.news])

    def test_find_all_sources_private(self):
        """Find all the sources, including the ones marked as private
        in a folder.
        """
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'Global News')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('documentation', 'Documentation')
        factory.manage_addFolder('section', 'Section')
        factory = self.root.section.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('local', 'Local News')
        factory = self.root.section.manage_addProduct['Silva']
        factory.manage_addFolder('documentation', 'Documentation')

        metadata = getUtility(IMetadataService)
        binding = metadata.getMetadata(self.root.section.local)
        binding.setValues('snn-np-settings', {'is_private': 'yes'}, reindex=1)

        # Globally, or somewhere else we should only see the global folder.
        service = getUtility(IServiceNews)
        tests.assertContentItemsEqual(
            list(service.get_all_sources()),
            [self.root.news])
        tests.assertContentItemsEqual(
            list(service.get_all_sources(self.root)),
            [self.root.news])
        tests.assertContentItemsEqual(
            list(service.get_all_sources(self.root.documentation)),
            [self.root.news])

        # Inside section, or in a sub folder of it we should see the
        # local folder.
        tests.assertContentItemsEqual(
            list(service.get_all_sources(self.root.section)),
            [self.root.news, self.root.section.local])
        tests.assertContentItemsEqual(
            list(service.get_all_sources(self.root.section.documentation)),
            [self.root.news, self.root.section.local])

    def test_subjects(self):
        """Test the subjects tree management.
        """
        service = queryUtility(IServiceNews)
        subjects = service.get_subjects_tree()
        self.assertTrue(verifyObject(IReadableRoot, subjects))

        # Add
        service.add_subject('test1', 'Test 1')
        service.add_subject('test2', 'Test 2', 'test1')
        self.assertEqual(
            service.get_subjects(),
            [('generic', 'Generic'),
             ('test1', 'Test 1'),
             ('test2', 'Test 2'),
             ('root', 'root')])

        # Add duplicate
        with tests.assertRaises(DuplicateIdError):
            service.add_subject('test1', 'Test 1')

        # Rename test
        ## Adding subject to be renamed.
        service.add_subject('subject_to_be_renamed', 'SubjectToBeRenamed')

        ## Checking the new subject.
        self.assertEqual(
            service.get_subjects(),
            [('generic', 'Generic'),
             ('test1', 'Test 1'),
             ('test2', 'Test 2'),
             ('root', 'root'),
             ('subject_to_be_renamed', 'SubjectToBeRenamed')])

        ## Renaming the newly created subject.
        with self.layer.get_browser() as browser:
            browser.login('manager')
            self.assertEqual(browser.open(
                             '/root/service_news/manage_news',
                             method='POST',
                             form={'subjects:list': 'subject_to_be_renamed',
                                   'subject': 'new_subject_name',
                                   'title': 'NewSubjectTitle',
                                   'manage_rename_subject': 'Rename subject',
                                   },
                             form_enctype='multipart/form-data'),
                             200)

        ## Checking if it has been renamed correctly.
        self.assertEqual(
            service.get_subjects(),
            [('test1', 'Test 1'),
             (u'generic', u'Generic'),
             (u'new_subject_name', u'NewSubjectTitle'),
             ('test2', 'Test 2'),
             ('root', 'root')])

        ## Trying to rename with an invalid id.
        with self.layer.get_browser() as browser:
            browser.login('manager')
            self.assertEqual(browser.open(
                             '/root/service_news/manage_news',
                             method='POST',
                             form={'subjects:list': 'new_subject_name',
                                   'subject': 'subject_invalid_àccentéd_ìd',
                                   'title': 'NewSubjectTitle',
                                   'manage_rename_subject': 'Rename subject',
                                   },
                             form_enctype='multipart/form-data'),
                             200)

        ## Renaming should have failed.
        ## An ID containing accents is invalid.
        ## Checking nothing has changed.
        self.assertEqual(
            service.get_subjects(),
            [('test1', 'Test 1'),
             (u'generic', u'Generic'),
             (u'new_subject_name', u'NewSubjectTitle'),
             ('test2', 'Test 2'),
             ('root', 'root')])

        ## Trying to rename with a Title containing accents.
        with self.layer.get_browser() as browser:
            browser.login('manager')
            self.assertEqual(browser.open(
                             '/root/service_news/manage_news',
                             method='POST',
                             form={'subjects:list': 'new_subject_name',
                                   'subject': 'new_subject_name',
                                   'title': 'TitleCanContainÀccénts',
                                   'manage_rename_subject': 'Rename subject',
                                   },
                             form_enctype='multipart/form-data'),
                             200)

        ## Renaming should have been done correctly.
        ## A Title containing accents is valid.
        ## Checking the new title is there.
        self.assertEqual(
            service.get_subjects(),
            [('test1', 'Test 1'),
             (u'generic', u'Generic'),
             (u'new_subject_name', u'TitleCanContainÀccénts'),
             ('test2', 'Test 2'),
             ('root', 'root')])

        ## Cleaning up.
        service.remove_subject('new_subject_name')

        # Remove
        service.remove_subject('generic')
        self.assertEqual(
            service.get_subjects(),
            [('test1', 'Test 1'), ('test2', 'Test 2'), ('root', 'root')])

        # Remove not a leaf
        with self.assertRaises(ValueError):
            service.remove_subject('test1')

        # Remove
        service.remove_subject('test2')
        self.assertEqual(
            service.get_subjects(),
            [('test1', 'Test 1'),
             ('root', 'root')])

        # Export
        with self.layer.get_browser() as browser:
            browser.login('manager')
            self.assertEqual(
                browser.open('/root/service_news/manage_tree',
                             query=[('subjects', '1')]),
                200)
            self.assertEqual(
                browser.headers['Content-Disposition'],
                'inline;filename=subjects.json')
            self.assertEqual(
                browser.headers['Content-Type'],
                'application/json')
            self.assertEqual(
                browser.json,
                {u'children': [{u'children': [], u'id': u'test1', u'title': u'Test 1'}],
                 u'id': u'root',
                 u'title': u'root'})

    def test_target_audiences(self):
        """Test the target audience management.
        """
        service = queryUtility(IServiceNews)
        self.assertTrue(
            verifyObject(IReadableRoot, service.get_target_audiences_tree()))

        # Add
        service.add_target_audience('test1', 'Test 1')
        service.add_target_audience('test2', 'Test 2', 'test1')
        self.assertEqual(
            service.get_target_audiences(),
            [('test1', 'Test 1'),
             ('all', 'All'),
             ('test2', 'Test 2'),
             ('root', 'root')])

        # Add duplicate
        with self.assertRaises(DuplicateIdError):
            service.add_target_audience('test1', 'Test 1')

        # Rename test
        ## Adding target to be renamed.
        service.add_target_audience('target_to_be_renamed', 'TargetToBeRenamed')

        ## Checking the new target.
        self.assertEqual(
            service.get_target_audiences(),
            [('test1', 'Test 1'),
             ('target_to_be_renamed', 'TargetToBeRenamed'),
             ('all', 'All'),
             ('test2', 'Test 2'),
             ('root', 'root'),
             ])

        ## Renaming the newly created target.
        with self.layer.get_browser() as browser:
            browser.login('manager')
            self.assertEqual(browser.open(
                             '/root/service_news/manage_news',
                             method='POST',
                             form={'target_audiences:list': 'target_to_be_renamed',
                                   'target_audience': 'new_target_name',
                                   'title': 'NewTargetTitle',
                                   'manage_rename_target_audience': 'Rename target audience',
                                   },
                             form_enctype='multipart/form-data'),
                                   200)

        ## Checking if it has been renamed correctly.
        self.assertEqual(
            service.get_target_audiences(),
            [('test1', 'Test 1'),
             (u'all', u'All'),
             ('test2', 'Test 2'),
             ('root', 'root'),
             (u'new_target_name', u'NewTargetTitle')
             ])

        ## Trying to rename with an invalid id.
        with self.layer.get_browser() as browser:
            browser.login('manager')
            self.assertEqual(browser.open(
                             '/root/service_news/manage_news',
                             method='POST',
                             form={'target_audiences:list': 'new_target_name',
                                   'target_audience': 'targeti_nvalid_àccentéd_ìd',
                                   'title': 'NewTargetTitle',
                                   'manage_rename_target_audience': 'Rename target audience',
                                   },
                             form_enctype='multipart/form-data'),
                             200)

        ## Renaming should have failed.
        ## An ID containing accents is invalid.
        ## Checking nothing has changed.
        self.assertEqual(
            service.get_target_audiences(),
            [('test1', 'Test 1'),
             (u'all', u'All'),
             ('test2', 'Test 2'),
             ('root', 'root'),
             (u'new_target_name', u'NewTargetTitle')
             ])

        ## Trying to rename with a Title containing accents.
        with self.layer.get_browser() as browser:
            browser.login('manager')
            self.assertEqual(browser.open(
                             '/root/service_news/manage_news',
                             method='POST',
                             form={'target_audiences:list': 'new_target_name',
                                   'target_audience': 'new_target_name',
                                   'title': 'TitleCanContainÀccénts',
                                   'manage_rename_target_audience': 'Rename target audience',
                                   },
                             form_enctype='multipart/form-data'),
                             200)

        ## Renaming should have been done correctly.
        ## A Title containing accents is valid.
        ## Checking the new title is there.
        self.assertEqual(
            service.get_target_audiences(),
            [('test1', 'Test 1'),
             (u'all', u'All'),
             ('test2', 'Test 2'),
             ('root', 'root'),
             (u'new_target_name', u'TitleCanContainÀccénts')
             ])

        ## Cleaning up.
        service.remove_target_audience('new_target_name')

        # Remove
        service.remove_target_audience('all')
        self.assertEqual(
            service.get_target_audiences(),
            [('test1', 'Test 1'),
             ('test2', 'Test 2'),
             ('root', 'root')])

        # Remove not a leaf
        with self.assertRaises(ValueError):
            service.remove_target_audience('test1')

        # Remove
        service.remove_target_audience('test2')
        self.assertEqual(
            service.get_target_audiences(),
            [('test1', 'Test 1'),
             ('root', 'root')])

        # Export
        with self.layer.get_browser() as browser:
            browser.login('manager')
            self.assertEqual(
                browser.open('/root/service_news/manage_tree'),
                200)
            self.assertEqual(
                browser.headers['Content-Disposition'],
                'inline;filename=target_audiences.json')
            self.assertEqual(
                browser.headers['Content-Type'],
                'application/json')
            self.assertEqual(
                browser.json,
                {u'children': [{u'children': [], u'id': u'test1', u'title': u'Test 1'}],
                 u'id': u'root',
                 u'title': u'root'})


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ServiceNewsTestCase))
    return suite
