# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.intid.interfaces import IIntIds
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from silva.app.document.interfaces import IDocument, IDocumentVersion
from silva.app.news.datetimeutils import zone_names
from silva.core.interfaces import INonPublishable, IPublication, IContent
from silva.core.interfaces import ISilvaService
from silva.app.news.datetimeutils import local_timezone

_ = MessageFactory('silva_news')


class ISilvaNewsExtension(Interface):
    """Marker interface for SNN Extension"""


@grok.provider(IContextSourceBinder)
def subjects_source(context):
    service = getUtility(IServiceNewsCategorization)
    result = []
    for value, title in service.get_subjects():
        result.append(SimpleTerm(
            value=value, token=value, title=title))
    return SimpleVocabulary(result)


@grok.provider(IContextSourceBinder)
def target_audiences_source(context):
    service = getUtility(IServiceNewsCategorization)
    result = []
    for value, title in service.get_target_audiences():
        result.append(SimpleTerm(
            value=value, token=value, title=title))
    return SimpleVocabulary(result)


def get_subjects_tree(form):
    service = getUtility(IServiceNewsCategorization)
    return service.get_subjects_tree()


def get_target_audiences_tree(form):
    service = getUtility(IServiceNewsCategorization)
    return service.get_target_audiences_tree()


class INewsCategorization(Interface):
    """Categorize news information by subject and target audience.
    """

    def get_subjects():
        """Returns the list of subjects."""

    def get_target_audiences():
        """Returns the list of target audiences."""

    def set_subjects(subjects):
        """Updates the list of subjects"""

    def set_target_audiences(target_audiences):
        """Updates the list of target_audiences"""


class INewsItem(IDocument):
    """News item
    """


class INewsItemVersion(IDocumentVersion, INewsCategorization):
    """Silva news item version.

    This contains the real content for a news item.
    """

    def is_private():
        """Returns true if the item is private.

        Private items are picked up only by news filters in the same
        container as the source.
        """

    def fulltext():
        """Returns a string containing all the words of all content.

        For fulltext ZCatalog search.
        XXX This should really be on an interface in the Silva core"""


class IAgendaItem(INewsItem):
    """Agenda item
    """


class IAgendaItemVersion(INewsItemVersion):

    def get_start_datetime():
        """Returns start_datetime
        """

    def get_end_datetime():
        """Returns end_datetime
        """

    def get_location():
        """Returns location
        """

    def set_start_datetime(value):
        """Sets the start datetime to value (DateTime)"""

    def set_end_datetime(value):
        """Sets the end datetime to value (DateTime)"""

    def set_location(value):
        """Sets the location"""


class INewsPublication(IPublication):
    """Publication that contains agenda and news items
    """


class INewsItemFilter(INonPublishable, INewsCategorization):
    """Filter agenda and news items

    A NewsItemFilter picks up news from news sources. Editors can
    browse through this news. It can also be used by
    public pages to expose published news items to end users.

    A super-class for the News Filters (NewsFilter, AgendaFilter)
    which contains shared code for both filters
    """

    def get_sources():
        """return the source list of this newsitemfilter"""

    def set_sources(sources_list):
        """set the source list of this newsitemfilter"""

    def add_source(source):
        """add a"""

    def keep_to_path():
        """Returns true if the item should keep to path"""

    def set_keep_to_path(value):
        """Removes the filter from the list of filters where the item
        should appear"""

    def get_excluded_items():
        """Returns a list of all excluded items
        """

    def add_excluded_item(target):
        """Exclude the target from any result list.
        """

    def remove_excluded_item(target):
        """Remove the exclusion on targte from any result list.
        """

    def is_excluded_item(target):
        """Return true if target is excluded.
        """

    def search_items(keywords, meta_types=None):
        """ Returns the items from the catalog that have keywords
        in fulltext"""

    #functions to aid in compatibility between news and agenda filters
    # and viewers, so the viewers can pull from both types of filters

    def get_items_by_date(
        month, year, timezone=local_timezone, meta_types=None):
        """For looking through the archives
        This is different because AgendaFilters search on start/end
        datetime, whereas NewsFilters look at display datetime
        """

    def get_next_items(numdays, meta_types=None):
        """ Note: ONLY called by AgendaViewers
        Returns the next <number> AGENDAitems,
        should return items that conform to the
        AgendaItem-interface (IAgendaItemVersion), although it will in
        any way because it requres start_datetime to be set.
        NewsViewers use only get_last_items.
        """

    def get_last_items(number, number_id_days=0, meta_types=None):
        """Returns the last (number) published items
           This is _only_ used by News Viewers.
        """

    def get_allowed_meta_types():
        """Return allowed meta_type for items that the filter should
        return.
        """


class INewsFilter(INewsItemFilter):
    """Filter for news items
    """

    def show_agenda_items():
        """should we also show agenda items?"""

    def set_show_agenda_items(flag):
        """sets whether to show agenda items"""

    def get_all_items(meta_types=None):
        """Returns all items, only to be used on the back-end"""



