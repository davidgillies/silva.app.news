# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.4 $

import unittest
import Zope
from Testing import makerequest

from Products.SilvaNews.ServiceNews import DuplicateError, NotEmptyError
from Products.Silva.tests.test_SilvaObject import hack_add_user

def set(key, value):
    pass

def add_helper(object, typename, id, title):
    getattr(object.manage_addProduct['Silva'], 'manage_add%s' % typename)(id, title)
    return getattr(object, id)

def add_helper_news(object, typename, id, title):
    getattr(object.manage_addProduct['SilvaNews'], 'manage_add%s' % typename)(id, title)
    return getattr(object, id)

class ServiceNewsBaseTestCase(unittest.TestCase):
    def setUp(self):
        get_transaction().begin()
        self.connection = Zope.DB.open()
        self.root = makerequest.makerequest(self.connection.root()['Application'])
        self.REQUEST = self.root.REQUEST
        self.REQUEST.set = lambda a, b: None
        hack_add_user(self.REQUEST)
        self.sroot = sroot = add_helper(self.root, 'Root', 'root', 'Root')
        self.service_news = service_news = add_helper_news(self.root, 'ServiceNews', 'service_news', 'ServiceNews')

    def tearDown(self):
        get_transaction().abort()
        self.connection.close()

class ServiceNewsTestCase(ServiceNewsBaseTestCase):
    """Test the ServiceNews interface.
    """
    # We're not going to test specific units here but just make a small general test of each datamember,
    # since the methods are very simple data-manipulating things, not really suited to test in units, also
    # the chance of anything going wrong here is minimal. Still it's nice to know that they work :)
    def test_subjects(self):
        self.service_news.add_subject('test1')
        self.service_news.add_subject('test2', 'test1')
        self.assert_('test1' in self.service_news.subjects())
        self.assert_('test2' in self.service_news.subjects())
        self.assert_(len(self.service_news.subjects()) == 2)
        self.assert_(self.service_news.subject_tree() == [('test1', 0), ('test2', 1)])
        self.assert_(self.service_news.subject_form_tree() == [('test1', 'test1'), ('&nbsp;&nbsp;test2', 'test2')])
        self.assertRaises(DuplicateError, self.service_news.add_subject, 'test1')
        self.assertRaises(NotEmptyError, self.service_news.remove_subject, 'test1')
        self.service_news.remove_subject('test2')
        self.assert_(self.service_news.subject_tree() == [('test1', 0)])

    def test_target_audiences(self):
        self.service_news.add_target_audience('test1')
        self.service_news.add_target_audience('test2', 'test1')
        self.assert_('test1' in self.service_news.target_audiences())
        self.assert_('test2' in self.service_news.target_audiences())
        self.assert_(len(self.service_news.target_audiences()) == 2)
        self.assert_(self.service_news.target_audience_tree() == [('test1', 0), ('test2', 1)])
        self.assert_(self.service_news.target_audience_form_tree() == [('test1', 'test1'), ('&nbsp;&nbsp;test2', 'test2')])
        self.assertRaises(DuplicateError, self.service_news.add_target_audience, 'test1')
        self.assertRaises(NotEmptyError, self.service_news.remove_target_audience, 'test1')
        self.service_news.remove_target_audience('test2')
        self.assert_(self.service_news.target_audience_tree() == [('test1', 0)])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ServiceNewsTestCase, 'test'))
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
