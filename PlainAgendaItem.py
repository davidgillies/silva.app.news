# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.16 $

from zope.interface import implements

# Zope
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Globals import InitializeClass

# Silva interfaces
from silva.core import conf as silvaconf
from Products.Silva import SilvaPermissions
from Products.Silva.interfaces import IVersionedContent

# Silva
from Products.SilvaNews.interfaces import IAgendaItem, IAgendaItemVersion
from Products.SilvaNews.AgendaItem import AgendaItem, AgendaItemVersion

class PlainAgendaItemVersion(AgendaItemVersion):
    """Silva News PlainAgendaItemVersion
    """
    security = ClassSecurityInfo()

    meta_type = "Silva Agenda Item Version"

    implements(IAgendaItemVersion)

InitializeClass(PlainAgendaItemVersion)

class PlainAgendaItem (AgendaItem):
    """A News item for events. Includes date and location
       metadata, as well settings for subjects and audiences.
    """
    security = ClassSecurityInfo()
    meta_type = "Silva Agenda Item"
    implements(IAgendaItem)
    silvaconf.icon("www/agenda_item.png")
    silvaconf.priority(3.8)
    silvaconf.versionClass(PlainAgendaItemVersion)
InitializeClass(PlainAgendaItem)
