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

class IAgendaItem(Base):
    """Silva News AgendaItem, interface for some agendaitems
    """
    def protected_start_datetime(self):
        """Returns start_datetime for filters
        """
        pass

    def start_datetime(self):
        """Returns start_datetime for clients
        """
        pass

    def protected_end_datetime(self):
        """Returns end_datetime for filters
        """
        pass

    def end_datetime(self):
        """Returns end_datetime for clients
        """
        pass

    def protected_location(self):
        """Returns location for filters
        """
        pass

    def location(self):
        """Returns location for clients
        """
        pass

    def protected_info(self):
        """Returns info for filters
        """
        pass

    def info(self):
        """Returns info for clients
        """
        pass
