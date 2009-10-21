# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# zope imports
import zLOG
log_severity = zLOG.INFO

# silva imports
from Products.SilvaNews.Tree import Root, Node
from silva.core.upgrade.upgrade import BaseUpgrader

VERSION='1.3'


class ArticleDisplayTimeSetter(BaseUpgrader):
    """set an attribute '_display_time' on all AgendaItems"""

    def upgrade(self, obj):
        zLOG.LOG(
            'SilvaNews',
            log_severity,
            'Add display_date attribute to AgendaItem %s' %
                '/'.join(obj.getPhysicalPath())
            )
        if not hasattr(obj, '_display_time'):
            obj._display_time = True
        return obj


adts = ArticleDisplayTimeSetter(VERSION, 'Silva Agenda Item Version')


class ServiceLocaleSetter(BaseUpgrader):
    """set attributes '_locale' and '_date_format' on service_news"""

    def upgrade(self, obj):
        zLOG.LOG(
            'SilvaNews',
            log_severity,
            'Add _locale and _date_format attributes to News Service'
            )
        if not hasattr(obj, '_locale') or not hasattr(obj, '_date_format'):
            obj._locale = 'en'
            obj._date_format = 'medium'
        return obj


sls = ServiceLocaleSetter(VERSION, 'Silva News Service')


class SubjectTargetAudienceUpdater(BaseUpgrader):
    """convert subjects and target audiences to trees"""

    def upgrade(self, obj):
        zLOG.LOG(
            'SilvaNews',
            log_severity,
            'Change format of subjects and target audiences storage on '\
            'News Service'
            )
        if type(obj._subjects) == dict:
            root = Root()
            self._build_tree(root, obj._subjects)
            obj._subjects = root

        if type(obj._target_audiences == dict):
            root = Root()
            self._build_tree(root, obj._target_audiences)
            obj._target_audiences = root

        obj._p_changed = 1
        return obj

    def _build_tree(self, root, data):
        # first find all the items that have no parent, then
        # walk through those items recursively
        for itemid, value in data.items():
            if value[0] == None:
                # root element
                self._build_item(itemid, root, data)

    def _build_item(self, elid, parent, data):
        node = Node(elid, elid)
        parent.addChild(node)
        if data.has_key(elid):
            for childid in data[elid][1:]:
                self._build_item(childid, node, data)


staa = SubjectTargetAudienceUpdater(VERSION, 'Silva News Service')


class DisplayDateTimeSetter(BaseUpgrader):
    """set attribute 'display_datetime' of news items"""

    def upgrade(self, obj):
        zLOG.LOG(
            'SilvaNews',
            log_severity,
            'Add _display_datetime attribute to news item %s' %
                '/'.join(obj.getPhysicalPath())
            )
        if not hasattr(obj, '_display_datetime'):
            pdt = obj.publication_datetime()
            obj._display_datetime = pdt
        return obj


ddts_sav = DisplayDateTimeSetter(VERSION, 'Silva Article Version')
ddts_saiv = DisplayDateTimeSetter(VERSION, 'Silva Agenda Item Version')


class NumberToShowArchiveSetter(BaseUpgrader):
    """set attribute '_number_to_show_archive' on news items"""

    def upgrade(self, obj):
        zLOG.LOG(
            'SilvaNews',
            log_severity,
            'Add _number_to_show_archive attribute to news item %s' %
                '/'.join(obj.getPhysicalPath())
            )
        if not hasattr(obj, '_number_to_show_archive'):
            obj._number_to_show_archive = 10
        return obj


ntsas_snv = NumberToShowArchiveSetter(VERSION, 'Silva News Viewer')
ntsas_sav = NumberToShowArchiveSetter(VERSION, 'Silva Agenda Viewer')
