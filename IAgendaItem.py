from Interface import Base

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
