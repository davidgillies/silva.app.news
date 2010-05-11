# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.18 $

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

# Silva
from silva.core import conf as silvaconf

# Silva
from Products.SilvaNews.NewsItem import NewsItem, NewsItemVersion


class PlainArticleVersion(NewsItemVersion):
    """Silva News PlainArticle version.
    """
    security = ClassSecurityInfo()
    meta_type = "Silva Article Version"

    def __init__(self, id):
        PlainArticleVersion.inheritedAttribute('__init__')(self, id)


InitializeClass(PlainArticleVersion)


class PlainArticle(NewsItem):
    """A News item that appears as an individual page. By adjusting
       settings the Author can determine which subjects, and
       for which audiences the Article should be presented.
    """
    # Silva News PlainArticle. All the data of the object is defined
    # on the version, except for publication_datetime (see SuperClass)

    security = ClassSecurityInfo()
    meta_type = "Silva Article"
    silvaconf.icon("www/news_item.png")
    silvaconf.priority(3.7)
    silvaconf.versionClass(PlainArticleVersion)


InitializeClass(PlainArticle)