class IAgendaFilter(INewsItemFilter):
    """Filter for agenda items
    """


class IViewer(IContent):
    """Base interface for SilvaNews Viewers"""

_number_to_show = [
    (_(u"number of days"), 1),
    (_(u"number of items"), 0)
]


@grok.provider(IContextSourceBinder)
def show_source(context):
    terms = []
    for info in _number_to_show:
        title, value = info
        terms.append(SimpleTerm(value=value, token=value, title=title))
    return SimpleVocabulary(terms)

_week_days_list = [
    (_(u'Monday'),    0),
    (_(u'Tuesday'),   1),
    (_(u'Wednesday'), 2),
    (_(u'Thursday'),  3),
    (_(u'Friday'),    4),
    (_(u'Saturday'),  5),
    (_(u'Sunday'),    6)
]

@grok.provider(IContextSourceBinder)
def week_days_source(context):
    week_days_terms = []
    for info in _week_days_list:
        title, value = info
        week_days_terms.append(
            SimpleTerm(value=value, token=value, title=title))
    return SimpleVocabulary(week_days_terms)

@grok.provider(IContextSourceBinder)
def timezone_source(context):
    terms = []
    for zone in zone_names:
        terms.append(SimpleTerm(title=zone,
                                value=zone,
                                token=zone))
    return SimpleVocabulary(terms)

@grok.provider(IContextSourceBinder)
def filters_source(context):
    terms = []
    get_token = getUtility(IIntIds).register
    get_filters = getUtility(IServiceNews).get_all_filters
    for filter in get_filters():
        path = "/".join(filter.getPhysicalPath())
        terms.append(SimpleTerm(value=filter,
                                title="%s (%s)" % (filter.get_title(), path),
                                token=str(get_token(filter))))
    return SimpleVocabulary(terms)

@grok.provider(IContextSourceBinder)
def news_source(context):
    terms = []
    get_token = getUtility(IIntIds).register
    get_sources = getUtility(IServiceNews).get_all_sources
    for source in get_sources(context):
        path = "/".join(source.getPhysicalPath())
        terms.append(SimpleTerm(value=source,
                                title="%s (%s)" % (source.get_title(), path),
                                token=str(get_token(source))))
    return SimpleVocabulary(terms)


class INewsViewer(IViewer):
    """Viewer for news items
    """
    # manipulators
    def set_number_to_show(number):
        """Set the number of items to show on the front page.
        """

    def set_number_to_show_archive(number):
        """Set the number to show per page in the archives.
        """

    def set_number_is_days(onoff):
        """If set to True, the number to show will be by days back, not number.
        """

    # accessors
    def number_to_show():
        """Amount of news items to show.
        """

    def number_to_show_archive():
        """Number of items per page to show in the archive.
        """

    def number_is_days():
        """If number_is_days is True, the number_to_show will control
        days back to show instead of number of items.
        """

    def get_filters():
        """Returns a list of associated filters.
        """

    def set_filters(filter_list):
        """set a list of the filters.
        """

    def add_filter(filter):
        """ add a filter.
        """

    def get_items():
        """Get items from the filters according to the number to show.
        """

    def get_items_by_date(month, year):
        """Given a month and year, give all items published then.
        """

    def search_items(keywords):
        """Search the items in the filters.
        """

    def set_proxy(item, force=False):
        """ Set the news viewer as parent of the item if proxy mode enabled.
        """

class IAggregator(INewsViewer):
    """Aggregator of RSS items
    """


class IAgendaViewer(INewsViewer):
    """Viewer for agenda items
    """

    def days_to_show():
        """Return number of days to show on front page.
        """

    def set_days_to_show(number):
        """Sets the number of days to show in the agenda.
        """


class IServiceNewsCategorization(ISilvaService):
    """Defines subjects and target audiences.
    """

    def get_subjects():
        """Return all of the subjects.
        """

    def get_target_audiences():
        """Return all of the target_audiences.
        """

    def get_subjects_tree():
        """Return the tree of subjects.
        """

    def get_target_audiences_tree():
        """Return the tree of target_audiences.
        """


class IServiceNews(IServiceNewsCategorization):
    """A service that configures service news settings.
    """

    def add_subject(subject, parent):
        """Adds a subject to the tree of subjects.

        Subject is added under parent. If parent is None, the subject
        is added to the root.
        """

    def add_target_audience(target_audience, parent):
        """Adds a target_audience to the tree of target_audiences.

        Target audience is added under parent. If parent is None, the
        target_audience is added to the root.
        """

    def remove_subject(subject):
        """Removes the subject from the tree of subjects.
        """

    def remove_target_audience(target_audience):
        """Removes the target_audience from the tree of target_audiences.
        """

    # ACCESSORS
    def get_all_filters():
        """Return all the Silva News Filter contents from the site.
        """

    def get_all_sources(item=None):
        """Return all sources for News Item, global, or below the given item.
        """
