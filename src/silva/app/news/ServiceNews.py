# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from datetime import datetime

from five import grok
from zope.component import getUtility
import localdatetime

from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent

from silva.core.interfaces import IContainer
from silva.core import conf as silvaconf
from silva.core.services.base import SilvaService
from silva.core.services.interfaces import ICatalogService
from silva.core.views import views as silvaviews
import Products.Silva.SilvaPermissions as SilvaPermissions
from Products.Silva.ExtensionRegistry import meta_types_for_interface

from silva.app.news import Tree
from silva.app.news.interfaces import IServiceNews, INewsItemFilter
from silva.app.news.datetimeutils import (
    local_timezone, get_timezone, zone_names)


class TimezoneMixin(object):

    security = ClassSecurityInfo()
    week_days_list = [('Mon',0), ('Tue',1), ('Wed',2),
        ('Thu',3), ('Fri',4), ('Sat',5), ('Sun',6)]

    def __init__(self):
        self._timezone = local_timezone
        self._timezone_name = 'local'

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'default_timezone')
    def default_timezone(self):
        return local_timezone

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'default_timezone_name')
    def default_timezone_name(self):
        return 'local'

    # ACCESSORS
    security.declareProtected(
        SilvaPermissions.AccessContentsInformation,'get_timezone')
    def get_timezone(self):
        return getattr(self, '_timezone', self.default_timezone())

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_timezone_name')
    def get_timezone_name(self):
        return getattr(self, '_timezone_name',
            self.default_timezone_name())

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_timezone_name')
    def set_timezone_name(self, name):
        self._timezone = get_timezone(name)
        self._timezone_name = name

    security.declareProtected(
        'View', 'timezone_list')
    def timezone_list(self):
        default = self.default_timezone_name()
        zones = list(zone_names)
        if default not in zone_names:
            zones.append(default)
        return zones

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_first_weekday')
    def set_first_weekday(self, weekday):
        if weekday not in range(0, 7):
            raise ValueError("weekday should be between 0 and 6")
        self._first_weekday = weekday

    security.declareProtected(
        'View', 'get_first_weekday')
    def get_first_weekday(self):
        return getattr(self, '_first_weekday', 0)


InitializeClass(TimezoneMixin)


