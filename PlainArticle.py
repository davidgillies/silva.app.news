# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.18 $

from zope.interface import implements

# Zope
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from App.class_init import InitializeClass

# Silva
from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews

from Products.Silva import SilvaPermissions
from Products.Silva.transform.rendererreg import getRendererRegistry
from Products.Silva.transform.renderer.xsltrendererbase import XSLTRendererBase

# Silva
from Products.SilvaNews.NewsItem import NewsItem, NewsItemVersion
from Products.SilvaNews.interfaces import INewsItem, INewsItemVersion


class PlainArticleVersion(NewsItemVersion):
    """Silva News PlainArticle version.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva Article Version"

    implements(INewsItemVersion)

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


class ArticleRenderer(XSLTRendererBase):
    silvaconf.context(PlainArticle)
    silvaconf.title('Basic XSLT Renderer')
    silvaconf.XSLT('article.xslt')


class ArticleView(silvaviews.View):
    """ View on a News Item (either Article / Agenda ) """

    silvaconf.context(PlainArticle)

    def render(self):
        registry = getRendererRegistry()
        renderers = registry.getRenderersForMetaType('Silva Article')
        renderer = renderers['Basic XSLT Renderer']
        return renderer.render(self.context)
