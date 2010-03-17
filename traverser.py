from five import grok
from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds
from zope.location.interfaces import LocationError
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.traversing.interfaces import ITraversable
from Products.SilvaNews.interfaces import INewsViewer, INewsItem
from Acquisition import aq_base

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
            return aq_base(obj)
        raise LocationError
