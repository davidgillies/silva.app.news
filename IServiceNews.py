# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.2 $

from Interface import Base

class IServiceNews(Base):
    """ServiceNews is a service that provides lists of subjects and target_audiences
    to Filter-objects (e.g. NewsFilter, AgendaFilter) and a front-end to the manager
    to edit these lists. The lists are dicts with the content as key and a a list of parent (first item)
    and children (the rest of the items) as value
    """

    def add_subject(self, subject, parent):
        """Adds a subject to the list of subjects under parent (if parent is None, the subject
        is added to the root)
        """

    def add_target_audience(self, subject, parent):
        """Adds a target_audience to the list of target_audiences under parent (if parent is None, the
        target_audience is added to the root)
        """

    def remove_subject(self, subject):
        """Removes the subject from the list of subjects
        """

    def remove_target_audience(self, target_audience):
        """Removes the target_audience from the list of target_audiences
        """

    # ACCESSORS
    def subjects(self):
        """Return the list of subjects
        """

    def subject_tree(self):
        """Returns a list of tuples (indent, subject) containing each subject in the subjectlist
        """

    def subject_form_tree(self):
        """Returns a list of tuples (indent * 2 * '&nbsp;' + subject, subject) containing each subject
        in the subjectlist, for use with formulator
        """

    def target_audience_form_tree(self):
        """Returns a list of tuples (indent * 2 * '&nbsp;' + target_audience, target_audience) containing
        each target_audience in the target_audiencelist, for use with formulator
        """

    def target_audiences(self):
        """Return the list of target_audiences
        """

    def target_audience_tree(self):
        """Returns a list of tuples (indent, target_audience) containing each target_audience in the subjectlist
        """
