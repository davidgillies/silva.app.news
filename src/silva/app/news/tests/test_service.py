# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
import unittest

from zope.component import queryUtility
from zope.interface.verify import verifyObject
from silva.app.news.interfaces import IServiceNews
from silva.app.news.Tree import DuplicateIdError, IReadableRoot
from silva.app.news.tests.SilvaNewsTestCase import FunctionalLayer


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

    def test_subjects(self):
        service = self.root.service_news
        self.assertTrue(
            verifyObject(IReadableRoot, service.get_subjects_tree()))

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
        with self.assertRaises(DuplicateIdError):
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
        service = self.root.service_news
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
