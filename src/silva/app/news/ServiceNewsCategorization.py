# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.component import getUtility
from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo

from silva.core import conf as silvaconf
from silva.core.services.base import SilvaService
from silva.app.news.interfaces import IServiceNews
from silva.app.news.interfaces import IServiceNewsCategorization
from silva.app.news.widgets.tree import Tree
from silva.app.news.Tree import create_filtered_tree
from silva.core.interfaces import ISilvaLocalService
from zeam.form import silva as silvaforms

_ = MessageFactory('silva_news')


class ServiceNewsCategorization(SilvaService):
    """Provides lists of subjects and target_audiences for filters.
    """
    grok.implements(IServiceNewsCategorization, ISilvaLocalService)
    grok.name('service_news_categorization')
    security = ClassSecurityInfo()
    meta_type = 'Silva News Categorization Service'
    silvaconf.icon('www/newsservice.gif')

    manage_options = (
        {'label': 'Edit', 'action': 'manage_news'},
        ) + SilvaService.manage_options

    _local_subjects = None
    _local_audience_targets = None

    def _get_service(self):
        service = getattr(self, '_v_service_news', None)
        if service is None:
            self._v_service_news = service = getUtility(IServiceNews)
        return service

    security.declareProtected('View', 'get_subjects_tree')
    def get_subjects_tree(self):
        tree = self._get_service().get_subjects_tree()
        subjects =  self._local_subjects
        if subjects is not None:
            return create_filtered_tree(tree, subjects)
        return tree

    security.declareProtected('View', 'get_target_audiences_tree')
    def get_target_audiences_tree(self):
        tree = self._get_service().get_target_audiences_tree()
        audiences = self._local_target_audiences
        if audiences is not None:
            return create_filtered_tree(tree, audiences)
        return tree

    security.declareProtected('View', 'get_subjects')
    def get_subjects(self):
        """returns a list of (id, title) tuples"""
        return [(x.id(), x.title())
                for x in  self.get_subjects_tree().get_elements()]

    security.declareProtected('View', 'get_target_audiences')
    def get_target_audiences(self):
        """returns a list of (id, title) tuples"""
        return [(x.id(), x.title())
                for x in self.get_target_audiences_tree().get_elements()]


InitializeClass(ServiceNewsCategorization)


@grok.provider(IContextSourceBinder)
def global_subjects_source(context):
    service = getUtility(IServiceNews)
    result = []
    for value, title in service.get_subjects():
        result.append(SimpleTerm(
            value=value, token=value, title=title))
    return SimpleVocabulary(result)


@grok.provider(IContextSourceBinder)
def global_target_audiences_source(context):
    service = getUtility(IServiceNews)
    result = []
    for value, title in service.get_target_audiences():
        result.append(SimpleTerm(
            value=value, token=value, title=title))
    return SimpleVocabulary(result)


def get_global_subjects_tree(form):
    service = getUtility(IServiceNews)
    return service.get_subjects_tree()


def get_global_target_audiences_tree(form):
    service = getUtility(IServiceNews)
    return service.get_target_audiences_tree()


class INewsCategorizationFields(Interface):
    _local_subjects = Tree(
        title=_(u"subjects"),
        description=_("select subjects that should appear in SMI"),
        value_type=schema.Choice(source=global_subjects_source),
        tree=get_global_subjects_tree,
        required=True)
    _local_target_audiences = Tree(
        title=_(u"target audiences"),
        description=_("select target audiences that should appear in SMI"),
        value_type=schema.Choice(source=global_target_audiences_source),
        tree=get_global_target_audiences_tree,
        required=True)


class ManageNewsCategorization(silvaforms.ZMIForm):
    grok.name('manage_news')

    label = _(u"Restrict categories for editors")
    description = _(u"You can from here restrict all subjects and "
                    "target audiences usable for news and agenda items.")
    fields = silvaforms.Fields(INewsCategorizationFields)
    actions = silvaforms.Actions(
        silvaforms.EditAction())
    ignoreContent = False
