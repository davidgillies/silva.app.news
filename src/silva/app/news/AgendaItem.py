# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from icalendar import vDatetime, Calendar
from icalendar.interfaces import IEvent
from dateutil.rrule import rrulestr

# ztk
from five import grok
from zope import interface, schema
from zope.cachedescriptors.property import CachedProperty
from zope.component import getAdapter, getUtility, getMultiAdapter
from zope.i18nmessageid import MessageFactory
from zope.traversing.browser import absoluteURL

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

# Silva
from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews
from silva.core.conf.interfaces import ITitledContent
from zeam.form import silva as silvaforms
from Products.Silva import SilvaPermissions

# SilvaNews
from silva.app.document.interfaces import IDocumentDetails
from silva.app.news.interfaces import IAgendaItem, IAgendaItemVersion
from silva.app.news.interfaces import INewsViewer
from silva.app.news.interfaces import IServiceNews
from silva.app.news.NewsItem import NewsItemDetailsForm
from silva.app.news.NewsItem import NewsItemView, NewsItemListItemView
from silva.app.news.NewsItem import NewsItem, NewsItemVersion
from silva.app.news.NewsItem import NewsItemCatalogingAttributes
from silva.app.news.NewsCategorization import INewsCategorizationSchema

from silva.app.news.datetimeutils import (datetime_with_timezone,
    CalendarDatetime, datetime_to_unixtimestamp, get_timezone, RRuleData, UTC)
from silva.app.news.interfaces import timezone_source
from silva.app.news.widgets.recurrence import Recurrence


_marker = object()
_ = MessageFactory('silva_news')

class AgendaItemVersion(NewsItemVersion):
    """Silva News AgendaItemVersion
    """
    grok.implements(IAgendaItemVersion)

    security = ClassSecurityInfo()
    meta_type = "Silva Agenda Item Version"

    _start_datetime = None
    _end_datetime = None
    _display_time = True
    _location = ''
    _recurrence = None
    _all_day = False
    _timezone_name = None

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_timezone_name')
    def set_timezone_name(self, name):
        self._timezone_name = name

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_timezone_name')
    def get_timezone_name(self):
        timezone_name = getattr(self, '_timezone_name', None)
        if timezone_name is None:
            timezone_name = getUtility(IServiceNews).get_timezone_name()
        return timezone_name

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_timezone')
    def get_timezone(self):
        if not hasattr(self, '_v_timezone'):
            self._v_timezone = get_timezone(self.get_timezone_name())
        return self._v_timezone

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_rrule')
    def get_rrule(self):
        if self._recurrence is not None:
            return rrulestr(str(self._recurrence),
                            dtstart=self._start_datetime)
        return None

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_calendar_datetime')
    def get_calendar_datetime(self):
        if not self._start_datetime:
            return None
        return CalendarDatetime(self._start_datetime,
                                self._end_datetime,
                                recurrence=self.get_rrule())

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_display_time')
    def set_display_time(self, display_time):
        self._display_time = display_time

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_start_datetime')
    def set_start_datetime(self, value):
        self._start_datetime = datetime_with_timezone(
            value, self.get_timezone())

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_end_datetime')
    def set_end_datetime(self, value):
        self._end_datetime = datetime_with_timezone(
            value, self.get_timezone())

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_recurrence')
    def set_recurrence(self, recurrence):
        self._recurrence = recurrence

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_location')
    def set_location(self, value):
        self._location = value

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_all_day')
    def set_all_day(self, value):
        self._all_day = bool(value)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'display_time')
    def display_time(self):
        """returns True if the time parts of the datetimes should be displayed
        """
        return self._display_time

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_start_datetime')
    def get_start_datetime(self, tz=_marker):
        """Returns the start date/time
        """
        if tz is _marker:
            tz = self.get_timezone()
        cd = self.get_calendar_datetime()
        if cd:
            return cd.get_start_datetime(tz)
        return None

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_end_datetime')
    def get_end_datetime(self, tz=_marker):
        """Returns the start date/time
        """
        if tz is _marker:
            tz = self.get_timezone()
        cd = self.get_calendar_datetime()
        if cd:
            return cd.get_end_datetime(tz)
        return None

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_recurrence')
    def get_recurrence(self):
        if self._recurrence is not None:
            return str(self._recurrence)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_recurrence')
    def get_end_recurrence_datetime(self):
        if self._recurrence is not None:
            dt_string = RRuleData(self.get_recurrence()).get('UNTIL')
            if dt_string:
                return vDatetime.from_ical(dt_string).\
                    replace(tzinfo=UTC).astimezone(self.get_timezone())

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_location')
    def get_location(self):
        """Returns location manual
        """
        return self._location

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_all_day')
    def is_all_day(self):
        return self._all_day

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_all_day')
    get_all_day = is_all_day

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'fulltext')
    def fulltext(self):
        """Deliver the contents as plain text, for full-text search
        """
        parenttext = AgendaItemVersion.inheritedAttribute('fulltext')(self)
        return "%s %s" % (parenttext, self._location)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_timestamp_ranges')
    def get_timestamp_ranges(self):
        return self.get_calendar_datetime().\
            get_unixtimestamp_ranges()


