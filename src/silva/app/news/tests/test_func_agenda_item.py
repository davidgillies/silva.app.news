# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
from datetime import datetime

from silva.app.news.datetimeutils import get_timezone
from silva.app.news.testing import FunctionalLayer
from Products.Silva.ftesting import smi_settings
from Products.Silva.testing import Transaction


class TestAgendaItemAddTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        with Transaction(catalog=True):
            factory = self.root.manage_addProduct['silva.app.news']
            factory.manage_addNewsPublication('news', 'News Publication')

    @unittest.skip('XXX need update')
    def test_agenda_item_add_form(self):
        with self.layer.get_web_browser(smi_settings) as browser:
            browser.login('manager')
            browser.options.handle_errors = False

            browser.open('/root/edit#adding/Silva Agenda Item!/news')
            form = browser.get_form('addform')
            self.assertTrue(form)
            form.get_control('addform.field.id').value = 'event'
            form.get_control('addform.field.title').value = 'Event'
            form.get_control('addform.field.timezone_name').value = 'Europe/Paris'
            form.get_control('addform.field.start_datetime.day').value = '01'
            form.get_control('addform.field.start_datetime.month').value = '09'
            form.get_control('addform.field.start_datetime.year').value = '2010'
            form.get_control('addform.field.start_datetime.hour').value = '10'
            form.get_control('addform.field.start_datetime.min').value = '20'
            form.get_control('addform.field.subjects').value = ['generic']
            form.get_control('addform.field.target_audiences').value = ['all']

            form.get_control('addform.action.save_edit').submit()

            item = getattr(self.root.news, 'event', False)
            self.assertTrue(item)
            version = item.get_editable()
            self.assertTrue(version)

            self.assertEquals('event', item.id)
            self.assertEquals('Event', version.get_title())
            self.assertEquals('Europe/Paris', version.get_timezone_name())
            self.assertEquals([u'generic'], version.get_subjects())
            self.assertEquals([u'all'], version.get_target_audiences())
            self.assertEquals(
                datetime(2010, 9, 1, 10, 20, 0,
                         tzinfo=get_timezone('Europe/Paris')),
                version.get_start_datetime())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAgendaItemAddTestCase))
    return suite

