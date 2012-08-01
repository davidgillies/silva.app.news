# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from silva.core.interfaces import IPublicationWorkflow
from silva.app.news.testing import FunctionalLayer
from silva.app.news.AgendaItem.content import AgendaItemOccurrence, _marker


class SilvaNewsTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

    def add_published_news_item(self, parent, id, title, **kw):
        factory = parent.manage_addProduct['silva.app.news']
        factory.manage_addNewsItem(id, title, **kw)
        item = parent._getOb(id)
        IPublicationWorkflow(item).publish()
        return item

    def add_published_agenda_item(
        self, parent, id, title, sdt, edt=_marker, all_day=_marker):
        factory = parent.manage_addProduct['silva.app.news']
        factory.manage_addAgendaItem(id, title)
        item = parent._getOb(id)
        version = item.get_editable()
        version.set_occurrences([
                AgendaItemOccurrence(
                    start_datetime=sdt,
                    end_datetime=edt,
                    all_day=all_day)])
        IPublicationWorkflow(item).publish()
        return item


