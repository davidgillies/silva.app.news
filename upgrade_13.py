from Products.SilvaNews import upgrade_registry

# zope imports
import zLOG

log_severity = zLOG.INFO

# silva imports
from Products.Silva.interfaces import IUpgrader
from Products.SilvaNews.Tree import Root, Node

# upgraders for SilvaNews-1.2 (or before) to SilvaNews-1.3

class DummyUpgrader:
    __implements__ = IUpgrader

    def upgrade(self, obj):
        return obj

upgrade_registry.registerUpgrader(
    DummyUpgrader(), '1.2', 'Silva Root')

class ArticleDisplayTimeSetter:
    """set an attribute '_display_time' on all AgendaItems"""

    __implements__ = IUpgrader

    def upgrade(self, obj):
        zLOG.LOG(
            'SilvaNews',
            log_severity,
            'Add display_date attribute to AgendaItem %s' % 
                '/'.join(obj.getPhysicalPath())
            )
        if not hasattr(obj, '_display_time'):
            obj._display_time = True

        return obj

upgrade_registry.registerUpgrader(
    ArticleDisplayTimeSetter(), '1.3', 'Silva Agenda Item Version')

class ServiceLocaleSetter:
    """set attributes '_locale' and '_date_format' on service_news"""
    __implements__ = IUpgrader

    def upgrade(self, obj):
        zLOG.LOG(
            'SilvaNews',
            log_severity,
            'Add _locale and _date_format attributes to News Service'
            )
        if not hasattr(obj, '_locale') or not hasattr(obj, '_date_format'):
            obj._locale = 'en'
            obj._date_format = 'medium'
        return obj

upgrade_registry.registerUpgrader(
    ServiceLocaleSetter(), '1.3', 'Silva News Service')

class SubjectTargetAudienceUpdater:
    """convert subjects and target audiences to trees"""
    __implements__ = IUpgrader

    def upgrade(self, obj):
        zLOG.LOG(
            'SilvaNews',
            log_severity,
            'Change format of subjects and target audiences storage on '\
            'News Service'
            )
        if type(obj._subjects) == dict:
            root = Root()
            self._build_tree(root, obj._subjects)
            obj._subjects = root

        if type(obj._target_audiences == dict):
            root = Root()
            self._build_tree(root, obj._target_audiences)
            obj._target_audiences = root

        obj._p_changed = 1
        return obj

    def _build_tree(self, root, data):
        # first find all the items that have no parent, then 
        # walk through those items recursively
        for itemid, value in data.items():
            if value[0] == None:
                # root element
                self._build_item(itemid, root, data)

    def _build_item(self, elid, parent, data):
        node = Node(elid, elid)
        parent.addChild(node)
        if data.has_key(elid):
            for childid in data[elid][1:]:
                self._build_item(childid, node, data)
    
upgrade_registry.registerUpgrader(
    SubjectTargetAudienceUpdater(), '1.3', 'Silva News Service')

class DisplayDateTimeSetter:
    """set attribute 'display_datetime' of news items"""
    __implements__ = IUpgrader

    def upgrade(self, obj):
        zLOG.LOG(
            'SilvaNews',
            log_severity,
            'Add _display_datetime attribute to news item %s' % 
                '/'.join(obj.getPhysicalPath())
            )
        if not hasattr(obj, '_display_datetime'):
            pdt = obj.publication_datetime()
            obj._display_datetime = pdt
        return obj

upgrade_registry.registerUpgrader(
    DisplayDateTimeSetter(), '1.3', 'Silva Article Version')
upgrade_registry.registerUpgrader(
    DisplayDateTimeSetter(), '1.3', 'Silva Agenda Item Version')

class NumberToShowArchiveSetter:
    """set attribute '_number_to_show_archive' on news items"""
    __implements__ = IUpgrader

    def upgrade(self, obj):
        zLOG.LOG(
            'SilvaNews',
            log_severity,
            'Add _number_to_show_archive attribute to news item %s' % 
                '/'.join(obj.getPhysicalPath())
            )
        if not hasattr(obj, '_number_to_show_archive'):
            obj._number_to_show_archive = 10
        return obj

upgrade_registry.registerUpgrader(
    NumberToShowArchiveSetter(), '1.3', 'Silva News Viewer')
upgrade_registry.registerUpgrader(
    NumberToShowArchiveSetter(), '1.3', 'Silva Agenda Viewer')

