# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# ztk
from five import grok
from zope import interface, schema
from zope.i18nmessageid import MessageFactory
from zope.component import IFactory

# Silva
from silva.core.conf.interfaces import ITitledContent
from zeam.form import silva as silvaforms

# SilvaNews
from ..interfaces import IAgendaItem, IAgendaItemContent
from ..interfaces import timezone_source, get_default_tz_name
from silva.app.news.AgendaItem import AgendaItemOccurrence
from silva.app.news.NewsCategorization import INewsCategorizationFields
from silva.app.news.NewsItem.smi import NewsItemDetailsForm
from silva.app.news.widgets.recurrence import Recurrence

_ = MessageFactory('silva_news')


class IAgendaItemOccurrenceFields(interface.Interface):
    timezone_name = schema.Choice(
        source=timezone_source,
        title=_(u"Timezone"),
        description=_(u"Defines the time zone for dates"),
        required=True)
    start_datetime = schema.Datetime(
        title=_(u"Start date/time"),
        required=True)
    end_datetime = schema.Datetime(
        title=_(u"End date/time"),
        required=False)
    all_day = schema.Bool(
        title=_(u"All day"))
    recurrence = Recurrence(title=_("Recurrence"), required=False)
    end_recurrence_datetime = schema.Datetime(
        title=_(u"Recurrence end date"),
        description=_(u"Date on which the recurrence stops. Required if "
                      u"any recurrence is set"),
        required=False)
    location = schema.TextLine(
        title=_(u"Location"),
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


grok.global_utility(
    AgendaItemOccurrence, provides=IFactory,
    name=IAgendaItemOccurrenceFields.__identifier__, direct=True)


class IAgendaItemFields(INewsCategorizationFields):
    occurrences = schema.List(
        title=_(u"Occurrences"),
        description=_(u"When and where the event will happens."),
        value_type=schema.Object(schema=IAgendaItemOccurrenceFields),
        min_length=1)
    external_url = schema.URI(
        title=_(u"External URL"),
        description=_(u"external URL with more information about this event."),
        required=False)


AgendaItemFields = silvaforms.Fields(IAgendaItemFields)
AgendaItemFields['occurrences'].mode = 'input-list'
AgendaItemFields['occurrences'].valueField.dataManager = \
    silvaforms.SilvaDataManager
AgendaItemFields['occurrences'].valueField.objectFields[
    'timezone_name'].defaultValue = get_default_tz_name


class AgendaItemAddForm(silvaforms.SMIAddForm):
    grok.context(IAgendaItem)
    grok.name(u"Silva Agenda Item")

    fields = silvaforms.Fields(ITitledContent, AgendaItemFields)


class AgendaItemDetailsForm(NewsItemDetailsForm):
    grok.context(IAgendaItemContent)

    label = _(u"Agenda item details")
    fields = silvaforms.Fields(ITitledContent, AgendaItemFields).omit('id')
    actions = silvaforms.Actions(
        silvaforms.CancelAction(),
        silvaforms.EditAction())


# Prevent object validation, AgendaItemOccurrence doesn't validate
import zope.schema._field
zope.schema._field.Object._validate = zope.schema._field.Field._validate
