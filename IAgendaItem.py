from Interface import Base

class IAgendaItem(Base):
    """Silva AgendaItem, interface for some agendaitems
    """
    def start_datetime(self):
        """Returns start_datetime for clients
        """
        pass

    def end_datetime(self):
        """Returns end_datetime for clients
        """
        pass

    def location(self):
        """Returns location for clients
        """
        pass

    def info(self):
        """Returns info for clients
        """
        pass
