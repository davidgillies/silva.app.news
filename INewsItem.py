from Interface import Base

class INewsItem(Base):
    """Silva News NewsItem interface
    """
    def in_filter(self, filter):
        """Returns true if the item should appear in filter, false if not
        """
        pass

    def set_filter(self, filter_path, on_or_off):
        """Updates the list of filters where the item should
        appear
        """
        pass

    def filters(self):
        """Returns the list of filters
        """
        pass

    def creation_datetime(self):
        """Returns the time of creation
        """
        pass
