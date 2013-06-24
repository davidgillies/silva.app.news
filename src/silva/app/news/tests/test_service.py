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


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ServiceNewsTestCase))
    return suite
