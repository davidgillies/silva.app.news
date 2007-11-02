# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.18 $

from zope.interface import implements

# Zope
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Globals import InitializeClass

# Silva interfaces
from Products.SilvaNews.interfaces import INewsItem, INewsItemVersion
from Products.Silva.interfaces import IVersionedContent

# Silva
from Products.Silva import SilvaPermissions
from Products.SilvaNews.NewsItem import NewsItem, NewsItemVersion

class PlainArticle(NewsItem):
    """A News item that appears as an individual page. By adjusting
       settings the Author can determine which subjects, and
       for which audiences the Article should be presented.
    """
    # Silva News PlainArticle. All the data of the object is defined 
    # on the version, except for publication_datetime (see SuperClass)

    security = ClassSecurityInfo()

    meta_type = "Silva Article"

    implements((INewsItem, IVersionedContent))

InitializeClass(PlainArticle)

class PlainArticleVersion(NewsItemVersion):
    """Silva News PlainArticle version.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva Article Version"

    implements(INewsItemVersion)

    def __init__(self, id):
        PlainArticleVersion.inheritedAttribute('__init__')(self, id)

InitializeClass(PlainArticleVersion)
