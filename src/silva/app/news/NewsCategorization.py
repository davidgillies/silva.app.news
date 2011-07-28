# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from Products.Silva import SilvaPermissions

from silva.app.news.interfaces import INewsCategorization
from silva.app.news.interfaces import get_subjects_tree, get_target_audiences_tree
from silva.app.news.interfaces import subjects_source, target_audiences_source
from silva.app.news.widgets.tree import Tree

_ = MessageFactory('silva_news')


class NewsCategorization(object):
    grok.implements(INewsCategorization)
    security = ClassSecurityInfo()

    def __init__(self, id):
        super(NewsCategorization, self).__init__(id)
        self._subjects = set()
        self._target_audiences = set()

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

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_target_audiences')
    def get_target_audiences(self):
        """Returns the target audiences
        """
        return set(self._target_audiences or [])

InitializeClass(NewsCategorization)



class INewsCategorizationSchema(Interface):
    subjects = Tree(
        title=_(u"subjects"),
        value_type=schema.Choice(source=subjects_source),
        tree=get_subjects_tree,
        required=True)
    target_audiences = Tree(
        title=_(u"target audiences"),
        value_type=schema.Choice(source=target_audiences_source),
        tree=get_target_audiences_tree,
        required=True)

