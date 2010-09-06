# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from Products.SilvaNews.AgendaItem import AgendaItem, AgendaItemVersion
from Products.SilvaNews.interfaces import IAgendaItem
from Products.SilvaNews.interfaces import (
    subject_source, target_audiences_source)

from five import grok
from silva.core import conf as silvaconf
from silva.core.conf.interfaces import ITitledContent
from zeam.form import silva as silvaforms
from zope import interface, schema
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('silva_news')


class PlainAgendaItemVersion(AgendaItemVersion):
    """Silva News PlainAgendaItemVersion
    """
    security = ClassSecurityInfo()
    meta_type = "Silva Agenda Item Version"


InitializeClass(PlainAgendaItemVersion)


class PlainAgendaItem(AgendaItem):
    """A News item for events. Includes date and location
       metadata, as well settings for subjects and audiences.
    """
    security = ClassSecurityInfo()
    meta_type = "Silva Agenda Item"
    silvaconf.icon("www/agenda_item.png")
    silvaconf.priority(3.8)
    silvaconf.versionClass(PlainAgendaItemVersion)


InitializeClass(PlainAgendaItem)


class IAgendaItemSchema(interface.Interface):
    _start_datetime = schema.Datetime(
        title=_(u"start date/time"),
        required=False) # True
    _end_datetime = schema.Datetime(
        title=_(u"end date/time"),
        required=False)
    _location = schema.TextLine(
        title=_(u"location"),
        description=_(u"The location where the event is taking place."),
        required=False)
    _subjects = schema.List(
        title=_(u"subjects"),
        value_type=schema.Choice(source=subject_source),
        required=True)
    _target_audiences = schema.List(
        title=_(u"target audiences"),
        value_type=schema.Choice(source=target_audiences_source),
        required=True)


class AgendaItemAddForm(silvaforms.SMIAddForm):
    grok.context(IAgendaItem)
    grok.name(u"Silva Agenda Item")

    fields = silvaforms.Fields(ITitledContent, IAgendaItemSchema)


class AgendaEditProperties(silvaforms.RESTKupuEditProperties):
    grok.context(IAgendaItem)

    label = _(u"agenda item properties")
    fields = silvaforms.Fields(IAgendaItemSchema)
    actions = silvaforms.Actions(silvaforms.EditAction())
