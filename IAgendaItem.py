# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.4 $

from Interface import Base

class IAgendaItem(Base):
    """Silva AgendaItem, interface for some agendaitems
    Since the objects do not define more (required) functionality than it's
    SuperClass NewsItem, the interface is empty (but exists for system-specific reasons anyway)
    """

class IAgendaItemVersion(Base):
    def start_datetime(self):
        """Returns start_datetime
        """

    def location(self):
        """Returns location
        """

    def location_manual(self):
        """Returns manually entered location
        """

    def set_start_datetime(self, value):
        """Sets the start datetime to value (DateTime)"""

    def set_location(self, value):
        """Sets the location"""

    def set_location_manual(self, value):
        """Sets the manual location"""

    def fulltext(self):
        """Returns the full content of the object's version, divided by spaces (for
        ZCatalog fulltext-search)"""

    def to_xml(self):
        """Returns an XML-representation of the object"""