InitializeClass(AgendaItemVersion)


class AgendaItem(NewsItem):
    """A News item for events. Includes date and location
       metadata, as well settings for subjects and audiences.
    """
    security = ClassSecurityInfo()
    grok.implements(IAgendaItem)
    meta_type = "Silva Agenda Item"
    silvaconf.icon("www/agenda_item.png")
    silvaconf.priority(3.8)
    silvaconf.version_class(AgendaItemVersion)

    @property
    def item_order(self):
        version_id = self.get_public_version()
        if version_id is None:
            version_id = self.get_approved_version()
            if version_id is None:
                return None
        version = getattr(self, version_id, None)
        if version is None:
            return None
        order_date = version.get_start_datetime()
        if order_date is None:
            return None
        return datetime_to_unixtimestamp(order_date)


InitializeClass(AgendaItem)


class AgendaViewMixin(object):

    def event_url(self):
        return "%s/event.ics" % absoluteURL(self.context, self.request)

    @CachedProperty
    def timezone(self):
        timezone = getattr(self.request, 'timezone', None)
        if not timezone:
            timezone = self.content.get_timezone()
        return timezone

    @CachedProperty
    def formatted_start_date(self):
        dt = self.content.get_start_datetime(self.timezone)
        if dt:
            service_news = getUtility(IServiceNews)
            return service_news.format_date(dt, not self.content.is_all_day())

    @CachedProperty
    def formatted_end_date(self):
        dt = self.content.get_end_datetime(self.timezone)
        if dt:
            service_news = getUtility(IServiceNews)
            return service_news.format_date(dt, not self.content.is_all_day())


class AgendaItemView(NewsItemView, AgendaViewMixin):
    """ Index view for agenda items """
    grok.context(IAgendaItem)


class IAgendaItemSchema(INewsCategorizationSchema):
    timezone_name = schema.Choice(
        source=timezone_source,
        title=_(u"timezone"),
        description=_(u"Defines the time zone for dates."),
        required=True)
    start_datetime = schema.Datetime(
        title=_(u"start date/time"),
        required=True)
    end_datetime = schema.Datetime(
        title=_(u"end date/time"),
        required=False)
    _all_day = schema.Bool(
        title=_(u"all day"))
    recurrence = Recurrence(title=_("recurrence"), required=False)
    end_recurrence_datetime = schema.Datetime(
        title=_(u"recurrence end date"),
        description=_(u"Date on which the recurrence stops. Required if "
                      u"any recurrence is set."),
        required=False)
    _location = schema.TextLine(
        title=_(u"location"),
        description=_(u"The location where the event is taking place."),
        required=False)

    @interface.invariant
    def enforce_end_recurrence_datetime(content):
        """ Enforce to set end_recurrence_datetime if recurrence is set
        """
        if not content.recurrence:
            # recurrence not set, bail out
            return

        if not content.end_recurrence_datetime:
            raise interface.Invalid(
                _(u"End recurrence date must be set when "
                  u"recurrence is."))

    @interface.invariant
    def enforce_start_date_before_end_date(content):
        if not content.end_datetime:
            return
        if content.start_datetime > content.end_datetime:
            raise interface.Invalid(
                _(u"End date must not is before start date."))

    @interface.invariant
    def enforce_end_recurrence_date_after_start_date(content):
        if not content.end_recurrence_datetime:
            return

        if content.start_datetime and \
                content.end_recurrence_datetime < content.start_datetime:
            raise interface.Invalid(
                _(u"End recurrence date must not be before start date."))

        if content.end_datetime and \
                content.end_recurrence_datetime < content.end_datetime:
            raise interface.Invalid(
                _(u"End recurrence date must not be before end date."))


