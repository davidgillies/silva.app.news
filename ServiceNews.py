# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $
import Globals
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.Silva.helpers import add_and_edit
from IServiceNews import IServiceNews

class NotEmptyError(Exception):
    pass

class DuplicateError(Exception):
    pass

class ServiceNews(SimpleItem):
    """This object provides lists of subjects and target_audiences for Filters
    """
    __implements__ = IServiceNews
    security = ClassSecurityInfo()
    meta_type = 'Silva ServiceNews'
    manage_options = (
                      {'label': 'Edit', 'action': 'edit_tab'},
                      {'label': 'Info', 'action': 'info_tab'}
                      ) + SimpleItem.manage_options

    edit_tab = PageTemplateFile('www/serviceNewsEditTab', globals(), __name__='edit_tab')
    info_tab = PageTemplateFile('www/serviceNewsInfoTab', globals(), __name__='info_tab')

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self._subjects = {}
        self._target_audiences = {}
        self._locations = {}
        self._common_infos = {}
        self._specific_infos = {}

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
        """Adds a target audience to the dict, first item in the value is the parent
        """
        if self._target_audiences.has_key(target_audience):
            message = "%s is already in the list of target audiences" % target_audience
            raise DuplicateError, message
        self._target_audiences[target_audience] = [parent]
        if parent:
            self._target_audiences[parent].append(target_audience)
        self._p_changed = 1

    security.declareProtected('Setup ServiceNews',
                              'add_location')
    def add_location(self, location):
        """Adds the subject to the dict, no parents or children
        """
        if self._locations.has_key(location):
            message = "%s is already in the list of locations" % location
            raise DuplicateError, message
        self._locations[location] = 1
        self._p_changed = 1

    security.declareProtected('Setup ServiceNews',
                              'add_common_info')
    def add_common_info(self, common_info):
        """Adds the common_info to the dict, no parents or children
        """
        if self._common_infos.has_key(common_info):
            message = "%s is already in the list of common_info-items" % common_info
            raise DuplicateError, message
        self._common_infos[common_info] = 1
        self._p_changed = 1

    security.declareProtected('Setup ServiceNews',
                              'add_specific_info')
    def add_specific_info(self, specific_info):
        """Adds the specific_info to the dict, no parents or children
        """
        if self._specific_infos.has_key(specific_info):
            message = "%s is already in the list of specific_info-items" % specific_info
            raise DuplicateError, message
        self._specific_infos[specific_info] = 1
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

    security.declareProtected('Setup ServiceNews',
                              'remove_location')
    def remove_location(self, location):
        """Removes a location from the dict
        """
        if not self._locations.has_key(location):
            message = "%s cannot be found in the list of locations" % location
            raise KeyError, message
        del(self._locations[location])
        self._p_changed = 1

    security.declareProtected('Setup ServiceNews',
                              'remove_common_info')
    def remove_common_info(self, common_info):
        """Removes a common_info from the dict
        """
        if not self._common_infos.has_key(common_info):
            message = "%s cannot be found in the list of common_info-items" % common_info
            raise KeyError, message
        del(self._common_infos[common_info])
        self._p_changed = 1

    security.declareProtected('Setup ServiceNews',
                              'remove_specific_info')
    def remove_specific_info(self, specific_info):
        """Removes a specific_info from the dict
        """
        if not self._specific_infos.has_key(specific_info):
            message = "%s cannot be found in the list of specific_info-items" % specific_info
            raise KeyError, message
        del(self._specific_infos[specific_info])
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
        """Returns a list of tuples (subject, depth) that makes it easy to create a tree
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
        """Returns a list of tuples (depth * 2 * '&nbsp;' + subject, subject) that makes it
        easy to create a tree in formulator forms
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
        """Returns a list of tuples (target_audience, depth) that makes it easy to create a tree
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
        """Returns a list of tuples (depth * 2 * '&nbsp;' + target_audience, target_audience) that makes it
        easy to create a tree in formulator-forms
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

    security.declareProtected('View',
                              'locations')
    def locations(self):
        """Returns a flat list of all locations
        """
        locations = self._locations.keys()
        locations.sort()
        return locations

    security.declareProtected('View',
                              'common_infos')
    def common_infos(self):
        """Returns a flat list of all common_infos
        """
        common_infos = self._common_infos.keys()
        common_infos.sort()
        return common_infos

    security.declareProtected('View',
                              'specific_infos')
    def specific_infos(self):
        """Returns a flat list of all specific_infos
        """
        specific_infos = self._specific_infos.keys()
        specific_infos.sort()
        # send an empty option as well, so the user can choose not to provide any specific info...
        specific_infos = ['Geen informatie'] + specific_infos
        return specific_infos

    security.declareProtected('Setup ServiceNews',
                              'manage_add_subject')
    def manage_add_subject(self, REQUEST):
        """Add a subject"""
        if not REQUEST.has_key('subject') or not REQUEST.has_key('parent') or REQUEST['subject'] == '':
            return self.edit_tab(manage_tabs_message='No subject or parent specified')

        if REQUEST['parent']:
            try:
                self.add_subject(REQUEST['subject'], REQUEST['parent'])
            except DuplicateError, e:
                print "Exception"
                return self.edit_tab(manage_tabs_message=e)
        else:
            try:
                self.add_subject(REQUEST['subject'])
            except DuplicateError, e:
                print "Exception"
                return self.edit_tab(manage_tabs_message=e)

        return self.edit_tab(manage_tabs_message='Subject %s added' % REQUEST['subject'])

    security.declareProtected('Setup ServiceNews',
                              'manage_remove_subject')
    def manage_remove_subject(self, REQUEST):
        """Remove a subject"""
        if not REQUEST.has_key('subjects'):
            return self.edit_tab(manage_tabs_message='No subjects specified')

        for subject in REQUEST['subjects']:
            try:
                self.remove_subject(subject)
            except (KeyError, NotEmptyError), e:
                return self.edit_tab(manage_tabs_message=e)

        return self.edit_tab(manage_tabs_message='Subjects %s removed' % str(REQUEST['subjects']))

    security.declareProtected('Setup ServiceNews',
                              'manage_add_target_audience')
    def manage_add_target_audience(self, REQUEST):
        """Add a target_audience"""
        if not REQUEST.has_key('target_audience') or not REQUEST.has_key('parent') or REQUEST['target_audience'] == '':
            return self.edit_tab(manage_tabs_message='No target audience or parent specified')

        if REQUEST['parent']:
            try:
                self.add_target_audience(REQUEST['target_audience'], REQUEST['parent'])
            except DuplicateError, e:
                return self.edit_tab(manage_tabs_message=e)
        else:
            try:
                self.add_target_audience(REQUEST['target_audience'])
            except DuplicateError, e:
                return self.edit_tab(manage_tabs_message=e)

        return self.edit_tab(manage_tabs_message='Target audience %s added' % REQUEST['target_audience'])

    security.declareProtected('Setup ServiceNews',
                              'manage_remove_target_audience')
    def manage_remove_target_audience(self, REQUEST):
        """Remove a target_audience"""
        if not REQUEST.has_key('target_audiences'):
            return self.edit_tab(manage_tabs_message='No target audience specified')

        for target_audience in REQUEST['target_audiences']:
            try:
                self.remove_target_audience(target_audience)
            except (KeyError, NotEmptyError), e:
                return self.edit_tab(manage_tabs_message=e)

        return self.edit_tab(manage_tabs_message='Target audiences %s removed' % str(REQUEST['target_audiences']))

    security.declareProtected('Setup ServiceNews',
                              'manage_add_location')
    def manage_add_location(self, REQUEST):
        """Add a location"""
        if not REQUEST.has_key('location') or REQUEST['location'] == '':
            return self.edit_tab(manage_tabs_message='No location specified')

        try:
            self.add_location(REQUEST['location'])
        except DuplicateError, e:
            return self.edit_tab(manage_tabs_message=e)

        return self.edit_tab(manage_tabs_message='Location %s added' % REQUEST['location'])

    security.declareProtected('Setup ServiceNews',
                              'manage_remove_location')
    def manage_remove_location(self, REQUEST):
        """Remove a location"""
        if not REQUEST.has_key('location'):
            return self.edit_tab(manage_tabs_message='No locations specified')

        for location in REQUEST['locations']:
            try:
                self.remove_location(location)
            except KeyError, e:
                return self.edit_tab(manage_tabs_message=e)

        return self.edit_tab(manage_tabs_message='Locations %s removed' % str(REQUEST['locations']))

    security.declareProtected('Setup ServiceNews',
                              'manage_add_common_info')
    def manage_add_common_info(self, REQUEST):
        """Add a common_info"""
        if not REQUEST.has_key('common_info') or REQUEST['common_info'] == '':
            return self.edit_tab(manage_tabs_message='No common info item specified')

        try:
            self.add_common_info(REQUEST['common_info'])
        except DuplicateError, e:
            return self.edit_tab(manage_tabs_message=e)

        return self.edit_tab(manage_tabs_message='Common info item %s added' % REQUEST['common_info'])

    security.declareProtected('Setup ServiceNews',
                              'manage_remove_common_info')
    def manage_remove_common_info(self, REQUEST):
        """Remove a common_info"""
        if not REQUEST.has_key('common_info'):
            return self.edit_tab(manage_tabs_message='No common info items specified')

        for common_info in REQUEST['common_infos']:
            try:
                self.remove_common_info(common_info)
            except KeyError, e:
                return self.edit_tab(manage_tabs_message=e)

        return self.edit_tab(manage_tabs_message='Common info items %s removed' % str(REQUEST['common_infos']))

    security.declareProtected('Setup ServiceNews',
                              'manage_add_specific_info')
    def manage_add_specific_info(self, REQUEST):
        """Add a specific_info"""
        if not REQUEST.has_key('specific_info') or REQUEST['specific_info'] == '':
            return self.edit_tab(manage_tabs_message='No specific info item specified')

        try:
            self.add_specific_info(REQUEST['specific_info'])
        except DuplicateError, e:
            return self.edit_tab(manage_tabs_message=e)

        return self.edit_tab(manage_tabs_message='Specific info item %s added' % REQUEST['specific_info'])

    security.declareProtected('Setup ServiceNews',
                              'manage_remove_specific_info')
    def manage_remove_specific_info(self, REQUEST):
        """Remove a specific_info"""
        if not REQUEST.has_key('specific_info'):
            return self.edit_tab(manage_tabs_message='No specific info items specified')

        for specific_info in REQUEST['specific_infos']:
            try:
                self.remove_specific_info(specific_info)
            except KeyError, e:
                return self.edit_tab(manage_tabs_message=e)

        return self.edit_tab(manage_tabs_message='Specific info items %s removed' % str(REQUEST['specific_infos']))

Globals.InitializeClass(ServiceNews)

manage_addServiceNewsForm = PageTemplateFile(
        'www/serviceNewsAdd', globals(),
        __name__ = 'manage_addServiceNewsForm')

def manage_addServiceNews(self, id, title='', REQUEST=None):
    """Add service to folder
    """
    # add actual object
    id = self._setObject(id, ServiceNews(id, title))
    # respond to the add_and_edit button if necessary
    add_and_edit(self, id, REQUEST)
    return ''
