# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.interface import Interface
from zope.component import getUtility
from zope import schema
from zope.i18nmessageid import MessageFactory

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from Products.Silva import SilvaPermissions

from silva.app.news.interfaces import INewsCategorization, IServiceNews
from silva.app.news.interfaces import (
    get_subjects_tree, get_target_audiences_tree)
from silva.app.news.interfaces import subjects_source, target_audiences_source
from silva.app.news.widgets.tree import Tree

_ = MessageFactory('silva_news')


class NewsCategorization(object):
    grok.implements(INewsCategorization)
    security = ClassSecurityInfo()

    def __init__(self, id):
        super(NewsCategorization, self).__init__(id)
        self._subjects = set(['root'])
        self._target_audiences = set(['root'])

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_subjects')
    def set_subjects(self, subjects):
        self._subjects = set(subjects)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_target_audiences')
    def set_target_audiences(self, target_audiences):
        self._target_audiences = set(target_audiences)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_subjects')
    def get_subjects(self):
        """Returns the subjects
        """
        return set(self._subjects or [])
        ## We need to make sure that selected subjects
        ## in the filter have not been deleted or renamed in the ZMI
        ## and thus that are still valid.
        news_service = getUtility(IServiceNews)
        valid_subs_tree = news_service.get_subjects_tree()
        invalid_subs = set()
        for sub in self._subjects:
            try:
                if valid_subs_tree.get_element(sub) is None:
                    invalid_subs.add(sub)
            except KeyError:
                invalid_subs.add(sub)
        ## We set and return only the valid subjects.
        self._subjects = self._subjects - invalid_subs
        return set(self._subjects or [])

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_target_audiences')
    def get_target_audiences(self):
        """Returns the target audiences
        """
        return set(self._target_audiences or [])
        ## We need to make sure that selected targets
        ## in the filter have not been deleted or renamed in the ZMI
        ## and thus that are still valid.
        news_service = getUtility(IServiceNews)
        valid_targets_tree = news_service.get_target_audiences_tree()
        invalid_targets = set()
        for tar in self._target_audiences:
            try:
                if valid_targets_tree.get_element(tar) is None:
                    invalid_targets.add(tar)
            except KeyError:
                invalid_targets.add(tar)
        ## We set and return only the valid target audiences.
        self._target_audiences = self._target_audiences - invalid_targets
        return set(self._target_audiences or [])

InitializeClass(NewsCategorization)


class INewsCategorizationFields(Interface):
    subjects = Tree(
        title=_(u"Subjects"),
        value_type=schema.Choice(source=subjects_source),
        tree=get_subjects_tree,
        required=True)
    target_audiences = Tree(
        title=_(u"Target audiences"),
        value_type=schema.Choice(source=target_audiences_source),
        tree=get_target_audiences_tree,
        required=True)