def get_default_tz_name(form):
    util = getUtility(IServiceNews)
    return util.get_timezone_name()


def process_data(data):
    """preprocess the data before setting the content"""
    timezone = get_timezone(data['timezone_name'])
    date_fields = ['start_datetime',
                   'end_datetime',
                   'end_recurrence_datetime']
    # set timezone on datetime fields
    for name in date_fields:
        if data.has_key(name) and data[name] is not silvaforms.NO_VALUE:
            data[name] = data[name].replace(tzinfo=timezone)

    # copy data from end recurrence datetime to the recurrence field
    if data.has_key('recurrence') and \
            data['recurrence'] is not silvaforms.NO_VALUE:
        recurrence = RRuleData(data['recurrence'])
        recurrence['UNTIL'] = vDatetime(
            data['end_recurrence_datetime'].astimezone(UTC))
        data['recurrence'] = str(recurrence)

    if data.has_key('recurrence_end_datetime'):
        del data['recurrence_end_datetime']
    return data


class AgendaItemAddForm(silvaforms.SMIAddForm):
    grok.context(IAgendaItem)
    grok.name(u"Silva Agenda Item")

    fields = silvaforms.Fields(ITitledContent, IAgendaItemSchema)
    fields['timezone_name'].defaultValue = get_default_tz_name

    def _edit(self, parent, content, data):
        data = process_data(data)
        return super(AgendaItemAddForm, self)._edit(parent, content, data)


class EditAction(silvaforms.EditAction):

    def applyData(self, form, content, data):
        data = process_data(data)
        return super(EditAction, self).applyData(form, content, data)


class AgendaItemDetailsForm(NewsItemDetailsForm):
    grok.context(IAgendaItem)

    label = _(u"Agenda item details")
    fields = silvaforms.Fields(ITitledContent, IAgendaItemSchema).omit('id')
    actions = silvaforms.Actions(silvaforms.CancelAction(), EditAction())


class AgendaItemCatalogingAttributes(NewsItemCatalogingAttributes):
    grok.context(IAgendaItem)

    @property
    def start_datetime(self):
        if self.version is not None:
            return self.version.get_start_datetime()

    @property
    def end_datetime(self):
        if self.version is not None:
            return self.version.get_end_datetime()


class AgendaItemInlineView(silvaviews.View):
    """ Inline rendering for calendar event tooltip """
    grok.context(IAgendaItem)
    grok.name('tooltip.html')

    def render(self):
        details = getMultiAdapter(
            (self.content, self.request), IDocumentDetails)
        return u'<div>' + details.get_introduction() + u"</div>"


class AgendaItemListItemView(NewsItemListItemView, AgendaViewMixin):
    """ Render as a list items (search results)
    """
    grok.context(IAgendaItem)


class AgendaItemICS(silvaviews.View):
    """ render an ics event
    """
    grok.context(IAgendaItem)
    grok.require('zope2.View')
    grok.name('event.ics')

    def update(self):
        self.viewer = INewsViewer(self.context, None)
        self.request.response.setHeader('Content-Type', 'text/calendar')
        self.content = self.context.get_viewable()
        self.event_factory = getAdapter(self.content, IEvent)

    def render(self):
        cal = Calendar()
        cal.add('prodid', '-//Silva News Calendaring//lonely event//')
        cal.add('version', '2.0')
        cal.add_component(self.event_factory(self.viewer, self.request))
        return cal.as_string()