class ServiceNews(SilvaService, TimezoneMixin):
    """Provides settings for various news settings.
    """
    grok.implements(IServiceNews)
    grok.name('service_news')
    security = ClassSecurityInfo()
    meta_type = 'Silva News Service'

    silvaconf.icon('www/newsservice.gif')

    manage_options = (
        {'label': 'Edit', 'action': 'manage_news'},
        ) + SilvaService.manage_options

    def __init__(self, id):
        SilvaService.__init__(self, id)
        self._subjects = Tree.Root()
        self._target_audiences = Tree.Root()
        self._locale = 'en'
        self._date_format = 'medium'
        self.add_subject(u'generic', u'Generic')
        self.add_target_audience(u'all', u'All')

    def get_all_filters(self):
        catalog = getUtility(ICatalogService)
        query = {
            'meta_type': {
                'operator': 'or',
                'query': meta_types_for_interface(INewsItemFilter)}}
        return (brain.getObject() for brain in catalog(query))

    def get_all_sources(self, item=None):
        catalog = getUtility(ICatalogService)

        brains = catalog({
                'meta_type': 'Silva News Publication',
                'snn-np-settingsis_private':'no'})

        if item is not None:
            while not IContainer.providedBy(item):
                item = aq_parent(item)

            paths = []
            parts = item.getPhysicalPath()
            for size in range(1, len(parts) + 1):
                paths.append('/'.join(parts[:size]))

            brains += catalog({
                    'snn-np-settingsis_private': 'yes',
                    'parent_path': paths})

        return (brain.getObject() for brain in brains)

    security.declareProtected('Setup ServiceNews',
                                'add_subject')
    def add_subject(self, id, title, parent=None):
        """add a subject to the tree"""
        node = Tree.Node(id, title)
        parentnode = self._subjects
        if parent is not None:
            parentnode = self._subjects.get_element(parent)
        parentnode.add_child(node)
        self._p_changed = 1

    security.declareProtected('Setup ServiceNews',
                                'add_target_audience')
    def add_target_audience(self, id, title, parent=None):
        """add a target audience to the tree"""
        node = Tree.Node(id, title)
        parentnode = self._target_audiences
        if parent is not None:
            parentnode = self._target_audiences.get_element(parent)
        parentnode.add_child(node)
        self._p_changed = 1

    security.declareProtected('View', 'get_subjects_tree')
    def get_subjects_tree(self):
        return self._subjects

    security.declareProtected('View', 'get_subjects')
    def get_subjects(self):
        """returns a list of (id, title) tuples"""
        return [(x.id(), x.title())
                for x in  self._subjects.get_elements()]

    security.declareProtected('View', 'get_target_audiences')
    def get_target_audiences(self):
        """returns a list of (id, title) tuples"""
        return [(x.id(), x.title())
                for x in self._target_audiences.get_elements()]

    security.declareProtected('View', 'get_target_audiences_tree')
    def get_target_audiences_tree(self):
        return self._target_audiences

    security.declareProtected('Setup ServiceNews',
                                'remove_subject')
    def remove_subject(self, id):
        """removes a subject by id"""
        node = self._subjects.get_element(id)
        if node.children():
            raise ValueError, 'node not empty'
        node.parent().remove_child(node)
        self._p_changed = 1

    security.declareProtected('Setup ServiceNews',
                                'remove_target_audience')
    def remove_target_audience(self, id):
        """removes a target audience by id"""
        node = self._target_audiences.get_element(id)
        if node.children():
            raise ValueError, 'node not empty'
        node.parent().remove_child(node)
        self._p_changed = 1

    security.declareProtected('View', 'locale')
    def locale(self):
        """returns the current locale (used to format public dates)"""
        return self._locale

    security.declareProtected('View', 'date_format')
    def date_format(self):
        """returns the current date format

            Z3's locale package has a nunber of different date formats to
            choose from per locale, managers can set what format to use
            on this service (since there's no better place atm)
        """
        return self._date_format

    security.declareProtected('View', 'format_date')
    def format_date(self, dt, display_time=True):
        """returns a formatted datetime string
           takes the service's locale setting into account
        """
        if not dt:
            return ''
        if not isinstance(dt, datetime):
            dt = dt.asdatetime()
        return localdatetime.get_formatted_date(
            dt,
            size=self._date_format,
            locale=self._locale,
            display_time=display_time)


InitializeClass(ServiceNews)


def flatten_tree_helper(tree, ret, depth=0):
    els = tree.children()
    els.sort(lambda a, b: cmp(a.id(), b.id()))
    for el in els:
        ret.append((el.id(), el.title(), depth))
        flatten_tree_helper(el, ret, depth+1)


