# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import SilvaNewsTestCase
from DateTime import DateTime


class AgendaFilterTestCase(SilvaNewsTestCase.NewsBaseTestCase):
    """Test the AgendaFilter interfaces
    """
    def test_get_next_items(self):
        # add an Agenda Filter to the root
        
        self.af = self.add_agenda_filter(self.root, 'af','af')
        self.af.set_subjects(['sub'])
        self.af.set_target_audiences(['ta'])
        self.af.add_source('/root/source1',1)
        
        now = DateTime()
        
        #add an item that ends in the range
        ai1 = self.add_published_agenda_item(self.source1,
                                             'ai1','ai1',
                                             sdt=now-5,
                                             edt=now+1)
        
        #add an item that starts in the range (but ends 
        # after the range
        ai2 = self.add_published_agenda_item(self.source1,
                                             'ai2','ai2',
                                             sdt=now+1,
                                             edt=now+5)
        
        # add an item that starts before and ends after
        # the rangep
        ai3 = self.add_published_agenda_item(self.source1,
                                             'ai3','ai3',
                                             sdt=now-5,
                                             edt=now+5)
        
        results = self.af.get_next_items(2)
        
        self.assertEquals(len(results),3)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AgendaFilterTestCase))
    return suite
