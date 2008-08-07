# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.17 $

from zope.interface import implements

# Zope
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

# Silva
from Products.Silva.Asset import Asset
import Products.Silva.SilvaPermissions as SilvaPermissions

# SilvaNews interfaces
from interfaces import IFilter

class Filter(Asset):
    """
    Filter object, a small object that shows a couple of different
    screens to different users, a filter for all NewsItem-objects to
    the editor and a filter (containing some different info) for all
    published NewsItem-objects for the end-users.
    """
    security = ClassSecurityInfo()
    
    implements(IFilter)

    _allowed_source_types = ['Silva News Publication']

    def __init__(self, id):
        Filter.inheritedAttribute('__init__')(self, id)
        self._subjects = []
        self._target_audiences = []

    # ACCESSORS

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'subjects')
    def subjects(self):
        """Returns a list of subjects
        """
        return self._subjects

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'target_audiences')
    def target_audiences(self):
        """Returns a list of target audiences
        """
        return self._target_audiences

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_subjects')
    def set_subjects(self, subjects):
        """Sets the subjects"""
        self._subjects = subjects
        self.synchronize_with_service()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_target_audiences')
    def set_target_audiences(self, ta):
        self._target_audiences = ta
        self.synchronize_with_service()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'synchronize_with_service')
    def synchronize_with_service(self):
        """Checks whether the lists of subjects and target_audiences
        only contain items that the service_news-lists contain (to remove
        items from the object's list that are removed in the service)
        """
        # XXX This isn't called yet from anywhere since the methods it was
        # called from are replaced by metadata functionality
        service_subjects = [s[0] for s in self.service_news.subjects()]
        service_target_audiences = [t[0] for t in self.service_news.target_audiences()]

        removed_subjects = []
        removed_target_audiences = []

        subjects = self._subjects[:]
        target_audiences = self._target_audiences[:]

        new_subs = []
        for i in range(len(subjects)):
            s = subjects[i]
            if  s in service_subjects:
                new_subs.append(s)
        
        new_tas = []
        for i in range(len(target_audiences)):
            ta = target_audiences[i]
            if ta in service_target_audiences:
                new_tas.append(ta)

        self._subjects = new_subs
        self._target_audiences = new_tas

        self.reindex_object()
        return removed_subjects + removed_target_audiences

InitializeClass(Filter)