class ManageServiceNews(silvaviews.ZMIView):
    grok.name('manage_news')
    grok.context(ServiceNews)

    def update(self):
        self.status = None
        self.renaming = []
        for action in  ['manage_add_subject',
                        'manage_remove_subject',
                        'manage_add_target_audience',
                        'manage_remove_target_audience',
                        'manage_rename_start',
                        'manage_rename_subjects',
                        'manage_rename_target_audiences',
                        'manage_set_locale']:
            if action in self.request:
                getattr(self, action)()

    def subject_tree(self):
        """returns a list (id, title, depth) for all elements in the tree"""
        ret = []
        flatten_tree_helper(self.context._subjects, ret)
        return ret

    def target_audience_tree(self):
        """returns a list (id, title, depth) for all elements in the tree"""
        ret = []
        flatten_tree_helper(self.context._target_audiences, ret)
        return ret

    def manage_add_subject(self):
        """Add a subject"""
        if (not self.request.has_key('subject') or not
            self.request.has_key('parent') or self.request['subject'] == ''
            or not self.request.has_key('title') or self.request['title'] == ''):
            self.status ='Missing id or title'
            return

        if self.request['parent']:
            try:
                self.context.add_subject(unicode(self.request['subject']),
                                         unicode(self.request['title']),
                                         unicode(self.request['parent']))
            except Tree.DuplicateIdError, e:
                self.status = e
                return
        else:
            try:
                self.context.add_subject(unicode(self.request['subject']),
                                         unicode(self.request['title']))
            except Tree.DuplicateIdError, e:
                self.status = e
                return

        self.status ='Subject %s added' % unicode(self.request['subject'])

    def manage_remove_subject(self):
        """Remove a subject"""
        if not self.request.has_key('subjects'):
            self.status ='No subjects specified'
            return

        subs = [unicode(s) for s in self.request['subjects']]
        for subject in subs:
            try:
                self.context.remove_subject(subject)
            except (KeyError, ValueError), e:
                self.status = e
                return

        self.status ='Subjects %s removed' % ', '.join(subs)

    def manage_add_target_audience(self):
        """Add a target_audience"""
        if (not self.request.has_key('target_audience') or
                not self.request.has_key('parent') or
                self.request['target_audience'] == '' or
                not self.request.has_key('title') or
                self.request['title'] == ''):
            self.status ='Missing id or title'
            return

        if self.request['parent']:
            try:
                self.context.add_target_audience(
                    unicode(self.request['target_audience'], 'UTF-8'),
                    unicode(self.request['title'], 'UTF-8'),
                    unicode(self.request['parent'], 'UTF-8'))
            except Tree.DuplicateIdError, e:
                self.status = e
                return
        else:
            try:
                self.context.add_target_audience(
                    unicode(self.request['target_audience'], 'UTF-8'),
                    unicode(self.request['title'], 'UTF-8'))
            except Tree.DuplicateIdError, e:
                self.status = e
                return

        self.status ='Target audience %s added' % (
            unicode(self.request['target_audience'], 'UTF-8'))

    def manage_remove_target_audience(self):
        """Remove a target_audience"""
        if not self.request.has_key('target_audiences'):
            self.status ='No target audience specified'
            return

        tas = [unicode(t, 'UTF-8') for t in self.request['target_audiences']]
        for target_audience in tas:
            try:
                self.context.remove_target_audience(target_audience)
            except (KeyError, ValueError), e:
                self.status = e
                return

        self.status ='Target audiences %s removed' % ', '.join(tas)

    def manage_rename_start(self):
        """Rename one or more items"""
        if (not self.request.has_key('subjects') and not
                self.request.has_key('target_audiences')):
            self.status ='No items selected to rename'
            return
        return self.manage_rename_view()

    def manage_rename_subjects(self):
        """Rename subjects"""
        illegal = []
        for name, value in self.request.form.items():
            if name.startswith('title_'):
                continue
            uname = unicode(name, 'UTF-8')
            uvalue = unicode(value, 'UTF-8')
            subject = self.context._subjects.get_element(uname)
            if uvalue != subject.id():
                try:
                    subject.set_id(uvalue)
                except Tree.DuplicateIdError:
                    illegal.append(uvalue)
                    continue
            title = unicode(self.request.form['title_%s' % name], 'UTF-8')
            subject.set_title(title)
            self.context._p_changed = 1
        if illegal:
            self.status = \
                'Items %s could not be renamed (name already in use).' % (
                ', '.join(illegal))
        else:
            self.status ='Items renamed'

    def manage_rename_target_audiences(self):
        """Rename target audiences"""
        illegal = []
        for name, value in self.request.form.items():
            if name.startswith('title_'):
                continue
            uname = unicode(name, 'UTF-8')
            uvalue = unicode(value, 'UTF-8')
            audience = self.context._target_audiences.getElement(uname)
            if uvalue != audience.id():
                try:
                    audience.set_id(uvalue)
                except Tree.DuplicateIdError:
                    illegal.append(uvalue)
                    continue
            title = unicode(self.request.form['title_%s' % name], 'UTF-8')
            audience.set_title(title)
            self.context._p_changed = 1
        if illegal:
            self.status = \
                'Items %s could not be renamed (name already in use).' % (
                ', '.join(illegal))
        else:
            self.status ='Items renamed'

    # XXX we probably want to move these elsewhere, for now however this seems
    # the most logical location
    def manage_set_locale(self):
        """set the locale and date format

            used for displaying public date/times
        """
        field_errors = {
            'locale': "No locale provided!",
            'date_format': "No date format provided!",
            'timezone_name': "No timezone provided!",
            'first_weekday': "No first weekday provided!"
        }
        for field, error in field_errors.iteritems():
            if not self.request.has_key(field) or not self.request[field]:
                self.status = error
                return

        self.context._locale = self.request['locale']
        self.context._date_format = self.request['date_format']
        self.context.set_timezone_name(self.request['timezone_name'])
        self.context.set_first_weekday(int(self.request['first_weekday']))
        self.status ='Locale set'

