# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.5 $

from Interface import Base

class INewsItem(Base):
    """Silva News Item interface
    """
    def creation_datetime(self):
        """Returns the time of creation
        """
        pass

    def to_xml(self, context):
        """Returns XML of the item"""
        pass

class INewsItemVersion(Base):
    def set_subjects(self, subjects):
        """Sets the subjects"""

    def set_target_audiences(self, target_audiences):
        """Sets the target audiences"""

    def source_path(self):
        """Returns the path (tuple) of the object this version belongs to"""

    def is_private(self):
        """Returns true if the item is private (picked up only by newsfilters in the same folder
        as the source)"""

    def subjects(self):
        """Returns the subjects"""

    def target_audiences(self):
        """Returns the target audiences"""

    def fulltext(self):
        """Returns a string containing all the words of all content divided by spaces (for
        fulltext ZCatalog search)"""

    def content_xml(self):
        """Returns the document-element of the XML-content (not used by all subclasses)"""

    def to_xml(self):
        """Returns an XML representation of the object"""
