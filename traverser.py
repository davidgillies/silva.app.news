from five import grok
from zope.component import getUtility, getMultiAdapter
from zope.app.intid.interfaces import IIntIds
from zope.location.interfaces import LocationError
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.traversing.interfaces import ITraversable
from Products.SilvaNews.interfaces import (INewsViewer,
    INewsItem, INewsItemVersion)
from zope.traversing.browser.interfaces import IAbsoluteURL
from silva.core.views.absoluteurl import AbsoluteURL
from Acquisition import aq_base


class NewsItemAbsoluteURL(AbsoluteURL, grok.MultiAdapter):
    grok.adapts(INewsItem, IBrowserRequest)
    grok.provides(IAbsoluteURL)

    def _get_path(self):
        intids = getUtility(IIntIds)
        id = intids.register(self.context)
        return '++items++%s' % id

    def _get_parent_absolute_url(self):
        return getMultiAdapter(
            (self.context.__parent__, self.request,), IAbsoluteURL)

    def __str__(self):
        if INewsViewer.providedBy(self.context.__parent__):
            base_url = str(self._get_parent_absolute_url())
            return base_url + '/' + self._get_path()
        else:
            return super(NewsItemAbsoluteURL, self).__str__()

    __call__ = __str__

    def breadcrumbs(self):
        bc = super(NewsItemAbsoluteURL, self).breadcrumbs()
        bc[-1]['url'] = str(self)
        return bc


class NewsItemVersionAbsoluteURL(AbsoluteURL, grok.MultiAdapter):
    grok.adapts(INewsItemVersion, IBrowserRequest)
    grok.provides(IAbsoluteURL)

    def __init__(self, context, request):
        super(NewsItemVersionAbsoluteURL, self).__init__(context, request)
        self.content_url = getMultiAdapter(
            (self.context.get_content(), self.request), IAbsoluteURL)

    def __str__(self):
        return str(self.content_url)

    __call__ = __str__

    def breadcrumbs(self):
        return self.content_url.breadcrumbs()


class NewsViewerTraverser(grok.MultiAdapter):
    grok.adapts(INewsViewer, IBrowserRequest)
    grok.implements(ITraversable)
    grok.name('items')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, remaining):
        self.request.timezone = self.context.get_timezone()
        intids = getUtility(IIntIds)
        try:
            obj = intids.getObject(int(name))
        except ValueError:
            raise LocationError
        if INewsItem.providedBy(obj):
            next = aq_base(obj)
            next.__name__ = '++items++%s' % name
            return next
        raise LocationError
