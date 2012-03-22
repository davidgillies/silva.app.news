# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface

from DateTime import DateTime
from datetime import datetime

from silva.core.conf.interfaces import ITitledContent
from silva.core.smi.content import ContentEditMenu
from silva.core.smi.content.publish import IPublicationFields
from silva.core.smi.content.publish import Publish
from silva.core.views import views as silvaviews
from silva.ui.menu import MenuItem
from zeam.form import silva as silvaforms
from zeam.form import autofields

from ..interfaces import INewsItem, INewsItemContent
from ..NewsCategorization import INewsCategorizationSchema


_ = MessageFactory('silva_news')


class INewsItemSchema(INewsCategorizationSchema):
    external_url = schema.URI(
        title=_(u"External URL"),
        description=_(u"external URL with more information "
                      u"about this news item."),
        required=False)


class NewsItemAddForm(silvaforms.SMIAddForm):
    grok.context(INewsItem)
    grok.name(u"Silva News Item")

    fields = silvaforms.Fields(ITitledContent, INewsItemSchema)


class NewsItemDetailsForm(silvaforms.SMIEditForm):
    grok.context(INewsItem)
    grok.name('details')

    label = _(u"News item details")
    fields = silvaforms.Fields(ITitledContent, INewsItemSchema).omit('id')


class NewsItemDetailsMenu(MenuItem):
    grok.adapts(ContentEditMenu, INewsItemContent)
    grok.require('silva.ChangeSilvaContent')
    grok.order(15)

    name = _('Details')
    screen = NewsItemDetailsForm


class NewsItemPublicationPortlet(silvaviews.Viewlet):
    grok.context(INewsItemContent)
    grok.view(Publish)
    grok.viewletmanager(silvaforms.SMIFormPortlets)
    grok.order(20)

    def update(self):
        viewable = self.context.get_viewable()
        self.display_date = None
        if viewable is not None:
            format = self.request.locale.dates.getFormatter('dateTime').format
            convert = lambda d: d is not None and format(d.asdatetime()) or None
            self.display_date = convert(viewable.get_display_datetime())


# Add display datetime on publish smi tab

class INewsItemPublicationFields(Interface):
    display_datetime = schema.Datetime(title=_("Display datetime"))


class NewsItemPublication(grok.Adapter):
    grok.context(INewsItemContent)
    grok.provides(INewsItemPublicationFields)

    @apply
    def display_datetime():

        def getter(self):
            current = self.context.get_unapproved_version_display_datetime()
            if current is None:
                return datetime.now()
            return current

        def setter(self, value):
            self.context.set_unapproved_version_display_datetime(
                DateTime(value))

        return property(getter, setter)


class NewsItemPublicationFields(autofields.AutoFields):
    autofields.context(INewsItemContent)
    autofields.group(IPublicationFields)
    autofields.order(20)
    fields = silvaforms.Fields(INewsItemPublicationFields)



