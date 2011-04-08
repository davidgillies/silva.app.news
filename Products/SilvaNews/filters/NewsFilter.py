# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision$

from itertools import imap

from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from five import grok
from zeam.utils.batch import batch

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from Products.Silva import SilvaPermissions
from silva.core import conf as silvaconf
from zeam.form import silva as silvaforms
from zeam.form import table as tableforms
from zeam.form.table.select import SelectField
from silva.core.conf.interfaces import ITitledContent
from silva.core.interfaces import IVersionManager
from silva.ui.menu import MenuItem, ContentMenu
from silva.ui.rest import Screen

# SilvaNews
from Products.SilvaNews.widgets.path import Path
from Products.SilvaNews.interfaces import INewsFilter, INewsQualifiers
from Products.SilvaNews.filters.NewsItemFilter import NewsItemFilter
from Products.SilvaNews import interfaces

_ = MessageFactory('silva_news')


class NewsFilter(NewsItemFilter):
    """To enable editors to channel newsitems on a site, all items
        are passed from NewsFolder to NewsViewer through filters. On a filter
        you can choose which NewsFolders you want to channel items for and
        filter the items on several criteria (as well as individually).
    """
    security = ClassSecurityInfo()

    meta_type = "Silva News Filter"
    grok.implements(INewsFilter)
    silvaconf.icon("www/news_filter.png")
    silvaconf.priority(3.2)

    _article_meta_types = ['Silva Article Version']
    _agenda_item_meta_types = ['Silva Agenda Item Version']

    def __init__(self, id):
        super(NewsFilter, self).__init__(id)
        self._show_agenda_items = 0

    # ACCESSORS

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_all_items')
    def get_all_items(self, meta_types=None):
        """
        Returns all items available to this filter. This function will
        probably only be used in the back-end, but nevertheless has
        AccessContentsInformation-security because it does not reveal
        any 'secret' information...
        """
        if not self.get_sources():
            return []
        query = self._prepare_query(meta_types)
        results = self._query_items(**query)
        return results

    security.declarePrivate('get_allowed_meta_types')
    def get_allowed_meta_types(self):
        """Returns the allowed meta_types for this filter"""
        allowed = self._article_meta_types[:]
        if self.show_agenda_items():
            allowed += self._agenda_item_meta_types[:]
        return allowed

    # MANIPULATORS

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'show_agenda_items')
    def show_agenda_items(self):
        return self._show_agenda_items

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_show_agenda_items')
    def set_show_agenda_items(self, value):
        self._show_agenda_items = not not int(value)


InitializeClass(NewsFilter)


class NewsFilterAddForm(silvaforms.SMIAddForm):
    grok.context(INewsFilter)
    grok.name(u'Silva News Filter')


class INewsFilterSchema(INewsQualifiers):
    _keep_to_path = schema.Bool(
        title=_(u"stick to path"))

    _show_agenda_items = schema.Bool(
        title=_(u"show agenda items"))

    sources = schema.Set(
        value_type=schema.Choice(source=interfaces.news_source),
        title=_(u"sources"),
        description=_(u"Use predefined sources."))


class NewsFilterEditForm(silvaforms.SMIEditForm):
    """ Base form for filters """
    grok.context(INewsFilter)
    fields = silvaforms.Fields(INewsFilterSchema)


class Items(silvaforms.SMIComposedForm):
    grok.adapts(Screen, interfaces.INewsFilter)
    grok.context(interfaces.INewsFilter)
    grok.require('silva.ChangeSilvaContent')
    grok.name('items')
    label = _('Items')

    offset = 0

    def publishTraverse(self, request, name):
        try:
            offset = int(name)
            self.offset = offset
            return self
        except (TypeError, ValueError):
            pass
        return super(Items, self).publishTraverse(request, name)


class ExcludeAction(silvaforms.Action):
    def __call__(self, form, content, line):
        item = content.context
        news_filter = form.context
        news_filter.add_excluded_item(item)


class UnExcludeAction(silvaforms.Action):
    def __call__(self, form, content, line):
        item = content.context
        news_filter = form.context
        news_filter.remove_excluded_item(item)


class IItemSelection(ITitledContent):
    path = Path(title=_(u'path'), html_target="_blank")
    publication_datetime = schema.Datetime(title=_(u'publication date'))
    expiration_datetime = schema.Datetime(title=_(u'expiration date'))


class ItemSelection(grok.Adapter):
    grok.context(interfaces.INewsItem)
    grok.implements(IItemSelection)

    def __init__(self, context):
        super(ItemSelection, self).__init__(context)
        self.version = self.context.get_viewable() or \
            self.context.get_previewable() or \
            self.context.get_editable()
        self.manager = IVersionManager(self.version)

    @property
    def path(self):
        path = self.context.getPhysicalPath()
        root_path = self.context.get_root().getPhysicalPath()
        if root_path == path[:len(root_path)]:
            return "/".join(path[len(root_path):])
        return "/".join(path)

    @property
    def title(self):
        return self.context.get_title_or_id()

    @property
    def publication_datetime(self):
        dt = self.manager.get_publication_datetime()
        if dt is not None:
            return dt.asdatetime()

    @property
    def expiration_datetime(self):
        dt = self.manager.get_expiration_datetime()
        if dt is not None:
            return dt.asdatetime()


class ItemsForm(silvaforms.SMISubTableForm):
    grok.baseclass()
    grok.view(Items)
    grok.context(interfaces.INewsFilter)

    ignoreRequest = True
    ignoreContent = False

    label = _('Available news items')
    mode = silvaforms.DISPLAY
    tableFields = silvaforms.Fields(IItemSelection).omit('id')
    emptyDescription = _(u"There are no items.")

    def selectFieldFactory(self, *args, **kw):
        selected = SelectField(*args, **kw)
        selected.ignoreRequest = True
        return selected


class ItemListForm(ItemsForm):
    grok.order(10)
    count = 5

    label = _('Active items')
    tableActions = tableforms.TableActions(
        ExcludeAction(identifier='ignore'))

    def getItems(self):
        self.batch = batch(list(self.context.get_all_items()),
            start=self.parent.offset,
            count=self.count)
        return [IItemSelection(i) for i in self.batch]


class IgnoredItems(ItemsForm):
    grok.order(20)

    label = _('Ignored items')
    tableActions = tableforms.TableActions(
        UnExcludeAction(identifier='unignore'))

    def getItems(self):
        intids = getUtility(IIntIds)
        def get_item(intid):
            target = intids.getObject(intid)
            return IItemSelection(target)
        return imap(get_item, self.context.get_excluded_items())


class ItemsMenu(MenuItem):
    grok.adapts(ContentMenu, interfaces.INewsFilter)
    grok.require('silva.ChangeSilvaContent')
    grok.order(30)
    name = _('Items')
    screen = Items


