# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision$

from zope import schema
from zope.i18nmessageid import MessageFactory
from five import grok
from zeam.utils.batch import batch

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from Products.Silva import SilvaPermissions

from silva.core import conf as silvaconf
from silva.core.conf.interfaces import ITitledContent
from silva.core.interfaces import IVersionManager
from silva.ui.menu import MenuItem, ContentMenu
from zeam.form import silva as silvaforms
from zeam.form import table as tableforms
from zeam.form.base.datamanager import BaseDataManager


# SilvaNews
from silva.app.news.widgets.path import Path
from silva.app.news.interfaces import INewsFilter
from silva.app.news.filters.NewsItemFilter import NewsItemFilter
from silva.app.news.filters.NewsItemFilter import INewsItemFilterSchema
from silva.app.news import interfaces

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

    _article_meta_types = ['Silva Article']
    _agenda_item_meta_types = ['Silva Agenda Item']

    def __init__(self, id):
        super(NewsFilter, self).__init__(id)
        self._show_agenda_items = 0

    # ACCESSORS

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_all_items')
    def get_all_items(self, meta_types=None):
        """
        Returns all items available to this filter. This function will
        probably only be used in the back-end.
        """
        if not self.get_sources():
            return []
        query = self._prepare_query(meta_types)
        results = self._query_items(
            filter_excluded_items=False, public_only=False, **query)
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


class INewsFilterSchema(INewsItemFilterSchema):
    _show_agenda_items = schema.Bool(
        title=_(u"show agenda items"))


class NewsFilterAddForm(silvaforms.SMIAddForm):
    grok.context(INewsFilter)
    grok.name(u'Silva News Filter')

    fields = silvaforms.Fields(ITitledContent, INewsFilterSchema)


class NewsFilterEditForm(silvaforms.SMIEditForm):
    """ Base form for filters """
    grok.context(INewsFilter)

    fields = silvaforms.Fields(ITitledContent, INewsFilterSchema).omit('id')


class ExcludeAction(silvaforms.Action):
    def __call__(self, form, content, selected, deselected, unchanged):
        news_filter = form.context
        for line in selected:
            content = line.getContentData().getContent()
            news_filter.remove_excluded_item(content)
        for line in deselected:
            content = line.getContentData().getContent()
            news_filter.add_excluded_item(content)


class IItemSelection(ITitledContent):
    path = Path(title=_(u'path'), html_target="_blank")
    publication_datetime = schema.Datetime(title=_(u'publication date'))
    expiration_datetime = schema.Datetime(title=_(u'expiration date'))


class ItemSelection(BaseDataManager):

    def __init__(self, content, filter):
        self.filter = filter
        self.content = content
        self.version = self.content.get_viewable() or \
            self.content.get_previewable() or \
            self.content.get_editable()
        self.manager = IVersionManager(self.version)

    def get(self, identifier):
        try:
            return getattr(self, identifier)
        except AttributeError:
            raise KeyError(identifier)

    @property
    def select(self):
        return not self.filter.is_excluded_item(self.content)

    @property
    def path(self):
        path = self.content.getPhysicalPath()
        root_path = self.content.get_root().getPhysicalPath()
        if root_path == path[:len(root_path)]:
            return "/".join(path[len(root_path):])
        return "/".join(path)

    @property
    def title(self):
        return self.content.get_title_or_id()

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


class Items(silvaforms.SMITableForm):
    grok.baseclass()
    grok.context(interfaces.INewsItemFilter)
    grok.require('silva.ChangeSilvaContent')
    grok.name('items')
    label = _('Items')

    description = _('uncheck items you want to ignore')
    ignoreRequest = True
    ignoreContent = False

    mode = silvaforms.DISPLAY
    emptyDescription = _(u"There are no items.")
    tableFields = silvaforms.Fields(IItemSelection).omit('id')
    tableActions = tableforms.TableSelectionActions(
        ExcludeAction(identifier='update', title=_("Update")))

    def prepareSelectedField(self, field):
        field.ignoreContent = False
        field.ignoreRequest = True


class NewsFilterItems(Items):
    offset = 0
    count = 10

    def publishTraverse(self, request, name):
        try:
            offset = int(name)
            self.offset = offset
            return self
        except (TypeError, ValueError):
            pass
        return super(Items, self).publishTraverse(request, name)

    def getItems(self):
        def build_item_selection(item):
            return ItemSelection(item, self.context)

        self.batch = self.getBatch(factory=build_item_selection)
        return list(self.batch)

    def getBatch(self, factory=None):
        return batch(list(self.context.get_all_items()),
            start=self.offset,
            count=self.count,
            factory=factory)


class ItemsMenu(MenuItem):
    grok.adapts(ContentMenu, interfaces.INewsItemFilter)
    grok.require('silva.ChangeSilvaContent')
    grok.order(30)
    name = _('Items')
    screen = Items


