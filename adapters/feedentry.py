import re
from zope.interface import implements
from Products.Silva.adapters import interfaces
from Products.SilvaDocument.adapters import feedentry

class NewsItemFeedEntryAdapter(feedentry.DocumentFeedEntryAdapter):
    """Adapter for Silva News Items (article, agenda) to get an atom/rss feed entry 
    representation."""

    implements(interfaces.IFeedEntry)

    def __init__(self, context):
        self.context = context
        self.version = self.context.get_viewable()
        self.ms = self.context.service_metadata
        
    def html_description(self):
        return self.version.get_intro()

    def date_updated(self):
        return self.version.display_datetime()
    
    def date_published(self):
        return self.context.get_first_publication_date()

class AgendaItemFeedEntryAdapter(NewsItemFeedEntryAdapter):
    
    implements(interfaces.IFeedEntry)

    def location(self):
        return self.version.location()

    def start_datetime(self):
        return self.version.start_datetime().HTML4()

    def end_datetime(self):
        edt = self.version.end_datetime()
        return (edt and edt.HTML4()) or edt
