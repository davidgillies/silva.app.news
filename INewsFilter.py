# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $
from Interfaces import Base

class INewsFilter(Base):
    """NewsFilter object, a small object that shows a couple
    of different screens to different users, a filter for all NewsItem-objects
    to the editor and a filter (containing some different info) for all
    published NewsItem-objects for the end-users.
    """
    def keep_to_path(self):
        """Returns true if the item should keep to path
        """

    def number_to_show(self):
        """Returns true if the item should keep to path
        """

    def subjects(self):
        """Returns the list of subjects
        """

    def target_audiences(self):
        """Returns the list of target audiences
        """

    def set_keep_to_path(self, value):
        """Removes the filter from the list of filters where the item
        should appear
        """

    def set_subject(self, subject, on_or_off):
        """Updates the list of subjects
        """

    def set_target_audience(self, target_audience, on_or_off):
        """Updates the list of target_audiences
        """

    def set_number_to_show(self, number):
        """Updates the list of target_audiences
        """

    def get_all_items(self, meta_types=['Silva News Article']):
        """Returns all items, only to be used on the back-end
        """

    def get_all_public_items(self, meta_types=['Silva News Article']):
        """Returns all published items
        """

    def get_last_public_items(self, meta_types=['Silva News Article']):
        """Returns the last self._number_to_show published items
        """

    def _check_meta_types(self, meta_types):
        """Raises an exception if one of the meta_types is not in an allowed list of meta_types
        """
