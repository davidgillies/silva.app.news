# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from five import grok
from zope.component import getUtility
from zope.lifecycleevent.interfaces import IObjectCreatedEvent


from Products.SilvaMetadata.interfaces import IMetadataService
from Products.Silva.Publication import Publication
from Products.Silva.Folder.addables import AddableContents
from Products.Silva.cataloging import CatalogingAttributes

from silva.core import conf as silvaconf
from silva.core.interfaces import IAsset
from zeam.form import silva as silvaforms

from .interfaces import INewsPublication, INewsItemContent, INewsItemFilter
from .interfaces import INewsViewer, IServiceNewsCategorization



class NewsPublication(Publication):
    """A special publication type (a.k.a. News Source) for news
    and agenda items. News Filters and Agenda Filters can pick up
    news from these sources anywhere in a Silva site.
    """
    security = ClassSecurityInfo()

    grok.implements(INewsPublication)
    meta_type = "Silva News Publication"
    silvaconf.icon("www/news_source.png")
    silvaconf.priority(3)


InitializeClass(NewsPublication)


class NewsAddableContents(AddableContents):
    grok.context(INewsPublication)
    REQUIRES = [
        INewsItemContent, INewsItemFilter,
        INewsViewer, INewsPublication, IAsset]


class NewsPublicationCatalogingAttributes(CatalogingAttributes):
    grok.context(INewsPublication)

    @property
    def parent_path(self):
        return '/'.join(self.context.aq_inner.aq_parent.getPhysicalPath())


class NewsPublicationAddForm(silvaforms.SMIAddForm):
    grok.context(INewsPublication)
    grok.name(u"Silva News Publication")


@silvaconf.subscribe(INewsPublication, IObjectCreatedEvent)
def news_publication_created(publication, event):
    """news publications should have their 'hide_from_tocs' set to
       'hide'.  This can be done after they are added
    """
    binding = getUtility(IMetadataService).getMetadata(publication)
    binding.setValues('silva-extra', {'hide_from_tocs': 'hide'}, reindex=1)
    binding.setValues('snn-np-settings', {'is_private': 'no'}, reindex=1)

    factory = publication.manage_addProduct['silva.app.news']
    factory.manage_addNewsViewer(
        'index', publication.get_title_or_id())
    factory.manage_addNewsFilter(
        'filter', 'Filter for %s' % publication.get_title_or_id())

    viewer = publication._getOb('index')
    filter = publication._getOb('filter')

    # Configure the new filter and viewer.

    service = getUtility(IServiceNewsCategorization)
    filter.set_subjects(service.get_subjects_tree().get_ids(1))
    filter.set_target_audiences(service.get_target_audiences_tree().get_ids(1))
    filter.add_source(publication)

    viewer.add_filter(filter)


