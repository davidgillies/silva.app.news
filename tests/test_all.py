# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $
import unittest
import Zope

from Products.SilvaNews.tests import test_ServiceNews, test_Filter, test_Viewer

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(test_ServiceNews.test_suite())
    suite.addTest(test_Filter.test_suite())
    suite.addTest(test_Viewer.test_suite())
    return suite

def main():
    unittest.TextTestRunner(verbosity=1).run(test_suite())

if __name__ == '__main__':
    main()
    
