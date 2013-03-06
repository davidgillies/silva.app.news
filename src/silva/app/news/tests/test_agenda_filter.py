# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt
# coding=utf-8

import unittest
from datetime import datetime
from dateutil.relativedelta import relativedelta

from zope.interface.verify import verifyObject

from Products.Silva.testing import tests

from silva.app.news.interfaces import IAgendaFilter
from silva.app.news.tests.SilvaNewsTestCase import SilvaNewsTestCase


class AgendaFilterTestCase(SilvaNewsTestCase):
    """Test the AgendaFilter interfaces
    """

    def test_filter(self):
        factory = self.root.manage_addProduct['silva.app.news']
        with tests.assertTriggersEvents('ContentCreatedEvent'):
            factory.manage_addAgendaFilter('filter', 'Agenda Filter')
        nfilter = self.root._getOb('filter', None)
        self.assertTrue(verifyObject(IAgendaFilter, nfilter))

    def test_get_next_items(self):
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'News')
        factory.manage_addAgendaFilter('filter', 'Agenda Filter')

        self.root.filter.set_sources([self.root.news])

        now = datetime.now()
        #add an item that ends in the range
        self.add_published_agenda_item(
            self.root.news,
            'sport', 'Sport competition',
            sdt=now - relativedelta(hours=5),
            edt=now + relativedelta(hours=1))
        #add an item that starts in the range (but ends after the
        # range)
        self.add_published_agenda_item(
            self.root.news,
            'poetry', 'Poetry competition',
            sdt=now + relativedelta(1),
            edt=now + relativedelta(5))
        # add an item that starts before and ends after the range
        self.add_published_agenda_item(
            self.root.news,
            'petanque', u'Pétanque competition',
            sdt=now - relativedelta(5),
            edt=now + relativedelta(5))

        self.assertItemsEqual(
           [b.getPath() for b in self.root.filter.get_next_items(10)],
           ['/root/news/poetry/0', '/root/news/petanque/0',
            '/root/news/sport/0'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AgendaFilterTestCase))
    return suite
