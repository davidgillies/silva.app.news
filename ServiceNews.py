# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.9 $

import Globals
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.Silva.helpers import add_and_edit
from interfaces import IServiceNews

class NotEmptyError(Exception):
    pass

class DuplicateError(Exception):
    pass

# XXX needs an icon

class ServiceNews(SimpleItem):
    """This object provides lists of subjects and target_audiences for Filters
    """
    __implements__ = IServiceNews
    security = ClassSecurityInfo()
    meta_type = 'Silva News Service'
    
    manage_options = (
                      {'label': 'Edit', 'action': 'manage_main'},
   #                   {'label': 'Info', 'action': 'manage_info_tab'}
                      ) + SimpleItem.manage_options

    manage_main = edit_tab = PageTemplateFile('www/serviceNewsEditTab',
                                              globals(), __name__='edit_tab')
    manage_rename_view = PageTemplateFile('www/serviceNewsRenameView',
                                             globals(), __name__='manage_rename_view')
    manage_info_tab = PageTemplateFile('www/serviceNewsInfoTab',
                                       globals(), __name__='manage_info_tab')

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self._subjects = {}
        self._target_audiences = {}

    security.declareProtected('Setup ServiceNews',
                              'add_subject')
    def add_subject(self, subject, parent=None):
        """Adds the subject to the dict, first item in value is the parent
        """
        if self._subjects.has_key(subject):
            message = "%s is already in the list of subjects" % subject
            raise DuplicateError, message
        self._subjects[subject] = [parent]
        if parent:
            self._subjects[parent].append(subject)
        self._p_changed = 1

    security.declareProtected('Setup ServiceNews',
                              'add_target_audience')
    def add_target_audience(self, target_audience, parent=None):
        """
        Adds a target audience to the dict, first item in the value is
        the parent
        """
        if self._target_audiences.has_key(target_audience):
            message = "%s is already in the list of target audiences" % target_audience
            raise DuplicateError, message
        self._target_audiences[target_audience] = [parent]
        if parent:
            self._target_audiences[parent].append(target_audience)
        self._p_changed = 1

    security.declareProtected('Setup ServiceNews',
                              'remove_subject')
    def remove_subject(self, subject):
        """Removes a subject from the dict
        """
        if not self._subjects.has_key(subject):
            message = "%s cannot be found in the list of subjects" % subject
            raise KeyError, message
        if len(self._subjects[subject]) > 1:
            message = "%s contains children" % subject
            raise NotEmptyError, message
        del(self._subjects[subject])
        for key in self._subjects.keys():
            if subject in self._subjects[key]:
                self._subjects[key].remove(subject)
        self._p_changed = 1

    security.declareProtected('Setup ServiceNews',
                              'remove_target_audience')
    def remove_target_audience(self, target_audience):
        """Removes a target audience from the dict
        """
        if not self._target_audiences.has_key(target_audience):
            message = "%s cannot be found in the list of target audiences" % target_audience
            raise KeyError, message
        if len(self._target_audiences[target_audience]) > 1:
            message = "%s contains children" % target_audience
            raise NotEmptyError, message
        del(self._target_audiences[target_audience])
        for key in self._target_audiences.keys():
            if target_audience in self._target_audiences[key]:
                self._target_audiences[key].remove(target_audience)
        self._p_changed = 1

    # ACCESSORS
    security.declareProtected('View',
                              'subjects')
    def subjects(self):
        """Returns a flat list of all subjects
        """
        return self._subjects.keys()

    security.declareProtected('View',
                              'subject_tree')
    def subject_tree(self, parent=None, depth=0):
        """
        Returns a list of tuples (subject, depth) that makes it easy
        to create a tree
        """
        returnvalue = []
        keys = self._subjects.keys()
        keys.sort()
        for key in keys:
            if self._subjects[key][0] == parent:
                returnvalue.append((key, depth))
                # recurse
                if len(self._subjects[key]) > 1:
                    returnvalue += self.subject_tree(key, depth+1)
        return returnvalue

    security.declareProtected('View',
                              'subject_form_tree')
    def subject_form_tree(self, parent=None, depth=0):
        """
        Returns a list of tuples (depth * 2 * '&nbsp;' + subject,
        subject) that makes it easy to create a tree in formulator
        forms
        """
        returnvalue = []
        keys = self._subjects.keys()
        keys.sort()
        for key in keys:
            if self._subjects[key][0] == parent:
                returnvalue.append((depth * 2 * '&nbsp;' + key, key))
                # recurse
                if len(self._subjects[key]) > 1:
                    returnvalue += self.subject_form_tree(key, depth+1)
        return returnvalue

    security.declareProtected('View',
                              'target_audiences')
    def target_audiences(self):
        """Returns a flat list of target audiences
        """
        return self._target_audiences.keys()

    security.declareProtected('View',
                              'target_audience_tree')
    def target_audience_tree(self, parent=None, depth=0):
        """
        Returns a list of tuples (target_audience, depth) that makes
        it easy to create a tree
        """
        returnvalue = []
        keys = self._target_audiences.keys()
        keys.sort()
        for key in keys:
            if self._target_audiences[key][0] == parent:
                returnvalue.append((key, depth))
                # recurse
                if len(self._target_audiences[key]) > 1:
                    returnvalue += self.target_audience_tree(key, depth+1)
        return returnvalue

    security.declareProtected('View',
                              'target_audience_form_tree')
    def target_audience_form_tree(self, parent=None, depth=0):
        """
        Returns a list of tuples (depth * 2 * '&nbsp;' +
        target_audience, target_audience) that makes it easy to create
        a tree in formulator-forms
        """
        returnvalue = []
        keys = self._target_audiences.keys()
        keys.sort()
        for key in keys:
            if self._target_audiences[key][0] == parent:
                returnvalue.append((depth * 2 * '&nbsp;' + key, key))
                # recurse
                if len(self._target_audiences[key]) > 1:
                    returnvalue += self.target_audience_form_tree(key, depth+1)
        return returnvalue

    security.declareProtected('Setup ServiceNews',
                              'manage_add_subject')
    def manage_add_subject(self, REQUEST):
        """Add a subject"""
        if not REQUEST.has_key('subject') or not REQUEST.has_key('parent') or REQUEST['subject'] == '':
            return self.edit_tab(manage_tabs_message='No subject or parent specified')

        if REQUEST['parent']:
            try:
                self.add_subject(unicode(REQUEST['subject'], 'UTF-8'), unicode(REQUEST['parent'], 'UTF-8'))
            except DuplicateError, e:
                return self.edit_tab(manage_tabs_message=e)
        else:
            try:
                self.add_subject(unicode(REQUEST['subject'], 'UTF-8'))
            except DuplicateError, e:
                return self.edit_tab(manage_tabs_message=e)

        return self.edit_tab(manage_tabs_message='Subject %s added' % unicode(REQUEST['subject'], 'UTF-8'))

    security.declareProtected('Setup ServiceNews',
                              'manage_remove_subject')
    def manage_remove_subject(self, REQUEST):
        """Remove a subject"""
        if not REQUEST.has_key('subjects'):
            return self.edit_tab(manage_tabs_message='No subjects specified')

        subs = [unicode(s, 'UTF-8') for s in REQUEST['subjects']]
        for subject in subs:
            try:
                self.remove_subject(subject)
            except (KeyError, NotEmptyError), e:
                return self.edit_tab(manage_tabs_message=e)

        return self.edit_tab(manage_tabs_message='Subjects %s removed' % ', '.join(subs))
        
    security.declareProtected('Setup ServiceNews',
                              'manage_add_target_audience')
    def manage_add_target_audience(self, REQUEST):
        """Add a target_audience"""
        if (not REQUEST.has_key('target_audience') or
            not REQUEST.has_key('parent') or REQUEST['target_audience'] == ''):
            return self.edit_tab(manage_tabs_message='No target audience or parent specified')

        if REQUEST['parent']:
            try:
                self.add_target_audience(unicode(REQUEST['target_audience'], 'UTF-8'), unicode(REQUEST['parent'], 'UTF-8'))
            except DuplicateError, e:
                return self.edit_tab(manage_tabs_message=e)
        else:
            try:
                self.add_target_audience(unicode(REQUEST['target_audience'], 'UTF-8'))
            except DuplicateError, e:
                return self.edit_tab(manage_tabs_message=e)

        return self.edit_tab(manage_tabs_message='Target audience %s added' % unicode(REQUEST['target_audience'], 'UTF-8'))

    security.declareProtected('Setup ServiceNews',
                              'manage_remove_target_audience')
    def manage_remove_target_audience(self, REQUEST):
        """Remove a target_audience"""
        if not REQUEST.has_key('target_audiences'):
            return self.edit_tab(manage_tabs_message='No target audience specified')

        tas = [unicode(t, 'UTF-8') for t in REQUEST['target_audiences']]
        for target_audience in tas:
            try:
                self.remove_target_audience(target_audience)
            except (KeyError, NotEmptyError), e:
                return self.edit_tab(manage_tabs_message=e)

        return self.edit_tab(manage_tabs_message='Target audiences %s removed' % ', '.join(tas))

    security.declareProtected('Setup ServiceNews',
                              'manage_rename_start')
    def manage_rename_start(self, REQUEST):
        """Rename one or more items"""
        if not REQUEST.has_key('subjects') and not REQUEST.has_key('target_audiences'):
            return self.edit_tab(manage_tabs_message='No items selected to rename')
        return self.manage_rename_view()

    security.declareProtected('Setup ServiceNews', 
                              'manage_rename_subjects')
    def manage_rename_subjects(self, REQUEST):
        """Rename subjects"""
        illegal = []
        for name, value in REQUEST.form.items():
            name = unicode(name, 'UTF-8')
            value = unicode(value, 'UTF-8')
            if value in self._subjects.keys():
                illegal.append(value)
            else:
                self._subjects[value] = self._subjects[name]
                del self._subjects[name]
        if illegal:
            return self.edit_tab(manage_tabs_message='Items %s could not be renamed (name already in use).' % ', '.join(illegal))
        else:
            return self.edit_tab(manage_tabs_message='Items renamed')

    security.declareProtected('Setup ServiceNews', 
                              'manage_rename_target_audiences')
    def manage_rename_target_audiences(self, REQUEST):
        """Rename target audiences"""
        illegal = []
        for name, value in REQUEST.form.items():
            name = unicode(name, 'UTF-8')
            value = unicode(value, 'UTF-8')
            if value in self._target_audiences.keys():
                illegal.append(value)
            else:
                self._target_audiences[value] = self._target_audiences[name]
                del self._target_audiences[name]
        if illegal:
            return self.edit_tab(manage_tabs_message='Items %s could not be renamed (name already in use).' % ', '.join(illegal))
        else:
            return self.edit_tab(manage_tabs_message='Items renamed')

Globals.InitializeClass(ServiceNews)

manage_addServiceNewsForm = PageTemplateFile(
        'www/serviceNewsAdd', globals(),
        __name__ = 'manage_addServiceNewsForm')

def manage_addServiceNews(self, id, title='', REQUEST=None):
    """Add service to folder
    """
    # add actual object
    id = self._setObject(id, ServiceNews(id, unicode(title, 'UTF-8')))
    # respond to the add_and_edit button if necessary
    add_and_edit(self, id, REQUEST)
    return ''
